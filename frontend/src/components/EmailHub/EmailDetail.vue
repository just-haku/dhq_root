<template>
  <div class="email-detail-overlay" @click.self="$emit('close')">
    <div class="email-detail-container glass-panel">
      <div class="detail-header">
        <div class="sender-info">
          <div class="avatar">{{ senderInitial }}</div>
          <div>
            <h3>{{ email.sender_name }}</h3>
            <p>{{ email.sender_email }}</p>
          </div>
        </div>
        <button class="btn-icon" @click="$emit('close')">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <div class="detail-content">
        <div class="email-meta-card">
          <h2>{{ email.subject }}</h2>
          <div class="meta-row">
            <span class="label">Date:</span>
            <span>{{ formatDate(email.processed_at.$date) }}</span>
          </div>
          <div v-if="email.is_collaboration" class="ai-extracted-box mt-4">
            <h4><i class="fas fa-robot mr-2"></i> AI Extracted Data</h4>
            <div class="extraction-grid">
              <div class="item">
                <span class="label">Scope:</span>
                <input v-model="email.ai_data.scope" class="inline-input" />
              </div>
              <div class="item">
                <span class="label">Platform:</span>
                <input v-model="email.ai_data.platform" class="inline-input" />
              </div>
              <div class="item">
                <span class="label">Price:</span>
                <input v-model="email.ai_data.price" class="inline-input" />
              </div>
            </div>
            <button class="btn btn-primary btn-sm mt-4 w-full" @click="convertToCollaboration">
              <i class="fas fa-plus-circle mr-2"></i> Create Collaboration
            </button>
          </div>
        </div>

        <div class="email-body mt-6">
          {{ email.body }}
        </div>
        
        <div class="mt-8 flex gap-3 pb-2">
           <button class="btn btn-outline border-slate-600 text-slate-300">
               <i class="fas fa-reply mr-2"></i> Reply
           </button>
           <button class="btn bg-indigo-600 hover:bg-indigo-500 text-white" @click="showAIDraft = !showAIDraft">
               <i class="fas fa-robot mr-2"></i> AI Reply
           </button>
        </div>

        <!-- AI Drafting Area -->
        <div v-if="showAIDraft" class="ai-draft-section mt-6 pt-6 border-t border-slate-700/50">
          <div class="flex justify-between items-center mb-4">
            <h3 class="flex items-center gap-2">
              <i class="fas fa-robot text-primary"></i>
              AI Assistant Reply
            </h3>
            
            <select v-model="selectedAIProvider" @change="saveAIPreference" class="prompt-select text-sm bg-slate-900 border border-slate-700 text-white rounded px-2 py-1">
               <option value="local_deepseek">Local DeepSeek R1 7B</option>
               <option value="local_1.5b">Local DeepSeek R1 1.5B</option>
               <option value="openai">OpenAI (BYOK)</option>
               <option value="anthropic">Anthropic (BYOK)</option>
               <option value="deepseek">DeepSeek External (BYOK)</option>
            </select>
          </div>
          
          <div v-if="queuePosition > 0" class="queue-banner bg-indigo-900/50 text-indigo-200 p-2 text-center text-sm rounded mb-3">
              <i class="fas fa-spinner fa-spin mr-2"></i> You are position {{ queuePosition }} in queue...
          </div>
          <div v-if="isAISearching" class="queue-banner bg-blue-900/50 text-blue-200 p-2 text-center text-sm rounded mb-3">
              <i class="fas fa-globe fa-spin mr-2"></i> Searching the web for "{{ searchQueryActive }}"...
          </div>

          <div class="email-ai-chat border border-slate-700 rounded-xl bg-slate-900/50 flex flex-col" style="height: 400px;">
             <!-- Messages Area -->
             <div class="flex-grow overflow-y-auto p-4 flex flex-col gap-3 custom-scrollbar" ref="chatArea">
                <div v-if="activeChatContent.length === 0" class="text-slate-500 text-center mt-10">
                   <p>Start drafting a reply with AI assistance.</p>
                   <button class="btn btn-sm btn-outline mt-3" @click="injectEmailContext"><i class="fas fa-quote-right mr-2"></i> Quote Email Content</button>
                </div>
                <div v-for="(msg, i) in activeChatContent" :key="i" class="flex relative w-full mb-4" :class="msg.role === 'user' ? 'justify-end' : 'justify-start'">
                    <div v-if="msg.role !== 'user'" class="w-8 h-8 rounded-full flex-shrink-0 mr-3 mt-1 bg-slate-900 border border-indigo-500/30 overflow-hidden shadow-lg">
                        <img src="/ai_avatar.png" class="w-full h-full object-cover">
                    </div>
                    <div class="message-bubble text-sm" :class="msg.role === 'user' ? 'bg-blue-600 text-white px-4 py-2 rounded-xl rounded-br-sm max-w-[80%] whitespace-pre-wrap shadow-md' : 'text-slate-200 py-1 max-w-[90%]'">
                        <div v-if="msg.role === 'user'">{{ msg.content }}</div>
                        <template v-else>
                            <div v-if="msg.isTyping && !msg.content && !isAISearching" class="flex space-x-1 p-2 items-center bg-slate-800/40 rounded-lg inline-flex mt-1 border border-slate-700/50">
                                <div class="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
                                <div class="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                                <div class="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
                            </div>
                            <div v-else class="markdown-body ai-markdown" :class="{'streaming-cursor': msg.isTyping}" v-html="renderAIMessage(msg.content)"></div>
                        </template>
                    </div>
                </div>
             </div>
             
             <!-- Input Area -->
             <div class="p-3 border-t border-slate-700 flex gap-2 items-center bg-slate-800/80 rounded-b-xl">
                 <button class="w-10 h-10 flex-shrink-0 flex items-center justify-center rounded border border-slate-600 text-slate-300 hover:bg-slate-700 transition" @click="injectEmailContext" title="Quote Email">
                    <i class="fas fa-quote-right"></i>
                 </button>
                 <input 
                    type="text" 
                    v-model="newMessage"
                    placeholder="Ask the AI to draft a reply..."
                    class="flex-grow bg-slate-900 border border-slate-700 rounded-full px-4 py-2 text-white focus:outline-none focus:border-blue-500"
                    @keyup.enter="handleSendMessage"
                 />
                 <button 
                    class="w-10 h-10 flex-shrink-0 rounded-full flex items-center justify-center text-white transition-colors"
                    :class="newMessage.trim() ? 'bg-blue-600 hover:bg-blue-500' : 'bg-slate-700 text-slate-500'"
                    @click="handleSendMessage"
                    :disabled="!newMessage.trim()"
                 >
                    <i class="fas fa-paper-plane"></i>
                 </button>
             </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, onUnmounted } from 'vue'
import { apiGet, apiPost } from '@/utils/api'
import { showSuccess, showError } from '@/utils/notification'
import { io } from 'socket.io-client'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'
import mk from 'markdown-it-katex'

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        const highlighted = hljs.highlight(str, { language: lang }).value;
        return `<pre class="hljs relative group"><button class="copy-btn absolute top-2 right-2 opacity-0 group-hover:opacity-100 bg-slate-700 text-xs px-2 py-1 rounded transition-opacity" onclick="navigator.clipboard.writeText(decodeURIComponent('${encodeURIComponent(str)}'))">Copy</button><code class="language-${lang}">${highlighted}</code></pre>`;
      } catch (__) {}
    }
    return `<pre class="hljs relative group"><button class="copy-btn absolute top-2 right-2 opacity-0 group-hover:opacity-100 bg-slate-700 text-xs px-2 py-1 rounded transition-opacity" onclick="navigator.clipboard.writeText(decodeURIComponent('${encodeURIComponent(str)}'))">Copy</button><code>${md.utils.escapeHtml(str)}</code></pre>`;
  }
}).use(mk);

const renderAIMessage = (rawText) => {
    if (!rawText) return "";
    let text = rawText;
    if (text.includes("<think>") && !text.includes("</think>")) text += "</think>";
    const thinkRegex = /<think>([\s\S]*?)<\/think>/g;
    text = text.replace(thinkRegex, (match, p1) => {
        const renderedThinking = md.render(p1.trim());
        return `<details class="think-accordion" open><summary><i class="fas fa-brain mr-2"></i> Thinking Process...</summary><div class="think-body">${renderedThinking}</div></details>`;
    });
    return md.render(text);
};

const props = defineProps({
  email: Object
})

const emit = defineEmits(['close', 'converted'])

const showAIDraft = ref(false)
const selectedAIProvider = ref(localStorage.getItem('dhq_ai_model') || 'local_deepseek')
const saveAIPreference = () => { localStorage.setItem('dhq_ai_model', selectedAIProvider.value); }

const activeChatContent = ref([])
const newMessage = ref('')
const isAISearching = ref(false)
const searchQueryActive = ref('')
const queuePosition = ref(0)
const chatArea = ref(null)
const aiSessionId = ref(null)
let socket = null

const scrollToBottom = () => {
    nextTick(() => {
        if (chatArea.value) chatArea.value.scrollTop = chatArea.value.scrollHeight;
    });
}

const senderInitial = computed(() => {
    return (props.email.sender_name || props.email.sender_email || '?').charAt(0).toUpperCase()
})

const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleString()
}

const injectEmailContext = () => {
    newMessage.value = `Draft a reply to the following email:\nSubject: ${props.email.subject}\n\nBody:\n${props.email.body}\n\n`;
}

const handleSendMessage = async () => {
  if (!newMessage.value.trim()) return;
  const text = newMessage.value;
  newMessage.value = '';
  
  activeChatContent.value.push({ role: 'user', content: text });
  scrollToBottom();
  
  const providerStr = selectedAIProvider.value.startsWith('local_') ? 'local' : selectedAIProvider.value;
  const modelNameStr = selectedAIProvider.value === 'local_1.5b' ? 'deepseek-r1:1.5b' : 'deepseek-r1:7b';
  
  const payload = {
      session_id: aiSessionId.value,
      prompt: text,
      provider: providerStr,
      model_name: modelNameStr
  };
  
  const token = localStorage.getItem('token');
  try {
      const response = await fetch(`${window.location.protocol}//${window.location.host}/api/ai/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify(payload)
      });
      if (!response.ok) return;
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      const aiMsg = { role: 'assistant', content: '', isTyping: true };
      activeChatContent.value.push(aiMsg);
      scrollToBottom();
      
      let buffer = '';
      while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunkStr = decoder.decode(value, {stream:true});
          buffer += chunkStr;
          const lines = buffer.split('\n');
          buffer = lines.pop();
          for (const line of lines) {
              if (line.startsWith('data: ')) {
                  try {
                      const dataStr = line.replace('data: ', '');
                      if (dataStr.trim() === '[DONE]') continue;
                      const data = JSON.parse(dataStr);
                      if (data.session_id) aiSessionId.value = data.session_id;
                      if (data.error) aiMsg.content += `\n\n**Error:** ${data.error}`;
                      else if (data.status === 'searching') { isAISearching.value = true; searchQueryActive.value = data.query; }
                      else if (data.status === 'search_complete') isAISearching.value = false;
                      else if (data.content !== undefined) aiMsg.content += data.content;
                      scrollToBottom();
                  } catch(e) {}
              }
          }
      }
      if (buffer && buffer.startsWith('data: ')) {
          try {
              const data = JSON.parse(buffer.replace('data: ', ''));
              if (data.content !== undefined) aiMsg.content += data.content;
          } catch(e) {}
      }
      aiMsg.isTyping = false;
  } catch (e) {
      console.error("Fetch failed", e);
      if (activeChatContent.value.length > 0) activeChatContent.value[activeChatContent.value.length-1].isTyping = false;
  }
}

const convertToCollaboration = async () => {
    try {
        await apiPost(`/emails/${props.email._id.$oid}/convert`)
        showSuccess('Collaboration created successfully!')
        emit('converted')
    } catch (e) {
        showError('Failed to create collaboration')
    }
}

onMounted(() => {
    const token = localStorage.getItem('token') || '';
    socket = io({ auth: { token }, transports: ['websocket', 'polling'], reconnection: false });
    socket.on('connect_error', () => { console.warn("Socket.IO queue connection bypassed."); });
    socket.on('ai_queue_status', (data) => {
        if (data.status === 'processing') queuePosition.value = 0;
        else if (data.position) queuePosition.value = data.position;
    });
})

onUnmounted(() => {
    if (socket) socket.disconnect();
})
</script>

<style scoped>
.email-detail-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.8);
  backdrop-filter: blur(8px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.email-detail-container {
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  border-radius: 24px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.detail-header {
  padding: 1.5rem;
  background: rgba(255,255,255,0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sender-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.avatar {
  width: 48px;
  height: 48px;
  background: var(--primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1.25rem;
}

.detail-content {
  padding: 1.5rem;
  overflow-y: auto;
}

.email-meta-card {
  padding: 1.5rem;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.05);
}

.label {
  color: var(--text-tertiary);
  font-weight: 600;
  margin-right: 0.5rem;
}

.ai-extracted-box {
  padding: 1rem;
  background: rgba(99, 102, 241, 0.1);
  border: 1px dashed rgba(99, 102, 241, 0.3);
  border-radius: 12px;
}

.extraction-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-top: 0.5rem;
}

.inline-input {
  background: transparent;
  border: none;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  color: #fff;
  width: 100%;
  padding: 2px 0;
}

.inline-input:focus {
  outline: none;
  border-bottom-color: var(--primary);
}

.email-body {
  white-space: pre-wrap;
  color: var(--text-secondary);
  line-height: 1.6;
}

:deep(.markdown-body) {
  font-family: inherit;
  color: inherit;
  line-height: 1.6;
}
:deep(.markdown-body p) { margin-bottom: 0.5rem; }
:deep(.markdown-body pre) { 
  background: #1e1e24; 
  padding: 1rem; 
  border-radius: 0.5rem; 
  overflow-x: auto; 
  margin: 1rem 0; 
}
:deep(.markdown-body code:not(pre code)) {
  background: rgba(255,255,255,0.1);
  padding: 0.15rem 0.3rem;
  border-radius: 4px;
}
:deep(.markdown-body a) { color: #818cf8; text-decoration: underline; }
:deep(.katex) { font-size: 1.1em; }

:deep(.think-accordion) {
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.5);
  margin: 0.75rem 0;
  overflow: hidden;
}
:deep(.think-accordion summary) {
  cursor: pointer;
  font-weight: 600;
  color: #a5b4fc;
  padding: 0.6rem 1rem;
  font-size: 0.85rem;
  list-style: none;
  display: flex;
  align-items: center;
}
:deep(.think-accordion summary::-webkit-details-marker) { display: none; }
:deep(.think-accordion[open] summary) {
  border-bottom: 1px solid rgba(99, 102, 241, 0.15);
}
:deep(.think-body) {
  padding: 0.75rem 1rem;
  font-size: 0.85rem;
  color: #94a3b8;
  line-height: 1.6;
}
:deep(.think-body p) { margin: 0.25rem 0; }

.streaming-cursor::after {
    content: '▋';
    animation: emailBlink 1s step-end infinite;
    display: inline-block;
    vertical-align: bottom;
    margin-left: 4px;
    color: #a5b4fc;
}
@keyframes emailBlink { 50% { opacity: 0; } }
</style>
