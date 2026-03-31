import asyncio
import json
import uuid
import httpx
import os
import aiofiles
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from duckduckgo_search import DDGS

from app.models.chat import AIChatSession, AIChatMessage, UserAPIKey
from app.models.user import User
from app.models.system import SystemConfig
from app.api.auth import get_current_user
from app.core.encryption import get_encryption_service
from app.socketio_server import sio

router = APIRouter()

# Global state for queue
local_llm_lock = asyncio.Lock()
waiting_queue = [] # List of dicts: {"req_id": str, "user_id": str}

async def notify_queue_positions():
    """Broadcast current queue position to all waiting users"""
    for i, req in enumerate(waiting_queue):
        position = i + 1
        await sio.emit(
            'ai_queue_status', 
            {'position': position}, 
            room=f"user_{req['user_id']}"
        )

# Pydantic models
class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    prompt: str
    provider: str = 'local' # 'local', 'openai', 'anthropic', 'deepseek', 'civitai'
    model_name: Optional[str] = 'deepseek-r1:7b' # or deepseek-r1:1.5b

class APIKeyRequest(BaseModel):
    provider_name: str
    api_key: str

@router.get("/keys")
async def get_my_keys(current_user: User = Depends(get_current_user)):
    keys = UserAPIKey.objects(user=current_user)
    return [{"provider_name": k.provider_name, "created_at": k.created_at} for k in keys]

@router.post("/keys")
async def save_api_key(req: APIKeyRequest, current_user: User = Depends(get_current_user)):
    enc_service = get_encryption_service()
    encrypted_key, _ = enc_service.encrypt(req.api_key.encode('utf-8'))
    
    # Update or create
    existing = UserAPIKey.objects(user=current_user, provider_name=req.provider_name).first()
    if existing:
        existing.encrypted_key = encrypted_key
        existing.save()
    else:
        UserAPIKey(
            user=current_user,
            provider_name=req.provider_name,
            encrypted_key=encrypted_key
        ).save()
    
    return {"status": "success"}

@router.get("/sessions")
async def get_sessions(current_user: User = Depends(get_current_user)):
    sessions = AIChatSession.objects(user=current_user).order_by('-updated_at')
    return [{"id": str(s.id), "title": s.title, "updated_at": s.updated_at} for s in sessions]

@router.post("/sessions")
async def create_session(title: str, current_user: User = Depends(get_current_user)):
    session = AIChatSession(user=current_user, title=title)
    session.save()
    return {"id": str(session.id), "title": session.title}

class RenameRequest(BaseModel):
    title: str

@router.put("/sessions/{session_id}")
async def rename_session(session_id: str, req: RenameRequest, current_user: User = Depends(get_current_user)):
    try:
        session = AIChatSession.objects(id=session_id, user=current_user).first()
    except Exception:
        raise HTTPException(status_code=404, detail="Invalid session ID")
        
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session.title = req.title
    session.save()
    return {"status": "success", "title": session.title}

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, current_user: User = Depends(get_current_user)):
    try:
        session = AIChatSession.objects(id=session_id, user=current_user).first()
        if session:
            AIChatMessage.objects(session=session).delete()
            session.delete()
            return {"status": "success"}
    except Exception:
        pass
    raise HTTPException(status_code=404, detail="Session not found")

@router.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, current_user: User = Depends(get_current_user)):
    try:
        session = AIChatSession.objects(id=session_id, user=current_user).first()
    except Exception:
        raise HTTPException(status_code=404, detail="Invalid session ID")
        
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = AIChatMessage.objects(session=session).order_by('timestamp')
    return [{"role": m.role, "content": m.content, "timestamp": m.timestamp} for m in messages]

def perform_web_search_sync(query: str) -> str:
    """Use duckduckgo to search and return formatted text synchronously"""
    try:
        results = DDGS().text(query, max_results=3)
        formatted_results = "\n".join([
            f"Source: {r['title']} ({r['href']})\nSnippet: {r['body']}"
            for r in results
        ])
        return f"Internet Search Results for '{query}':\n{formatted_results}"
    except Exception as e:
        return f"Search failed: {str(e)}"

async def generate_response_stream(req: ChatRequest, current_user: User, system_prompt: str, context_messages: list):
    """Generator for streaming LLM response, handling tags"""
    
    provider = req.provider.lower()
    
    # Power Saver AI Limitation
    config = SystemConfig.get_config()
    if config.power_mode == 'power_saver' and config.ps_disable_ai and provider == 'local':
        req.model_name = "deepseek-r1:1.5b"
        
    headers = {}
    url = ""
    payload = {}
    
    messages_payload = [{"role": "system", "content": system_prompt}]
    for m in context_messages:
        messages_payload.append({"role": m.role, "content": m.content})
    messages_payload.append({"role": "user", "content": req.prompt})
    
    is_first_message = False
    
    session = None
    if req.session_id:
        try:
            session = AIChatSession.objects(id=req.session_id).first()
        except:
            pass
            
    if not session:
        session = AIChatSession(user=current_user, title=req.prompt[:50] + "...").save()
        is_first_message = True
    elif AIChatMessage.objects(session=session).count() == 0:
        is_first_message = True
    
    AIChatMessage(session=session, role='user', content=req.prompt).save()

    raw_key = None
    if provider != 'local':
        user_key = UserAPIKey.objects(user=current_user, provider_name=provider).first()
        if not user_key:
            yield f"data: {json.dumps({'error': f'API key for {provider} not found.'})}\n\n"
            return
            
        enc_service = get_encryption_service()
        try:
            raw_key = enc_service.decrypt(user_key.encrypted_key).decode('utf-8')
        except Exception as e:
            yield f"data: {json.dumps({'error': 'Failed to decrypt API key.'})}\n\n"
            return
            
        if provider == 'openai':
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {raw_key}", "Content-Type": "application/json"}
            payload = {"model": req.model_name or "gpt-4o", "messages": messages_payload, "stream": True}
        elif provider == 'anthropic':
            url = "https://api.anthropic.com/v1/messages"
            headers = {"x-api-key": raw_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
            payload = {"model": req.model_name or "claude-3-opus-20240229", "messages": [m for m in messages_payload if m['role'] != 'system'], "system": system_prompt, "stream": True, "max_tokens": 4096}
        elif provider == 'deepseek':
            url = "https://api.deepseek.com/chat/completions"
            headers = {"Authorization": f"Bearer {raw_key}", "Content-Type": "application/json"}
            payload = {"model": req.model_name or "deepseek-reasoner", "messages": messages_payload, "stream": True}
        else:
            yield f"data: {json.dumps({'error': f'Unsupported external provider: {provider}'})}\n\n"
            return
    else:
        url = "http://localhost:11434/api/chat"
        # In power saver, req.model_name is already overridden to 1.5b above
        payload = {"model": req.model_name or "deepseek-r1:7b", "messages": messages_payload, "stream": True}

    full_response = ""
    in_search_tag = False
    in_file_tag = False
    
    # helper for sending requests
    async def run_llm_request(current_payload):
        nonlocal full_response, in_search_tag, in_file_tag, messages_payload
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", url, headers=headers, json=current_payload) as response:
                if response.status_code != 200:
                    err_text = await response.aread()
                    yield f"data: {json.dumps({'error': f'API {response.status_code}: {err_text.decode('utf-8')}'})}\n\n"
                    return
                
                async for chunk in response.aiter_lines():
                    if not chunk: continue
                    chunk_text = ""
                    try:
                        if provider in ['local']:
                            data = json.loads(chunk)
                            chunk_text = data.get("message", {}).get("content", "")
                        elif provider == 'anthropic':
                            if chunk.startswith("data: "):
                                data = json.loads(chunk[6:])
                                if data.get("type") == "content_block_delta":
                                    chunk_text = data.get("delta", {}).get("text", "")
                        else: # openai, deepseek standard format
                            if chunk.startswith("data: "):
                                if chunk == "data: [DONE]": break
                                data = json.loads(chunk[6:])
                                if data.get("choices") and len(data["choices"]) > 0:
                                    chunk_text = data["choices"][0].get("delta", {}).get("content", "") or ""
                    except Exception as e:
                        continue
                        
                    if not chunk_text: continue
                    full_response += chunk_text
                    
                    if "<search>" in full_response and "</search>" not in full_response:
                        in_search_tag = True
                        continue
                    if in_search_tag and "</search>" in full_response:
                        start_idx = full_response.find("<search>") + 8
                        end_idx = full_response.find("</search>")
                        query = full_response[start_idx:end_idx].strip()
                        
                        yield f"data: {json.dumps({'status': 'searching', 'query': query})}\n\n"
                        
                        search_results = await asyncio.to_thread(perform_web_search_sync, query)
                        
                        AIChatMessage(session=session, role='assistant', content=full_response[:start_idx-8]).save()
                        AIChatMessage(session=session, role='tool', content=search_results).save()
                        
                        messages_payload.append({"role": "assistant", "content": full_response[:start_idx-8]})
                        messages_payload.append({"role": "system", "content": search_results + "\nContinue your response."})
                        
                        yield f"data: {json.dumps({'status': 'search_complete'})}\n\n"
                        
                        # Stop this stream
                        in_search_tag = False
                        yield "<SEARCH_RESTART>"
                        return

                    if "<create_file " in full_response and "</create_file>" not in full_response:
                        in_file_tag = True
                        continue
                    if in_file_tag and "</create_file>" in full_response:
                        start_tag_idx = full_response.find("<create_file filename=\"") + 23
                        end_name_idx = full_response.find("\">", start_tag_idx)
                        filename_raw = full_response[start_tag_idx:end_name_idx]
                        
                        content_start_idx = end_name_idx + 2
                        content_end_idx = full_response.find("</create_file>")
                        
                        file_content = full_response[content_start_idx:content_end_idx]
                        
                        os.makedirs("app/storage/temp_downloads", exist_ok=True)
                        file_ext = os.path.splitext(filename_raw)[1]
                        file_base = os.path.splitext(filename_raw)[0]
                        unique_id = uuid.uuid4().hex[:8]
                        safe_filename = f"{file_base}_{unique_id}{file_ext}"
                        
                        file_path = f"app/storage/temp_downloads/{safe_filename}"
                        async with aiofiles.open(file_path, "w") as f:
                            await f.write(file_content)
                            
                        download_link = f"\n\n[Download {safe_filename}](/api/downloads/{safe_filename})\n\n"
                        
                        tag_start = full_response.find("<create_file ")
                        tag_end = content_end_idx + 14
                        full_response = full_response[:tag_start] + download_link + full_response[tag_end:]
                        
                        yield f"data: {json.dumps({'content': download_link})}\n\n"
                        in_file_tag = False
                        continue
                    
                    if not in_search_tag and not in_file_tag:
                        yield f"data: {json.dumps({'content': chunk_text})}\n\n"
                        
            # Output session ID to client when done
            yield f"data: {json.dumps({'session_id': str(session.id)})}\n\n"

    # Execute generator, handle restart if search happened
    while True:
        restart = False
        if provider == 'anthropic':
            payload["messages"] = [m for m in messages_payload if m['role'] != 'system']
        else:
            payload["messages"] = messages_payload
            
        async for chunk in run_llm_request(payload):
            if chunk == "<SEARCH_RESTART>":
                restart = True
                break
            yield chunk
            
        if not restart:
            break

    AIChatMessage(session=session, role='assistant', content=full_response).save()

    if is_first_message:
        asyncio.create_task(auto_rename_session(str(session.id), req.prompt, provider, req.model_name or "deepseek-r1:7b", raw_key))

async def auto_rename_session(session_id: str, first_prompt: str, provider: str, model_name: str, raw_key: str):
    sys_prompt = "Respond ONLY with a 3-5 word descriptive title for a chat that begins with the following prompt. Do not use quotes, punctuation, or thinking processes."
    payload = {"model": model_name, "stream": False, "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": first_prompt}]}
    url = headers = None
    
    if provider == 'openai':
        url, headers = "https://api.openai.com/v1/chat/completions", {"Authorization": f"Bearer {raw_key}"}
    elif provider == 'anthropic':
        url, headers = "https://api.anthropic.com/v1/messages", {"x-api-key": raw_key, "anthropic-version": "2023-06-01"}
        payload = {"model": model_name, "max_tokens": 20, "system": sys_prompt, "messages": [{"role": "user", "content": first_prompt}]}
    elif provider == 'deepseek':
        url, headers = "https://api.deepseek.com/chat/completions", {"Authorization": f"Bearer {raw_key}"}
    elif provider == 'local':
        url, headers = "http://localhost:11434/api/chat", {}
        
    if not url: return

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                title = data.get("message", {}).get("content", "") if provider == 'local' else (data.get("content", [{}])[0].get("text", "") if provider == 'anthropic' else data.get("choices", [{}])[0].get("message", {}).get("content", ""))
                
                title = title.replace("<think>", "").replace("</think>", "").replace('"', '').strip()
                if '\n' in title: title = title.split('\n')[-1].strip()
                
                if title:
                    session = AIChatSession.objects(id=session_id).first()
                    session.title = title[:50]
                    session.save()
    except Exception:
        pass


@router.post("/chat")
async def ai_chat_endpoint(req: ChatRequest, current_user: User = Depends(get_current_user)):
    system_prompt = (
        "You are an advanced AI assistant. "
        "If you need to search the internet to answer a prompt, output exactly: <search>your query</search>. Wait for the system to provide the results. "
        "If the user asks you to create a downloadable file, wrap the exact file content inside <create_file filename=\"name.ext\">content</create_file>."
        "\nIMPORTANT: Make sure you provide continuing conversational text replying to the user AFTER you declare the search or file creation tools, otherwise they won't know it's finished!"
    )
    
    context_messages = []
    if req.session_id:
        try:
            session = AIChatSession.objects(id=req.session_id, user=current_user).first()
            if session:
                session.updated_at = datetime.utcnow()
                session.save()
                msgs_qs = AIChatMessage.objects(session=session).order_by('timestamp')
                context_messages = list(msgs_qs)[-20:]
        except:
            pass

    if req.provider.lower() == 'local':
        req_obj = {"req_id": str(uuid.uuid4()), "user_id": str(current_user.id)}
        waiting_queue.append(req_obj)
        await notify_queue_positions()
        
        async def queue_wrapper():
            try:
                while True:
                    await asyncio.sleep(0.5)
                    if len(waiting_queue) > 0 and waiting_queue[0]["req_id"] == req_obj["req_id"]:
                        if not local_llm_lock.locked():
                            await local_llm_lock.acquire()
                            break
                
                await sio.emit('ai_queue_status', {'position': 0, 'status': 'processing'}, room=f"user_{req_obj['user_id']}")
                
                async for chunk in generate_response_stream(req, current_user, system_prompt, context_messages):
                    yield chunk
            finally:
                if req_obj in waiting_queue:
                    waiting_queue.remove(req_obj)
                if local_llm_lock.locked():
                    local_llm_lock.release()
                await notify_queue_positions()
                
        return StreamingResponse(queue_wrapper(), media_type="text/event-stream")
    else:
        return StreamingResponse(
            generate_response_stream(req, current_user, system_prompt, context_messages),
            media_type="text/event-stream"
        )

@router.get("/downloads/{filename}")
async def download_ai_file(filename: str):
    file_path = f"app/storage/temp_downloads/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found or expired")
    return FileResponse(file_path, filename=filename)

def start_download_cleanup_task():
    async def cleanup_task():
        while True:
            await asyncio.sleep(3600)  # Hourly
            try:
                storage_dir = "app/storage/temp_downloads"
                if not os.path.exists(storage_dir):
                    continue
                cutoff = datetime.now() - timedelta(hours=72)
                for f in os.listdir(storage_dir):
                    fpath = os.path.join(storage_dir, f)
                    if os.path.isfile(fpath):
                        mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
                        if mtime < cutoff:
                            try:
                                os.remove(fpath)
                            except:
                                pass
            except Exception as e:
                print(f"Cleanup error: {e}")

    asyncio.create_task(cleanup_task())
