<template>
  <div class="chat-interface">
    <!-- Sidebar with rooms and users -->
    <div class="chat-sidebar">
      <!-- Room List -->
      <div class="room-section">
        <div class="section-header">
          <h3>Rooms</h3>
          <button @click="showCreateRoom = true" class="create-btn">+</button>
        </div>
        <div class="room-list">
          <div 
            v-for="room in rooms" 
            :key="room.id"
            class="room-item"
            :class="{ active: activeRoom?.id === room.id }"
            @click="joinRoom(room)"
          >
            <div class="room-icon">💬</div>
            <div class="room-info">
              <div class="room-name">{{ room.name }}</div>
              <div class="room-meta">
                <span class="member-count">{{ room.member_count }} members</span>
                <span v-if="room.message_count > 0" class="message-count">
                  {{ room.message_count }} messages
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Online Users -->
      <div class="users-section">
        <div class="section-header">
          <h3>Online Users</h3>
          <span class="online-count">({{ onlineUsers.length }})</span>
        </div>
        <div class="user-list">
          <div 
            v-for="user in onlineUsers" 
            :key="user.id"
            class="user-item"
            @click="startPrivateChat(user)"
          >
            <div class="user-avatar">👤</div>
            <div class="user-info">
              <div class="user-name">{{ user.display_name || user.username }}</div>
              <div class="user-role">{{ user.role }}</div>
            </div>
            <div class="online-indicator">🟢</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Chat Area -->
    <div class="chat-main">
      <!-- Room Header -->
      <div v-if="activeRoom" class="chat-header">
        <div class="header-left">
          <h3>{{ activeRoom.name }}</h3>
          <span class="room-type">{{ activeRoom.room_type }}</span>
        </div>
        <div class="header-right">
          <button @click="leaveRoom" class="leave-btn">Leave</button>
        </div>
      </div>

      <!-- Private Chat Header -->
      <div v-else-if="activePrivateChat" class="chat-header">
        <div class="header-left">
          <h3>{{ activePrivateChat.display_name || activePrivateChat.username }}</h3>
          <span class="chat-type">Private Chat</span>
        </div>
        <div class="header-right">
          <button @click="closePrivateChat" class="close-btn">✕</button>
        </div>
      </div>

      <!-- Messages Area -->
      <div v-if="activeRoom || activePrivateChat" class="messages-container" ref="messagesContainer">
        <div 
          v-for="message in messages" 
          :key="message.id"
          class="message"
          :class="{ 
            'own-message': isOwnMessage(message),
            'system-message': message.message_type === 'SYSTEM'
          }"
        >
          <div v-if="!isOwnMessage(message) && message.sender" class="message-avatar">
            {{ message.sender.display_name?.[0] || message.sender.username?.[0] }}
          </div>
          
          <div class="message-content">
            <div v-if="!isOwnMessage(message) && message.sender" class="message-sender">
              {{ message.sender.display_name || message.sender.username }}
            </div>
            
            <div class="message-text">
              {{ message.content }}
            </div>
            
            <div class="message-meta">
              <span class="message-time">{{ formatTime(message.timestamp) }}</span>
              <span v-if="message.is_edited" class="edited-indicator">(edited)</span>
            </div>
          </div>
        </div>

        <!-- Typing Indicator -->
        <div v-if="typingUsers.length > 0" class="typing-indicator">
          <div class="typing-text">
            {{ getTypingText() }}
          </div>
          <div class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>

      <!-- Welcome Screen -->
      <div v-else class="welcome-screen">
        <div class="welcome-content">
          <h2>Welcome to DHQ Hub</h2>
          <p>Select a room or start a private chat to begin messaging</p>
        </div>
      </div>

      <!-- Message Input -->
      <div v-if="activeRoom || activePrivateChat" class="message-input">
        <div class="input-container">
          <input
            v-model="messageInput"
            @keydown.enter="sendMessage"
            @input="handleTyping"
            placeholder="Type your message..."
            class="message-field"
          />
          <button @click="sendMessage" :disabled="!messageInput.trim()" class="send-btn">
            Send
          </button>
        </div>
      </div>
    </div>

    <!-- Create Room Modal -->
    <div v-if="showCreateRoom" class="modal-overlay" @click="showCreateRoom = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Create Room</h3>
          <button @click="showCreateRoom = false" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Room Name</label>
            <input v-model="newRoom.name" placeholder="Enter room name" />
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="newRoom.description" placeholder="Room description"></textarea>
          </div>
          <div class="form-group">
            <label>Room Type</label>
            <select v-model="newRoom.room_type">
              <option value="GENERAL">General</option>
              <option value="PROJECT">Project</option>
              <option value="PRIVATE">Private</option>
              <option value="ANNOUNCEMENT">Announcement</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="createRoom" :disabled="!newRoom.name" class="create-room-btn">
            Create Room
          </button>
          <button @click="showCreateRoom = false" class="cancel-btn">
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { io } from 'socket.io-client'
import { getSocketIoUrl, apiGet, apiPost } from '../../utils/api.js'

export default {
  name: 'ChatInterface',
  setup() {
    // Socket connection
    const socket = ref(null)
    const isConnected = ref(false)
    
    // State
    const rooms = ref([])
    const onlineUsers = ref([])
    const activeRoom = ref(null)
    const activePrivateChat = ref(null)
    const messages = ref([])
    const messageInput = ref('')
    const typingUsers = ref([])
    const showCreateRoom = ref(false)
    const newRoom = ref({
      name: '',
      description: '',
      room_type: 'GENERAL'
    })
    const messagesContainer = ref(null)
    
    // Get auth token
    const getAuthHeaders = () => {
      const token = localStorage.getItem('token')
      return token ? { 'Authorization': `Bearer ${token}` } : {}
    }
    
    // Initialize Socket.IO connection
    const initSocket = () => {
      const token = localStorage.getItem('token')
      if (!token) return
      
      socket.value = io(getSocketIoUrl(), {
        auth: { token },
        transports: ['websocket', 'polling']
      })
      
      socket.value.on('connect', () => {
        isConnected.value = true
        console.log('Connected to chat server')
      })
      
      socket.value.on('disconnect', () => {
        isConnected.value = false
        console.log('Disconnected from chat server')
      })
      
      socket.value.on('connected', (data) => {
        console.log('Chat connection established:', data)
      })
      
      socket.value.on('new_message', (message) => {
        if (activeRoom.value && message.room_id === activeRoom.value.id) {
          messages.value.push(message)
          scrollToBottom()
        }
      })
      
      socket.value.on('new_private_message', (message) => {
        if (activePrivateChat.value && message.sender_id === activePrivateChat.value.id) {
          messages.value.push(message)
          scrollToBottom()
        }
      })
      
      socket.value.on('user_online', (user) => {
        if (!onlineUsers.value.find(u => u.id === user.user_id)) {
          onlineUsers.value.push({
            id: user.user_id,
            username: user.username,
            display_name: user.display_name,
            role: user.role || 'USER'
          })
        }
      })
      
      socket.value.on('user_offline', (data) => {
        onlineUsers.value = onlineUsers.value.filter(u => u.id !== data.user_id)
      })
      
      socket.value.on('user_typing', (data) => {
        if (activeRoom.value && data.room_id === activeRoom.value.id) {
          if (data.is_typing) {
            if (!typingUsers.value.find(u => u.user_id === data.user_id)) {
              typingUsers.value.push({
                user_id: data.user_id,
                username: data.username
              })
            }
          } else {
            typingUsers.value = typingUsers.value.filter(u => u.user_id !== data.user_id)
          }
        }
      })
      
      socket.value.on('error', (error) => {
        console.error('Socket error:', error)
      })
    }
    
    // Load rooms
    const loadRooms = async () => {
      try {
        const response = await apiGet('/hub/rooms')
        
        if (response.ok) {
          rooms.value = await response.json()
        }
      } catch (error) {
        console.error('Error loading rooms:', error)
      }
    }
    
    // Load online users
    const loadOnlineUsers = async () => {
      try {
        const response = await apiGet('/hub/users/online')
        
        if (response.ok) {
          onlineUsers.value = await response.json()
        }
      } catch (error) {
        console.error('Error loading online users:', error)
      }
    }
    
    // Join room
    const joinRoom = async (room) => {
      // Leave current room if any
      if (activeRoom.value) {
        socket.value?.emit('leave_room', { room_id: activeRoom.value.id })
      }
      
      activeRoom.value = room
      activePrivateChat.value = null
      messages.value = []
      
      // Join socket room
      socket.value?.emit('join_room', { 
        room_id: room.id,
        user_id: getCurrentUserId()
      })
      
      // Load room messages
      try {
        const response = await apiGet(`/hub/rooms/${room.id}/messages`)
        
        if (response.ok) {
          const roomMessages = await response.json()
          messages.value = roomMessages.reverse()
          scrollToBottom()
        }
      } catch (error) {
        console.error('Error loading room messages:', error)
      }
    }
    
    // Leave room
    const leaveRoom = () => {
      if (activeRoom.value) {
        socket.value?.emit('leave_room', { room_id: activeRoom.value.id })
        activeRoom.value = null
        messages.value = []
      }
    }
    
    // Start private chat
    const startPrivateChat = (user) => {
      activeRoom.value = null
      activePrivateChat.value = user
      messages.value = []
      
      // Load private conversation
      loadPrivateConversation(user.id)
    }
    
    // Close private chat
    const closePrivateChat = () => {
      activePrivateChat.value = null
      messages.value = []
    }
    
    // Load private conversation
    const loadPrivateConversation = async (userId) => {
      try {
        const response = await apiGet(`/hub/conversations/${userId}`)
        
        if (response.ok) {
          const privateMessages = await response.json()
          messages.value = privateMessages.reverse()
          scrollToBottom()
        }
      } catch (error) {
        console.error('Error loading private conversation:', error)
      }
    }
    
    // Send message
    const sendMessage = () => {
      if (!messageInput.value.trim()) return
      
      const content = messageInput.value.trim()
      messageInput.value = ''
      
      if (activeRoom.value) {
        socket.value?.emit('send_message', {
          room_id: activeRoom.value.id,
          content: content
        })
      } else if (activePrivateChat.value) {
        socket.value?.emit('send_private_message', {
          recipient_id: activePrivateChat.value.id,
          content: content
        })
      }
    }
    
    // Handle typing
    let typingTimeout = null
    const handleTyping = () => {
      if (activeRoom.value) {
        // Start typing
        socket.value?.emit('typing_start', {
          room_id: activeRoom.value.id
        })
        
        // Clear existing timeout
        if (typingTimeout) {
          clearTimeout(typingTimeout)
        }
        
        // Stop typing after 3 seconds
        typingTimeout = setTimeout(() => {
          socket.value?.emit('typing_stop', {
            room_id: activeRoom.value.id
          })
        }, 3000)
      }
    }
    
    // Create room
    const createRoom = async () => {
      try {
        const response = await apiPost('/hub/rooms', newRoom.value)
        
        if (response.ok) {
          const room = await response.json()
          rooms.value.push(room)
          showCreateRoom.value = false
          newRoom.value = { name: '', description: '', room_type: 'GENERAL' }
          joinRoom(room)
        }
      } catch (error) {
        console.error('Error creating room:', error)
      }
    }
    
    // Utility functions
    const getCurrentUserId = () => {
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      return user.id || user.sub
    }
    
    const isOwnMessage = (message) => {
      const userId = getCurrentUserId()
      return message.sender_id === userId
    }
    
    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    }
    
    const getTypingText = () => {
      const usernames = typingUsers.value.map(u => u.username)
      if (usernames.length === 1) {
        return `${usernames[0]} is typing...`
      } else if (usernames.length === 2) {
        return `${usernames[0]} and ${usernames[1]} are typing...`
      } else {
        return `${usernames.length} people are typing...`
      }
    }
    
    const scrollToBottom = () => {
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
        }
      })
    }
    
    // Lifecycle
    onMounted(() => {
      initSocket()
      loadRooms()
      loadOnlineUsers()
    })
    
    onUnmounted(() => {
      if (socket.value) {
        socket.value.disconnect()
      }
      if (typingTimeout) {
        clearTimeout(typingTimeout)
      }
    })
    
    return {
      socket,
      isConnected,
      rooms,
      onlineUsers,
      activeRoom,
      activePrivateChat,
      messages,
      messageInput,
      typingUsers,
      showCreateRoom,
      newRoom,
      messagesContainer,
      joinRoom,
      leaveRoom,
      startPrivateChat,
      closePrivateChat,
      sendMessage,
      handleTyping,
      createRoom,
      isOwnMessage,
      formatTime,
      getTypingText
    }
  }
}
</script>

<style scoped>
.chat-interface {
  display: flex;
  height: 100%;
  background: var(--glass-bg-primary);
  backdrop-filter: var(--glass-blur-lg);
  -webkit-backdrop-filter: var(--glass-blur-lg);
  position: relative;
  overflow: hidden;
}

.chat-interface::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 4s ease-in-out infinite;
}

.chat-sidebar {
  width: 300px;
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  -webkit-backdrop-filter: var(--glass-blur-md);
  border-right: 1px solid var(--glass-border);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.chat-sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: shimmer 5s ease-in-out infinite;
}

.room-section,
.users-section {
  flex: 1;
  padding: 1rem;
  border-bottom: 1px solid var(--glass-border);
  position: relative;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.create-btn {
  background: var(--primary-gradient);
  color: white;
  border: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: var(--glass-shadow-md);
}

.create-btn:hover {
  transform: scale(1.1);
  box-shadow: var(--glass-shadow-lg);
}

.room-list,
.user-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.room-item,
.user-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: var(--glass-bg-tertiary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  position: relative;
  overflow: hidden;
}

.room-item::before,
.user-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: all 0.3s ease;
}

.room-item:hover,
.user-item:hover {
  background: var(--glass-bg-hover);
  border-color: var(--glass-border-hover);
  transform: translateY(-2px);
  box-shadow: var(--glass-shadow-md);
}

.room-item.active {
  background: var(--glass-bg-hover);
  border-left: 3px solid var(--primary-color);
  box-shadow: var(--glass-shadow-md);
}

.room-icon,
.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--glass-bg-tertiary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
}

.room-info,
.user-info {
  flex: 1;
  min-width: 0;
}

.room-name,
.user-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.875rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.room-meta,
.user-role {
  font-size: 0.75rem;
  color: var(--text-secondary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.member-count,
.message-count {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.online-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.8), rgba(6, 182, 212, 0.8));
  box-shadow: 0 0 4px rgba(16, 185, 129, 0.3);
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--glass-bg-primary);
  position: relative;
}

.chat-main::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: shimmer 6s ease-in-out infinite;
}

.chat-header {
  background: var(--glass-bg-secondary);
  backdrop-filter: var(--glass-blur-md);
  -webkit-backdrop-filter: var(--glass-blur-md);
  border-bottom: 1px solid var(--glass-border);
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
}

.chat-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: shimmer 4s ease-in-out infinite;
}

.chat-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.2rem;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.online-count {
  background: var(--glass-bg-tertiary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.chat-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.2rem;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.online-count {
  background: var(--glass-bg-tertiary);
  backdrop-filter: var(--glass-blur-sm);
  -webkit-backdrop-filter: var(--glass-blur-sm);
  border: 1px solid var(--glass-border);
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  color: var(--text-secondary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.room-type,
.chat-type {
  background: var(--glass-bg-tertiary);
  color: var(--text-secondary);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.leave-btn,
.close-btn {
  background: #ef4444;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.messages-container {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  display: flex;
  gap: 0.75rem;
  max-width: 70%;
}

.message.own-message {
  margin-left: auto;
  flex-direction: row-reverse;
}

.message.system-message {
  justify-content: center;
  max-width: 100%;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #3b82f6;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.message-content {
  flex: 1;
}

.message-sender {
  font-size: 0.75rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.message-text {
  background: white;
  padding: 0.75rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  word-wrap: break-word;
}

.message.own-message .message-text {
  background: #3b82f6;
  color: white;
}

.message-meta {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.message.own-message .message-meta {
  text-align: right;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.typing-dots {
  display: flex;
  gap: 0.25rem;
}

.typing-dots span {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #6b7280;
  animation: typing 1.4s infinite;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-6px);
  }
}

.welcome-screen {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.welcome-content {
  text-align: center;
  color: #6b7280;
}

.welcome-content h2 {
  color: #1f2937;
  margin-bottom: 1rem;
}

.message-input {
  background: white;
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
}

.input-container {
  display: flex;
  gap: 0.75rem;
}

.message-field {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.message-field:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.send-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 0.5rem;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.modal-header h3 {
  margin: 0;
  color: #1f2937;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.modal-footer {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.create-room-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.375rem;
  cursor: pointer;
}

.cancel-btn {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  padding: 0.75rem 1.5rem;
  border-radius: 0.375rem;
  cursor: pointer;
}
</style>
