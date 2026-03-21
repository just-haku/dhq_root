# Digital HQ - Collaboration System Detailed Documentation

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [User Interface Components](#user-interface-components)
3. [Data Structures & Models](#data-structures--models)
4. [Form Field Specifications](#form-field-specifications)
5. [Validation Logic](#validation-logic)
6. [Video Management System](#video-management-system)
7. [Drive Integration](#drive-integration)
8. [Status Management](#status-management)
9. [API Endpoints](#api-endpoints)
10. [Error Handling](#error-handling)
11. [User Experience Flow](#user-experience-flow)

---

## 🎯 System Overview

### Purpose
The Collaboration system is designed to manage video collaborations between creators and brands, providing a comprehensive workflow from creation to completion.

### Key Features
- **Filter System**: On Going, Halted, Declined, Done (Default: On Going)
- **Dynamic Video Sections**: Expand based on number of videos
- **Platform Support**: TikTok, Instagram, YouTube
- **Payment Tracking**: Paid, Product, Paid Product
- **Video Draft Management**: Upload or link videos with Drive integration
- **Status Management**: Halt, Decline, Done with reasons
- **Quota Management**: Integration with Drive storage quotas

---

## 🎨 User Interface Components

### Main Collaboration Interface

```vue
<template>
  <div class="collaboration">
    <!-- Header Section -->
    <div class="collaboration-header">
      <h1>Collaborations</h1>
      <button class="btn-primary" @click="createNewCollaboration">
        <i class="fas fa-plus"></i>
        Create New Collaboration
      </button>
    </div>

    <!-- Filter Tabs -->
    <div class="filter-tabs">
      <button 
        v-for="filter in filters" 
        :key="filter.value"
        :class="{ active: activeFilter === filter.value }"
        @click="setActiveFilter(filter.value)"
      >
        <i :class="filter.icon"></i>
        {{ filter.label }}
        <span class="count" v-if="getFilterCount(filter.value)">
          {{ getFilterCount(filter.value) }}
        </span>
      </button>
    </div>

    <!-- Collaboration List -->
    <div class="collaboration-list">
      <div 
        v-for="collab in filteredCollaborations" 
        :key="collab.id"
        class="collaboration-card"
        @click="viewCollaboration(collab)"
      >
        <!-- Card Content -->
      </div>
    </div>
  </div>
</template>
```

### Filter Tab Configuration

```javascript
const filterTabs = [
  {
    value: 'On Going',
    label: 'On Going',
    color: '#3b82f6',
    icon: 'fas fa-play-circle',
    description: 'Active collaborations in progress'
  },
  {
    value: 'Halted',
    label: 'Halted',
    color: '#f59e0b',
    icon: 'fas fa-pause-circle',
    description: 'Collaborations temporarily stopped'
  },
  {
    value: 'Declined',
    label: 'Declined',
    color: '#ef4444',
    icon: 'fas fa-times-circle',
    description: 'Rejected collaboration proposals'
  },
  {
    value: 'Done',
    label: 'Done',
    color: '#10b981',
    icon: 'fas fa-check-circle',
    description: 'Completed collaborations'
  }
]
```

---

## 📊 Data Structures & Models

### Complete Collaboration Model

```javascript
const collaborationModel = {
  // Basic Information
  id: {
    type: String,
    required: true,
    generated: true,
    description: 'Unique identifier for the collaboration'
  },
  name: {
    type: String,
    required: true,
    minLength: 3,
    maxLength: 50,
    validation: /^[a-zA-Z0-9\s\-_]+$/,
    description: 'Human-readable collaboration name'
  },
  channel: {
    type: String,
    required: true,
    minLength: 2,
    maxLength: 30,
    validation: /^[a-zA-Z0-9_\-\.@]+$/,
    description: 'Social media channel name'
  },
  platform: {
    type: Array<String>,
    required: true,
    minItems: 1,
    maxItems: 3,
    allowedValues: ['TikTok', 'Instagram', 'YouTube'],
    description: 'Platforms where content will be posted'
  },
  collaboratorEmail: {
    type: String,
    required: false,
    validation: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    description: 'Optional collaborator email for notifications'
  },
  type: {
    type: String,
    required: true,
    allowedValues: ['Paid', 'Product', 'Paid Product'],
    defaultValue: 'Paid',
    description: 'Type of compensation'
  },
  price: {
    type: Number,
    required: true,
    min: 0,
    max: 9999999,
    step: 0.01,
    conditional: {
      when: 'type',
      equals: 'Product',
      action: 'disable',
      setValue: 0
    },
    description: 'Total compensation amount'
  },
  numVideos: {
    type: Number,
    required: true,
    min: 1,
    max: 50,
    description: 'Number of videos to be created'
  },

  // Status Information
  status: {
    type: String,
    allowedValues: ['On Going', 'Halted', 'Declined', 'Done'],
    defaultValue: 'On Going',
    description: 'Current collaboration status'
  },
  completedVideos: {
    type: Number,
    default: 0,
    description: 'Number of completed videos'
  },
  haltReason: {
    type: String,
    required: false,
    description: 'Reason for halting collaboration'
  },
  declineReason: {
    type: String,
    required: false,
    description: 'Reason for declining collaboration'
  },

  // Video Details (Dynamic Array)
  videos: [{
    id: String,
    index: Number,
    number: Number,
    
    // Content Fields
    script: {
      value: String,
      maxLength: 5000,
      expandable: true,
      collapsible: true,
      autoSave: true,
      wordCount: Number,
      characterCount: Number
    },
    title: {
      value: String,
      maxLength: 100,
      autoSave: true,
      characterCount: Number
    },
    subtitles: {
      value: String,
      maxLength: 2000,
      expandable: true,
      collapsible: true,
      autoSave: true,
      wordCount: Number,
      characterCount: Number
    },
    caption: {
      value: String,
      maxLength: 3000,
      expandable: true,
      collapsible: true,
      autoSave: true,
      wordCount: Number,
      characterCount: Number,
      hashtagHighlight: true,
      mentionHighlight: true
    },
    hashtags: {
      value: String,
      maxLength: 1000,
      expandable: true,
      collapsible: true,
      autoSave: true,
      hashtagCount: Number,
      validation: /^(\s*#[a-zA-Z0-9_]+\s*)*$/
    },

    // Media Fields
    draftFile: File,
    draftLink: String,
    thumbnail: String,

    // Status Fields
    invitation: Boolean,
    postLinks: Object, // Dynamic based on selected platforms
    paid: Boolean,
    done: Boolean,

    // Metadata
    metadata: {
      duration: Number,
      format: String,
      size: Number,
      uploadedAt: String,
      completedAt: String,
      lastModified: String
    },

    // UI State
    uiState: {
      scriptExpanded: Boolean,
      subtitlesExpanded: Boolean,
      captionExpanded: Boolean,
      hashtagsExpanded: Boolean,
      isUploading: Boolean,
      uploadProgress: Number,
      showThumbnail: Boolean
    }
  }],

  // System Fields
  collaborationLink: String,
  createdAt: String,
  updatedAt: String,
  createdBy: String,
  creatorRole: String
}
```

---

## 📝 Form Field Specifications

### Name Field (Required - Short Input)

```javascript
const nameFieldSpec = {
  type: 'text',
  label: 'Name',
  placeholder: 'Enter collaboration name',
  required: true,
  minLength: 3,
  maxLength: 50,
  validation: {
    pattern: /^[a-zA-Z0-9\s\-_]+$/,
    errorMessage: 'Name must be 3-50 characters and contain only letters, numbers, spaces, hyphens, and underscores'
  },
  realTimeValidation: true,
  autoSave: false,
  description: 'This name will be used to identify the collaboration and generate the storage path',
  examples: [
    'Summer Fashion Campaign',
    'Tech Product Review',
    'Brand Partnership 2024'
  ],
  ui: {
    icon: 'fas fa-tag',
    color: '#3b82f6',
    size: 'medium'
  }
}
```

### Channel Field (Required - Short Input)

```javascript
const channelFieldSpec = {
  type: 'text',
  label: 'Channel',
  placeholder: '@channelname or channel name',
  required: true,
  minLength: 2,
  maxLength: 30,
  validation: {
    pattern: /^[a-zA-Z0-9_\-\.@]+$/,
    errorMessage: 'Channel name must be 2-30 characters'
  },
  realTimeValidation: true,
  autoSave: false,
  description: 'The social media channel where the content will be posted',
  examples: [
    '@fashionista',
    '@techguru',
    'Brand Official'
  ],
  ui: {
    icon: 'fab fa-instagram',
    color: '#E4405F',
    size: 'medium'
  }
}
```

### Platform Field (Required - Checkboxes)

```javascript
const platformFieldSpec = {
  type: 'checkbox',
  label: 'Platform',
  required: true,
  minSelected: 1,
  maxSelected: 3,
  options: [
    {
      value: 'TikTok',
      label: 'TikTok',
      icon: 'fab fa-tiktok',
      color: '#000000',
      description: 'TikTok platform for short-form videos (15-60 seconds)',
      requirements: 'Vertical format (9:16), music-focused content'
    },
    {
      value: 'Instagram',
      label: 'Instagram',
      icon: 'fab fa-instagram',
      color: '#E4405F',
      description: 'Instagram platform for photos and videos',
      requirements: 'Square (1:1) or vertical (4:5) format, high-quality visuals'
    },
    {
      value: 'YouTube',
      label: 'YouTube',
      icon: 'fab fa-youtube',
      color: '#FF0000',
      description: 'YouTube platform for long-form videos',
      requirements: 'Horizontal format (16:9), minimum 10 minutes recommended'
    }
  ],
  validation: {
    minSelected: 1,
    maxSelected: 3,
    errorMessage: 'At least one platform must be selected'
  },
  description: 'Select all platforms where this collaboration will be posted',
  ui: {
    layout: 'horizontal',
    size: 'large',
    showDescriptions: true
  }
}
```

### Collaborator Email Field (Not Required - Short Input)

```javascript
const collaboratorEmailFieldSpec = {
  type: 'email',
  label: 'Collaborator Email',
  placeholder: 'collaborator@example.com',
  required: false,
  validation: {
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    errorMessage: 'Please enter a valid email address'
  },
  realTimeValidation: true,
  autoSave: false,
  description: 'Optional: Email of the collaborator for notifications and updates',
  features: {
    emailValidation: true,
    domainCheck: true,
    suggestions: true
  },
  ui: {
    icon: 'fas fa-envelope',
    color: '#6b7280',
    size: 'medium'
  }
}
```

### Type Field (Required - Dropdown Menu)

```javascript
const typeFieldSpec = {
  type: 'select',
  label: 'Type',
  required: true,
  defaultValue: 'Paid',
  options: [
    {
      value: 'Paid',
      label: 'Paid',
      description: 'Monetary compensation for collaboration',
      icon: 'fas fa-dollar-sign',
      color: '#10b981',
      requirements: 'Price must be specified'
    },
    {
      value: 'Product',
      label: 'Product',
      description: 'Free products/services provided',
      icon: 'fas fa-box',
      color: '#3b82f6',
      requirements: 'Price automatically set to $0'
    },
    {
      value: 'Paid Product',
      label: 'Paid Product',
      description: 'Products at discounted price',
      icon: 'fas fa-tag',
      color: '#f59e0b',
      requirements: 'Price must be specified (discounted rate)'
    }
  ],
  validation: {
    required: true,
    errorMessage: 'Collaboration type is required'
  },
  description: 'Type of compensation for this collaboration',
  conditionalLogic: {
    when: 'value',
    equals: 'Product',
    then: {
      disableField: 'price',
      setFieldValue: 'price',
      setValue: 0,
      showMessage: 'Price is automatically set to $0 for Product type'
    }
  },
  ui: {
    icon: 'fas fa-handshake',
    color: '#8b5cf6',
    size: 'medium',
    showIcons: true
  }
}
```

### Price Field (Required - Number Input)

```javascript
const priceFieldSpec = {
  type: 'number',
  label: 'Price',
  placeholder: '0.00',
  required: true,
  min: 0,
  max: 9999999,
  step: 0.01,
  validation: {
    min: 0,
    max: 9999999,
    errorMessage: 'Price must be a positive number between $0 and $9,999,999'
  },
  formatting: {
    currency: 'USD',
    prefix: '$',
    thousandsSeparator: ',',
    decimalPlaces: 2
  },
  conditional: {
    when: 'type',
    equals: 'Product',
    action: 'disable',
    setValue: 0,
    message: 'Price is automatically set to $0 for Product type'
  },
  description: 'Total compensation amount',
  features: {
    currencyFormatting: true,
    quickAmounts: [100, 500, 1000, 5000],
    calculator: true
  },
  ui: {
    icon: 'fas fa-dollar-sign',
    color: '#10b981',
    size: 'medium'
  }
}
```

### Number of Videos Field (Required - Number Input)

```javascript
const numVideosFieldSpec = {
  type: 'number',
  label: 'Number of Videos',
  placeholder: '1',
  required: true,
  min: 1,
  max: 50,
  validation: {
    min: 1,
    max: 50,
    errorMessage: 'Number of videos must be between 1 and 50'
  },
  description: 'How many videos will be created for this collaboration',
  onChange: 'updateVideoSections',
  features: {
    quickCounts: [1, 3, 5, 10],
    slider: true,
    preview: true
  },
  ui: {
    icon: 'fas fa-video',
    color: '#ef4444',
    size: 'medium'
  }
}
```

---

## ✅ Validation Logic

### Comprehensive Form Validation

```javascript
const validateCollaborationForm = (form) => {
  const errors = []
  const warnings = []
  const info = []

  // Name Validation
  if (!form.name || form.name.trim().length < 3) {
    errors.push({
      field: 'name',
      message: 'Name is required and must be at least 3 characters',
      type: 'error'
    })
  } else if (form.name.length > 50) {
    errors.push({
      field: 'name',
      message: 'Name cannot exceed 50 characters',
      type: 'error'
    })
  } else if (!/^[a-zA-Z0-9\s\-_]+$/.test(form.name)) {
    errors.push({
      field: 'name',
      message: 'Name can only contain letters, numbers, spaces, hyphens, and underscores',
      type: 'error'
    })
  }

  // Channel Validation
  if (!form.channel || form.channel.trim().length < 2) {
    errors.push({
      field: 'channel',
      message: 'Channel is required and must be at least 2 characters',
      type: 'error'
    })
  } else if (form.channel.length > 30) {
    errors.push({
      field: 'channel',
      message: 'Channel name cannot exceed 30 characters',
      type: 'error'
    })
  }

  // Platform Validation
  if (!form.platform || form.platform.length === 0) {
    errors.push({
      field: 'platform',
      message: 'At least one platform must be selected',
      type: 'error'
    })
  } else if (form.platform.length > 3) {
    errors.push({
      field: 'platform',
      message: 'Maximum 3 platforms can be selected',
      type: 'error'
    })
  }

  // Email Validation (Optional)
  if (form.collaboratorEmail && form.collaboratorEmail.trim()) {
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.collaboratorEmail)) {
      warnings.push({
        field: 'collaboratorEmail',
        message: 'Collaborator email format appears to be invalid',
        type: 'warning'
      })
    } else {
      info.push({
        field: 'collaboratorEmail',
        message: 'Collaborator will receive notifications at this email',
        type: 'info'
      })
    }
  }

  // Type Validation
  if (!form.type) {
    errors.push({
      field: 'type',
      message: 'Collaboration type is required',
      type: 'error'
    })
  }

  // Price Validation
  if (form.type !== 'Product') {
    if (form.price === undefined || form.price === null || form.price < 0) {
      errors.push({
        field: 'price',
        message: 'Price is required and must be a positive number',
        type: 'error'
      })
    } else if (form.price > 9999999) {
      errors.push({
        field: 'price',
        message: 'Price cannot exceed $9,999,999',
        type: 'error'
      })
    } else if (form.price === 0 && form.type === 'Paid') {
      warnings.push({
        field: 'price',
        message: 'Price is set to $0 for a Paid collaboration. Consider using Product type instead',
        type: 'warning'
      })
    }
  }

  // Number of Videos Validation
  if (!form.numVideos || form.numVideos < 1 || form.numVideos > 50) {
    errors.push({
      field: 'numVideos',
      message: 'Number of videos must be between 1 and 50',
      type: 'error'
    })
  } else if (form.numVideos > 10) {
    warnings.push({
      field: 'numVideos',
      message: `Large number of videos (${form.numVideos}). Consider breaking into smaller collaborations`,
      type: 'warning'
    })
  }

  return {
    isValid: errors.length === 0,
    errors: errors,
    warnings: warnings,
    info: info,
    canSubmit: errors.length === 0,
    summary: {
      totalErrors: errors.length,
      totalWarnings: warnings.length,
      totalInfo: info.length
    }
  }
}
```

### Real-time Field Validation

```javascript
const fieldValidation = reactive({
  name: { valid: true, message: '', type: 'success' },
  channel: { valid: true, message: '', type: 'success' },
  platform: { valid: true, message: '', type: 'success' },
  collaboratorEmail: { valid: true, message: '', type: 'success' },
  type: { valid: true, message: '', type: 'success' },
  price: { valid: true, message: '', type: 'success' },
  numVideos: { valid: true, message: '', type: 'success' }
})

const validateField = (fieldName, value, context = {}) => {
  switch (fieldName) {
    case 'name':
      if (!value || value.trim().length < 3) {
        fieldValidation.name = { 
          valid: false, 
          message: 'Name must be at least 3 characters', 
          type: 'error' 
        }
      } else if (value.length > 50) {
        fieldValidation.name = { 
          valid: false, 
          message: 'Name cannot exceed 50 characters', 
          type: 'error' 
        }
      } else if (!/^[a-zA-Z0-9\s\-_]+$/.test(value)) {
        fieldValidation.name = { 
          valid: false, 
          message: 'Invalid characters in name', 
          type: 'error' 
        }
      } else {
        fieldValidation.name = { 
          valid: true, 
          message: 'Valid collaboration name', 
          type: 'success' 
        }
      }
      break

    case 'channel':
      if (!value || value.trim().length < 2) {
        fieldValidation.channel = { 
          valid: false, 
          message: 'Channel must be at least 2 characters', 
          type: 'error' 
        }
      } else if (value.length > 30) {
        fieldValidation.channel = { 
          valid: false, 
          message: 'Channel name too long', 
          type: 'error' 
        }
      } else {
        fieldValidation.channel = { 
          valid: true, 
          message: 'Valid channel name', 
          type: 'success' 
        }
      }
      break

    case 'platform':
      if (!value || value.length === 0) {
        fieldValidation.platform = { 
          valid: false, 
          message: 'At least one platform required', 
          type: 'error' 
        }
      } else if (value.length > 3) {
        fieldValidation.platform = { 
          valid: false, 
          message: 'Too many platforms selected', 
          type: 'error' 
        }
      } else {
        fieldValidation.platform = { 
          valid: true, 
          message: `${value.length} platform(s) selected`, 
          type: 'success' 
        }
      }
      break

    case 'collaboratorEmail':
      if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
        fieldValidation.collaboratorEmail = { 
          valid: false, 
          message: 'Invalid email format', 
          type: 'error' 
        }
      } else if (value) {
        fieldValidation.collaboratorEmail = { 
          valid: true, 
          message: 'Valid email address', 
          type: 'success' 
        }
      } else {
        fieldValidation.collaboratorEmail = { 
          valid: true, 
          message: 'Optional field', 
          type: 'info' 
        }
      }
      break

    case 'price':
      if (context.type !== 'Product') {
        if (value === undefined || value === null || value < 0) {
          fieldValidation.price = { 
            valid: false, 
            message: 'Price must be positive', 
            type: 'error' 
          }
        } else if (value > 9999999) {
          fieldValidation.price = { 
            valid: false, 
            message: 'Price too high', 
            type: 'error' 
          }
        } else {
          fieldValidation.price = { 
            valid: true, 
            message: `Price: $${value.toFixed(2)}`, 
            type: 'success' 
          }
        }
      } else {
        fieldValidation.price = { 
          valid: true, 
          message: 'Free product collaboration', 
          type: 'info' 
        }
      }
      break

    case 'numVideos':
      if (!value || value < 1 || value > 50) {
        fieldValidation.numVideos = { 
          valid: false, 
          message: 'Must be between 1 and 50', 
          type: 'error' 
        }
      } else if (value > 10) {
        fieldValidation.numVideos = { 
          valid: true, 
          message: `${value} videos (large collaboration)`, 
          type: 'warning' 
        }
      } else {
        fieldValidation.numVideos = { 
          valid: true, 
          message: `${value} video(s) planned`, 
          type: 'success' 
        }
      }
      break
  }
}
```

---

## 🎥 Video Management System

### Dynamic Video Section Generation

```javascript
const generateVideoSections = (numVideos, platforms) => {
  const videos = []
  
  for (let i = 0; i < numVideos; i++) {
    const videoSection = {
      // Basic Info
      id: `video-${i + 1}`,
      index: i,
      number: i + 1,
      
      // Content Fields with Enhanced Features
      script: {
        value: '',
        required: false,
        maxLength: 5000,
        expandable: true,
        collapsible: true,
        autoSave: true,
        autoSaveDelay: 1000,
        wordCount: 0,
        characterCount: 0,
        features: {
          wordCount: true,
          characterCount: true,
          lineNumbers: false,
          syntaxHighlighting: false,
          findReplace: true,
          undoRedo: true,
          fullscreen: true
        },
        ui: {
          placeholder: 'Enter video script content here...',
          minHeight: '100px',
          maxHeight: '500px',
          resize: 'vertical'
        }
      },
      
      title: {
        value: '',
        required: false,
        maxLength: 100,
        autoSave: true,
        autoSaveDelay: 500,
        characterCount: 0,
        features: {
          characterCount: true,
          suggestions: true,
          titleCase: true
        },
        ui: {
          placeholder: 'Enter video title...',
          maxLength: 100
        }
      },
      
      subtitles: {
        value: '',
        required: false,
        maxLength: 2000,
        expandable: true,
        collapsible: true,
        autoSave: true,
        autoSaveDelay: 1000,
        wordCount: 0,
        characterCount: 0,
        features: {
          wordCount: true,
          characterCount: true,
          timestampFormat: true,
          lineNumbers: true
        },
        ui: {
          placeholder: 'Enter subtitle text with timestamps (e.g., 00:00:01 - Hello world)...',
          minHeight: '80px',
          maxHeight: '300px'
        }
      },
      
      caption: {
        value: '',
        required: false,
        maxLength: 3000,
        expandable: true,
        collapsible: true,
        autoSave: true,
        autoSaveDelay: 1000,
        wordCount: 0,
        characterCount: 0,
        features: {
          wordCount: true,
          characterCount: true,
          hashtagHighlight: true,
          mentionHighlight: true,
          emojiSupport: true,
          linkPreview: true
        },
        ui: {
          placeholder: 'Enter social media caption with hashtags and mentions...',
          minHeight: '100px',
          maxHeight: '400px'
        }
      },
      
      hashtags: {
        value: '',
        required: false,
        maxLength: 1000,
        expandable: true,
        collapsible: true,
        autoSave: true,
        autoSaveDelay: 1000,
        hashtagCount: 0,
        features: {
          hashtagCount: true,
          hashtagSuggestions: true,
          trendingHashtags: true,
          hashtagValidation: true
        },
        validation: {
          pattern: /^(\s*#[a-zA-Z0-9_]+\s*)*$/,
          errorMessage: 'Hashtags must start with # and contain only letters, numbers, and underscores'
        },
        ui: {
          placeholder: '#hashtag1 #hashtag2 #hashtag3...',
          minHeight: '60px',
          maxHeight: '200px'
        }
      },
      
      // Media Management
      draftFile: null,
      draftLink: '',
      thumbnail: null,
      
      // Status Fields
      invitation: false,
      postLinks: generatePostLinkStructure(platforms),
      paid: false,
      done: false,
      
      // Metadata Tracking
      metadata: {
        duration: null,
        format: null,
        size: null,
        resolution: null,
        frameRate: null,
        uploadedAt: null,
        completedAt: null,
        lastModified: null,
        processingStatus: 'pending' // pending, processing, completed, failed
      },
      
      // UI State Management
      uiState: {
        scriptExpanded: false,
        subtitlesExpanded: false,
        captionExpanded: false,
        hashtagsExpanded: false,
        isUploading: false,
        uploadProgress: 0,
        showThumbnail: false,
        showVideoPreview: false,
        isProcessing: false,
        lastSaved: null,
        hasUnsavedChanges: false
      }
    }
    
    videos.push(videoSection)
  }
  
  return videos
}

const generatePostLinkStructure = (platforms) => {
  const postLinks = {}
  platforms.forEach(platform => {
    postLinks[platform] = {
      value: '',
      required: false,
      validation: {
        pattern: /^https?:\/\/.+\..+/,
        errorMessage: 'Please enter a valid URL'
      },
      features: {
        urlValidation: true,
        linkPreview: true,
        autoFormat: true
      },
      ui: {
        placeholder: `https://${platform.toLowerCase()}.com/...`,
        icon: getPlatformIcon(platform),
        color: getPlatformColor(platform)
      }
    }
  })
  return postLinks
}
```

### Video Section Update Logic

```javascript
const updateVideoSections = async () => {
  const currentCount = collaborationForm.videos.length
  const newCount = collaborationForm.numVideos
  
  if (newCount > currentCount) {
    // Add new video sections
    const newSections = []
    for (let i = currentCount; i < newCount; i++) {
      const newSection = generateSingleVideoSection(i, collaborationForm.platform)
      newSections.push(newSection)
    }
    
    // Add sections to form
    collaborationForm.videos.push(...newSections)
    
    // Show notification
    showSuccess(`Added ${newCount - currentCount} new video section(s)`)
    
    // Auto-expand first new section
    if (newSections.length > 0) {
      newSections[0].uiState.scriptExpanded = true
    }
    
  } else if (newCount < currentCount) {
    // Remove excess video sections with confirmation
    const sectionsToRemove = currentCount - newCount
    const hasContentInRemovableSections = collaborationForm.videos
      .slice(newCount)
      .some(video => hasContent(video))
    
    let confirmed = true
    
    if (hasContentInRemovableSections) {
      confirmed = await showConfirm(
        `Reducing video count from ${currentCount} to ${newCount} will delete data from ${sectionsToRemove} video section(s). ` +
        `${sectionsToRemove} section(s) contain content. Continue?`,
        'Confirm Video Count Change',
        {
          type: 'warning',
          confirmText: 'Yes, delete sections',
          cancelText: 'Cancel'
        }
      )
    }
    
    if (confirmed) {
      // Store removed sections for potential undo
      const removedSections = collaborationForm.videos.slice(newCount)
      
      // Remove sections
      collaborationForm.videos.splice(newCount)
      
      // Show notification with undo option
      showWarning(
        `Removed ${sectionsToRemove} video section(s)`,
        {
          action: 'undo',
          label: 'Undo',
          callback: () => undoVideoSectionRemoval(removedSections)
        }
      )
    } else {
      // Revert the number
      collaborationForm.numVideos = currentCount
    }
  }
}

const hasContent = (video) => {
  return video.script.value ||
         video.title.value ||
         video.subtitles.value ||
         video.caption.value ||
         video.hashtags.value ||
         video.draftFile ||
         video.draftLink ||
         video.invitation ||
         Object.values(video.postLinks).some(link => link.value)
}

const undoVideoSectionRemoval = (removedSections) => {
  collaborationForm.videos.push(...removedSections)
  collaborationForm.numVideos = collaborationForm.videos.length
  showSuccess('Video sections restored')
}
```

---

## 💾 Drive Integration

### Storage Path Configuration

```javascript
const storageConfig = {
  basePath: '/home/haku/storage/DHQ_Root',
  userPath: (userId) => `${storageConfig.basePath}/${userId}`,
  collaborationPath: (userId, collaborationName) => {
    const safeName = collaborationName
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, '-')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '')
    
    return `${storageConfig.userPath(userId)}/collaborations/${safeName}`
  },
  videoPath: (userId, collaborationName, videoIndex, fileName) => {
    const collabPath = storageConfig.collaborationPath(userId, collaborationName)
    return `${collabPath}/video_${videoIndex + 1}_${fileName}`
  },
  thumbnailPath: (userId, collaborationName, videoIndex) => {
    const collabPath = storageConfig.collaborationPath(userId, collaborationName)
    return `${collabPath}/video_${videoIndex + 1}_thumbnail.jpg`
  }
}
```

### Video Upload Workflow with Quota Management

```javascript
const handleVideoUpload = async (event, videoIndex) => {
  try {
    const file = event.target.files[0]
    if (!file) return
    
    // Step 1: File Type Validation
    const allowedTypes = [
      'video/mp4',
      'video/mov',
      'video/avi',
      'video/webm',
      'video/mkv',
      'video/flv',
      'video/wmv'
    ]
    
    if (!allowedTypes.includes(file.type)) {
      showError(
        'Invalid file type. Please upload MP4, MOV, AVI, WebM, MKV, FLV, or WMV files.',
        { duration: 5000 }
      )
      return
    }
    
    // Step 2: File Size Validation
    const maxSize = 2 * 1024 * 1024 * 1024 // 2GB
    if (file.size > maxSize) {
      showError(
        `File size (${formatFileSize(file.size)}) exceeds 2GB limit.`,
        { duration: 5000 }
      )
      return
    }
    
    // Step 3: Quota Checking
    const quotaCheck = checkQuota(file.size)
    if (!quotaCheck.hasEnough) {
      const quotaExceeded = quotaCheck.excess
      const options = [
        {
          label: 'Delete Files',
          action: () => openFileManager(),
          style: 'primary'
        },
        {
          label: 'Contact Operator',
          action: () => requestQuotaIncrease(quotaExceeded),
          style: 'secondary'
        }
      ]
      
      showError(
        `Insufficient quota. You need ${formatFileSize(quotaExceeded)} more storage.`,
        { options, duration: 10000 }
      )
      return
    }
    
    // Step 4: Generate Storage Path
    const collaborationName = collaborationForm.name
    const storagePath = storageConfig.videoPath(
      userId,
      collaborationName,
      videoIndex,
      file.name
    )
    
    // Step 5: Show Upload Progress
    collaborationForm.videos[videoIndex].uiState.isUploading = true
    collaborationForm.videos[videoIndex].uiState.uploadProgress = 0
    
    // Step 6: Create Directory Structure
    await createDirectoryStructure(storagePath)
    
    // Step 7: Upload File with Progress Tracking
    const uploadResult = await uploadFileWithProgress(file, storagePath, (progress) => {
      collaborationForm.videos[videoIndex].uiState.uploadProgress = progress
    })
    
    // Step 8: Process Video (Generate Thumbnail, Extract Metadata)
    collaborationForm.videos[videoIndex].uiState.isProcessing = true
    
    const [thumbnailPath, metadata] = await Promise.all([
      generateThumbnail(uploadResult.filePath),
      extractVideoMetadata(uploadResult.filePath)
    ])
    
    // Step 9: Update Video Data
    collaborationForm.videos[videoIndex] = {
      ...collaborationForm.videos[videoIndex],
      draftFile: file,
      draftLink: uploadResult.fileUrl,
      thumbnail: thumbnailPath,
      metadata: {
        duration: metadata.duration,
        format: metadata.format,
        size: file.size,
        resolution: metadata.resolution,
        frameRate: metadata.frameRate,
        uploadedAt: new Date().toISOString(),
        lastModified: new Date().toISOString(),
        processingStatus: 'completed'
      },
      uiState: {
        ...collaborationForm.videos[videoIndex].uiState,
        isUploading: false,
        isProcessing: false,
        uploadProgress: 100,
        lastSaved: new Date().toISOString(),
        hasUnsavedChanges: false
      }
    }
    
    // Step 10: Update Quota
    updateQuota(file.size, true)
    
    // Step 11: Show Success Message
    showSuccess(
      `Video uploaded successfully! Storage used: ${formatFileSize(file.size)}`,
      { duration: 3000 }
    )
    
    // Step 12: Log Activity
    logActivity('video_uploaded', {
      collaborationId: collaborationModal.currentCollab?.id,
      videoIndex: videoIndex,
      fileName: file.name,
      fileSize: file.size,
      filePath: storagePath,
      duration: metadata.duration
    })
    
    // Step 13: Auto-save collaboration
    await autoSaveCollaboration()
    
  } catch (error) {
    console.error('Video upload failed:', error)
    
    // Reset UI state
    collaborationForm.videos[videoIndex].uiState.isUploading = false
    collaborationForm.videos[videoIndex].uiState.isProcessing = false
    collaborationForm.videos[videoIndex].uiState.uploadProgress = 0
    
    // Show error message
    showError(
      'Video upload failed. Please check your internet connection and try again.',
      { duration: 5000 }
    )
  }
}

const createDirectoryStructure = async (filePath) => {
  const pathParts = filePath.split('/')
  pathParts.pop() // Remove filename
  
  let currentPath = ''
  for (const part of pathParts) {
    if (!part) continue
    currentPath += '/' + part
    
    try {
      await api.post('/api/drive/create-directory', { path: currentPath })
    } catch (error) {
      // Directory might already exist, continue
      console.log('Directory exists or creation failed:', currentPath)
    }
  }
}

const uploadFileWithProgress = async (file, path, onProgress) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('path', path)
  
  const response = await api.post('/api/drive/upload', formData, {
    onUploadProgress: (progressEvent) => {
      if (progressEvent.lengthComputable) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        onProgress(progress)
      }
    },
    timeout: 300000 // 5 minutes timeout
  })
  
  return response.data
}
```

### Video Link Management

```javascript
const handleVideoLink = async (videoIndex, link) => {
  try {
    if (!link) {
      // Clear existing link
      await clearVideoLink(videoIndex)
      return
    }
    
    // Step 1: URL Validation
    const urlPattern = /^https?:\/\/.+\..+/
    if (!urlPattern.test(link)) {
      showError(
        'Please enter a valid URL (http:// or https://)',
        { duration: 3000 }
      )
      return
    }
    
    // Step 2: URL Accessibility Check
    collaborationForm.videos[videoIndex].uiState.isProcessing = true
    
    const accessibilityCheck = await checkUrlAccessibility(link)
    if (!accessibilityCheck.accessible) {
      showError(
        'URL is not accessible. Please check the URL and try again.',
        { duration: 5000 }
      )
      collaborationForm.videos[videoIndex].uiState.isProcessing = false
      return
    }
    
    // Step 3: Video Validation
    const videoValidation = await validateVideoUrl(link)
    if (!videoValidation.isValidVideo) {
      showError(
        'URL does not point to a valid video file.',
        { duration: 5000 }
      )
      collaborationForm.videos[videoIndex].uiState.isProcessing = false
      return
    }
    
    // Step 4: Get Video Metadata
    const metadata = await getVideoMetadataFromUrl(link)
    
    // Step 5: Generate Thumbnail from URL
    const thumbnailPath = await generateThumbnailFromUrl(link)
    
    // Step 6: Update Video Data
    collaborationForm.videos[videoIndex] = {
      ...collaborationForm.videos[videoIndex],
      draftLink: link,
      draftFile: null,
      thumbnail: thumbnailPath,
      metadata: {
        ...metadata,
        uploadedAt: new Date().toISOString(),
        lastModified: new Date().toISOString(),
        processingStatus: 'completed'
      },
      uiState: {
        ...collaborationForm.videos[videoIndex].uiState,
        isProcessing: false,
        lastSaved: new Date().toISOString(),
        hasUnsavedChanges: false
      }
    }
    
    // Step 7: Show Success Message
    showSuccess(
      'Video link added successfully!',
      { duration: 3000 }
    )
    
    // Step 8: Log Activity
    logActivity('video_link_added', {
      collaborationId: collaborationModal.currentCollab?.id,
      videoIndex: videoIndex,
      link: link,
      duration: metadata.duration
    })
    
    // Step 9: Auto-save collaboration
    await autoSaveCollaboration()
    
  } catch (error) {
    console.error('Video link validation failed:', error)
    
    collaborationForm.videos[videoIndex].uiState.isProcessing = false
    
    showError(
      'Invalid video link. Please check the URL and try again.',
      { duration: 5000 }
    )
  }
}

const clearVideoLink = async (videoIndex) => {
  collaborationForm.videos[videoIndex] = {
    ...collaborationForm.videos[videoIndex],
    draftLink: '',
    draftFile: null,
    thumbnail: null,
    metadata: {
      ...collaborationForm.videos[videoIndex].metadata,
      duration: null,
      format: null,
      size: null,
      uploadedAt: null,
      processingStatus: 'pending'
    }
  }
  
  showSuccess('Video link cleared')
  await autoSaveCollaboration()
}
```

### Video Management Functions

```javascript
const viewVideo = (videoIndex) => {
  const video = collaborationForm.videos[videoIndex]
  let videoUrl = ''
  
  if (video.draftFile) {
    // Local file preview
    videoUrl = URL.createObjectURL(video.draftFile)
  } else if (video.draftLink) {
    // External URL
    videoUrl = video.draftLink
  }
  
  if (videoUrl) {
    // Open video in modal
    videoModal.videoUrl = videoUrl
    videoModal.videoIndex = videoIndex
    videoModal.videoTitle = `Video ${videoIndex + 1}: ${video.title.value || 'Untitled'}`
    videoModal.visible = true
    
    // Log view activity
    logActivity('video_viewed', {
      collaborationId: collaborationModal.currentCollab?.id,
      videoIndex: videoIndex,
      source: video.draftFile ? 'local' : 'external'
    })
  } else {
    showError('No video available to view')
  }
}

const replaceVideo = (videoIndex) => {
  // Show confirmation dialog
  showConfirm(
    'This will replace the current video. The existing video will be removed. Continue?',
    'Replace Video',
    {
      type: 'warning',
      confirmText: 'Replace Video',
      cancelText: 'Cancel'
    }
  ).then(confirmed => {
    if (confirmed) {
      // Clear existing video data
      collaborationForm.videos[videoIndex] = {
        ...collaborationForm.videos[videoIndex],
        draftFile: null,
        draftLink: '',
        thumbnail: null,
        metadata: {
          ...collaborationForm.videos[videoIndex].metadata,
          duration: null,
          format: null,
          size: null,
          uploadedAt: null,
          processingStatus: 'pending'
        }
      }
      
      // Trigger file selection
      const input = document.querySelector(`#videoInput-${videoIndex}`)
      if (input) {
        input.click()
      }
      
      showSuccess('Ready to upload new video')
    }
  })
}

const showThumbnail = async (videoIndex) => {
  const video = collaborationForm.videos[videoIndex]
  
  if (!video.thumbnail) {
    // Generate thumbnail if it doesn't exist
    if (video.draftFile || video.draftLink) {
      collaborationForm.videos[videoIndex].uiState.isProcessing = true
      
      try {
        const videoSource = video.draftFile ? video.draftFile : video.draftLink
        const thumbnailPath = await generateThumbnail(videoSource)
        
        collaborationForm.videos[videoIndex].thumbnail = thumbnailPath
        collaborationForm.videos[videoIndex].uiState.isProcessing = false
        
        // Now show the thumbnail
        openThumbnailModal(videoIndex)
      } catch (error) {
        collaborationForm.videos[videoIndex].uiState.isProcessing = false
        showError('Failed to generate thumbnail')
      }
    } else {
      showError('No video available to generate thumbnail')
    }
  } else {
    // Show existing thumbnail
    openThumbnailModal(videoIndex)
  }
}

const openThumbnailModal = (videoIndex) => {
  const video = collaborationForm.videos[videoIndex]
  
  thumbnailModal.thumbnailUrl = video.thumbnail
  thumbnailModal.videoIndex = videoIndex
  thumbnailModal.videoTitle = `Video ${videoIndex + 1} Thumbnail`
  thumbnailModal.visible = true
  
  // Log thumbnail view activity
  logActivity('thumbnail_viewed', {
    collaborationId: collaborationModal.currentCollab?.id,
    videoIndex: videoIndex
  })
}
```

---

## 📊 Status Management

### Halt Collaboration Workflow

```javascript
const haltCollaboration = async () => {
  try {
    // Step 1: Get Halt Reason
    const reason = await promptWithValidation(
      'Please provide a reason for halting this collaboration:',
      'Halt Collaboration',
      {
        placeholder: 'Enter detailed reason (minimum 5 characters)...',
        minLength: 5,
        maxLength: 500,
        required: true,
        validation: (value) => {
          if (!value || value.trim().length < 5) {
            return 'Reason must be at least 5 characters long'
          }
          return null
        }
      }
    )
    
    if (!reason) return
    
    // Step 2: Show Confirmation Dialog
    const confirmed = await showConfirm(
      `Are you sure you want to halt this collaboration?\n\nCollaboration: ${collaborationModal.currentCollab.name}\nReason: ${reason}\n\nThis will pause all ongoing work and notify the collaborator.`,
      'Halt Collaboration',
      {
        type: 'warning',
        confirmText: 'Halt Collaboration',
        cancelText: 'Cancel',
        details: {
          icon: 'fas fa-pause-circle',
          color: '#f59e0b'
        }
      }
    )
    
    if (!confirmed) return
    
    // Step 3: Update Collaboration Status
    const collaborationId = collaborationModal.currentCollab.id
    const haltData = {
      status: 'Halted',
      haltReason: reason.trim(),
      haltedAt: new Date().toISOString(),
      haltedBy: userId,
      previousStatus: collaborationModal.currentCollab.status
    }
    
    const response = await api.patch(`/api/collaborations/${collaborationId}`, haltData)
    
    // Step 4: Update Local State
    const index = collaborations.value.findIndex(c => c.id === collaborationId)
    if (index > -1) {
      collaborations.value[index] = {
        ...collaborations.value[index],
        ...haltData
      }
    }
    
    // Step 5: Update Modal State
    collaborationModal.currentCollab.status = 'Halted'
    collaborationModal.currentCollab.haltReason = reason.trim()
    collaborationModal.currentCollab.haltedAt = haltData.haltedAt
    
    // Step 6: Notify Collaborator
    if (collaborationModal.currentCollab.collaboratorEmail) {
      await sendCollaborationNotification({
        type: 'halted',
        collaborationId: collaborationId,
        recipientEmail: collaborationModal.currentCollab.collaboratorEmail,
        data: {
          collaborationName: collaborationModal.currentCollab.name,
          reason: reason.trim(),
          haltedAt: haltData.haltedAt,
          collaborationLink: collaborationModal.currentCollab.collaborationLink
        }
      })
    }
    
    // Step 7: Show Success Message
    showSuccess(
      `Collaboration "${collaborationModal.currentCollab.name}" halted successfully`,
      { duration: 3000 }
    )
    
    // Step 8: Log Activity
    logActivity('collaboration_halted', {
      collaborationId: collaborationId,
      reason: reason.trim(),
      previousStatus: haltData.previousStatus
    })
    
    // Step 9: Close Modal
    closeCollaborationModal()
    
  } catch (error) {
    console.error('Failed to halt collaboration:', error)
    showError(
      'Failed to halt collaboration. Please try again.',
      { duration: 5000 }
    )
  }
}
```

### Decline Collaboration Workflow

```javascript
const declineCollaboration = async () => {
  try {
    // Step 1: Get Decline Reason
    const reason = await promptWithValidation(
      'Please provide a reason for declining this collaboration:',
      'Decline Collaboration',
      {
        placeholder: 'Enter detailed reason (minimum 5 characters)...',
        minLength: 5,
        maxLength: 500,
        required: true,
        validation: (value) => {
          if (!value || value.trim().length < 5) {
            return 'Reason must be at least 5 characters long'
          }
          return null
        },
        suggestions: [
          'Budget constraints',
          'Timeline conflicts',
          'Brand misalignment',
          'Creative differences',
          'Resource limitations'
        ]
      }
    )
    
    if (!reason) return
    
    // Step 2: Show Confirmation Dialog
    const confirmed = await showConfirm(
      `Are you sure you want to decline this collaboration?\n\nCollaboration: ${collaborationModal.currentCollab.name}\nReason: ${reason}\n\nThis will permanently decline the collaboration and notify the collaborator.`,
      'Decline Collaboration',
      {
        type: 'error',
        confirmText: 'Decline Collaboration',
        cancelText: 'Cancel',
        details: {
          icon: 'fas fa-times-circle',
          color: '#ef4444'
        }
      }
    )
    
    if (!confirmed) return
    
    // Step 3: Update Collaboration Status
    const collaborationId = collaborationModal.currentCollab.id
    const declineData = {
      status: 'Declined',
      declineReason: reason.trim(),
      declinedAt: new Date().toISOString(),
      declinedBy: userId,
      previousStatus: collaborationModal.currentCollab.status
    }
    
    const response = await api.patch(`/api/collaborations/${collaborationId}`, declineData)
    
    // Step 4: Update Local State
    const index = collaborations.value.findIndex(c => c.id === collaborationId)
    if (index > -1) {
      collaborations.value[index] = {
        ...collaborations.value[index],
        ...declineData
      }
    }
    
    // Step 5: Update Modal State
    collaborationModal.currentCollab.status = 'Declined'
    collaborationModal.currentCollab.declineReason = reason.trim()
    collaborationModal.currentCollab.declinedAt = declineData.declinedAt
    
    // Step 6: Notify Collaborator
    if (collaborationModal.currentCollab.collaboratorEmail) {
      await sendCollaborationNotification({
        type: 'declined',
        collaborationId: collaborationId,
        recipientEmail: collaborationModal.currentCollab.collaboratorEmail,
        data: {
          collaborationName: collaborationModal.currentCollab.name,
          reason: reason.trim(),
          declinedAt: declineData.declinedAt,
          collaborationLink: collaborationModal.currentCollab.collaborationLink
        }
      })
    }
    
    // Step 7: Show Success Message
    showSuccess(
      `Collaboration "${collaborationModal.currentCollab.name}" declined successfully`,
      { duration: 3000 }
    )
    
    // Step 8: Log Activity
    logActivity('collaboration_declined', {
      collaborationId: collaborationId,
      reason: reason.trim(),
      previousStatus: declineData.previousStatus
    })
    
    // Step 9: Close Modal
    closeCollaborationModal()
    
  } catch (error) {
    console.error('Failed to decline collaboration:', error)
    showError(
      'Failed to decline collaboration. Please try again.',
      { duration: 5000 }
    )
  }
}
```

### Mark Video Done Workflow

```javascript
const markVideoDone = async (videoIndex) => {
  try {
    const video = collaborationForm.videos[videoIndex]
    
    // Step 1: Validate Video Completion Requirements
    const completionValidation = validateVideoCompletion(video, collaborationForm.platform)
    
    if (!completionValidation.isValid) {
      const missingFields = completionValidation.missingFields.map(field => field.label).join(', ')
      showError(
        `Cannot mark video as done. Missing required fields: ${missingFields}`,
        { duration: 5000 }
      )
      
      // Highlight missing fields
      completionValidation.missingFields.forEach(field => {
        field.uiState.highlighted = true
        setTimeout(() => {
          field.uiState.highlighted = false
        }, 3000)
      })
      
      return
    }
    
    // Step 2: Show Warnings if Any
    if (completionValidation.warnings.length > 0) {
      const continueAnyway = await showConfirm(
        `Warnings:\n${completionValidation.warnings.join('\n')}\n\nContinue marking video as done?`,
        'Video Completion Warnings',
        {
          type: 'warning',
          confirmText: 'Mark Done Anyway',
          cancelText: 'Cancel'
        }
      )
      
      if (!continueAnyway) return
    }
    
    // Step 3: Show Final Confirmation
    const confirmed = await showConfirm(
      `Are you sure this video is complete and ready to be marked as done?\n\nVideo: ${videoIndex + 1}\nTitle: ${video.title.value || 'Untitled'}\n\nOnce marked as done, you cannot edit the video content.`,
      'Mark Video Done',
      {
        type: 'success',
        confirmText: 'Mark Done',
        cancelText: 'Cancel',
        details: {
          icon: 'fas fa-check-circle',
          color: '#10b981'
        }
      }
    )
    
    if (!confirmed) return
    
    // Step 4: Update Video Status
    collaborationForm.videos[videoIndex] = {
      ...collaborationForm.videos[videoIndex],
      done: true,
      completedAt: new Date().toISOString(),
      metadata: {
        ...collaborationForm.videos[videoIndex].metadata,
        completedAt: new Date().toISOString()
      }
    }
    
    // Step 5: Update Collaboration Completion Status
    const completedVideos = collaborationForm.videos.filter(v => v.done).length
    const totalVideos = collaborationForm.videos.length
    
    if (completedVideos === totalVideos) {
      // All videos completed, mark collaboration as done
      await markCollaborationFullyDone()
    } else {
      // Partial completion
      await updateCollaborationProgress()
    }
    
    // Step 6: Show Success Message
    showSuccess(
      `Video ${videoIndex + 1} marked as done! (${completedVideos}/${totalVideos} completed)`,
      { duration: 3000 }
    )
    
    // Step 7: Log Activity
    logActivity('video_completed', {
      collaborationId: collaborationModal.currentCollab?.id,
      videoIndex: videoIndex,
      videoTitle: video.title.value,
      completionProgress: `${completedVideos}/${totalVideos}`
    })
    
    // Step 8: Auto-save collaboration
    await autoSaveCollaboration()
    
  } catch (error) {
    console.error('Failed to mark video as done:', error)
    showError(
      'Failed to mark video as done. Please try again.',
      { duration: 5000 }
    )
  }
}

const validateVideoCompletion = (video, platforms) => {
  const missingFields = []
  const warnings = []
  
  // Check required content fields
  if (!video.script.value || video.script.value.trim().length < 10) {
    missingFields.push({
      field: 'script',
      label: 'Script',
      current: video.script.value.length,
      required: 10
    })
  }
  
  if (!video.title.value || video.title.value.trim().length < 3) {
    missingFields.push({
      field: 'title',
      label: 'Title',
      current: video.title.value.length,
      required: 3
    })
  }
  
  if (!video.caption.value || video.caption.value.trim().length < 10) {
    missingFields.push({
      field: 'caption',
      label: 'Caption',
      current: video.caption.value.length,
      required: 10
    })
  }
  
  // Check video media
  if (!video.draftFile && !video.draftLink) {
    missingFields.push({
      field: 'video',
      label: 'Video Draft',
      current: 'none',
      required: 'file or link'
    })
  }
  
  // Check post links for all platforms
  const missingPostLinks = []
  platforms.forEach(platform => {
    if (!video.postLinks[platform] || !video.postLinks[platform].value) {
      missingPostLinks.push(platform)
    }
  })
  
  if (missingPostLinks.length > 0) {
    missingFields.push({
      field: 'postLinks',
      label: 'Post Links',
      current: missingPostLinks.join(', '),
      required: platforms.join(', ')
    })
  }
  
  // Check for warnings
  if (video.hashtags.value.length === 0) {
    warnings.push('No hashtags provided - may reduce visibility')
  }
  
  if (!video.invitation && video.paid) {
    warnings.push('Paid collaboration without invitation checkbox')
  }
  
  return {
    isValid: missingFields.length === 0,
    missingFields: missingFields,
    warnings: warnings
  }
}

const markCollaborationFullyDone = async () => {
  try {
    const collaborationId = collaborationModal.currentCollab.id
    
    const doneData = {
      status: 'Done',
      completedAt: new Date().toISOString(),
      completedBy: userId,
      completedVideos: collaborationForm.videos.length,
      totalVideos: collaborationForm.videos.length
    }
    
    const response = await api.patch(`/api/collaborations/${collaborationId}`, doneData)
    
    // Update local state
    const index = collaborations.value.findIndex(c => c.id === collaborationId)
    if (index > -1) {
      collaborations.value[index] = {
        ...collaborations.value[index],
        ...doneData
      }
    }
    
    // Update modal state
    collaborationModal.currentCollab.status = 'Done'
    collaborationModal.currentCollab.completedAt = doneData.completedAt
    
    // Notify collaborator
    if (collaborationModal.currentCollab.collaboratorEmail) {
      await sendCollaborationNotification({
        type: 'completed',
        collaborationId: collaborationId,
        recipientEmail: collaborationModal.currentCollab.collaboratorEmail,
        data: {
          collaborationName: collaborationModal.currentCollab.name,
          completedAt: doneData.completedAt,
          totalVideos: doneData.totalVideos,
          collaborationLink: collaborationModal.currentCollab.collaborationLink
        }
      })
    }
    
    showSuccess(
      `🎉 Collaboration "${collaborationModal.currentCollab.name}" marked as fully completed!`,
      { duration: 5000 }
    )
    
    logActivity('collaboration_completed', {
      collaborationId: collaborationId,
      totalVideos: doneData.totalVideos
    })
    
  } catch (error) {
    console.error('Failed to mark collaboration as done:', error)
    showError(
      'Failed to mark collaboration as done. Please try again.',
      { duration: 5000 }
    )
  }
}
```

---

## 🔌 API Endpoints

### Collaboration Management Endpoints

```javascript
const collaborationAPI = {
  // Basic CRUD Operations
  createCollaboration: {
    method: 'POST',
    url: '/api/collaborations',
    description: 'Create a new collaboration',
    request: {
      name: String,
      channel: String,
      platform: Array<String>,
      collaboratorEmail: String,
      type: String,
      price: Number,
      numVideos: Number
    },
    response: {
      id: String,
      collaborationLink: String,
      status: String,
      createdAt: String
    }
  },
  
  getCollaborations: {
    method: 'GET',
    url: '/api/collaborations',
    description: 'Get all collaborations for current user',
    query: {
      status: String,
      page: Number,
      limit: Number,
      sortBy: String,
      sortOrder: String
    },
    response: {
      collaborations: Array,
      total: Number,
      page: Number,
      totalPages: Number
    }
  },
  
  getCollaboration: {
    method: 'GET',
    url: '/api/collaborations/:id',
    description: 'Get a specific collaboration by ID',
    response: {
      collaboration: Object
    }
  },
  
  updateCollaboration: {
    method: 'PATCH',
    url: '/api/collaborations/:id',
    description: 'Update collaboration details',
    request: {
      name: String,
      channel: String,
      platform: Array<String>,
      collaboratorEmail: String,
      type: String,
      price: Number,
      numVideos: Number,
      videos: Array
    },
    response: {
      collaboration: Object
    }
  },
  
  deleteCollaboration: {
    method: 'DELETE',
    url: '/api/collaborations/:id',
    description: 'Delete a collaboration',
    response: {
      success: Boolean,
      message: String
    }
  },
  
  // Status Management
  haltCollaboration: {
    method: 'PATCH',
    url: '/api/collaborations/:id/halt',
    description: 'Halt a collaboration',
    request: {
      reason: String
    },
    response: {
      collaboration: Object
    }
  },
  
  declineCollaboration: {
    method: 'PATCH',
    url: '/api/collaborations/:id/decline',
    description: 'Decline a collaboration',
    request: {
      reason: String
    },
    response: {
      collaboration: Object
    }
  },
  
  markCollaborationDone: {
    method: 'PATCH',
    url: '/api/collaborations/:id/done',
    description: 'Mark collaboration as completed',
    response: {
      collaboration: Object
    }
  },
  
  // Video Management
  uploadVideo: {
    method: 'POST',
    url: '/api/collaborations/:id/videos/:index/upload',
    description: 'Upload video for a collaboration',
    request: {
      file: File,
      videoIndex: Number
    },
    response: {
      fileUrl: String,
      filePath: String,
      thumbnail: String,
      metadata: Object
    }
  },
  
  updateVideo: {
    method: 'PATCH',
    url: '/api/collaborations/:id/videos/:index',
    description: 'Update video details',
    request: {
      script: String,
      title: String,
      subtitles: String,
      caption: String,
      hashtags: String,
      invitation: Boolean,
      postLinks: Object,
      paid: Boolean,
      done: Boolean
    },
    response: {
      video: Object
    }
  },
  
  deleteVideo: {
    method: 'DELETE',
    url: '/api/collaborations/:id/videos/:index',
    description: 'Delete a video from collaboration',
    response: {
      success: Boolean,
      message: String
    }
  },
  
  // Utility Endpoints
  generateThumbnail: {
    method: 'POST',
    url: '/api/collaborations/:id/videos/:index/thumbnail',
    description: 'Generate thumbnail for video',
    request: {
      videoPath: String
    },
    response: {
      thumbnailUrl: String,
      thumbnailPath: String
    }
  },
  
  extractMetadata: {
    method: 'GET',
    url: '/api/collaborations/:id/videos/:index/metadata',
    description: 'Extract video metadata',
    response: {
      duration: Number,
      format: String,
      size: Number,
      resolution: String,
      frameRate: Number
    }
  },
  
  // Notifications
  sendNotification: {
    method: 'POST',
    url: '/api/collaborations/:id/notify',
    description: 'Send notification to collaborator',
    request: {
      type: String,
      recipientEmail: String,
      data: Object
    },
    response: {
      success: Boolean,
      messageId: String
    }
  }
}
```

---

## 🚨 Error Handling

### Error Types and Handling Strategies

```javascript
const errorHandling = {
  // Validation Errors
  validationErrors: {
    name: {
      message: 'Invalid collaboration name',
      action: 'highlightField',
      recovery: 'provideNameSuggestions'
    },
    channel: {
      message: 'Invalid channel name',
      action: 'highlightField',
      recovery: 'formatChannelName'
    },
    platform: {
      message: 'Invalid platform selection',
      action: 'highlightField',
      recovery: 'suggestPlatforms'
    },
    price: {
      message: 'Invalid price amount',
      action: 'highlightField',
      recovery: 'formatPrice'
    }
  },
  
  // File Upload Errors
  uploadErrors: {
    fileSize: {
      message: 'File size exceeds limit',
      action: 'showFileSizeWarning',
      recovery: 'suggestCompression'
    },
    fileType: {
      message: 'Unsupported file type',
      action: 'showSupportedFormats',
      recovery: 'suggestConversion'
    },
    quotaExceeded: {
      message: 'Storage quota exceeded',
      action: 'showQuotaManagement',
      recovery: 'suggestCleanup'
    },
    networkError: {
      message: 'Network connection failed',
      action: 'retryUpload',
      recovery: 'checkConnection'
    }
  },
  
  // API Errors
  apiErrors: {
    unauthorized: {
      message: 'Authentication required',
      action: 'redirectToLogin',
      recovery: 'refreshToken'
    },
    forbidden: {
      message: 'Access denied',
      action: 'showPermissionError',
      recovery: 'requestAccess'
    },
    notFound: {
      message: 'Collaboration not found',
      action: 'redirectToCollaborations',
      recovery: 'searchCollaborations'
    },
    serverError: {
      message: 'Server error occurred',
      action: 'retryRequest',
      recovery: 'contactSupport'
    }
  },
  
  // Business Logic Errors
  businessErrors: {
    collaborationLocked: {
      message: 'Collaboration is locked for editing',
      action: 'showLockInfo',
      recovery: 'requestUnlock'
    },
    videoProcessingFailed: {
      message: 'Video processing failed',
      action: 'showProcessingError',
      recovery: 'retryProcessing'
    },
    quotaLimitReached: {
      message: 'Account quota limit reached',
      action: 'showUpgradeOptions',
      recovery: 'requestQuotaIncrease'
    }
  }
}

const handleError = (error, context) => {
  const errorType = determineErrorType(error)
  const errorConfig = errorHandling[errorType]?.[error.code] || errorHandling[errorType]?.default
  
  if (errorConfig) {
    // Show error message
    showError(errorConfig.message, {
      duration: errorConfig.duration || 5000,
      type: errorConfig.type || 'error',
      actions: errorConfig.actions ? [errorConfig.action] : []
    })
    
    // Attempt recovery
    if (errorConfig.recovery) {
      executeRecoveryStrategy(errorConfig.recovery, error, context)
    }
  } else {
    // Default error handling
    showError('An unexpected error occurred. Please try again.', {
      duration: 5000,
      type: 'error'
    })
    
    // Log error for debugging
    console.error('Unhandled error:', error)
  }
}

const executeRecoveryStrategy = (strategy, error, context) => {
  switch (strategy) {
    case 'provideNameSuggestions':
      showNameSuggestions(context)
      break
    case 'formatChannelName':
      autoFormatChannelName(context)
      break
    case 'suggestPlatforms':
      showPlatformSuggestions(context)
      break
    case 'formatPrice':
      autoFormatPrice(context)
      break
    case 'showFileSizeWarning':
      showFileSizeWarning(error.details.fileSize, error.details.maxSize)
      break
    case 'suggestCompression':
      showCompressionOptions(error.details.filePath)
      break
    case 'showSupportedFormats':
      showSupportedFormatsDialog()
      break
    case 'suggestConversion':
      showFileConversionOptions(error.details.filePath)
      break
    case 'showQuotaManagement':
      openQuotaManagementModal()
      break
    case 'suggestCleanup':
      showFileCleanupSuggestions()
      break
    case 'retryUpload':
      retryFileUpload(context.fileIndex, context.filePath)
      break
    case 'checkConnection':
      checkNetworkConnection()
      break
    case 'redirectToLogin':
      router.push('/login')
      break
    case 'refreshToken':
      refreshAuthenticationToken()
      break
    case 'showPermissionError':
      showPermissionDeniedDialog()
      break
    case 'requestAccess':
      sendAccessRequest(context.collaborationId)
      break
    case 'redirectToCollaborations':
      router.push('/collaboration')
      break
    case 'searchCollaborations':
      showCollaborationSearch(context.searchTerm)
      break
    case 'retryRequest':
      retryApiRequest(context.requestConfig)
      break
    case 'contactSupport':
      openSupportChat()
      break
    case 'showLockInfo':
      showCollaborationLockInfo(context.lockInfo)
      break
    case 'requestUnlock':
      sendUnlockRequest(context.collaborationId)
      break
    case 'showProcessingError':
      showVideoProcessingError(error.details)
      break
    case 'retryProcessing':
      retryVideoProcessing(context.videoIndex)
      break
    case 'showUpgradeOptions':
      showAccountUpgradeOptions()
      break
    case 'requestQuotaIncrease':
      openQuotaIncreaseRequest()
      break
    default:
      console.warn('Unknown recovery strategy:', strategy)
  }
}
```

---

## 🎭 User Experience Flow

### Complete User Journey

```javascript
// 1. Initial State - User lands on Collaboration page
const initialState = {
  view: 'list',
  activeFilter: 'On Going',
  selectedCollaboration: null,
  isCreating: false,
  isEditing: false
}

// 2. Create Collaboration Flow
const createCollaborationFlow = [
  {
    step: 'open_modal',
    action: 'click "Create New Collaboration" button',
    ui: {
      modal: 'collaboration-modal',
      backdrop: 'visible',
      focus: 'name-field'
    }
  },
  {
    step: 'fill_basic_info',
    action: 'fill required fields (name, channel, platform, type, price, numVideos)',
    validation: 'real-time validation with visual feedback',
    ui: {
      progress: 'form-progress-bar',
      validation: 'field-level indicators',
      button: 'disabled until valid'
    }
  },
  {
    step: 'start_collaboration',
    action: 'click "Start Collaboration" button',
    processing: 'show loading state',
    success: 'show success message with link',
    navigation: 'redirect to collaboration details'
  },
  {
    step: 'video_sections_generated',
    action: 'dynamic video sections appear based on numVideos',
    ui: {
      sections: 'expandable video cards',
      autoSave: 'enabled',
      progress: 'video completion tracking'
    }
  }
]

// 3. Edit Collaboration Flow
const editCollaborationFlow = [
  {
    step: 'open_collaboration',
    action: 'click collaboration card',
    ui: {
      modal: 'collaboration-modal',
      mode: 'edit',
      data: 'pre-filled from existing collaboration'
    }
  },
  {
    step: 'modify_details',
    action: 'edit any field or video section',
    validation: 'real-time validation',
    autoSave: 'automatic saving with visual indicator'
  },
  {
    step: 'save_changes',
    action: 'click "Save" button or auto-save triggers',
    processing: 'show saving state',
    success: 'show success message',
    error: 'show error with retry option'
  }
]

// 4. Video Management Flow
const videoManagementFlow = [
  {
    step: 'upload_video',
    action: 'click "Upload" button in video section',
    ui: {
      filePicker: 'open file dialog',
      dragDrop: 'enabled',
      validation: 'file type and size check'
    }
  },
  {
    step: 'quota_check',
    action: 'system checks available storage quota',
    success: 'proceed with upload',
    error: 'show quota exceeded message with options'
  },
  {
    step: 'upload_progress',
    action: 'upload file with progress tracking',
    ui: {
      progressBar: 'visible',
      percentage: 'real-time update',
      status: 'uploading'
    }
  },
  {
    step: 'video_processing',
    action: 'generate thumbnail and extract metadata',
    ui: {
      processing: 'show processing indicator',
      thumbnail: 'generate and display'
    }
  },
  {
    step: 'upload_complete',
    action: 'show video preview and management options',
    ui: {
      preview: 'video player',
      actions: 'view, replace, thumbnail buttons',
      metadata: 'display video information'
    }
  }
]

// 5. Status Management Flow
const statusManagementFlow = [
  {
    step: 'halt_collaboration',
    action: 'click "Halt" button',
    ui: {
      dialog: 'reason input modal',
      validation: 'minimum character requirement',
      confirmation: 'final confirmation dialog'
    }
  },
  {
    step: 'decline_collaboration',
    action: 'click "Decline" button',
    ui: {
      dialog: 'reason input modal',
      suggestions: 'pre-defined reasons',
      confirmation: 'final confirmation dialog'
    }
  },
  {
    step: 'mark_video_done',
    action: 'click "Done" checkbox for video',
    validation: 'check completion requirements',
    ui: {
      validation: 'highlight missing fields',
      confirmation: 'final confirmation dialog',
      progress: 'update completion progress'
    }
  },
  {
    step: 'collaboration_completion',
    action: 'all videos marked as done',
    ui: {
      status: 'automatically change to "Done"',
      notification: 'completion celebration',
      summary: 'show completion statistics'
    }
  }
]

// 6. Error Recovery Flow
const errorRecoveryFlow = [
  {
    step: 'error_occurs',
    action: 'system encounters error',
    ui: {
      message: 'show error message',
      type: 'error, warning, or info',
      duration: 'based on severity'
    }
  },
  {
    step: 'analyze_error',
    action: 'system determines error type and recovery options',
    ui: {
      actions: 'show recovery buttons',
      suggestions: 'provide helpful suggestions',
      help: 'link to documentation or support'
    }
  },
  {
    step: 'user_action',
    action: 'user selects recovery option',
    ui: {
      processing: 'show recovery progress',
      success: 'show recovery success',
      failure: 'show alternative options'
    }
  }
]
```

### Micro-interactions and Animations

```javascript
const microInteractions = {
  // Form Field Interactions
  fieldFocus: {
    animation: 'field-glow',
    duration: '200ms',
    easing: 'ease-out'
  },
  fieldValidation: {
    success: 'checkmark-appear',
    error: 'shake-animation',
    duration: '300ms'
  },
  buttonHover: {
    scale: '1.05',
    shadow: 'elevated',
    duration: '150ms'
  },
  buttonClick: {
    scale: '0.95',
    duration: '100ms'
  },
  
  // Video Section Interactions
  sectionExpand: {
    animation: 'slide-down',
    duration: '300ms',
    easing: 'ease-out'
  },
  sectionCollapse: {
    animation: 'slide-up',
    duration: '250ms',
    easing: 'ease-in'
  },
  uploadProgress: {
    animation: 'progress-bar-fill',
    duration: 'based on upload time',
    easing: 'linear'
  },
  
  // Status Changes
  statusChange: {
    animation: 'fade-to-color',
    duration: '500ms',
    easing: 'ease-in-out'
  },
  completionCelebration: {
    animation: 'confetti-burst',
    duration: '2000ms',
    easing: 'ease-out'
  },
  
  // Modal Interactions
  modalOpen: {
    animation: 'scale-fade-in',
    duration: '300ms',
    easing: 'ease-out'
  },
  modalClose: {
    animation: 'scale-fade-out',
    duration: '250ms',
    easing: 'ease-in'
  },
  
  // List Interactions
  cardHover: {
    scale: '1.02',
    shadow: 'elevated',
    duration: '200ms'
  },
  cardClick: {
    scale: '0.98',
    duration: '100ms'
  },
  filterChange: {
    animation: 'slide-fade',
    duration: '400ms',
    easing: 'ease-in-out'
  }
}
```

---

## 📈 Performance Considerations

### Optimization Strategies

```javascript
const performanceOptimizations = {
  // Data Management
  debouncedAutoSave: {
    delay: 1000,
    maxWait: 5000,
    strategy: 'debounce'
  },
  virtualScrolling: {
    enabled: true,
    itemHeight: 100,
    bufferSize: 10
  },
  lazyLoading: {
    enabled: true,
    threshold: 100,
    rootMargin: '50px'
  },
  
  // Image and Video Optimization
  thumbnailGeneration: {
    quality: 'medium',
    size: '320x180',
    format: 'webp'
  },
  videoCompression: {
    enabled: true,
    quality: 80,
    format: 'mp4'
  },
  imageOptimization: {
    enabled: true,
    formats: ['webp', 'avif'],
    quality: 85
  },
  
  // Network Optimization
  requestBatching: {
    enabled: true,
    batchSize: 5,
    delay: 100
  },
  caching: {
    enabled: true,
    strategy: 'cache-first',
    ttl: 300000 // 5 minutes
  },
  compression: {
    enabled: true,
    algorithm: 'gzip',
    level: 6
  },
  
  // UI Optimization
  componentMemoization: {
    enabled: true,
    strategy: 'shallow-compare'
  },
  stateOptimization: {
    enabled: true,
    strategy: 'selective-updates'
  },
  renderOptimization: {
    enabled: true,
    strategy: 'virtual-dom'
  }
}
```

---

*Last Updated: March 1, 2026*
*Version: 2.0.0 - Detailed Documentation*
*Author: Digital HQ Development Team (Haku)*
