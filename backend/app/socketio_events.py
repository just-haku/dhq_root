import socketio
from app.services.chat_service import get_chat_service
from app.models.chat import ChatRoom, ChatMessage, PrivateMessage
from app.models.user import User
from app.api.auth import verify_token
from app.socketio_games import register_game_handlers

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=["http://localhost:3000"],
    logger=True,
    engineio_logger=True
)

# Register game handlers
register_game_handlers(sio)

# Socket.IO event handlers
@sio.event
async def connect(sid, environ, auth):
    """Handle client connection"""
    try:
        # Extract token from auth or query string
        token = auth.get('token') if auth else None
        if not token:
            # Try to get from query string
            query_string = environ.get('QUERY_STRING', '')
            for param in query_string.split('&'):
                if param.startswith('token='):
                    token = param.split('=', 1)[1]
                    break
        
        if not token:
            await sio.emit('error', {'message': 'Authentication required'}, room=sid)
            await sio.disconnect(sid)
            return
        
        # Verify token and get user
        payload = verify_token(token)
        if not payload:
            await sio.emit('error', {'message': 'Invalid token'}, room=sid)
            await sio.disconnect(sid)
            return
        
        user_id = payload.get('sub')
        user = User.objects(id=user_id).first()
        
        if not user:
            await sio.emit('error', {'message': 'User not found'}, room=sid)
            await sio.disconnect(sid)
            return
        
        # Register connection
        chat_service = get_chat_service()
        chat_service.user_connected(user_id, sid)
        
        # Join user to their rooms
        rooms = chat_service.get_user_rooms(user)
        for room in rooms:
            room_sid = f"room_{room.id}"
            await sio.enter_room(sid, room_sid)
        
        # Join user to their personal room for private messages
        await sio.enter_room(sid, f"user_{user_id}")
        
        # Send connection success
        await sio.emit('connected', {
            'user_id': user_id,
            'username': user.username,
            'display_name': user.display_name
        }, room=sid)
        
        # Notify others that user is online
        await sio.emit('user_online', {
            'user_id': user_id,
            'username': user.username,
            'display_name': user.display_name
        }, room='broadcast')
        
        print(f"User {user.username} connected with socket {sid}")
        
    except Exception as e:
        print(f"Connection error: {e}")
        await sio.emit('error', {'message': 'Connection failed'}, room=sid)
        await sio.disconnect(sid)

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    try:
        chat_service = get_chat_service()
        chat_service.user_disconnected(sid)
        
        # Note: We can't easily get user_id here without tracking
        # The service handles removing online status
        
        print(f"Socket {sid} disconnected")
        
    except Exception as e:
        print(f"Disconnection error: {e}")

@sio.event
async def join_room(sid, data):
    """Join a chat room"""
    try:
        room_id = data.get('room_id')
        user_id = data.get('user_id')
        
        if not room_id or not user_id:
            await sio.emit('error', {'message': 'Missing room_id or user_id'}, room=sid)
            return
        
        room = ChatRoom.objects(id=room_id).first()
        user = User.objects(id=user_id).first()
        
        if not room or not user:
            await sio.emit('error', {'message': 'Room or user not found'}, room=sid)
            return
        
        # Check if user is member
        if user not in room.members:
            await sio.emit('error', {'message': 'Not a member of this room'}, room=sid)
            return
        
        # Join socket room
        room_sid = f"room_{room_id}"
        await sio.enter_room(sid, room_sid)
        
        # Notify room members
        await sio.emit('user_joined', {
            'user_id': str(user.id),
            'username': user.username,
            'display_name': user.display_name,
            'room_id': room_id
        }, room=room_sid)
        
        print(f"User {user.username} joined room {room.name}")
        
    except Exception as e:
        print(f"Join room error: {e}")
        await sio.emit('error', {'message': 'Failed to join room'}, room=sid)

@sio.event
async def leave_room(sid, data):
    """Leave a chat room"""
    try:
        room_id = data.get('room_id')
        
        if not room_id:
            await sio.emit('error', {'message': 'Missing room_id'}, room=sid)
            return
        
        room = ChatRoom.objects(id=room_id).first()
        if not room:
            await sio.emit('error', {'message': 'Room not found'}, room=sid)
            return
        
        # Leave socket room
        room_sid = f"room_{room_id}"
        await sio.leave_room(sid, room_sid)
        
        # Notify room members
        await sio.emit('user_left', {
            'room_id': room_id
        }, room=room_sid)
        
        print(f"Socket {sid} left room {room.name}")
        
    except Exception as e:
        print(f"Leave room error: {e}")
        await sio.emit('error', {'message': 'Failed to leave room'}, room=sid)

@sio.event
async def send_message(sid, data):
    """Send message to room"""
    try:
        room_id = data.get('room_id')
        user_id = data.get('user_id')
        content = data.get('content')
        message_type = data.get('message_type', 'TEXT')
        file_attachments = data.get('file_attachments', [])
        
        if not room_id or not user_id or not content:
            await sio.emit('error', {'message': 'Missing required fields'}, room=sid)
            return
        
        room = ChatRoom.objects(id=room_id).first()
        user = User.objects(id=user_id).first()
        
        if not room or not user:
            await sio.emit('error', {'message': 'Room or user not found'}, room=sid)
            return
        
        # Check if user is member
        if user not in room.members:
            await sio.emit('error', {'message': 'Not a member of this room'}, room=sid)
            return
        
        # Create message
        chat_service = get_chat_service()
        message = chat_service.send_room_message(
            room=room,
            sender=user,
            content=content,
            message_type=message_type,
            file_attachments=file_attachments
        )
        
        # Broadcast to room
        room_sid = f"room_{room_id}"
        message_data = message.to_dict(include_sender_info=True)
        
        await sio.emit('new_message', message_data, room=room_sid)
        
        print(f"Message sent in {room.name} by {user.username}")
        
    except Exception as e:
        print(f"Send message error: {e}")
        await sio.emit('error', {'message': 'Failed to send message'}, room=sid)

@sio.event
async def send_private_message(sid, data):
    """Send private message"""
    try:
        sender_id = data.get('sender_id')
        recipient_id = data.get('recipient_id')
        content = data.get('content')
        message_type = data.get('message_type', 'TEXT')
        file_attachments = data.get('file_attachments', [])
        
        if not sender_id or not recipient_id or not content:
            await sio.emit('error', {'message': 'Missing required fields'}, room=sid)
            return
        
        sender = User.objects(id=sender_id).first()
        recipient = User.objects(id=recipient_id).first()
        
        if not sender or not recipient:
            await sio.emit('error', {'message': 'User not found'}, room=sid)
            return
        
        # Create private message
        chat_service = get_chat_service()
        message = chat_service.send_private_message(
            sender=sender,
            recipient=recipient,
            content=content,
            message_type=message_type,
            file_attachments=file_attachments
        )
        
        # Send to recipient's personal room
        recipient_room = f"user_{recipient_id}"
        message_data = message.to_dict(include_sender_info=True)
        
        await sio.emit('new_private_message', message_data, room=recipient_room)
        
        # Also send to sender for confirmation
        await sio.emit('message_sent', message_data, room=sid)
        
        print(f"Private message from {sender.username} to {recipient.username}")
        
    except Exception as e:
        print(f"Send private message error: {e}")
        await sio.emit('error', {'message': 'Failed to send private message'}, room=sid)

@sio.event
async def typing_start(sid, data):
    """User started typing"""
    try:
        room_id = data.get('room_id')
        user_id = data.get('user_id')
        
        if not room_id or not user_id:
            return
        
        chat_service = get_chat_service()
        chat_service.set_typing(user_id, room_id, True)
        
        # Notify room members
        room_sid = f"room_{room_id}"
        await sio.emit('user_typing', {
            'user_id': user_id,
            'room_id': room_id,
            'is_typing': True
        }, room=room_sid, skip_sid=sid)
        
    except Exception as e:
        print(f"Typing start error: {e}")

@sio.event
async def typing_stop(sid, data):
    """User stopped typing"""
    try:
        room_id = data.get('room_id')
        user_id = data.get('user_id')
        
        if not room_id or not user_id:
            return
        
        chat_service = get_chat_service()
        chat_service.set_typing(user_id, room_id, False)
        
        # Notify room members
        room_sid = f"room_{room_id}"
        await sio.emit('user_typing', {
            'user_id': user_id,
            'room_id': room_id,
            'is_typing': False
        }, room=room_sid, skip_sid=sid)
        
    except Exception as e:
        print(f"Typing stop error: {e}")

# Create ASGI app
socket_app = socketio.ASGIApp(sio)
