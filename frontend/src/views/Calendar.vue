<template>
  <div class="legacy-page-container">
    <div class="page-title">

      <h1>Calendar</h1>
    
</div>
    
    <div class="page-subtitle">

      <p>Manage your schedule and events</p>
    
</div>

    <div class="page-actions">

      <button class="btn btn-primary" @click="createEvent">
        <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 5 L12 19 M5 12 L19 12" stroke="currentColor" stroke-width="2" fill="none"/>
        </svg>
        New Event
      </button>
      <button class="btn btn-outline" @click="toggleView">
        <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
          <rect x="3" y="4" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2" fill="none"/>
          <path d="M3 10 L21 10" stroke="currentColor" stroke-width="2"/>
          <path d="M8 2 L8 6 M16 2 L16 6" stroke="currentColor" stroke-width="2"/>
        </svg>
        {{ currentView }}
      </button>
    
</div>

    <div class="calendar-content">
      <!-- Calendar Navigation -->
      <div class="calendar-nav">
        <div class="nav-controls">
          <button class="btn btn-outline" @click="previousPeriod">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M15 18 L9 12 L15 6" stroke="currentColor" stroke-width="2" fill="none"/>
            </svg>
          </button>
          <div class="current-period">
            <h2>{{ currentPeriodLabel }}</h2>
          </div>
          <button class="btn btn-outline" @click="nextPeriod">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 6 L15 12 L9 18" stroke="currentColor" stroke-width="2" fill="none"/>
            </svg>
          </button>
        </div>
        
        <div class="view-controls">
          <button 
            v-for="view in viewOptions" 
            :key="view.value"
            class="view-btn"
            :class="{ active: currentView === view.value }"
            @click="currentView = view.value"
          >
            {{ view.label }}
          </button>
        </div>

        <div class="today-controls">
          <button class="btn btn-primary" @click="goToToday">Today</button>
        </div>
      </div>

      <!-- Calendar Grid -->
      <div class="calendar-container">
        <!-- Month View -->
        <div v-if="currentView === 'month'" class="month-view">
          <div class="weekdays">
            <div v-for="day in weekdays" :key="day" class="weekday">
              {{ day }}
            </div>
          </div>
          <div class="days-grid">
            <div 
              v-for="day in calendarDays" 
              :key="day.date"
              class="day-cell"
              :class="{ 
                'other-month': !day.currentMonth,
                'today': day.isToday,
                'selected': selectedDate === day.date,
                'has-events': day.events.length > 0
              }"
              @click="selectDate(day.date)"
            >
              <div class="day-number">{{ day.day }}</div>
              <div class="events-indicator">
                <div 
                  v-for="event in day.events.slice(0, 3)" 
                  :key="event.id"
                  class="event-dot"
                  :style="{ backgroundColor: event.color }"
                ></div>
                <span v-if="day.events.length > 3" class="more-events">
                  +{{ day.events.length - 3 }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Week View -->
        <div v-else-if="currentView === 'week'" class="week-view">
          <div class="week-header">
            <div v-for="day in weekDays" :key="day.date" class="week-day-header">
              <div class="day-name">{{ day.dayName }}</div>
              <div class="day-date">{{ day.day }}</div>
            </div>
          </div>
          <div class="time-grid">
            <div class="time-slots">
              <div v-for="hour in hours" :key="hour" class="time-slot">
                <div class="time-label">{{ formatHour(hour) }}</div>
                <div class="hour-events">
                  <div 
                    v-for="event in getEventsForHour(day.date, hour)" 
                    :key="event.id"
                    class="week-event"
                    :style="{ backgroundColor: event.color }"
                    @click="viewEvent(event)"
                  >
                    <div class="event-time">{{ formatTime(event.startTime) }}</div>
                    <div class="event-title">{{ event.title }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Day View -->
        <div v-else-if="currentView === 'day'" class="day-view">
          <div class="day-header">
            <h3>{{ selectedDateFormatted }}</h3>
            <div class="day-stats">
              <span class="stat">{{ selectedDayEvents.length }} events</span>
            </div>
          </div>
          <div class="day-time-grid">
            <div v-for="hour in hours" :key="hour" class="day-time-slot">
              <div class="time-label">{{ formatHour(hour) }}</div>
              <div class="day-hour-events">
                <div 
                  v-for="event in getEventsForHour(selectedDate, hour)" 
                  :key="event.id"
                  class="day-event"
                  :style="{ backgroundColor: event.color }"
                  @click="viewEvent(event)"
                >
                  <div class="event-time">{{ formatTime(event.startTime) }} - {{ formatTime(event.endTime) }}</div>
                  <div class="event-title">{{ event.title }}</div>
                  <div class="event-description">{{ event.description }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="calendar-sidebar">
        <!-- Mini Calendar -->
        <div class="mini-calendar">
          <div class="mini-header">
            <h4>{{ currentMonthYear }}</h4>
          </div>
          <div class="mini-weekdays">
            <div v-for="day in ['S', 'M', 'T', 'W', 'T', 'F', 'S']" :key="day" class="mini-weekday">
              {{ day }}
            </div>
          </div>
          <div class="mini-days">
            <div 
              v-for="day in miniCalendarDays" 
              :key="day.date"
              class="mini-day"
              :class="{ 
                'other-month': !day.currentMonth,
                'today': day.isToday,
                'selected': selectedDate === day.date,
                'has-events': day.events.length > 0
              }"
              @click="selectDate(day.date)"
            >
              {{ day.day }}
            </div>
          </div>
        </div>

        <!-- Upcoming Events -->
        <div class="upcoming-events">
          <h4>Upcoming Events</h4>
          <div class="events-list">
            <div 
              v-for="event in upcomingEvents" 
              :key="event.id"
              class="event-item"
              @click="viewEvent(event)"
            >
              <div class="event-color" :style="{ backgroundColor: event.color }"></div>
              <div class="event-info">
                <div class="event-title">{{ event.title }}</div>
                <div class="event-time">{{ formatDate(event.date) }} at {{ formatTime(event.startTime) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Event Categories -->
        <div class="event-categories">
          <h4>Categories</h4>
          <div class="category-list">
            <div 
              v-for="category in eventCategories" 
              :key="category.name"
              class="category-item"
            >
              <div class="category-color" :style="{ backgroundColor: category.color }"></div>
              <span class="category-name">{{ category.name }}</span>
              <span class="category-count">{{ category.count }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Event Modal -->
    <div v-if="showEventModal" class="modal-overlay" @click="closeEventModal">
      <div class="event-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ editingEvent ? 'Edit Event' : 'Create Event' }}</h3>
          <button class="btn-icon" @click="closeEventModal">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 6.41 L17.59 5 L12 10.59 L6.41 5 L5 6.41 L10.59 12 L5 17.59 L6.41 19 L12 13.41 L17.59 19 L19 17.59 L13.41 12 L19 6.41 Z" stroke="currentColor" stroke-width="2" fill="none"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Event Title</label>
            <input v-model="eventForm.title" type="text" class="form-input" placeholder="Enter event title" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Date</label>
              <input v-model="eventForm.date" type="date" class="form-input" />
            </div>
            <div class="form-group">
              <label>Time</label>
              <input v-model="eventForm.startTime" type="time" class="form-input" />
            </div>
          </div>
          <div class="form-group">
            <label>End Time</label>
            <input v-model="eventForm.endTime" type="time" class="form-input" />
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="eventForm.description" class="form-textarea" rows="3" placeholder="Add event description"></textarea>
          </div>
          <div class="form-group">
            <label>Category</label>
            <select v-model="eventForm.category" class="form-select">
              <option value="">Select category</option>
              <option v-for="category in eventCategories" :key="category.name" :value="category.name">
                {{ category.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Color</label>
            <div class="color-picker">
              <div 
                v-for="color in eventColors" 
                :key="color"
                class="color-option"
                :class="{ selected: eventForm.color === color }"
                :style="{ backgroundColor: color }"
                @click="eventForm.color = color"
              ></div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" @click="closeEventModal">Cancel</button>
          <button class="btn btn-danger" @click="deleteEvent" v-if="editingEvent">Delete</button>
          <button class="btn btn-primary" @click="saveEvent">
            {{ editingEvent ? 'Update' : 'Create' }} Event
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Reactive state
const currentView = ref('month')
const selectedDate = ref(new Date().toISOString().split('T')[0])
const currentMonth = ref(new Date().getMonth())
const currentYear = ref(new Date().getFullYear())
const showEventModal = ref(false)
const editingEvent = ref(null)

// View options
const viewOptions = [
  { value: 'day', label: 'Day' },
  { value: 'week', label: 'Week' },
  { value: 'month', label: 'Month' }
]

// Weekdays
const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

// Event form
const eventForm = ref({
  title: '',
  date: '',
  startTime: '',
  endTime: '',
  description: '',
  category: '',
  color: '#3b82f6'
})

// Event colors
const eventColors = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#ec4899', '#14b8a6', '#f97316', '#6366f1', '#84cc16'
]

// Event categories
const eventCategories = ref([
  { name: 'Meeting', color: '#3b82f6', count: 12 },
  { name: 'Task', color: '#10b981', count: 8 },
  { name: 'Reminder', color: '#f59e0b', count: 15 },
  { name: 'Personal', color: '#ef4444', count: 6 },
  { name: 'Work', color: '#8b5cf6', count: 20 }
])

// Mock events
const events = ref([
  {
    id: 1,
    title: 'Team Meeting',
    date: '2024-01-20',
    startTime: '10:00',
    endTime: '11:00',
    description: 'Weekly team sync meeting',
    category: 'Meeting',
    color: '#3b82f6'
  },
  {
    id: 2,
    title: 'Project Deadline',
    date: '2024-01-22',
    startTime: '17:00',
    endTime: '18:00',
    description: 'Submit final project deliverables',
    category: 'Task',
    color: '#ef4444'
  },
  {
    id: 3,
    title: 'Lunch with Client',
    date: '2024-01-23',
    startTime: '12:30',
    endTime: '14:00',
    description: 'Discuss project requirements',
    category: 'Meeting',
    color: '#10b981'
  },
  {
    id: 4,
    title: 'Code Review',
    date: '2024-01-24',
    startTime: '15:00',
    endTime: '16:00',
    description: 'Review pull requests',
    category: 'Work',
    color: '#8b5cf6'
  },
  {
    id: 5,
    title: 'Gym Session',
    date: '2024-01-25',
    startTime: '18:00',
    endTime: '19:00',
    description: 'Weekly workout',
    category: 'Personal',
    color: '#f59e0b'
  }
])

// Computed properties
const currentPeriodLabel = computed(() => {
  if (currentView.value === 'month') {
    return new Date(currentYear.value, currentMonth.value).toLocaleDateString('en-US', { 
      month: 'long', 
      year: 'numeric' 
    })
  } else if (currentView.value === 'week') {
    // Calculate week range
    return 'Week of ' + new Date(selectedDate.value).toLocaleDateString()
  } else {
    return new Date(selectedDate.value).toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    })
  }
})

const calendarDays = computed(() => {
  const days = []
  const firstDay = new Date(currentYear.value, currentMonth.value, 1)
  const lastDay = new Date(currentYear.value, currentMonth.value + 1, 0)
  const startDate = new Date(firstDay)
  startDate.setDate(startDate.getDate() - firstDay.getDay())
  
  for (let i = 0; i < 42; i++) {
    const date = new Date(startDate)
    date.setDate(startDate.getDate() + i)
    
    const dateStr = date.toISOString().split('T')[0]
    const dayEvents = events.value.filter(event => event.date === dateStr)
    
    days.push({
      date: dateStr,
      day: date.getDate(),
      currentMonth: date.getMonth() === currentMonth.value,
      isToday: dateStr === new Date().toISOString().split('T')[0],
      events: dayEvents
    })
  }
  
  return days
})

const miniCalendarDays = computed(() => {
  const days = []
  const firstDay = new Date(currentYear.value, currentMonth.value, 1)
  const lastDay = new Date(currentYear.value, currentMonth.value + 1, 0)
  const startDate = new Date(firstDay)
  startDate.setDate(startDate.getDate() - firstDay.getDay())
  
  for (let i = 0; i < 35; i++) {
    const date = new Date(startDate)
    date.setDate(startDate.getDate() + i)
    
    const dateStr = date.toISOString().split('T')[0]
    const dayEvents = events.value.filter(event => event.date === dateStr)
    
    days.push({
      date: dateStr,
      day: date.getDate(),
      currentMonth: date.getMonth() === currentMonth.value,
      isToday: dateStr === new Date().toISOString().split('T')[0],
      events: dayEvents
    })
  }
  
  return days
})

const currentMonthYear = computed(() => {
  return new Date(currentYear.value, currentMonth.value).toLocaleDateString('en-US', { 
    month: 'long', 
    year: 'numeric' 
  })
})

const selectedDateFormatted = computed(() => {
  return new Date(selectedDate.value).toLocaleDateString('en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
})

const selectedDayEvents = computed(() => {
  return events.value.filter(event => event.date === selectedDate.value)
})

const upcomingEvents = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  return events.value
    .filter(event => event.date >= today)
    .sort((a, b) => new Date(a.date) - new Date(b.date))
    .slice(0, 5)
})

const hours = computed(() => {
  return Array.from({ length: 24 }, (_, i) => i)
})

// Methods
const previousPeriod = () => {
  if (currentView.value === 'month') {
    currentMonth.value--
    if (currentMonth.value < 0) {
      currentMonth.value = 11
      currentYear.value--
    }
  } else if (currentView.value === 'week') {
    const date = new Date(selectedDate.value)
    date.setDate(date.getDate() - 7)
    selectedDate.value = date.toISOString().split('T')[0]
  } else {
    const date = new Date(selectedDate.value)
    date.setDate(date.getDate() - 1)
    selectedDate.value = date.toISOString().split('T')[0]
  }
}

const nextPeriod = () => {
  if (currentView.value === 'month') {
    currentMonth.value++
    if (currentMonth.value > 11) {
      currentMonth.value = 0
      currentYear.value++
    }
  } else if (currentView.value === 'week') {
    const date = new Date(selectedDate.value)
    date.setDate(date.getDate() + 7)
    selectedDate.value = date.toISOString().split('T')[0]
  } else {
    const date = new Date(selectedDate.value)
    date.setDate(date.getDate() + 1)
    selectedDate.value = date.toISOString().split('T')[0]
  }
}

const goToToday = () => {
  const today = new Date()
  selectedDate.value = today.toISOString().split('T')[0]
  currentMonth.value = today.getMonth()
  currentYear.value = today.getFullYear()
}

const toggleView = () => {
  const views = ['day', 'week', 'month']
  const currentIndex = views.indexOf(currentView.value)
  currentView.value = views[(currentIndex + 1) % views.length]
}

const selectDate = (date) => {
  selectedDate.value = date
  if (currentView.value === 'day') {
    // Update month if selecting different month
    const dateObj = new Date(date)
    currentMonth.value = dateObj.getMonth()
    currentYear.value = dateObj.getFullYear()
  }
}

const createEvent = () => {
  editingEvent.value = null
  eventForm.value = {
    title: '',
    date: selectedDate.value,
    startTime: '',
    endTime: '',
    description: '',
    category: '',
    color: '#3b82f6'
  }
  showEventModal.value = true
}

const viewEvent = (event) => {
  editingEvent.value = event
  eventForm.value = { ...event }
  showEventModal.value = true
}

const closeEventModal = () => {
  showEventModal.value = false
  editingEvent.value = null
}

const saveEvent = () => {
  if (editingEvent.value) {
    // Update existing event
    const index = events.value.findIndex(e => e.id === editingEvent.value.id)
    if (index > -1) {
      events.value[index] = { ...eventForm.value }
    }
  } else {
    // Create new event
    events.value.push({
      id: Date.now(),
      ...eventForm.value
    })
  }
  
  closeEventModal()
}

const deleteEvent = () => {
  if (editingEvent.value) {
    const index = events.value.findIndex(e => e.id === editingEvent.value.id)
    if (index > -1) {
      events.value.splice(index, 1)
    }
  }
  closeEventModal()
}

const getEventsForHour = (date, hour) => {
  return events.value.filter(event => {
    if (event.date !== date) return false
    const eventHour = parseInt(event.startTime.split(':')[0])
    return eventHour === hour
  })
}

const formatHour = (hour) => {
  return hour.toString().padStart(2, '0') + ':00'
}

const formatTime = (time) => {
  return time
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString()
}

onMounted(() => {
  console.log('Calendar component mounted')
})
</script>

<style scoped>
.calendar-content {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* Calendar Navigation */
.calendar-nav {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.nav-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.current-period h2 {
  color: #f1f5f9;
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

.view-controls {
  display: flex;
  gap: 0.5rem;
}

.view-btn {
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.3s ease;
}

.view-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #f1f5f9;
}

.view-btn.active {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.3);
  color: #60a5fa;
}

/* Calendar Container */
.calendar-container {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
}

/* Month View */
.month-view {
  width: 100%;
}

.weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.weekday {
  text-align: center;
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 600;
  padding: 0.5rem;
}

.days-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.5rem;
}

.day-cell {
  aspect-ratio: 1;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
}

.day-cell:hover {
  background: rgba(255, 255, 255, 0.1);
}

.day-cell.other-month {
  opacity: 0.3;
}

.day-cell.today {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.3);
}

.day-cell.selected {
  background: rgba(59, 130, 246, 0.3);
  border-color: #3b82f6;
}

.day-number {
  color: #f1f5f9;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.events-indicator {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
}

.event-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.more-events {
  color: #94a3b8;
  font-size: 0.75rem;
}

/* Week View */
.week-header {
  display: grid;
  grid-template-columns: 60px repeat(7, 1fr);
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.week-day-header {
  text-align: center;
  padding: 0.5rem;
}

.day-name {
  color: #f1f5f9;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.day-date {
  color: #94a3b8;
  font-size: 0.875rem;
}

.time-grid {
  display: grid;
  grid-template-columns: 60px 1fr;
}

.time-slots {
  display: flex;
  flex-direction: column;
}

.time-slot {
  display: flex;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  min-height: 60px;
}

.time-label {
  width: 60px;
  color: #94a3b8;
  font-size: 0.75rem;
  padding: 0.5rem;
  text-align: right;
}

.hour-events {
  flex: 1;
  padding: 0.25rem;
}

.week-event {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  color: white;
  font-size: 0.75rem;
  margin-bottom: 0.25rem;
  cursor: pointer;
}

/* Day View */
.day-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.day-header h3 {
  color: #f1f5f9;
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

.day-stats {
  color: #94a3b8;
  font-size: 0.875rem;
}

.day-time-grid {
  display: grid;
  grid-template-columns: 60px 1fr;
}

.day-time-slot {
  display: flex;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  min-height: 60px;
}

.day-hour-events {
  flex: 1;
  padding: 0.5rem;
}

.day-event {
  padding: 0.5rem;
  border-radius: 8px;
  color: white;
  margin-bottom: 0.5rem;
  cursor: pointer;
}

.event-time {
  font-size: 0.75rem;
  opacity: 0.8;
  margin-bottom: 0.25rem;
}

.event-title {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.event-description {
  font-size: 0.875rem;
  opacity: 0.9;
}

/* Sidebar */
.calendar-sidebar {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.mini-calendar {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1rem;
}

.mini-header h4 {
  color: #f1f5f9;
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  text-align: center;
}

.mini-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.25rem;
  margin-bottom: 0.5rem;
}

.mini-weekday {
  text-align: center;
  color: #94a3b8;
  font-size: 0.75rem;
  font-weight: 600;
}

.mini-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.25rem;
}

.mini-day {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  font-size: 0.75rem;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.mini-day:hover {
  background: rgba(255, 255, 255, 0.1);
}

.mini-day.other-month {
  opacity: 0.3;
}

.mini-day.today {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
}

.mini-day.selected {
  background: #3b82f6;
  color: white;
}

.mini-day.has-events::after {
  content: '';
  position: absolute;
  bottom: 2px;
  width: 4px;
  height: 4px;
  background: #3b82f6;
  border-radius: 50%;
}

.upcoming-events {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1rem;
}

.upcoming-events h4 {
  color: #f1f5f9;
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.event-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.event-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.event-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}

.event-info {
  flex: 1;
}

.event-title {
  color: #f1f5f9;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.event-time {
  color: #94a3b8;
  font-size: 0.75rem;
}

.event-categories {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1rem;
}

.event-categories h4 {
  color: #f1f5f9;
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.category-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.category-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.category-name {
  flex: 1;
  color: #f1f5f9;
  font-size: 0.875rem;
}

.category-count {
  color: #94a3b8;
  font-size: 0.75rem;
  font-weight: 600;
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

.event-modal {
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 2rem;
  width: 90%;
  max-width: 500px;
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-input,
.form-select,
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
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  background: rgba(255, 255, 255, 0.08);
}

.color-picker {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.color-option {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.color-option:hover {
  transform: scale(1.1);
}

.color-option.selected {
  border-color: white;
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

.btn-danger {
  background: linear-gradient(135deg, #ef4444, #f87171);
  color: white;
}

.btn-danger:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
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
  .calendar-content {
    grid-template-columns: 1fr;
  }
  
  .calendar-sidebar {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
  }
}

@media (max-width: 768px) {
  .calendar-nav {
    flex-direction: column;
    gap: 1rem;
  }
  
  .nav-controls {
    order: 2;
  }
  
  .view-controls {
    order: 1;
  }
  
  .today-controls {
    order: 3;
  }
  
  .days-grid {
    gap: 0.25rem;
  }
  
  .day-cell {
    padding: 0.25rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
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
