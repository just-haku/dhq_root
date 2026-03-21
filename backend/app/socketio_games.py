import socketio
from app.models.user import User

def register_game_handlers(sio):
    @sio.event
    async def join_game_room(sid, data):
        """User joined a game waiting room"""
        room_id = data.get('room_id')
        user_id = data.get('user_id')
        game_type = data.get('game_type')
        
        if not room_id or not user_id:
            return
        
        room_sid = f"game_{game_type}_{room_id}"
        await sio.enter_room(sid, room_sid)
        
        await sio.emit('player_joined', {
            'user_id': user_id,
            'room_id': room_id,
            'game_type': game_type
        }, room=room_sid)

    @sio.event
    async def start_game(sid, data):
        """Room master starts the game"""
        room_id = data.get('room_id')
        game_type = data.get('game_type')
        room_sid = f"game_{game_type}_{room_id}"
        
        # Logic to check if user is Room Master would go here
        await sio.emit('game_started', {
            'game_type': game_type,
            'room_id': room_id
        }, room=room_sid)

    @sio.event
    async def game_move(sid, data):
        """Broadcast a game move to all players in the room"""
        room_id = data.get('room_id')
        game_type = data.get('game_type')
        move_data = data.get('move')
        room_sid = f"game_{game_type}_{room_id}"
        
        await sio.emit('new_move', {
            'game_type': game_type,
            'move': move_data
        }, room=room_sid, skip_sid=sid)

    @sio.event
    async def game_chat(sid, data):
        """Chat within a game room"""
        room_id = data.get('room_id')
        game_type = data.get('game_type')
        message = data.get('message')
        user_id = data.get('user_id')
        username = data.get('username')
        
        room_sid = f"game_{game_type}_{room_id}"
        await sio.emit('game_message', {
            'message': message,
            'user_id': user_id,
            'username': username
        }, room=room_sid)
