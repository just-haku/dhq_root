<template>
  <div class="legacy-page-container">
    <div class="page-title">

      <h1>Messages</h1>
    
</div>
    
    <div class="page-subtitle">

      <p>Communicate with your team and collaborators</p>
    
</div>

    <div class="page-actions">

      <button class="btn btn-primary" @click="composeMessage">
        <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
          <path d="M3 8 L12 3 L21 8 L21 16 L12 21 L3 16 L3 8 Z" stroke="currentColor" stroke-width="2" fill="none"/>
          <path d="M3 8 L12 13 L21 8" stroke="currentColor" stroke-width="2" fill="none"/>
        </svg>
        New Message
      </button>
      <button class="btn btn-outline" @click="refreshMessages">
        <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
          <path d="M21 2 L13.5 9.5 L16.5 9.5 L16.5 12.5 L10.5 12.5 L10.5 6.5 L13.5 6.5 L21 14 L21 2 Z" stroke="currentColor" stroke-width="2" fill="none"/>
          <path d="M3 22 L10.5 14.5 L7.5 14.5 L7.5 11.5 L13.5 11.5 L13.5 17.5 L10.5 17.5 L3 10 L3 22 Z" stroke="currentColor" stroke-width="2" fill="none"/>
        </svg>
        Refresh
      </button>
    
</div>

    <div class="messages-content">
      <!-- Search and Filters -->
      <div class="messages-header">
        <div class="search-section">
          <div class="search-bar">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2" fill="none"/>
              <path d="M21 21 L16.65 16.65" stroke="currentColor" stroke-width="2" fill="none"/>
            </svg>
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Search messages..."
              class="search-input"
            />
          </div>
        </div>
        
        <div class="filter-section">
          <select v-model="selectedFilter" class="filter-select">
            <option value="all">All Messages</option>
            <option value="unread">Unread</option>
            <option value="starred">Starred</option>
            <option value="sent">Sent</option>
            <option value="drafts">Drafts</option>
          </select>
          
          <select v-model="selectedFolder" class="filter-select">
            <option value="inbox">Inbox</option>
            <option value="sent">Sent</option>
            <option value="drafts">Drafts</option>
            <option value="trash">Trash</option>
          </select>
        </div>
      </div>

      <div class="messages-layout">
        <!-- Conversations List -->
        <div class="conversations-panel">
          <div class="panel-header">
            <h3>Conversations</h3>
            <div class="panel-actions">
              <button class="btn-icon" @click="toggleCompose" title="Compose">
                <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 5 L12 19 M5 12 L19 12" stroke="currentColor" stroke-width="2" fill="none"/>
                </svg>
              </button>
            </div>
          </div>
          
          <div class="conversations-list">
            <div 
              v-for="conversation in filteredConversations" 
              :key="conversation.id"
              class="conversation-item"
              :class="{ 
                'active': selectedConversation === conversation.id,
                'unread': !conversation.read,
                'starred': conversation.starred
              }"
              @click="selectConversation(conversation.id)"
            >
              <div class="conversation-avatar">
                <img :src="conversation.avatar" :alt="conversation.name" />
                <div class="online-indicator" v-if="conversation.online"></div>
              </div>
              
              <div class="conversation-content">
                <div class="conversation-header">
                  <h4>{{ conversation.name }}</h4>
                  <span class="conversation-time">{{ formatTime(conversation.timestamp) }}</span>
                </div>
                <p class="conversation-preview">{{ conversation.lastMessage }}</p>
                <div class="conversation-meta">
                  <span class="message-count">{{ conversation.messageCount }} messages</span>
                  <div class="conversation-tags">
                    <span 
                      v-for="tag in conversation.tags" 
                      :key="tag"
                      class="tag"
                    >
                      {{ tag }}
                    </span>
                  </div>
                </div>
              </div>
              
              <div class="conversation-actions">
                <button class="btn-icon" @click.stop="toggleStar(conversation)" title="Star">
                  <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2 L15.09 8.26 L22 9.27 L17 14.14 L18.18 21.02 L12 17.77 L5.82 21.02 L7 14.14 L2 9.27 L8.91 8.26 L12 2 Z" stroke="currentColor" stroke-width="2" fill="none"/>
                  </svg>
                </button>
                <button class="btn-icon" @click.stop="deleteConversation(conversation)" title="Delete">
                  <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3 6 L5 6 L21 6 M19 6 L21 18" stroke="currentColor" stroke-width="2" fill="none"/>
                    <path d="M18 6 L6 18" stroke="currentColor" stroke-width="2" fill="none"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Messages Panel -->
        <div class="messages-panel">
          <div v-if="selectedConversation" class="messages-container">
            <!-- Conversation Header -->
            <div class="messages-header-bar">
              <div class="recipient-info">
                <img :src="currentConversation.avatar" :alt="currentConversation.name" />
                <div class="recipient-details">
                  <h4>{{ currentConversation.name }}</h4>
                  <span class="recipient-status">{{ currentConversation.online ? 'Online' : 'Offline' }}</span>
                </div>
              </div>
              
              <div class="message-actions">
                <button class="btn-icon" @click="toggleStar(currentConversation)" title="Star">
                  <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2 L15.09 8.26 L22 9.27 L17 14.14 L18.18 21.02 L12 17.77 L5.82 21.02 L7 14.14 L2 9.27 L8.91 8.26 L12 2 Z" stroke="currentColor" stroke-width="2" fill="none"/>
                  </svg>
                </button>
                <button class="btn-icon" @click="searchInConversation" title="Search">
                  <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                    <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2" fill="none"/>
                    <path d="M21 21 L16.65 16.65" stroke="currentColor" stroke-width="2" fill="none"/>
                  </svg>
                </button>
                <button class="btn-icon" @click="showConversationOptions" title="More">
                  <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                    <circle cx="12" cy="12" r="1" fill="currentColor"/>
                    <circle cx="12" cy="5" r="1" fill="currentColor"/>
                    <circle cx="12" cy="19" r="1" fill="currentColor"/>
                  </svg>
                </button>
              </div>
            </div>

            <!-- Messages List -->
            <div class="messages-list" ref="messagesList">
              <div 
                v-for="message in currentMessages" 
                :key="message.id"
                class="message-item"
                :class="{ 'sent': message.sent, 'received': !message.sent }"
              >
                <div class="message-avatar">
                  <img :src="message.avatar" :alt="message.sender" />
                </div>
                
                <div class="message-content">
                  <div class="message-header">
                    <span class="message-sender">{{ message.sender }}</span>
                    <span class="message-time">{{ formatMessageTime(message.timestamp) }}</span>
                  </div>
                  
                  <div class="message-body">
                    <p v-if="message.type === 'text'">{{ message.content }}</p>
                    <div v-else-if="message.type === 'image'" class="message-image">
                      <img :src="message.content" :alt="message.alt" />
                    </div>
                    <div v-else-if="message.type === 'file'" class="message-file">
                      <div class="file-info">
                        <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M14 2 L6 2 C4.9 2 4 2.9 4 4 L4 20 C4 21.1 4.9 22 6 22 L18 22 C19.1 22 20 21.1 20 20 L20 8 L14 2 Z" stroke="currentColor" stroke-width="2" fill="none"/>
                          <path d="M14 2 L14 8 L20 8" stroke="currentColor" stroke-width="2" fill="none"/>
                        </svg>
                        <div class="file-details">
                          <span class="file-name">{{ message.fileName }}</span>
                          <span class="file-size">{{ message.fileSize }}</span>
                        </div>
                      </div>
                      <button class="btn btn-sm btn-outline">Download</button>
                    </div>
                  </div>
                  
                  <div class="message-footer">
                    <div class="message-reactions">
                      <span 
                        v-for="reaction in message.reactions" 
                        :key="reaction.emoji"
                        class="reaction"
                      >
                        {{ reaction.emoji }} {{ reaction.count }}
                      </span>
                    </div>
                    <div class="message-status">
                      <span v-if="message.read" class="read-indicator">✓✓</span>
                      <span v-else class="sent-indicator">✓</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Message Input -->
            <div class="message-input-container">
              <div class="input-toolbar">
                <button class="btn-icon" @click="attachFile" title="Attach file">
                  <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M21 15 L21 19 C21 20.1 20.1 21 19 21 L5 21 C3.9 21 3 20.1 3 19 L3 5 C3 3.9 3.9 3 5 3 L16 3 L21 8 L21 15 Z" stroke="currentColor" stroke-width="2" fill="none"/>
                    <path d="M17 8 L17 3 L7 3 L7 8" stroke="currentColor" stroke-width="2" fill="none"/>
                  </svg>
                </button>
                <button class="btn-icon" @click="insertEmoji" title="Insert emoji">
                  <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
                    <circle cx="8" cy="10" r="1" fill="currentColor"/>
                    <circle cx="16" cy="10" r="1" fill="currentColor"/>
                    <path d="M8 14 C8 16 10 18 12 18 C14 18 16 16 16 14" stroke="currentColor" stroke-width="2" fill="none"/>
                  </svg>
                </button>
                <button class="btn-icon" @click="formatText" title="Format text">
                  <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3 7 L21 7 M3 12 L15 12 M3 17 L18 17" stroke="currentColor" stroke-width="2" fill="none"/>
                  </svg>
                </button>
              </div>
              
              <div class="message-input-wrapper">
                <textarea 
                  v-model="newMessage"
                  placeholder="Type your message..."
                  class="message-textarea"
                  @keydown="handleMessageKeydown"
                  rows="1"
                ></textarea>
                <button 
                  class="send-button"
                  @click="sendMessage"
                  :disabled="!newMessage.trim()"
                >
                  <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M2 21 L21 12 L2 3 L2 10 L17 12 L2 14 L2 21 Z" stroke="currentColor" stroke-width="2" fill="none"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Empty State -->
          <div v-else class="empty-state">
            <div class="empty-icon">
              <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M3 8 L12 3 L21 8 L21 16 L12 21 L3 16 L3 8 Z" stroke="currentColor" stroke-width="2" fill="none"/>
                <path d="M3 8 L12 13 L21 8" stroke="currentColor" stroke-width="2" fill="none"/>
              </svg>
            </div>
            <h3>No conversation selected</h3>
            <p>Select a conversation to start messaging</p>
            <button class="btn btn-primary" @click="composeMessage">Start New Conversation</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Compose Modal -->
    <div v-if="showComposeModal" class="modal-overlay" @click="closeComposeModal">
      <div class="compose-modal" @click.stop>
        <div class="modal-header">
          <h3>New Message</h3>
          <button class="btn-icon" @click="closeComposeModal">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 6.41 L17.59 5 L12 10.59 L6.41 5 L5 6.41 L10.59 12 L5 17.59 L6.41 19 L12 13.41 L17.59 19 L19 17.59 L13.41 12 L19 6.41 Z" stroke="currentColor" stroke-width="2" fill="none"/>
            </svg>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="form-group">
            <label>To:</label>
            <input v-model="composeForm.recipients" type="text" class="form-input" placeholder="Enter recipients..." />
          </div>
          
          <div class="form-group">
            <label>Subject:</label>
            <input v-model="composeForm.subject" type="text" class="form-input" placeholder="Enter subject..." />
          </div>
          
          <div class="form-group">
            <label>Message:</label>
            <textarea v-model="composeForm.message" class="form-textarea" rows="8" placeholder="Type your message..."></textarea>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-outline" @click="saveDraft">Save Draft</button>
          <button class="btn btn-primary" @click="sendNewMessage">Send Message</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'

// Reactive state
const selectedConversation = ref(null)
const searchQuery = ref('')
const selectedFilter = ref('all')
const selectedFolder = ref('inbox')
const newMessage = ref('')
const showComposeModal = ref(false)

// Compose form
const composeForm = ref({
  recipients: '',
  subject: '',
  message: ''
})

// Mock conversations
const conversations = ref([
  {
    id: 1,
    name: 'John Doe',
    avatar: 'https://picsum.photos/seed/john/40/40.jpg',
    lastMessage: 'Hey, how are you doing? I wanted to discuss the project timeline...',
    timestamp: new Date('2024-01-20T10:30:00'),
    read: false,
    starred: true,
    online: true,
    messageCount: 24,
    tags: ['work', 'urgent']
  },
  {
    id: 2,
    name: 'Jane Smith',
    avatar: 'https://picsum.photos/seed/jane/40/40.jpg',
    lastMessage: 'Can you review the latest design mockups when you get a chance?',
    timestamp: new Date('2024-01-20T09:15:00'),
    read: true,
    starred: false,
    online: false,
    messageCount: 18,
    tags: ['design', 'review']
  },
  {
    id: 3,
    name: 'Development Team',
    avatar: 'https://picsum.photos/seed/team/40/40.jpg',
    lastMessage: 'Sprint planning meeting scheduled for tomorrow at 2 PM',
    timestamp: new Date('2024-01-19T16:45:00'),
    read: false,
    starred: false,
    online: true,
    messageCount: 156,
    tags: ['team', 'meeting']
  },
  {
    id: 4,
    name: 'Alice Johnson',
    avatar: 'https://picsum.photos/seed/alice/40/40.jpg',
    lastMessage: 'Thanks for your help with the API integration!',
    timestamp: new Date('2024-01-19T14:20:00'),
    read: true,
    starred: true,
    online: true,
    messageCount: 42,
    tags: ['api', 'integration']
  },
  {
    id: 5,
    name: 'Bob Wilson',
    avatar: 'https://picsum.photos/seed/bob/40/40.jpg',
    lastMessage: 'The client feedback looks good. Let\'s proceed with the implementation.',
    timestamp: new Date('2024-01-18T11:30:00'),
    read: true,
    starred: false,
    online: false,
    messageCount: 67,
    tags: ['client', 'feedback']
  }
])

// Mock messages for each conversation
const messagesData = ref({
  1: [
    {
      id: 1,
      sender: 'John Doe',
      avatar: 'https://picsum.photos/seed/john/32/32.jpg',
      content: 'Hey, how are you doing?',
      timestamp: new Date('2024-01-20T10:00:00'),
      sent: false,
      read: true,
      type: 'text',
      reactions: []
    },
    {
      id: 2,
      sender: 'You',
      avatar: 'https://picsum.photos/seed/you/32/32.jpg',
      content: 'Hi John! I\'m doing great, thanks for asking. How about you?',
      timestamp: new Date('2024-01-20T10:05:00'),
      sent: true,
      read: true,
      type: 'text',
      reactions: []
    },
    {
      id: 3,
      sender: 'John Doe',
      avatar: 'https://picsum.photos/seed/john/32/32.jpg',
      content: 'I wanted to discuss the project timeline. I think we might need to adjust the deadline.',
      timestamp: new Date('2024-01-20T10:30:00'),
      sent: false,
      read: false,
      type: 'text',
      reactions: [{ emoji: '🤔', count: 1 }]
    }
  ],
  2: [
    {
      id: 1,
      sender: 'Jane Smith',
      avatar: 'https://picsum.photos/seed/jane/32/32.jpg',
      content: 'Can you review the latest design mockups when you get a chance?',
      timestamp: new Date('2024-01-20T09:15:00'),
      sent: false,
      read: true,
      type: 'text',
      reactions: []
    }
  ]
})

// Computed properties
const filteredConversations = computed(() => {
  let filtered = conversations.value

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(conv => 
      conv.name.toLowerCase().includes(query) ||
      conv.lastMessage.toLowerCase().includes(query)
    )
  }

  // Apply status filter
  if (selectedFilter.value === 'unread') {
    filtered = filtered.filter(conv => !conv.read)
  } else if (selectedFilter.value === 'starred') {
    filtered = filtered.filter(conv => conv.starred)
  }

  return filtered.sort((a, b) => b.timestamp - a.timestamp)
})

const currentConversation = computed(() => {
  return conversations.value.find(conv => conv.id === selectedConversation.value)
})

const currentMessages = computed(() => {
  return messagesData.value[selectedConversation.value] || []
})

// Methods
const selectConversation = (conversationId) => {
  selectedConversation.value = conversationId
  
  // Mark conversation as read
  const conversation = conversations.value.find(conv => conv.id === conversationId)
  if (conversation) {
    conversation.read = true
  }
  
  // Scroll to bottom of messages
  nextTick(() => {
    scrollToBottom()
  })
}

const toggleStar = (conversation) => {
  conversation.starred = !conversation.starred
}

const deleteConversation = (conversation) => {
  const index = conversations.value.findIndex(conv => conv.id === conversation.id)
  if (index > -1) {
    conversations.value.splice(index, 1)
    if (selectedConversation.value === conversation.id) {
      selectedConversation.value = null
    }
  }
}

const sendMessage = () => {
  if (!newMessage.value.trim()) return
  
  const message = {
    id: Date.now(),
    sender: 'You',
    avatar: 'https://picsum.photos/seed/you/32/32.jpg',
    content: newMessage.value,
    timestamp: new Date(),
    sent: true,
    read: false,
    type: 'text',
    reactions: []
  }
  
  if (!messagesData.value[selectedConversation.value]) {
    messagesData.value[selectedConversation.value] = []
  }
  
  messagesData.value[selectedConversation.value].push(message)
  
  // Update conversation
  const conversation = conversations.value.find(conv => conv.id === selectedConversation.value)
  if (conversation) {
    conversation.lastMessage = newMessage.value
    conversation.timestamp = new Date()
    conversation.messageCount++
  }
  
  newMessage.value = ''
  
  nextTick(() => {
    scrollToBottom()
  })
}

const handleMessageKeydown = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

const scrollToBottom = () => {
  const messagesList = document.querySelector('.messages-list')
  if (messagesList) {
    messagesList.scrollTop = messagesList.scrollHeight
  }
}

const formatTime = (date) => {
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return 'Just now'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
  return date.toLocaleDateString()
}

const formatMessageTime = (date) => {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const composeMessage = () => {
  showComposeModal.value = true
}

const closeComposeModal = () => {
  showComposeModal.value = false
  composeForm.value = {
    recipients: '',
    subject: '',
    message: ''
  }
}

const sendNewMessage = () => {
  console.log('Sending new message:', composeForm.value)
  closeComposeModal()
}

const saveDraft = () => {
  console.log('Saving draft:', composeForm.value)
}

const refreshMessages = () => {
  console.log('Refreshing messages...')
}

const toggleCompose = () => {
  composeMessage()
}

const searchInConversation = () => {
  console.log('Search in conversation...')
}

const showConversationOptions = () => {
  console.log('Show conversation options...')
}

const attachFile = () => {
  console.log('Attach file...')
}

const insertEmoji = () => {
  console.log('Insert emoji...')
}

const formatText = () => {
  console.log('Format text...')
}

onMounted(() => {
  console.log('Messages component mounted')
})
</script>

<style scoped>
.messages-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Messages Header */
.messages-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
}

.search-section {
  flex: 1;
  max-width: 400px;
}

.search-bar {
  position: relative;
}

.search-bar .icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  width: 1.25rem;
  height: 1.25rem;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 3rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #f1f5f9;
  font-size: 0.875rem;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
  background: rgba(255, 255, 255, 0.08);
}

.filter-section {
  display: flex;
  gap: 1rem;
}

.filter-select {
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #f1f5f9;
  font-size: 0.875rem;
  min-width: 150px;
}

/* Messages Layout */
.messages-layout {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 1.5rem;
  height: calc(100vh - 300px);
}

/* Conversations Panel */
.conversations-panel {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.panel-header h3 {
  color: #f1f5f9;
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
}

.panel-actions {
  display: flex;
  gap: 0.5rem;
}

.conversations-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.conversation-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 0.5rem;
}

.conversation-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.conversation-item.active {
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.conversation-item.unread {
  background: rgba(255, 255, 255, 0.02);
}

.conversation-avatar {
  position: relative;
  flex-shrink: 0;
}

.conversation-avatar img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.online-indicator {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 12px;
  height: 12px;
  background: #10b981;
  border: 2px solid rgba(15, 23, 42, 0.6);
  border-radius: 50%;
}

.conversation-content {
  flex: 1;
  min-width: 0;
}

.conversation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.conversation-header h4 {
  color: #f1f5f9;
  font-size: 0.875rem;
  font-weight: 600;
  margin: 0;
}

.conversation-time {
  color: #94a3b8;
  font-size: 0.75rem;
}

.conversation-preview {
  color: #94a3b8;
  font-size: 0.875rem;
  margin: 0 0 0.5rem 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.message-count {
  color: #64748b;
  font-size: 0.75rem;
}

.conversation-tags {
  display: flex;
  gap: 0.25rem;
}

.tag {
  padding: 0.125rem 0.375rem;
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
  border-radius: 4px;
  font-size: 0.625rem;
  font-weight: 500;
}

.conversation-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.conversation-item:hover .conversation-actions {
  opacity: 1;
}

/* Messages Panel */
.messages-panel {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
}

.messages-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.messages-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.recipient-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.recipient-info img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.recipient-details h4 {
  color: #f1f5f9;
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.25rem 0;
}

.recipient-status {
  color: #10b981;
  font-size: 0.75rem;
}

.message-actions {
  display: flex;
  gap: 0.5rem;
}

.messages-list {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.message-item {
  display: flex;
  gap: 1rem;
  max-width: 70%;
}

.message-item.sent {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-avatar img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.message-content {
  flex: 1;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.message-sender {
  color: #f1f5f9;
  font-size: 0.875rem;
  font-weight: 600;
}

.message-time {
  color: #94a3b8;
  font-size: 0.75rem;
}

.message-body {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 0.5rem;
}

.message-item.sent .message-body {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.3);
}

.message-body p {
  color: #f1f5f9;
  margin: 0;
  line-height: 1.5;
}

.message-image img {
  max-width: 100%;
  border-radius: 8px;
}

.message-file {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.file-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.file-name {
  color: #f1f5f9;
  font-size: 0.875rem;
  font-weight: 500;
}

.file-size {
  color: #94a3b8;
  font-size: 0.75rem;
}

.message-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.message-reactions {
  display: flex;
  gap: 0.5rem;
}

.reaction {
  padding: 0.25rem 0.5rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.reaction:hover {
  background: rgba(255, 255, 255, 0.2);
}

.message-status {
  color: #94a3b8;
  font-size: 0.75rem;
}

.read-indicator {
  color: #10b981;
}

/* Message Input */
.message-input-container {
  padding: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.input-toolbar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.message-input-wrapper {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
}

.message-textarea {
  flex: 1;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #f1f5f9;
  font-size: 0.875rem;
  resize: none;
  min-height: 44px;
  max-height: 120px;
  font-family: inherit;
}

.message-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  background: rgba(255, 255, 255, 0.08);
}

.send-button {
  padding: 0.75rem;
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  border: none;
  border-radius: 12px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Empty State */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 3rem;
}

.empty-icon {
  width: 64px;
  height: 64px;
  color: #64748b;
  margin-bottom: 1.5rem;
}

.empty-state h3 {
  color: #f1f5f9;
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
}

.empty-state p {
  color: #94a3b8;
  margin: 0 0 2rem 0;
}

/* Modal */
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

.compose-modal {
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 2rem;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.modal-header h3 {
  color: #f1f5f9;
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  color: #f1f5f9;
  font-weight: 500;
  font-size: 0.875rem;
}

.form-input,
.form-textarea {
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #f1f5f9;
  font-size: 0.875rem;
  transition: all 0.3s ease;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  background: rgba(255, 255, 255, 0.08);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

/* Buttons */
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-outline {
  background: rgba(255, 255, 255, 0.05);
  color: #f1f5f9;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-outline:hover {
  background: rgba(255, 255, 255, 0.1);
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
}

.btn-icon {
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-icon:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #f1f5f9;
}

.icon {
  width: 1rem;
  height: 1rem;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .messages-layout {
    grid-template-columns: 300px 1fr;
  }
  
  .messages-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .search-section {
    max-width: 100%;
  }
}

@media (max-width: 768px) {
  .messages-layout {
    grid-template-columns: 1fr;
    height: auto;
  }
  
  .conversations-panel {
    height: 400px;
  }
  
  .messages-panel {
    height: 500px;
  }
  
  .message-item {
    max-width: 85%;
  }
  
  .modal-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .modal-footer {
    flex-direction: column;
  }
}
</style>

<style scoped>
.legacy-page-container {
  padding: 1rem;
}
.page-title { margin-bottom: 0.5rem; }
.page-subtitle { color: var(--text-secondary); margin-bottom: 1rem; }
.page-actions { margin-bottom: 1.5rem; }
</style>
