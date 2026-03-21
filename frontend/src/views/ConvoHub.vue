<template>
  <div class="convo-hub-container glass-panel">
    <!-- Conversations Sidebar -->
    <div class="convo-sidebar">
      <div class="sidebar-header">
        <h2>Chats</h2>
        <div class="header-actions">
          <button class="action-btn" @click="createNewChat" title="New Chat">
            <i class="fas fa-edit"></i>
          </button>
        </div>
      </div>
      
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input type="text" v-model="searchQuery" placeholder="Search Messenger" />
      </div>

      <div class="chats-list custom-scrollbar">
        <div 
          v-for="chat in filteredChats" 
          :key="chat.id" 
          class="chat-item"
          :class="{ active: activeChatId === chat.id, unread: chat.unread }"
          @click="selectChat(chat)"
        >
          <div class="chat-avatar">
            <div class="avatar-circle">
              <img v-if="chat.avatar" :src="chat.avatar" />
              <span v-else>{{ chat.initials }}</span>
            </div>
            <div v-if="chat.online" class="online-status"></div>
          </div>
          <div class="chat-info">
            <div class="chat-name-row">
              <span class="chat-name">{{ chat.name }}</span>
              <span class="chat-time">{{ chat.time }}</span>
            </div>
            <div class="chat-message-preview">
              <span class="preview-text">{{ chat.lastMessage }}</span>
              <div v-if="chat.unread" class="unread-dot"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Active Chat Area -->
    <div class="chat-main">
      <template v-if="activeChat">
        <div class="chat-header">
          <div class="chat-header-user">
            <div class="avatar-circle-small">
              <img v-if="activeChat.avatar_url" :src="activeChat.avatar_url" />
              <span v-else>{{ getInitials(activeChat.name) }}</span>
            </div>
            <div class="user-meta">
              <span class="user-name">{{ activeChat.name }}</span>
              <span class="user-status">{{ activeChat.online ? 'Active now' : 'Offline' }}</span>
            </div>
          </div>
          <div class="chat-header-actions">
            <button class="chat-action-btn"><i class="fas fa-phone"></i></button>
            <button class="chat-action-btn"><i class="fas fa-video"></i></button>
            <button class="chat-action-btn" @click="showDetails = !showDetails"><i class="fas fa-info-circle"></i></button>
          </div>
        </div>

        <div class="messages-area custom-scrollbar" ref="messagesArea">
          <div v-for="(msg, index) in activeChatContent" :key="index" :class="['message-row', msg.sender_id === userStore.user?._id ? 'me' : 'them']">
            <div v-if="msg.sender_id !== userStore.user?._id" class="message-avatar-mini">
              <img v-if="activeChat.avatar_url" :src="activeChat.avatar_url" />
              <div v-else class="avatar-circle-mini">{{ getInitials(activeChat.name) }}</div>
            </div>
            <div class="message-bubble" :title="msg.timestamp">
              {{ msg.content }}
            </div>
          </div>
        </div>

        <div class="chat-input-area">
          <div class="input-actions-left">
            <button class="input-btn"><i class="fas fa-plus-circle"></i></button>
            <button class="input-btn"><i class="fas fa-images"></i></button>
            <button class="input-btn" @click="toggleInviteModal"><i class="fas fa-user-plus"></i></button>
          </div>
          <div class="input-wrapper">
            <input 
              type="text" 
              v-model="newMessage" 
              placeholder="Aa" 
              @keyup.enter="handleSendMessage"
            />
            <button class="emoji-btn"><i class="far fa-smile"></i></button>
          </div>
          <div class="input-actions-right">
            <button class="send-btn" @click="handleSendMessage" :disabled="!newMessage.trim()">
              <i class="fas fa-paper-plane"></i>
            </button>
          </div>
        </div>
      </template>
      <div v-else class="no-chat-selected">
        <div class="welcome-box">
          <i class="fas fa-comments"></i>
          <h3>Select a conversation to start messaging</h3>
          <button class="btn btn-primary mt-4" @click="showSearchModal = true">Start New Conversation</button>
        </div>
      </div>
    </div>

    <!-- Details Sidebar -->
    <transition name="slide">
      <div v-if="showDetails && activeChat" class="convo-details">
        <div class="details-user-info">
          <div class="avatar-circle-large">
            <img v-if="activeChat.avatar_url" :src="activeChat.avatar_url" />
            <span v-else>{{ getInitials(activeChat.name) }}</span>
          </div>
          <h3>{{ activeChat.name }}</h3>
          <p>{{ activeChat.online ? 'Active now' : 'Offline' }}</p>
        </div>
        
        <div class="details-sections">
          <div class="details-section">
            <button class="section-trigger">Chat Info <i class="fas fa-chevron-down"></i></button>
          </div>
          <div class="details-section" v-if="activeChat.room_type !== 'GENERAL'">
            <button class="btn btn-outline w-full mb-2" @click="toggleInviteModal">Invite Member</button>
          </div>
          <div class="details-section">
            <button class="section-trigger">Customize Chat <i class="fas fa-chevron-down"></i></button>
          </div>
          <div class="details-section">
            <button class="section-trigger">Media & Links <i class="fas fa-chevron-down"></i></button>
          </div>
          <div class="details-section">
            <button class="section-trigger">Privacy & Support <i class="fas fa-chevron-down"></i></button>
          </div>
        </div>
      </div>
    </transition>

    <!-- User Search Modal -->
    <div v-if="showSearchModal" class="modal-overlay" @click="showSearchModal = false">
      <div class="modal-content glass-panel" @click.stop>
        <div class="modal-header">
          <h3>New Message</h3>
          <button class="close-btn" @click="showSearchModal = false">&times;</button>
        </div>
        <div class="search-input-wrapper">
          <input 
            type="text" 
            v-model="userSearchQuery" 
            placeholder="Type username or display name..." 
            @input="handleUserSearch"
            ref="userInput"
          />
        </div>
        <div class="search-results custom-scrollbar">
          <div v-if="isSearching" class="loading-state">Searching...</div>
          <div v-else-if="userSearchResults.length === 0" class="empty-state">No users found</div>
          <div 
            v-for="user in userSearchResults" 
            :key="user.id" 
            class="user-result-item"
            @click="startNewConvo(user)"
          >
            <div class="user-avatar-small">
              <img v-if="user.avatar_url" :src="user.avatar_url" />
              <div v-else class="avatar-circle-mini">{{ getInitials(user.display_name) }}</div>
            </div>
            <div class="user-info">
              <span class="name">{{ user.display_name }}</span>
              <span class="username">@{{ user.username }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Invite Modal -->
    <div v-if="showInviteModal" class="modal-overlay" @click="showInviteModal = false">
      <div class="modal-content glass-panel" @click.stop>
        <div class="modal-header">
          <h3>Invite to {{ activeChat?.name }}</h3>
          <button class="close-btn" @click="showInviteModal = false">&times;</button>
        </div>
        <div class="search-input-wrapper">
          <input 
            type="text" 
            v-model="userSearchQuery" 
            placeholder="Search for users to invite..." 
            @input="handleUserSearch"
          />
        </div>
        <div class="search-results custom-scrollbar">
          <div 
            v-for="user in userSearchResults" 
            :key="user.id" 
            class="user-result-item"
            @click="inviteUser(user)"
          >
            <div class="user-avatar-small">
              <img v-if="user.avatar_url" :src="user.avatar_url" />
              <div v-else class="avatar-circle-mini">{{ getInitials(user.display_name) }}</div>
            </div>
            <div class="user-info">
              <span class="name">{{ user.display_name }}</span>
              <span class="username">@{{ user.username }}</span>
            </div>
            <button class="btn btn-sm btn-primary">Invite</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { apiGet, apiPost } from '@/utils/api.js'
import { useUserStore } from '@/stores/userStore.js'

const userStore = useUserStore()
const searchQuery = ref('')
const activeChatId = ref(null)
const newMessage = ref('')
const showDetails = ref(false)
const messagesArea = ref(null)

// Modal states
const showSearchModal = ref(false)
const showInviteModal = ref(false)
const userSearchQuery = ref('')
const userSearchResults = ref([])
const isSearching = ref(false)

const chats = ref([])
const activeChatContent = ref([])

const filteredChats = computed(() => {
  if (!searchQuery.value) return chats.value
  return chats.value.filter(c => c.name.toLowerCase().includes(searchQuery.value.toLowerCase()))
})

const activeChat = computed(() => chats.value.find(c => c.id === activeChatId.value))

const selectChat = async (chat) => {
  activeChatId.value = chat.id
  chat.unread = false
  await fetchMessages()
  scrollToBottom()
}

const fetchRooms = async () => {
  try {
    const rooms = await apiGet('/hub/rooms')
    chats.value = rooms.map(r => ({
      id: r.id,
      name: r.name,
      lastMessage: r.last_message || 'No messages yet',
      time: r.last_activity ? formatTime(r.last_activity) : '',
      unread: false,
      online: false, // Could be synced with /hub/users/online
      room_type: r.room_type,
      avatar_url: r.avatar_url || null
    }))
  } catch (e) {
    console.error('Failed to fetch rooms', e)
  }
}

const fetchMessages = async () => {
  if (!activeChatId.value) return
  try {
    const messages = await apiGet(`/hub/rooms/${activeChatId.value}/messages`)
    activeChatContent.value = messages.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
  } catch (e) {
    console.error('Failed to fetch messages', e)
  }
}

const handleSendMessage = async () => {
  if (!newMessage.value.trim() || !activeChatId.value) return
  const text = newMessage.value
  newMessage.value = ''
  
  try {
    const msg = await apiPost(`/hub/rooms/${activeChatId.value}/messages`, {
      content: text,
      message_type: 'TEXT'
    })
    activeChatContent.value.push(msg)
    scrollToBottom()
  } catch (e) {
    console.error('Failed to send message', e)
    newMessage.value = text // Restore on failure
  }
}

let searchTimeout = null
const handleUserSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  if (userSearchQuery.value.length < 2) {
    userSearchResults.value = []
    return
  }
  
  isSearching.value = true
  searchTimeout = setTimeout(async () => {
    try {
      const results = await apiGet(`/hub/users/search?q=${userSearchQuery.value}`)
      userSearchResults.value = results.filter(u => u.username !== userStore.user?.username)
    } catch (e) {
      console.error('Search failed', e)
    } finally {
      isSearching.value = false
    }
  }, 300)
}

const startNewConvo = async (user) => {
  showSearchModal.value = false
  userSearchQuery.value = ''
  
  // Messenger style: Start a room or just a private chat
  // Here we'll create a PRIVATE room if none exists
  try {
    const room = await apiPost('/hub/rooms', {
      name: `${userStore.user?.display_name}, ${user.display_name}`,
      room_type: 'PRIVATE',
      members: [user.id]
    })
    await fetchRooms()
    selectChat({ id: room.id })
  } catch (e) {
    console.error('Failed to start conversation', e)
  }
}

const inviteUser = async (user) => {
  try {
    await apiPost(`/hub/rooms/${activeChatId.value}/invite`, {
      username: user.username
    })
    showInviteModal.value = false
    userSearchQuery.value = ''
    alert(`Invited ${user.display_name} successfully!`)
  } catch (e) {
    console.error('Invite failed', e)
    alert('Invite failed: ' + (e.message || 'Unknown error'))
  }
}

const toggleInviteModal = () => {
  showInviteModal.value = !showInviteModal.value
  userSearchQuery.value = ''
  userSearchResults.value = []
}

const getInitials = (name) => {
  if (!name) return '?'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

const formatTime = (isoString) => {
  const date = new Date(isoString)
  const now = new Date()
  const diff = now - date
  if (diff < 86400000) return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  return date.toLocaleDateString([], { month: 'short', day: 'numeric' })
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesArea.value) {
      messagesArea.value.scrollTop = messagesArea.value.scrollHeight
    }
  })
}

const createNewChat = () => {
  showSearchModal.value = true
}

onMounted(async () => {
  await fetchRooms()
  // Auto select first room if exists
  if (chats.value.length > 0 && !activeChatId.value) {
    selectChat(chats.value[0])
  }
})
</script>

<style scoped>
.convo-hub-container {
  display: flex;
  height: calc(100vh - 120px);
  overflow: hidden;
  border-radius: 1.5rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
}

/* Sidebar */
.convo-sidebar {
  width: 360px;
  border-right: 1px solid var(--glass-border);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 1.5rem 1rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h2 {
  font-size: 1.5rem;
  font-weight: 800;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: var(--glass-bg-hover);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--primary-color);
  color: white;
}

.search-box {
  padding: 0 1rem 1rem;
  position: relative;
}

.search-box i {
  position: absolute;
  left: 1.75rem;
  top: 50%;
  transform: translateY(-50%) translateY(-0.5rem);
  color: var(--text-muted);
}

.search-box input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border-radius: 20px;
  border: none;
  background: var(--glass-bg-secondary);
  color: var(--text-primary);
  outline: none;
}

.chats-list {
  flex-grow: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.chat-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.chat-item:hover {
  background: var(--glass-bg-hover);
}

.chat-item.active {
  background: var(--glass-bg-hover);
}

.chat-avatar {
  position: relative;
  flex-shrink: 0;
}

.avatar-circle {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 700;
  overflow: hidden;
}

.avatar-circle img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.online-status {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 14px;
  height: 14px;
  background: #31a24c;
  border: 3px solid var(--glass-bg-primary);
  border-radius: 50%;
}

.chat-info {
  flex-grow: 1;
  min-width: 0;
}

.chat-name-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 2px;
}

.chat-name {
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-time {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.chat-message-preview {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.unread .preview-text {
  font-weight: 700;
  color: var(--text-primary);
}

.preview-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-grow: 1;
}

.unread-dot {
  width: 12px;
  height: 12px;
  background: var(--primary-color);
  border-radius: 50%;
  margin-left: 0.5rem;
  flex-shrink: 0;
}

/* Chat Main */
.chat-main {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  background: rgba(0,0,0,0.1);
}

.chat-header {
  height: 70px;
  padding: 0 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--glass-border);
  background: var(--glass-bg-primary);
}

.chat-header-user {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.avatar-circle-small {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  overflow: hidden;
}

.avatar-circle-small img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-meta {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 700;
  font-size: 1rem;
}

.user-status {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.chat-header-actions {
  display: flex;
  gap: 0.5rem;
}

.chat-action-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: transparent;
  color: var(--primary-color);
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 50%;
  transition: background 0.2s;
}

.chat-action-btn:hover {
  background: var(--glass-bg-hover);
}

.messages-area {
  flex-grow: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.message-row {
  display: flex;
  gap: 0.5rem;
  max-width: 70%;
}

.message-row.me {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-avatar-mini {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  align-self: flex-end;
}

.message-avatar-mini img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.message-bubble {
  padding: 0.75rem 1rem;
  border-radius: 1.25rem;
  font-size: 0.95rem;
  line-height: 1.4;
  word-break: break-word;
}

.them .message-bubble {
  background: var(--glass-bg-secondary);
  color: var(--text-primary);
  border-bottom-left-radius: 0.25rem;
}

.me .message-bubble {
  background: var(--primary-color);
  color: white;
  border-bottom-right-radius: 0.25rem;
}

.chat-input-area {
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--glass-bg-primary);
  border-top: 1px solid var(--glass-border);
}

.input-actions-left {
  display: flex;
  gap: 0.25rem;
}

.input-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  color: var(--primary-color);
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.input-wrapper {
  flex-grow: 1;
  position: relative;
  display: flex;
  align-items: center;
}

.input-wrapper input {
  width: 100%;
  padding: 0.75rem 3rem 0.75rem 1rem;
  border-radius: 20px;
  border: none;
  background: var(--glass-bg-secondary);
  color: var(--text-primary);
  outline: none;
}

.emoji-btn {
  position: absolute;
  right: 0.5rem;
  background: transparent;
  border: none;
  color: var(--primary-color);
  padding: 0.5rem;
  cursor: pointer;
}

.send-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: transparent;
  color: var(--primary-color);
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.send-btn:disabled {
  color: var(--text-muted);
  cursor: default;
}

.no-chat-selected {
  flex-grow: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.welcome-box {
  text-align: center;
  color: var(--text-muted);
}

.welcome-box i {
  font-size: 4rem;
  margin-bottom: 1rem;
  color: var(--glass-border);
}

/* Details Sidebar */
.convo-details {
  width: 320px;
  border-left: 1px solid var(--glass-border);
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
  background: var(--glass-bg-primary);
}

.details-user-info {
  text-align: center;
  margin-bottom: 2rem;
}

.avatar-circle-large {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: var(--primary-color);
  margin: 0 auto 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2.5rem;
  font-weight: 800;
  overflow: hidden;
}

.avatar-circle-large img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.details-user-info h3 {
  margin: 0;
  font-size: 1.5rem;
}

.details-user-info p {
  color: var(--text-muted);
  font-size: 0.9rem;
}

.details-sections {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.section-trigger {
  width: 100%;
  padding: 0.75rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.section-trigger:hover {
  background: var(--glass-bg-hover);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  width: 500px;
  max-width: 90vw;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
}

.modal-header {
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--glass-border);
}

.modal-header h3 {
  margin: 0;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  color: var(--text-muted);
  cursor: pointer;
}

.search-input-wrapper {
  padding: 1rem;
}

.search-input-wrapper input {
  width: 100%;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  border: none;
  background: var(--glass-bg-secondary);
  color: var(--text-primary);
  outline: none;
}

.search-results {
  flex-grow: 1;
  overflow-y: auto;
  padding: 1rem;
}

.user-result-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.user-result-item:hover {
  background: var(--glass-bg-hover);
}

.user-avatar-small {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.user-avatar-small img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-circle-mini {
  width: 100%;
  height: 100%;
  background: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.8rem;
  font-weight: 700;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-info .name {
  font-weight: 600;
}

.user-info .username {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.loading-state, .empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted);
}

.mt-4 {
  margin-top: 1rem;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.w-full {
  width: 100%;
}
</style>
