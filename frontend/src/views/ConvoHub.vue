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
      
      <div class="px-4 mb-2 flex gap-2">
        <button class="flex-1 py-1 px-2 rounded font-semibold text-sm transition-colors border" :class="chatTab === 'human' ? 'bg-primary-color border-primary-color text-white' : 'border-slate-600 text-slate-400 hover:text-white'" @click="chatTab = 'human'">Messages</button>
        <button class="flex-1 py-1 px-2 rounded font-semibold text-sm transition-colors border" :class="chatTab === 'ai' ? 'bg-primary-color border-primary-color text-white' : 'border-slate-600 text-slate-400 hover:text-white'" @click="chatTab = 'ai'">AI Chat</button>
      </div>

      <div v-show="chatTab === 'human'" class="chats-list custom-scrollbar">
        <div 
          v-for="chat in filteredChats" 
          :key="chat.id" 
          class="chat-item"
          :class="{ active: activeChatId === chat.id && !isAIChat, unread: chat.unread }"
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
      
      <div v-show="chatTab === 'ai'" class="chats-list custom-scrollbar">
        <div class="px-2 mb-2">
          <button class="w-full py-2.5 border border-dashed border-indigo-500/50 rounded-xl text-indigo-300 hover:bg-indigo-950/40 hover:border-indigo-400 transition-all duration-200 flex items-center justify-center gap-2" @click="createNewAIChat">
             <i class="fas fa-plus"></i> New AI Chat
          </button>
        </div>
        <div 
          v-for="session in aiSessions" 
          :key="session.id" 
          class="chat-item group"
          :class="{ active: activeChatId === session.id && isAIChat }"
          @click="selectAIChat(session)"
        >
          <div class="chat-avatar">
            <div class="avatar-circle bg-slate-900 border border-indigo-500/30 overflow-hidden" style="box-shadow: 0 0 12px rgba(99,102,241,0.2);">
              <img src="/ai_avatar.png" class="w-full h-full object-cover" />
            </div>
          </div>
          <div class="chat-info">
            <div class="chat-name-row">
              <span class="chat-name">{{ session.title }}</span>
              <span class="chat-time">{{ formatTime(session.updated_at) }}</span>
            </div>
            <div class="chat-message-preview">
              <span class="preview-text text-indigo-400/70"><i class="fas fa-sparkles text-xs mr-1"></i>AI Session</span>
            </div>
          </div>
          <button class="opacity-0 group-hover:opacity-100 transition-opacity ml-auto text-red-500/70 hover:text-red-400 p-1 flex-shrink-0" @click.stop="deleteChat(session)" title="Delete">
            <i class="fas fa-trash text-xs"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Active Chat Area -->
    <div class="chat-main">
      <template v-if="activeChat">
        <div class="chat-header">
          <div class="chat-header-user">
            <div class="avatar-circle-small" :class="isAIChat ? 'ai-header-avatar' : ''">
              <img v-if="isAIChat" src="/ai_avatar.png" class="w-full h-full object-cover" />
              <img v-else-if="activeChat.avatar_url" :src="activeChat.avatar_url" />
              <template v-else>
                 <span>{{ getInitials(activeChat.name) }}</span>
              </template>
            </div>
            <div class="user-meta">
              <span class="user-name">{{ activeChat.title || activeChat.name }}</span>
              <span class="user-status">{{ isAIChat ? 'AI Assistant • Online' : (activeChat.online ? 'Active now' : 'Offline') }}</span>
            </div>
          </div>
          <div class="chat-header-actions">
            <template v-if="!isAIChat">
                <button class="chat-action-btn"><i class="fas fa-phone"></i></button>
                <button class="chat-action-btn"><i class="fas fa-video"></i></button>
                <button class="chat-action-btn" @click="showDetails = !showDetails"><i class="fas fa-info-circle"></i></button>
            </template>
            <template v-else>
                <div class="ai-model-select">
                   <select v-model="selectedAIProvider" @change="saveAIPreference">
                       <option value="local_deepseek">Local DeepSeek R1 7B</option>
                       <option value="local_1.5b">Local DeepSeek R1 1.5B</option>
                       <option value="openai">OpenAI (BYOK)</option>
                       <option value="anthropic">Anthropic (BYOK)</option>
                       <option value="deepseek">DeepSeek External (BYOK)</option>
                   </select>
                </div>
                <button class="chat-action-btn ml-2" @click="renameChat(activeChat)" title="Rename Chat"><i class="fas fa-pen text-sm"></i></button>
                <button class="chat-action-btn ml-2 text-red-500 hover:text-red-400" @click="deleteChat(activeChat)" title="Delete Chat"><i class="fas fa-trash text-sm"></i></button>
            </template>
          </div>
        </div>
        
        <div v-if="isAIChat && queuePosition > 0" class="bg-indigo-900/40 text-indigo-300 p-2 text-center text-sm border-b border-indigo-800/50">
            <i class="fas fa-spinner fa-spin mr-2"></i> You are position <strong>{{ queuePosition }}</strong> in queue...
        </div>
        <div v-if="isAIChat && isAISearching" class="bg-blue-900/40 text-blue-300 p-2 text-center text-sm border-b border-blue-800/50">
            <i class="fas fa-globe fa-spin mr-2"></i> Searching the web for "<strong>{{ searchQueryActive }}</strong>"...
        </div>

        <div class="messages-area custom-scrollbar" ref="messagesArea">
          <div v-for="(msg, index) in activeChatContent" :key="index" :class="['message-row', isAIChat ? (msg.role === 'user' ? 'me' : 'them') : ((msg.sender_id && msg.sender_id === userStore.user?._id) || msg.role === 'user' ? 'me' : 'them')]">
            <div v-if="(!isAIChat && msg.sender_id !== userStore.user?._id) || (isAIChat && msg.role !== 'user')" class="message-avatar-mini" :style="isAIChat ? 'background: #0f172a; border-radius: 50%; box-shadow: 0 0 10px rgba(99,102,241,0.3);' : ''">
              <img v-if="activeChat.avatar_url && !isAIChat" :src="activeChat.avatar_url" />
              <div v-else class="avatar-circle-mini w-full h-full flex items-center justify-center">
                 <img v-if="isAIChat" src="/ai_avatar.png" class="w-full h-full rounded-full object-cover border border-indigo-500/30" />
                 <span v-else>{{ getInitials(activeChat.name) }}</span>
              </div>
            </div>
            <div class="message-bubble" :class="{ 'ai-bubble': isAIChat && msg.role !== 'user' }" :title="msg.timestamp">
              <template v-if="isAIChat && msg.role !== 'user'">
                  <div v-if="msg.isTyping && !msg.content && !isAISearching" class="flex space-x-1 p-2 items-center bg-slate-800/40 rounded-lg inline-flex mt-2 border border-slate-700/50">
                      <div class="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
                      <div class="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                      <div class="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
                  </div>
                  <div v-else class="markdown-body ai-markdown text-slate-100" :class="{'streaming-cursor': msg.isTyping}" v-html="renderAIMessage(msg.content)"></div>
              </template>
              <div v-else>{{ msg.content }}</div>
            </div>
          </div>
        </div>

        <div class="chat-input-area">
          <template v-if="isAIChat">
            <div class="input-wrapper flex-1">
              <input 
                type="text" 
                v-model="newMessage" 
                :placeholder="'Message AI Assistant...'"
                @keyup.enter="handleSendMessage"
                class="ai-input-field"
              />
            </div>
            <div class="input-actions-right">
              <button class="send-btn ai-send-btn" @click="handleSendMessage" :disabled="!newMessage.trim()">
                <i class="fas fa-paper-plane"></i>
              </button>
            </div>
          </template>
          <template v-else>
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
          </template>
        </div>
      </template>
      <div v-else class="no-chat-selected">
        <div class="welcome-box">
          <template v-if="isAIChat">
            <div class="ai-welcome-glow">
              <img src="/ai_avatar.png" class="w-24 h-24 rounded-full border-2 border-indigo-500/40 shadow-lg shadow-indigo-500/20 mx-auto" />
            </div>
            <h3 class="mt-4 text-lg font-bold text-slate-200">DHQ AI Assistant</h3>
            <p class="text-sm text-slate-400 mt-2 max-w-sm mx-auto">Ask me anything — I can write code, search the web, create files, and reason through complex problems.</p>
            <button class="btn btn-primary mt-6 px-6 py-2.5 rounded-xl shadow-lg shadow-indigo-500/20" @click="createNewAIChat"><i class="fas fa-plus mr-2"></i>Start New Chat</button>
          </template>
          <template v-else>
            <i class="fas fa-comments"></i>
            <h3>Select a conversation to start messaging</h3>
            <button class="btn btn-primary mt-4" @click="showSearchModal = true">Start New Conversation</button>
          </template>
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
import { ref, computed, onMounted, nextTick, watch, onUnmounted } from 'vue'
import { apiGet, apiPost } from '@/utils/api.js'
import { useUserStore } from '@/stores/userStore.js'
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
    
    if (text.includes("<think>") && !text.includes("</think>")) {
        text += "</think>";
    }

    const thinkRegex = /<think>([\s\S]*?)<\/think>/g;
    text = text.replace(thinkRegex, (match, p1) => {
        const renderedThinking = md.render(p1.trim());
        return `
<details class="think-accordion" open>
   <summary><i class="fas fa-brain mr-2"></i> Thinking Process...</summary>
   <div class="think-body">${renderedThinking}</div>
</details>
`;
    });
    
    return md.render(text);
};

const userStore = useUserStore()
let socket = null
const chatTab = ref('human')
const aiSessions = ref([])
const isAIChat = computed(() => chatTab.value === 'ai')
const queuePosition = ref(0)
const isAISearching = ref(false)
const searchQueryActive = ref("")
const selectedAIProvider = ref(localStorage.getItem('dhq_ai_model') || 'local_deepseek')

const saveAIPreference = () => {
    localStorage.setItem('dhq_ai_model', selectedAIProvider.value);
}
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

const activeChat = computed(() => {
    if (isAIChat.value) return aiSessions.value.find(c => c.id === activeChatId.value)
    return chats.value.find(c => c.id === activeChatId.value)
})

const selectAIChat = async (session) => {
    activeChatId.value = session.id
    try {
        const messages = await apiGet(`/ai/sessions/${session.id}/messages`)
        activeChatContent.value = messages.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
        scrollToBottom()
    } catch (e) {
        console.error('Failed to fetch AI messages', e)
    }
}

const selectChat = async (chat) => {
  activeChatId.value = chat.id
  chat.unread = false
  await fetchMessages()
  scrollToBottom()
}

const fetchAISessions = async () => {
  try {
    aiSessions.value = await apiGet('/ai/sessions')
  } catch (e) {
    console.error('Failed to fetch AI sessions', e)
  }
}

const renameChat = async (session) => {
    const newTitle = prompt("Enter new chat title:", session.title);
    if (newTitle && newTitle.trim() && newTitle.trim() !== session.title) {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${window.location.protocol}//${window.location.host}/api/ai/sessions/${session.id}`, {
                method: 'PUT',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ title: newTitle.trim() })
            });
            if (response.ok) {
                await fetchAISessions();
            } else {
                console.error("Rename failed", await response.text());
            }
        } catch (e) {
            console.error("Rename failed Exception", e);
        }
    }
}

const deleteChat = async (session) => {
    if (confirm(`Are you sure you want to delete this chat permanently?`)) {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${window.location.protocol}//${window.location.host}/api/ai/sessions/${session.id}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                activeChatId.value = null;
                await fetchAISessions();
            } else {
                console.error("Delete failed");
            }
        } catch (e) {
            console.error("Delete failed", e);
        }
    }
}

const createNewAIChat = async () => {
  try {
    const res = await apiPost('/ai/sessions?title=New+AI+Chat')
    await fetchAISessions()
    selectAIChat(res)
  } catch (e) {
    console.error('Failed to create AI chat', e)
  }
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
  
  if (isAIChat.value) {
      activeChatContent.value.push({ role: 'user', content: text, timestamp: new Date().toISOString() });
      scrollToBottom();
      
      const providerStr = selectedAIProvider.value.startsWith('local_') ? 'local' : selectedAIProvider.value;
      const modelNameStr = selectedAIProvider.value === 'local_1.5b' ? 'deepseek-r1:1.5b' : 'deepseek-r1:7b';
      
      const payload = {
          session_id: activeChatId.value,
          prompt: text,
          provider: providerStr,
          model_name: modelNameStr
      };
      
      const token = localStorage.getItem('token');
      
      console.log("Sending AI request:", payload);
      try {
          const response = await fetch(`${window.location.protocol}//${window.location.host}/api/ai/chat`, {
              method: 'POST',
              headers: { 
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${token}`
              },
              body: JSON.stringify(payload)
          });
          
          console.log("AI Chat API Response:", response.status, response.statusText);
          if (!response.ok) { 
              const errText = await response.text();
              console.error("AI chat HTTP error", response.status, errText); 
              return; 
          }
          
          const reader = response.body.getReader();
          const decoder = new TextDecoder('utf-8');
          
          const aiMsg = { role: 'assistant', content: '', timestamp: new Date().toISOString(), isTyping: true };
          activeChatContent.value.push(aiMsg);
          scrollToBottom();
          
          let buffer = '';
          while (true) {
              const { done, value } = await reader.read();
              if (done) break;
              
              const chunkStr = decoder.decode(value, {stream:true});
              buffer += chunkStr;
              
              const lines = buffer.split('\n');
              buffer = lines.pop(); // keep incomplete
              
              for (const line of lines) {
                  if (line.startsWith('data: ')) {
                      try {
                          const dataStr = line.replace('data: ', '');
                          if (dataStr.trim() === '[DONE]') continue;
                          const data = JSON.parse(dataStr);
                          console.log("AI stream chunk:", data);
                          
                          if (data.session_id) {
                              activeChatId.value = data.session_id; // Update active ID to new session if created
                              fetchAISessions(); // update list silently
                          }
                          
                          if (data.error) aiMsg.content += `\n\n**Error:** ${data.error}`;
                          else if (data.status === 'searching') {
                              isAISearching.value = true;
                              searchQueryActive.value = data.query;
                          } else if (data.status === 'search_complete') isAISearching.value = false;
                          else if (data.content !== undefined) aiMsg.content += data.content;
                          scrollToBottom();
                      } catch(e) {
                          console.error("AI stream parse error", e, line);
                      }
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
          // Delayed refresh to catch auto-renamed sessions
          setTimeout(() => fetchAISessions(), 3000);
      } catch (e) {
          console.error("Fetch failed", e);
          if (activeChatContent.value.length > 0) activeChatContent.value[activeChatContent.value.length-1].isTyping = false;
      }
      return;
  }
  
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
  await fetchAISessions()
  
  // Socket.io for queue
  const token = localStorage.getItem('token') || '';
  socket = io({
      auth: { token },
      transports: ['websocket', 'polling'],
      reconnection: false
  });
  
  socket.on('connect_error', () => {
      console.warn("Socket.IO queue connection bypassed.");
  });
  
  socket.on('ai_queue_status', (data) => {
      if (data.status === 'processing') queuePosition.value = 0;
      else if (data.position) queuePosition.value = data.position;
  });

  if (chats.value.length > 0 && !activeChatId.value) {
    selectChat(chats.value[0])
  }
})

onUnmounted(() => {
    if (socket) socket.disconnect();
})
</script>

<style scoped>
.ai-model-select {
  position: relative;
  display: flex;
  align-items: center;
  background: var(--glass-bg-secondary);
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  padding: 0;
  margin-right: 0.5rem;
}
.ai-model-select select {
  background: transparent;
  color: var(--text-primary);
  border: none;
  padding: 0.5rem 2rem 0.5rem 1rem;
  font-size: 0.85rem;
  font-weight: 600;
  outline: none;
  cursor: pointer;
  appearance: none;
}
.ai-model-select::after {
  content: '\f0d7';
  font-family: 'Font Awesome 5 Free';
  font-weight: 900;
  position: absolute;
  right: 0.6rem;
  color: var(--text-muted);
  pointer-events: none;
}

.message-bubble.ai-bubble {
  background: transparent !important;
  color: var(--text-primary) !important;
  box-shadow: none !important;
  max-width: 95% !important;
  padding: 0 0.5rem !important; 
}

.streaming-cursor::after {
    content: '▋';
    animation: blink 1s step-end infinite;
    display: inline-block;
    vertical-align: bottom;
    margin-left: 4px;
    color: #a5b4fc;
}
@keyframes blink { 50% { opacity: 0; } }

:deep(.ai-markdown) {
  font-family: inherit;
  color: inherit;
  background: transparent;
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
:deep(.ai-bubble) { width: 100%; border-radius: 8px !important; }

.bg-primary-color { background-color: var(--primary-color); }
.border-primary-color { border-color: var(--primary-color); }
.text-white { color: white; }
.hover\:text-white:hover { color: white; }

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
  max-width: 75%;
}

.message-row.them {
  max-width: 90%;
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
  background: linear-gradient(135deg, var(--primary-color), #7c3aed);
  color: white;
  border-bottom-right-radius: 0.25rem;
  box-shadow: 0 2px 12px rgba(99, 102, 241, 0.2);
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

/* AI-specific refinements */
.ai-header-avatar {
  background: #0f172a !important;
  border: 1.5px solid rgba(99, 102, 241, 0.4) !important;
  box-shadow: 0 0 14px rgba(99, 102, 241, 0.25);
}

.ai-input-field {
  width: 100%;
  padding: 0.85rem 1.25rem !important;
  border-radius: 24px !important;
  border: 1px solid rgba(99, 102, 241, 0.25) !important;
  background: rgba(15, 23, 42, 0.6) !important;
  color: var(--text-primary) !important;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.ai-input-field:focus {
  border-color: rgba(99, 102, 241, 0.5) !important;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
}

.ai-send-btn {
  background: linear-gradient(135deg, #6366f1, #7c3aed) !important;
  color: white !important;
  border-radius: 50% !important;
  box-shadow: 0 2px 10px rgba(99, 102, 241, 0.3);
  transition: transform 0.15s, box-shadow 0.15s;
}
.ai-send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4);
}
.ai-send-btn:disabled {
  opacity: 0.4;
  background: var(--glass-bg-secondary) !important;
  color: var(--text-muted) !important;
  box-shadow: none;
}

.ai-welcome-glow {
  animation: pulse-glow 3s ease-in-out infinite;
}
@keyframes pulse-glow {
  0%, 100% { filter: drop-shadow(0 0 8px rgba(99, 102, 241, 0.3)); }
  50% { filter: drop-shadow(0 0 20px rgba(99, 102, 241, 0.6)); }
}

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
  user-select: none;
  transition: background 0.15s;
}
:deep(.think-accordion summary:hover) {
  background: rgba(99, 102, 241, 0.08);
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
:deep(.think-body code) { 
  background: rgba(255, 255, 255, 0.06);
  padding: 0.1rem 0.3rem;
  border-radius: 3px;
}
</style>
