<template>
  <transition name="cropper-v5-fade">
    <div class="v5-overlay" @click.self="$emit('cancel')">
      <div class="v5-modal liquid-glass-premium" :class="{ 'v5-modal-wide': isBanner }">
        <!-- Header -->
        <header class="v5-header">
          <div class="v5-header-title">
            <div class="v5-title-icon"><i class="fas" :class="isBanner ? 'fa-image' : 'fa-user-edit'"></i></div>
            <h3>Adjust Your {{ isBanner ? 'Profile Banner' : 'Profile Picture' }}</h3>
          </div>
          <button class="v5-close-btn" @click="$emit('cancel')">
            <i class="fas fa-times"></i>
          </button>
        </header>

        <!-- Dynamic Creative Workspace -->
        <div class="v5-workspace">
          <div 
            class="v5-stage" 
            ref="stageRef"
            :style="{ height: isBanner ? '400px' : '480px' }"
            @mousedown="startDrag"
            @touchstart="startDrag"
            @wheel.prevent="handleWheel"
          >
            <!-- Draggable Image Layer -->
            <!-- V8 Strategy: Absolute Center Origin + Transform -->
            <div 
              v-if="imageSrc"
              class="v5-image-wrap"
              :style="{
                transform: `translate(-50%, -50%) translate3d(${posX}px, ${posY}px, 0) scale(${scale})`,
                transition: isDragging ? 'none' : 'transform 0.15s cubic-bezier(0.2, 0, 0.2, 1)'
              }"
            >
              <img 
                ref="imageRef" 
                :src="imageSrc" 
                class="v5-source-img" 
                crossorigin="anonymous"
                @load="handleLoad" 
                draggable="false"
              />
            </div>

            <!-- Cinematic Mask Overlay -->
            <div class="v5-mask-overlay">
              <div 
                class="v5-window" 
                :class="isBanner ? 'v5-window-banner' : 'v5-window-circle'"
                :style="windowStyle"
              ></div>
            </div>

            <!-- Reposition Hint -->
            <div class="v5-hint" :class="{ 'v5-hint-hidden': isDragging || !imgReady }">
              Drag to Reposition
            </div>
          </div>

          <!-- Interaction Controls -->
          <div class="v5-controls-area">
            <div class="v5-zoom-bar">
              <i class="fas fa-minus v5-zoom-min"></i>
              <input 
                type="range" 
                :min="minScale" 
                :max="maxScale" 
                step="0.0001" 
                v-model="zoomInput" 
                @input="handleSliderChange"
                class="v5-slider"
                :disabled="!imgReady"
              />
              <i class="fas fa-plus v5-zoom-max"></i>
            </div>
          </div>
        </div>

        <!-- Master Footer -->
        <footer class="v5-footer">
          <button class="v5-btn-secondary" @click="$emit('cancel')">Cancel</button>
          <button class="v5-btn-primary" @click="saveCrop" :disabled="processing || !imgReady">
            <span v-if="!processing">Apply Changes</span>
            <i v-else class="fas fa-spinner fa-spin"></i>
          </button>
        </footer>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  imageSrc: { type: String, required: true },
  aspectRatio: { type: Number, default: 1 }
})

const emit = defineEmits(['crop', 'cancel'])

const isBanner = computed(() => props.aspectRatio !== 1)

// Window Config
const windowWidth = computed(() => isBanner.value ? 560 : 320)
const windowHeight = computed(() => isBanner.value ? 240 : 320)

const windowStyle = computed(() => ({
  width: `${windowWidth.value}px`,
  height: `${windowHeight.value}px`
}))

// Refs
const stageRef = ref(null)
const imageRef = ref(null)

// State
const posX = ref(0)
const posY = ref(0)
const scale = ref(0.1) // Start small hide until load
const zoomInput = ref('0.1')
const minScale = ref(0.01)
const maxScale = ref(10)
const isDragging = ref(false)
const processing = ref(false)
const imgReady = ref(false)

let startX = 0
let startY = 0
let imgNaturalW = 0
let imgNaturalH = 0

// Robust Load Management
const handleLoad = () => {
  if (!imageRef.value) return
  
  imgNaturalW = imageRef.value.naturalWidth
  imgNaturalH = imageRef.value.naturalHeight
  
  if (imgNaturalW === 0 || imgNaturalH === 0) {
    console.warn('Image natural dimensions are 0, retrying...')
    setTimeout(handleLoad, 100)
    return
  }

  // Calculate Fill-to-Fit
  const scaleW = windowWidth.value / imgNaturalW
  const scaleH = windowHeight.value / imgNaturalH
  const baseScale = Math.max(scaleW, scaleH)
  
  minScale.value = baseScale
  scale.value = baseScale
  zoomInput.value = String(baseScale)
  maxScale.value = baseScale * 8
  
  posX.value = 0
  posY.value = 0
  
  imgReady.value = true
  constrainPosition()
}

onMounted(() => {
  // Catch cached images
  if (imageRef.value && imageRef.value.complete) {
    handleLoad()
  }
})

const handleSliderChange = () => {
  scale.value = parseFloat(zoomInput.value)
  constrainPosition()
}

const handleWheel = (e) => {
  if (!imgReady.value) return
  const delta = e.deltaY > 0 ? -0.015 : 0.015
  const newScale = Math.max(minScale.value, Math.min(maxScale.value, scale.value + delta))
  scale.value = newScale
  zoomInput.value = String(newScale)
  constrainPosition()
}

// Drag Interaction
const startDrag = (e) => {
  if (!imgReady.value) return
  isDragging.value = true
  const clientX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX
  const clientY = e.type.includes('touch') ? e.touches[0].clientY : e.clientY
  
  startX = clientX - posX.value
  startY = clientY - posY.value
  
  window.addEventListener('mousemove', onDragging)
  window.addEventListener('mouseup', endDrag)
  window.addEventListener('touchmove', onDragging, { passive: false })
  window.addEventListener('touchend', endDrag)
}

const onDragging = (e) => {
  if (!isDragging.value) return
  if (e.type === 'touchmove') e.preventDefault()
  
  const clientX = e.type.includes('touch') ? e.touches[0].clientX : e.clientX
  const clientY = e.type.includes('touch') ? e.touches[0].clientY : e.clientY
  
  posX.value = clientX - startX
  posY.value = clientY - startY
  
  constrainPosition()
}

const endDrag = () => {
  isDragging.value = false
  window.removeEventListener('mousemove', onDragging)
  window.removeEventListener('mouseup', endDrag)
  window.removeEventListener('touchmove', onDragging)
  window.removeEventListener('touchend', endDrag)
}

const constrainPosition = () => {
  if (!imgNaturalW) return
  
  const scaledW = imgNaturalW * scale.value
  const scaledH = imgNaturalH * scale.value
  
  const limitX = Math.max(0, (scaledW - windowWidth.value) / 2)
  const limitY = Math.max(0, (scaledH - windowHeight.value) / 2)
  
  posX.value = Math.max(-limitX, Math.min(limitX, posX.value))
  posY.value = Math.max(-limitY, Math.min(limitY, posY.value))
}

const saveCrop = async () => {
  if (processing.value || !imgReady.value) return
  processing.value = true
  
  try {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    
    // High-res output
    const outW = isBanner.value ? 2400 : 1200
    const outH = Math.round(outW / props.aspectRatio)
    
    canvas.width = outW
    canvas.height = outH
    
    const sScale = scale.value
    const sX = posX.value
    const sY = posY.value
    
    // Source mapping
    const sw = (windowWidth.value / sScale)
    const sh = (windowHeight.value / sScale)
    const sx = (imgNaturalW / 2) - (sw / 2) - (sX / sScale)
    const sy = (imgNaturalH / 2) - (sh / 2) - (sY / sScale)
    
    ctx.imageSmoothingEnabled = true
    ctx.imageSmoothingQuality = 'high'
    ctx.drawImage(imageRef.value, sx, sy, sw, sh, 0, 0, outW, outH)
    
    canvas.toBlob((blob) => {
      emit('crop', blob)
      processing.value = false
    }, 'image/jpeg', 0.95)
  } catch (err) {
    console.error('Save failed:', err)
    processing.value = false
  }
}

onUnmounted(endDrag)
</script>

<style scoped>
.v5-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.96);
  backdrop-filter: blur(25px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10002;
  padding: 1rem;
}

.liquid-glass-premium {
  background: linear-gradient(165deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.02) 100%);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 60px 120px rgba(0, 0, 0, 0.9);
  border-radius: 40px;
}

.v5-modal {
  width: 100%;
  max-width: 650px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: max-width 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  user-select: none;
  -webkit-user-select: none;
}

.v5-modal-wide {
  max-width: 900px;
}

.v5-header {
  padding: 2rem 2.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.v5-header-title {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.v5-title-icon {
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  color: white;
  border-radius: 12px;
}

.v5-header h3 {
  margin: 0;
  font-size: 1.35rem;
  font-weight: 800;
  color: white;
  letter-spacing: -0.01em;
}

.v5-close-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #94a3b8;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.v5-workspace {
  background: #000;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.v5-stage {
  position: relative;
  overflow: hidden;
  cursor: grab;
  background-image: 
    linear-gradient(45deg, #09090b 25%, transparent 25%), 
    linear-gradient(-45deg, #09090b 25%, transparent 25%), 
    linear-gradient(45deg, transparent 75%, #09090b 75%), 
    linear-gradient(-45deg, transparent 75%, #09090b 75%);
  background-size: 24px 24px;
  background-position: 0 0, 0 12px, 12px -12px, -12px 0px;
  background-color: #0c0c0e;
}

.v5-stage:active { cursor: grabbing; }

.v5-image-wrap {
  position: absolute;
  top: 50%;
  left: 50%;
  pointer-events: none;
  will-change: transform;
}

.v5-source-img {
  display: block;
  max-width: none !important;
  max-height: none !important;
}

.v5-mask-overlay {
  position: absolute;
  inset: 0;
  pointer-events: none;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.v5-window {
  border: 4px solid rgba(255, 255, 255, 0.95);
  box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.88);
  position: relative;
}

.v5-window-circle { border-radius: 50%; }
.v5-window-banner { border-radius: 12px; }

.v5-hint {
  position: absolute;
  bottom: 2rem;
  left: 0;
  right: 0;
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  z-index: 20;
  transition: opacity 0.3s;
}

.v5-hint-hidden { opacity: 0; }

.v5-controls-area {
  padding: 3rem;
}

.v5-zoom-bar {
  display: flex;
  align-items: center;
  gap: 2rem;
  max-width: 500px;
  margin: 0 auto;
}

.v5-zoom-min, .v5-zoom-max { font-size: 1.2rem; color: #4b5563; }

.v5-slider {
  -webkit-appearance: none;
  appearance: none;
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  outline: none;
}

.v5-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 32px;
  height: 32px;
  background: white;
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

.v5-footer {
  padding: 2.5rem;
  display: flex;
  justify-content: center;
  gap: 2.5rem;
  background: rgba(0, 0, 0, 0.4);
}

.v5-btn-secondary {
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  font-weight: 700;
  font-size: 1.1rem;
}

.v5-btn-primary {
  background: linear-gradient(135deg, #2374e1, #3982e4);
  color: white;
  border: none;
  padding: 1.2rem 4rem;
  border-radius: 20px;
  font-weight: 800;
  font-size: 1.2rem;
  cursor: pointer;
  box-shadow: 0 10px 30px rgba(35, 116, 225, 0.4);
}

.cropper-v5-fade-enter-active { animation: v5-in 0.6s cubic-bezier(0.16, 1, 0.3, 1); }
@keyframes v5-in { from { opacity: 0; transform: translateY(40px); scale: 1.05; } to { opacity: 1; transform: translateY(0); scale: 1; } }
</style>
