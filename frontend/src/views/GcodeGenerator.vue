<template>
  <div class="gcode-generator" v-if="systemStore.powerMode !== 'power_saver'">
    <!-- Header -->
    <div class="page-header">
      <div class="header-text">
        <h1><i class="fas fa-drafting-compass"></i> G-code Generator</h1>
        <p class="subtitle">Convert SVG, PNG, JPG, BMP &amp; PDF into machine-ready G-code for plotters &amp; CNC</p>
      </div>
    </div>
      <input ref="fileInput" type="file" accept=".svg,.png,.jpg,.jpeg,.bmp,.pdf" hidden @change="handleFileChange" />
    <!-- 3-Panel Preview Row -->
    <div class="preview-row">
      <!-- Original Image -->
      <div class="preview-card glass-panel">
        <div class="panel-label">ORIGINAL IMAGE</div>
        <div class="img-box" :class="{ empty: !uploadedFile }" @dragover.prevent="dragging = true" @dragleave.prevent="dragging = false" @drop.prevent="handleDrop" @click="$refs.fileInput.click()">
          <template v-if="!uploadedFile">
            <i class="fas fa-cloud-upload-alt drop-icon"></i>
            <p>Drop image here<br />or <strong>click here</strong> to upload</p>
            <div class="fmt-badges">
              <span v-for="f in ['SVG','PNG','JPG','BMP','PDF']" :key="f" class="badge">{{ f }}</span>
            </div>
          </template>
          <template v-else>
            <img v-if="originalPreviewUrl" :src="originalPreviewUrl" alt="Original" class="preview-img" />
            <div v-else class="preview-placeholder"><i class="fas fa-file-code fa-3x"></i><p>{{ uploadedFile.name }}</p></div>
          </template>
        </div>
        <div v-if="uploadedFile" class="img-meta">
          <span>{{ imgDims }}</span>
          <span>{{ formatFileSize(uploadedFile.size) }}</span>
        </div>
      </div>

      <!-- Generated SVG -->
      <div class="preview-card glass-panel">
        <div class="panel-label">
          <span>GENERATED SVG</span>
          <button v-if="svgData" class="header-action-btn" @click="showFullSvg = true" title="Expand View">
            <i class="fas fa-expand"></i>
          </button>
        </div>
        <div class="img-box" :class="{ empty: !svgData }">
          <template v-if="!svgData && !previewing">
            <i class="fas fa-vector-square drop-icon"></i>
            <p>Generate SVG to see vector preview</p>
          </template>
          <div v-else-if="previewing" class="spinner-container">
            <div class="spinner"></div>
            <p>Tracing vectors…</p>
          </div>
          <div v-else class="svg-holder" 
               ref="svgContainer"
               style="overflow: hidden; cursor: crosshair;"
               @mousedown="startPan" 
               @mousemove="doPan" 
               @mouseup="stopPan" 
               @mouseleave="stopPan"
               @wheel="handleWheel">
            <div class="svg-render-scale" :style="{ transform: `translate(${svgPan.x}px, ${svgPan.y}px) scale(${svgZoom})` }" v-html="svgData"></div>
          </div>
        </div>
        <div v-if="svgPages.length > 1" class="page-controls">
          <button class="btn-icon" :disabled="currentPageIndex === 0" @click="currentPageIndex--"><i class="fas fa-chevron-left"></i></button>
          <span>PAGE {{ currentPageIndex + 1 }} OF {{ svgPages.length }}</span>
          <button class="btn-icon" :disabled="currentPageIndex === svgPages.length - 1" @click="currentPageIndex++"><i class="fas fa-chevron-right"></i></button>
        </div>
        <div v-if="svgStats" class="img-meta svg-stats">
          <span><b class="stat-num">{{ svgStats.paths }}</b> PATHS</span>
          <span><b class="stat-num">{{ svgStats.nodes }}</b> NODES</span>
          <span><b class="stat-num">{{ svgStats.size_kb }}KB</b></span>
        </div>
        <div v-if="svgData" class="btn-download-svg" @click="downloadSvg">
          <i class="fas fa-download"></i> DOWNLOAD SVG
        </div>

        <!-- Zoom Controls Overlay -->
        <div v-if="svgData" class="zoom-controls">
          <button class="zoom-btn" @click="adjustZoom(1.2)" title="Zoom In"><i class="fas fa-plus"></i></button>
          <button class="zoom-btn" @click="adjustZoom(0.8)" title="Zoom Out"><i class="fas fa-minus"></i></button>
          <button class="zoom-btn" @click="resetView" title="Reset View"><i class="fas fa-expand-arrows-alt"></i></button>
          <div class="zoom-level">{{ Math.round(svgZoom * 100) }}%</div>
        </div>
      </div>

      <!-- G-code Output -->
      <div class="preview-card glass-panel">
        <div class="panel-label">
          <div class="tab-group">
            <button :class="['tab-btn', { active: !simulatorMode }]" @click="simulatorMode = false">G-CODE</button>
            <button :class="['tab-btn', { active: simulatorMode }]" @click="simulatorMode = true">SIMULATOR</button>
          </div>
          <button v-if="gcodeOutput" class="header-action-btn" @click="showFullGcode = true" title="Expand View">
            <i class="fas fa-expand"></i>
          </button>
        </div>
        <div class="img-box gcode-box" :class="{ empty: !gcodeOutput }">
          <template v-if="!gcodeOutput && !generating">
            <i class="fas fa-microchip drop-icon"></i>
            <p>NO GCODE GENERATED</p>
          </template>
          <div v-else-if="generating" class="spinner-container">
            <div class="spinner"></div>
            <p>Generating G-code…</p>
          </div>
          <div v-else-if="simulatorMode" class="gcode-simulator-container" 
               ref="gcodeContainer"
               @mousedown="startGcodePan" 
               @mousemove="doGcodePan" 
               @mouseup="stopGcodePan" 
               @mouseleave="stopGcodePan"
               @wheel="handleGcodeWheel">
            <canvas ref="gcodeCanvas" width="500" height="500"></canvas>
            
            <!-- G-code Zoom Controls -->
            <div class="zoom-controls">
              <button class="zoom-btn" @click="adjustGcodeZoom(1.5)" title="Zoom In"><i class="fas fa-plus"></i></button>
              <button class="zoom-btn" @click="adjustGcodeZoom(0.7)" title="Zoom Out"><i class="fas fa-minus"></i></button>
              <button class="zoom-btn" @click="resetGcodeView" title="Reset View"><i class="fas fa-expand-arrows-alt"></i></button>
              <div class="zoom-level">{{ Math.round(gcodeZoom * 100) }}%</div>
            </div>
          </div>
          <pre v-else class="gcode-text custom-scrollbar">{{ gcodeOutput }}</pre>
        </div>
        <div v-if="gcodeOutput" class="img-meta gcode-meta">
          <div class="gcode-stats">
            <span>{{ gcodeLineCount }} lines</span>
            <span v-if="currentTimeEstimate" class="time-estimate">
              <i class="fas fa-clock"></i> {{ currentTimeEstimate.estimated_completion || formatTime(currentTimeEstimate) }}
            </span>
          </div>
          <div class="gcode-actions">
            <button class="btn-icon" title="Copy" @click="copyGcode"><i class="fas fa-copy"></i></button>
            <button class="btn-icon" title="Download" @click="downloadGcode"><i class="fas fa-download"></i></button>
          </div>
        </div>
      </div>
    </div>

    <!-- Settings Row -->
    <div class="settings-row">
      <!-- IMAGE → SVG SETTINGS -->
      <div class="settings-card glass-panel">
        <div class="settings-header">IMAGE → SVG SETTINGS</div>

        <button class="generate-btn" :disabled="!uploadedFile || previewing" @click="generatePreview">
          <i class="fas fa-eye"></i>
          {{ previewing ? 'PROCESSING…' : 'GENERATE SVG' }}
        </button>

        <!-- Presets -->
        <div class="setting-group">
          <div class="setting-label">PRESETS</div>
          <div class="preset-grid">
            <button
              v-for="p in presets"
              :key="p.id"
              class="preset-btn"
              :class="{ active: activePreset === p.id }"
              @click="applyPreset(p)"
            >
              <span class="preset-name">{{ p.name }}</span>
              <span class="preset-desc">{{ p.desc }}</span>
            </button>
          </div>
        </div>

        <!-- Threshold -->
        <div class="setting-group">
          <div class="slider-row">
            <span class="setting-label">THRESHOLD</span>
            <span class="slider-val">{{ Math.round(svgSettings.threshold / 255 * 100) }}%</span>
          </div>
          <input type="range" min="0" max="255" v-model.number="svgSettings.threshold" class="slider" />
        </div>

        <!-- Detail Level -->
        <div class="setting-group">
          <div class="slider-row">
            <span class="setting-label">DETAIL LEVEL</span>
            <span class="slider-val">{{ svgSettings.detailLevel }}</span>
          </div>
          <input type="range" min="1" max="10" v-model.number="svgSettings.detailLevel" class="slider" />
        </div>
        
        <!-- Epsilon / Curve Precision -->
        <div class="setting-group mt-1">
          <div class="slider-row">
            <span class="setting-label" title="Lower = smoother curves & more nodes. Higher = blocky polygons.">CURVE PRECISION (EPSILON)</span>
            <span class="slider-val">{{ svgSettings.epsilonVal.toFixed(2) }}</span>
          </div>
          <input type="range" min="0.01" max="3.0" step="0.01" v-model.number="svgSettings.epsilonVal" class="slider" />
        </div>

        <!-- Smoothing -->
        <div class="setting-group">
          <div class="slider-row">
            <span class="setting-label">SMOOTHING</span>
            <span class="slider-val">{{ svgSettings.smoothing }}</span>
          </div>
          <input type="range" min="0" max="10" v-model.number="svgSettings.smoothing" class="slider" />
        </div>

        <!-- Despeckle -->
        <div class="setting-group">
          <div class="slider-row">
            <span class="setting-label">DESPECKLE</span>
            <span class="slider-val">{{ svgSettings.despeckle }}</span>
          </div>
          <input type="range" min="0" max="10" v-model.number="svgSettings.despeckle" class="slider" />
        </div>

        <!-- Color Mode -->
        <div class="setting-group">
          <div class="setting-label">COLOR MODE</div>
          <select v-model="svgSettings.colorMode" class="setting-select">
            <option value="bw">Black &amp; White</option>
            <option value="grayscale">Grayscale</option>
            <option value="color">Color</option>
          </select>
        </div>

        <!-- Trace Mode -->
        <div class="setting-group mt-2">
          <div class="setting-label">TRACE MODE</div>
          <select v-model="svgSettings.traceMode" class="setting-select">
            <option value="Outline Only">Outline Only</option>
            <option value="Object/Color Outlines">Object/Color Outlines</option>
          </select>
        </div>

        <!-- Output Mode -->
        <div class="setting-group mt-2 mb-2">
          <div class="setting-label">SVG OUTPUT MODE</div>
          <div class="toggle-group">
            <button :class="['toggle-btn', { active: svgSettings.outputMode === 'True Curves' }]" @click="svgSettings.outputMode = 'True Curves'">
              <i class="fas fa-bezier-curve"></i> True Curves
            </button>
            <button :class="['toggle-btn', { active: svgSettings.outputMode === 'Lines' }]" @click="svgSettings.outputMode = 'Lines'">
              <i class="fas fa-ruler-combined"></i> Lines
            </button>
          </div>
        </div>

        <!-- Potrace Settings -->
        <div class="setting-section-title mt-2">POTRACE CURVE SETTINGS</div>
        <div class="setting-group">
          <div class="slider-row">
            <span class="setting-label" title="Corner Threshold. Lower = sharper corners.">ALPHAMAX</span>
            <span class="slider-val">{{ svgSettings.alphamax.toFixed(2) }}</span>
          </div>
          <input type="range" min="0.0" max="1.4" step="0.05" v-model.number="svgSettings.alphamax" class="slider" />
        </div>
        <div class="setting-group">
          <div class="slider-row">
            <span class="setting-label" title="Optimization tolerance for Bezier Curves.">OPT. TOLERANCE</span>
            <span class="slider-val">{{ svgSettings.opttolerance.toFixed(2) }}</span>
          </div>
          <input type="range" min="0.0" max="1.0" step="0.05" v-model.number="svgSettings.opttolerance" class="slider" />
        </div>

        <!-- Hatching Settings -->
        <div class="setting-section-title mt-2">HATCHING FILL</div>
        <div class="setting-group">
          <label class="check-item mb-2">
            <input type="checkbox" v-model="svgSettings.hatch" />
            <span class="setting-label">ENABLE HATCHING (DOUBLE TRACE)</span>
          </label>
        </div>
        <div v-if="svgSettings.hatch">
          <div class="setting-group">
            <div class="slider-row">
              <span class="setting-label">SPACING (PX)</span>
              <span class="slider-val">{{ svgSettings.hatchSpacing.toFixed(1) }}</span>
            </div>
            <input type="range" min="1.0" max="20.0" step="0.5" v-model.number="svgSettings.hatchSpacing" class="slider" />
          </div>
          <div class="setting-group mb-2">
            <div class="slider-row">
              <span class="setting-label">HATCH ANGLE</span>
              <span class="slider-val">{{ svgSettings.hatchAngle }}°</span>
            </div>
            <input type="range" min="-90" max="90" step="5" v-model.number="svgSettings.hatchAngle" class="slider" />
          </div>
        </div>

        <!-- Checkboxes -->
        <div class="check-group">
          <label class="check-item">
            <input type="checkbox" v-model="svgSettings.invertColors" />
            <span>Invert Colors</span>
          </label>
          <label class="check-item">
            <input type="checkbox" v-model="svgSettings.removeBackground" />
            <span>Remove Background</span>
          </label>
          <label class="check-item">
            <input type="checkbox" v-model="svgSettings.limitPaths" />
            <span>Limit to 500 Paths (Recommended)</span>
          </label>
        </div>
      </div>

      <!-- SVG → G-CODE SETTINGS -->
      <div class="settings-card glass-panel">
        <div class="settings-header">SVG → G-CODE SETTINGS</div>

        <button class="generate-btn gcode-gen-btn" :disabled="!svgData || generating" @click="generateGcode">
          <i class="fas fa-microchip"></i>
          {{ generating ? 'GENERATING…' : 'GENERATE GCODE' }}
        </button>

        <!-- Machine Configuration -->
        <div class="setting-section-title">MACHINE CONFIGURATION</div>
        <div class="two-col">
          <div class="setting-group">
            <div class="setting-label">X-MAX (MM)</div>
            <input type="number" v-model.number="gcodeSettings.xMax" class="setting-input" min="1" />
          </div>
          <div class="setting-group">
            <div class="setting-label">Y-MAX (MM)</div>
            <input type="number" v-model.number="gcodeSettings.yMax" class="setting-input" min="1" />
          </div>
        </div>

        <div class="setting-group">
          <div class="setting-label">UNITS</div>
          <select v-model="gcodeSettings.units" class="setting-select">
            <option value="mm">Millimeters</option>
            <option value="in">Inches</option>
          </select>
        </div>

        <div class="setting-group">
          <div class="setting-label">ORIGIN</div>
          <select v-model="gcodeSettings.origin" class="setting-select">
            <option value="bottom-left">Bottom-Left</option>
            <option value="top-left">Top-Left</option>
            <option value="center">Center</option>
          </select>
        </div>

        <div class="setting-group">
          <div class="setting-label">SCALING</div>
          <select v-model="gcodeSettings.scaling" class="setting-select">
            <option value="fit">Fit to Bed</option>
            <option value="actual">Actual Size</option>
            <option value="manual">Manual Scale</option>
          </select>
        </div>

        <!-- Movement Parameters -->
        <div class="setting-section-title">MOVEMENT PARAMETERS</div>
        <div class="setting-group">
          <div class="setting-label">FEED RATE (MM/MIN)</div>
          <input type="number" v-model.number="gcodeSettings.feedRate" class="setting-input" min="100" />
        </div>
        <div class="setting-group">
          <div class="setting-label">TRAVEL SPEED (MM/MIN)</div>
          <input type="number" v-model.number="gcodeSettings.travelRate" class="setting-input" min="100" />
        </div>

        <!-- Pen Control -->
        <div class="setting-section-title">PEN CONTROL</div>
        <div class="two-col">
          <div class="setting-group">
            <div class="setting-label">Z UP (MM)</div>
            <input type="number" v-model.number="gcodeSettings.zUp" class="setting-input" />
          </div>
          <div class="setting-group">
            <div class="setting-label">Z DOWN (MM)</div>
            <input type="number" v-model.number="gcodeSettings.zDown" class="setting-input" />
          </div>
        </div>
        <div class="setting-group">
          <div class="setting-label">DWELL TIME (MS)</div>
          <input type="number" v-model.number="gcodeSettings.dwellTime" class="setting-input" min="0" />
        </div>

        <!-- Path Optimization -->
        <div class="setting-section-title">PATH OPTIMIZATION</div>
        <label class="check-item">
          <input type="checkbox" v-model="gcodeSettings.optimizePaths" />
          <span>Optimize Path Order</span>
        </label>
        <label class="check-item">
          <input type="checkbox" v-model="gcodeSettings.useArcs" />
          <span>Compress to Arcs (G2/G3)</span>
        </label>
        <div class="setting-group mt-2">
          <div class="setting-label">SIMPLIFICATION TOLERANCE</div>
          <input type="number" v-model.number="gcodeSettings.simplifyTolerance" class="setting-input" step="0.1" min="0" />
        </div>
        <div class="setting-group">
          <div class="setting-label">CURVE RESOLUTION (SEGMENTS)</div>
          <input type="number" v-model.number="gcodeSettings.curveResolution" class="setting-input" min="1" max="100" />
        </div>

        <!-- Save to Drive -->
        <div class="save-drive-area" v-if="gcodeOutput">
          <div class="setting-section-title">SAVE TO DRIVE</div>
          <p class="save-hint">Saves to <code>Generated Gcodes/</code> in your Drive</p>
          <div class="save-row">
            <input type="text" v-model="saveFilename" placeholder="Filename…" class="setting-input save-input" autocomplete="off" />
            <span class="ext">.nc</span>
            <button class="btn-save" :disabled="!saveFilename.trim() || saving" @click="saveToDrive">
              {{ saving ? '…' : 'Save' }}
            </button>
          </div>
          <p v-if="saveSuccess" class="save-ok"><i class="fas fa-check-circle"></i> Saved!</p>
          <p v-if="saveError" class="save-err"><i class="fas fa-times-circle"></i> {{ saveError }}</p>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div v-if="toast.visible" class="toast" :class="toast.type">{{ toast.message }}</div>

    <!-- SVG Expansion Modal -->
    <div v-if="showFullSvg" class="modal-overlay" @click.self="showFullSvg = false">
      <div class="modal-content glass-panel full-preview-modal">
        <div class="modal-header">
          <h3>SVG VECTOR PREVIEW</h3>
          <button class="close-btn" @click="showFullSvg = false"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-body">
           <div class="svg-holder fullscreen-svg-holder" 
               @mousedown="startPan" 
               @mousemove="doPan" 
               @mouseup="stopPan" 
               @mouseleave="stopPan"
               @wheel="handleWheel">
            <div class="svg-render-scale" :style="{ transform: `translate(${svgPan.x}px, ${svgPan.y}px) scale(${svgZoom})` }" v-html="svgData"></div>
          </div>
        </div>
        <div class="modal-footer">
           <div class="zoom-controls static-zoom">
            <button class="zoom-btn" @click="adjustZoom(1.5)"><i class="fas fa-plus"></i></button>
            <button class="zoom-btn" @click="adjustZoom(0.7)"><i class="fas fa-minus"></i></button>
            <button class="zoom-btn" @click="resetView"><i class="fas fa-expand-arrows-alt"></i></button>
            <div class="zoom-level">{{ Math.round(svgZoom * 100) }}%</div>
          </div>
        </div>
      </div>
    </div>

    <!-- G-code Expansion Modal -->
    <div v-if="showFullGcode" class="modal-overlay" @click.self="showFullGcode = false">
      <div class="modal-content glass-panel full-preview-modal">
        <div class="modal-header">
          <h3>G-CODE TOOLPATH SIMULATOR</h3>
          <button class="close-btn" @click="showFullGcode = false"><i class="fas fa-times"></i></button>
        </div>
        <div class="modal-body simulator-body">
          <div class="gcode-large-view"
               @mousedown="startGcodePan" 
               @mousemove="doGcodePan" 
               @mouseup="stopGcodePan" 
               @mouseleave="stopGcodePan"
               @wheel="handleGcodeWheel">
             <canvas id="largeGcodeCanvas" width="1000" height="1000"></canvas>
          </div>
        </div>
        <div class="modal-footer">
           <div class="zoom-controls static-zoom">
            <button class="zoom-btn" @click="adjustGcodeZoom(1.5)"><i class="fas fa-plus"></i></button>
            <button class="zoom-btn" @click="adjustGcodeZoom(0.7)"><i class="fas fa-minus"></i></button>
            <button class="zoom-btn" @click="resetGcodeView"><i class="fas fa-expand-arrows-alt"></i></button>
            <div class="zoom-level">{{ Math.round(gcodeZoom * 100) }}%</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="gcode-generator-disabled" v-else>
    <div class="disabled-message glass-panel">
      <i class="fas fa-bolt pulse-alert" style="font-size: 4rem; color: #f59e0b; margin-bottom: 1rem;"></i>
      <h2>G-code Generator Disabled</h2>
      <p>The G-code generator and toolpath emulator requires significant processing power and has been temporarily disabled to conserve energy during Power Saver mode.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { apiPost, apiPostForm } from '../utils/api.js'
import { useSystemStore } from '@/stores/systemStore.js'

const systemStore = useSystemStore()

// --- State ---
const fileInput = ref(null)
const uploadedFile = ref(null)
const originalPreviewUrl = ref('')
const imgDims = ref('')
const dragging = ref(false)

const svgPages = ref([])
const gcodePages = ref([])
const timeEstimates = ref([])
const currentPageIndex = ref(0)

const svgData = computed(() => svgPages.value[currentPageIndex.value]?.svg || '')
const svgStats = computed(() => svgPages.value[currentPageIndex.value]?.stats || null)
const gcodeOutput = computed(() => gcodePages.value[currentPageIndex.value] || '')
const currentTimeEstimate = computed(() => timeEstimates.value[currentPageIndex.value] || null)

const previewing = ref(false)
const generating = ref(false)
const saving = ref(false)
const activePreset = ref('balanced')
const saveFilename = ref('')
const saveSuccess = ref(false)
const saveError = ref('')
const toast = ref({ visible: false, message: '', type: 'success' })

// --- Pan & Zoom State ---
const svgZoom = ref(1)
const svgPan = ref({ x: 0, y: 0 })
const isPanning = ref(false)
const lastPanPos = ref({ x: 0, y: 0 })
const svgContainer = ref(null)

// --- G-code Pan & Zoom State ---
const gcodeZoom = ref(1)
const gcodePan = ref({ x: 0, y: 0 })
const isGcodePanning = ref(false)
const lastGcodePanPos = ref({ x: 0, y: 0 })
const gcodeContainer = ref(null)

// --- Fullscreen & Simulation State ---
const showFullSvg = ref(false)
const showFullGcode = ref(false)
const simulatorMode = ref(false)
const gcodeCanvas = ref(null)
const parsedGcode = ref([])

const svgSettings = ref({
  threshold: 127,
  detailLevel: 5,
  epsilonVal: 0.1, 
  smoothing: 0, // Set default smoothing to 0 to prevent blurring
  despeckle: 0, // Despeckle explicitly set to 0 to stop destroying thin lines!
  colorMode: 'bw',
  invertColors: false,
  traceMode: 'Object/Color Outlines',
  outputMode: 'True Curves',
  removeBackground: false,
  limitPaths: true,
  alphamax: 1.0,
  opttolerance: 0.2,
  hatch: false,
  hatchSpacing: 5,
  hatchAngle: 45.0
})

const gcodeSettings = ref({
  xMax: 300,
  yMax: 300,
  units: 'mm',
  origin: 'bottom-left',
  scaling: 'fit',
  feedRate: 2000,
  travelRate: 4000,
  zUp: 5,
  zDown: -1,
  dwellTime: 100,
  optimizePaths: true,
  simplifyTolerance: 0.5,
  curveResolution: 10,
  useArcs: false
})

// --- Presets ---
const presets = [
  // Presets updated with Despeckle AND Smoothing set to 0 to protect Potrace fidelity
  { id: 'fast', name: 'Fast & Simple', desc: 'Low detail, fast processing.', threshold: 127, detailLevel: 3, smoothing: 0, despeckle: 0 },
  { id: 'balanced', name: 'Balanced', desc: 'Good balance of detail and performance.', threshold: 127, detailLevel: 5, smoothing: 0, despeckle: 0 },
  { id: 'high-detail', name: 'High Detail', desc: 'Maximum detail, slower processing.', threshold: 127, detailLevel: 9, smoothing: 0, despeckle: 0 },
  { id: 'logo', name: 'Logo / Vector', desc: 'Clean edges, minimal smoothing.', threshold: 127, detailLevel: 7, smoothing: 0, despeckle: 0 },
  { id: 'sketch', name: 'Sketch', desc: 'Artistic sketch effect.', threshold: 150, detailLevel: 6, smoothing: 0, despeckle: 0 }
]

const applyPreset = (p) => {
  activePreset.value = p.id
  svgSettings.value.threshold = p.threshold
  svgSettings.value.detailLevel = p.detailLevel
  svgSettings.value.smoothing = p.smoothing
  svgSettings.value.despeckle = p.despeckle
}

// --- File Handling ---
const handleFileChange = (e) => {
  const f = e.target.files[0]
  if (f) setFile(f)
}

const handleDrop = (e) => {
  dragging.value = false
  const f = e.dataTransfer.files[0]
  if (f) setFile(f)
}

const setFile = (f) => {
  uploadedFile.value = f
  svgPages.value = []
  gcodePages.value = []
  currentPageIndex.value = 0
  saveSuccess.value = false
  saveError.value = ''
  if (f.type.startsWith('image/') && !f.name.endsWith('.svg')) {
    originalPreviewUrl.value = URL.createObjectURL(f)
    const img = new Image()
    img.onload = () => { imgDims.value = `${img.naturalWidth} × ${img.naturalHeight}` }
    img.src = originalPreviewUrl.value
  } else {
    originalPreviewUrl.value = ''
    imgDims.value = ''
  }
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1048576).toFixed(1)} MB`
}

// --- Preview / Generate SVG ---
const generatePreview = async () => {
  if (!uploadedFile.value) return
  previewing.value = true
  svgPages.value = []
  gcodePages.value = []
  currentPageIndex.value = 0

  try {
    const formData = new FormData()
    formData.append('file', uploadedFile.value)
    formData.append('threshold', svgSettings.value.threshold)
    formData.append('blur', svgSettings.value.smoothing > 1 ? svgSettings.value.smoothing : 0)
    formData.append('despeckle', svgSettings.value.despeckle)
    formData.append('detail_level', svgSettings.value.detailLevel)
    formData.append('epsilon_val', svgSettings.value.epsilonVal) 
    formData.append('smoothing', svgSettings.value.smoothing)
    formData.append('color_mode', svgSettings.value.colorMode)
    formData.append('invert_colors', svgSettings.value.invertColors)
    formData.append('trace_mode', svgSettings.value.traceMode)
    formData.append('output_mode', svgSettings.value.outputMode)
    formData.append('alphamax', svgSettings.value.alphamax)
    formData.append('opttolerance', svgSettings.value.opttolerance)
    formData.append('hatch', svgSettings.value.hatch)
    formData.append('hatch_spacing', svgSettings.value.hatchSpacing)
    formData.append('hatch_angle', svgSettings.value.hatchAngle)

    const res = await apiPostForm('/gcode/preview', formData)
    svgPages.value = res.pages || []
  } catch (err) {
    showToast('Vectorization failed: ' + (err.message || 'Unknown error'), 'error')
  } finally {
    previewing.value = false
  }
}

// --- Generate G-code ---
const generateGcode = async () => {
  if (!svgPages.value.length) return
  generating.value = true
  gcodePages.value = []
  timeEstimates.value = []

  try {
    const s = gcodeSettings.value
    const mappedPages = svgPages.value.map(p => ({
      svg: p.svg,
      width_mm: p.stats?.width_mm || null,
      height_mm: p.stats?.height_mm || null
    }))
    const res = await apiPost('/gcode/generate', {
      pages: mappedPages,
      feed_rate: s.feedRate,
      travel_rate: s.travelRate,
      x_max: s.xMax,
      y_max: s.yMax,
      units: s.units,
      origin: s.origin,
      scaling: s.scaling,
      z_up: s.zUp,
      z_down: s.zDown,
      dwell_time: s.dwellTime,
      optimize_paths: s.optimizePaths,
      simplify_tolerance: s.simplifyTolerance,
      curve_resolution: s.curveResolution,
      use_arcs: s.useArcs
    })
    gcodePages.value = res.gcodes.map(gc => gc.replace(/\\n/g, '\n'))
    timeEstimates.value = res.time_estimates || []
    
    // Auto-parse the first page
    if (gcodePages.value[0]) {
      parsedGcode.value = parseGcode(gcodePages.value[0])
    }
  } catch (err) {
    showToast('G-code generation failed: ' + (err.message || 'Unknown error'), 'error')
  } finally {
    generating.value = false
  }
}

const gcodeLineCount = computed(() => gcodeOutput.value ? gcodeOutput.value.split('\n').length : 0)

// --- Copy / Download ---
const copyGcode = async () => {
  await navigator.clipboard.writeText(gcodeOutput.value)
  showToast('Copied to clipboard!', 'success')
}

const downloadGcode = () => {
  const name = saveFilename.value.trim() || 'output'
  const blob = new Blob([gcodeOutput.value], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${name}.nc`
  a.click()
  URL.revokeObjectURL(url)
}

watch(gcodeOutput, (newVal) => {
  if (newVal) {
    parsedGcode.value = parseGcode(newVal)
    if (simulatorMode.value) {
      setTimeout(() => drawGcode(), 50)
    }
  }
})

watch(simulatorMode, (newVal) => {
  if (newVal) {
    setTimeout(() => drawGcode(), 50)
  }
})

watch(showFullGcode, (newVal) => {
  if (newVal) {
    setTimeout(() => {
      const largeCanvas = document.getElementById('largeGcodeCanvas')
      if (largeCanvas) drawGcode(largeCanvas)
    }, 100)
  }
})

const formatTime = (seconds) => {
  if (!seconds) return 'N/A'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.round(seconds % 60)
  return `${h > 0 ? h + 'h ' : ''}${m > 0 ? m + 'm ' : ''}${s}s`
}

watch([gcodeZoom, gcodePan], () => {
  drawGcode()
  if (showFullGcode.value) {
    nextTick(() => {
      const largeCanvas = document.getElementById('largeGcodeCanvas')
      if (largeCanvas) drawGcode(largeCanvas)
    })
  }
}, { deep: true })

const parseGcode = (gcode) => {
  const lines = gcode.split('\n')
  const paths = []
  let currentPath = []
  let x = 0, y = 0
  let isDown = false

  lines.forEach(line => {
    const cmd = line.trim().toUpperCase()
    if (!cmd || cmd.startsWith('(')) return

    const xMatch = cmd.match(/X([-+]?[0-9]*\.?[0-9]+)/)
    const yMatch = cmd.match(/Y([-+]?[0-9]*\.?[0-9]+)/)
    const zMatch = cmd.match(/Z([-+]?[0-9]*\.?[0-9]+)/)

    if (zMatch) {
      const zVal = parseFloat(zMatch[1])
      isDown = zVal <= gcodeSettings.value.zDown
      if (!isDown && currentPath.length > 0) {
        paths.push([...currentPath])
        currentPath = []
      }
    }

    if (xMatch || yMatch) {
      if (xMatch) x = parseFloat(xMatch[1])
      if (yMatch) y = parseFloat(yMatch[1])
      currentPath.push({ x, y, type: isDown ? 'link' : 'travel' })
    }
  })
  if (currentPath.length > 0) paths.push(currentPath)
  return paths
}

const drawGcode = (extCanvas = null) => {
  const canvas = extCanvas || gcodeCanvas.value
  if (!canvas || !parsedGcode.value.length) return
  const ctx = canvas.getContext('2d')
  
  const w = canvas.width
  const h = canvas.height
  
  // 1. Find bounding box of content
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity
  parsedGcode.value.flat().forEach(p => {
    minX = Math.min(minX, p.x); maxX = Math.max(maxX, p.x)
    minY = Math.min(minY, p.y); maxY = Math.max(maxY, p.y)
  })
  if (minX === Infinity) { minX = 0; maxX = 300; minY = 0; maxY = 300; }

  const rangeX = maxX - minX || 1
  const rangeY = maxY - minY || 1
  const midX = (minX + maxX) / 2
  const midY = (minY + maxY) / 2

  // 2. Base scale to fit comfortably in canvas
  const padding = 40
  const baseScale = Math.min((w - padding) / rangeX, (h - padding) / rangeY)

  // 3. Render
  ctx.clearRect(0, 0, w, h)
  ctx.fillStyle = '#1a1a1a'
  ctx.fillRect(0, 0, w, h)

  ctx.save()
  // Step A: User Pan & Zoom (anchored at cursor via handled math)
  ctx.translate(gcodePan.value.x, gcodePan.value.y)
  ctx.scale(gcodeZoom.value, gcodeZoom.value)

  // Step B: Center content in the viewport and flip Y for G-code coords
  ctx.translate(w / 2, h / 2)
  ctx.scale(1, -1) // Standard CNC Y-up
  ctx.scale(baseScale, baseScale)
  ctx.translate(-midX, -midY)

  parsedGcode.value.forEach(path => {
    if (path.length < 2) return
    ctx.beginPath()
    ctx.moveTo(path[0].x, path[0].y)

    for (let i = 1; i < path.length; i++) {
      ctx.strokeStyle = path[i].type === 'link' ? '#4ade80' : 'rgba(255,255,255,0.15)'
      ctx.setLineDash(path[i].type === 'link' ? [] : [5 / (baseScale * gcodeZoom.value), 5 / (baseScale * gcodeZoom.value)])
      ctx.lineWidth = (path[i].type === 'link' ? 1.5 : 0.8) / (baseScale * gcodeZoom.value)
      ctx.lineTo(path[i].x, path[i].y)
      ctx.stroke()
      ctx.beginPath()
      ctx.moveTo(path[i].x, path[i].y)
    }
  })
  
  ctx.restore()
}

const downloadSvg = () => {
  const name = saveFilename.value.trim() || 'output'
  const blob = new Blob([svgData.value], { type: 'image/svg+xml' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${name}.svg`
  a.click()
  URL.revokeObjectURL(url)
}

// --- Pan & Zoom Logic ---
const handleWheel = (e) => {
  if (!svgData.value) return
  e.preventDefault()
  
  const container = e.currentTarget
  const rect = container.getBoundingClientRect()
  
  // Mouse position relative to the container
  const mouseX = e.clientX - rect.left
  const mouseY = e.clientY - rect.top
  
  const delta = e.deltaY > 0 ? 0.9 : 1.1
  const newZoom = Math.min(Math.max(svgZoom.value * delta, 0.1), 100)
  
  // Anchor zoom at mouse cursor
  // NewPan = MousePos - (MousePos - OldPan) * (NewZoom / OldZoom)
  svgPan.value.x = mouseX - (mouseX - svgPan.value.x) * delta
  svgPan.value.y = mouseY - (mouseY - svgPan.value.y) * delta
  svgZoom.value = newZoom
}

// --- G-code Pan & Zoom Logic ---
const handleGcodeWheel = (e) => {
  if (!gcodeOutput.value) return
  e.preventDefault()
  
  const container = e.currentTarget
  const rect = container.getBoundingClientRect()
  const mouseX = e.clientX - rect.left
  const mouseY = e.clientY - rect.top
  
  const delta = e.deltaY > 0 ? 0.9 : 1.1
  const newZoom = Math.min(Math.max(gcodeZoom.value * delta, 0.1), 100)
  
  // Anchor zoom at mouse cursor
  gcodePan.value.x = mouseX - (mouseX - gcodePan.value.x) * delta
  gcodePan.value.y = mouseY - (mouseY - gcodePan.value.y) * delta
  gcodeZoom.value = newZoom
}

const startGcodePan = (e) => {
  isGcodePanning.value = true
  lastGcodePanPos.value = { x: e.clientX, y: e.clientY }
}

const doGcodePan = (e) => {
  if (!isGcodePanning.value) return
  const dx = e.clientX - lastGcodePanPos.value.x
  const dy = e.clientY - lastGcodePanPos.value.y
  gcodePan.value.x += dx
  gcodePan.value.y += dy
  lastGcodePanPos.value = { x: e.clientX, y: e.clientY }
}

const stopGcodePan = () => {
  isGcodePanning.value = false
}

const resetGcodeView = () => {
  gcodeZoom.value = 1
  gcodePan.value = { x: 0, y: 0 }
  drawGcode()
}

const adjustGcodeZoom = (factor) => {
  // Center-based zoom for buttons
  if (gcodeContainer.value) {
    const rect = gcodeContainer.value.getBoundingClientRect()
    const cx = rect.width / 2
    const cy = rect.height / 2
    gcodePan.value.x = cx - (cx - gcodePan.value.x) * factor
    gcodePan.value.y = cy - (cy - gcodePan.value.y) * factor
  }
  gcodeZoom.value = Math.min(Math.max(gcodeZoom.value * factor, 0.1), 100)
  drawGcode()
}

const startPan = (e) => {
  if (!svgData.value) return
  isPanning.value = true
  lastPanPos.value = { x: e.clientX, y: e.clientY }
}

const doPan = (e) => {
  if (!isPanning.value) return
  const dx = e.clientX - lastPanPos.value.x
  const dy = e.clientY - lastPanPos.value.y
  svgPan.value.x += dx
  svgPan.value.y += dy
  lastPanPos.value = { x: e.clientX, y: e.clientY }
}

const stopPan = () => {
  isPanning.value = false
}

const resetView = () => {
  svgZoom.value = 1
  svgPan.value = { x: 0, y: 0 }
}

const adjustZoom = (factor) => {
  svgZoom.value = Math.min(Math.max(svgZoom.value * factor, 0.1), 100)
}

// --- Save to Drive ---
const saveToDrive = async () => {
  if (!saveFilename.value.trim() || !gcodeOutput.value) return
  saving.value = true
  saveSuccess.value = false
  saveError.value = ''
  try {
    await apiPost('/gcode/save', {
      filename: saveFilename.value.trim(),
      gcode_data: gcodeOutput.value
    })
    saveSuccess.value = true
    showToast('Saved to Drive!', 'success')
  } catch (err) {
    if (err.status === 409 || err.message?.includes('409')) {
      saveError.value = 'A file with this name already exists in Generated Gcodes.'
    } else {
      saveError.value = 'Save failed: ' + (err.message || 'Unknown error')
    }
  } finally {
    saving.value = false
  }
}

// --- Toast ---
const showToast = (message, type = 'success') => {
  toast.value = { visible: true, message, type }
  setTimeout(() => { toast.value.visible = false }, 3500)
}

</script>

<style scoped>
.gcode-generator {
  padding: 1.25rem 1.5rem;
  max-width: 1600px;
  margin: 0 auto;
  font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* Header */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.page-header h1 {
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin: 0;
}

.page-header h1 i { color: var(--primary-color); }

.subtitle {
  color: var(--text-secondary);
  font-size: 0.85rem;
  margin-top: 0.25rem;
}

.upload-btn-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  background: var(--primary-color);
  color: white;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  transition: filter 0.2s;
  white-space: nowrap;
}

.upload-btn-header:hover { filter: brightness(1.2); }

/* Preview Row */
.preview-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

@media (max-width: 900px) {
  .preview-row { grid-template-columns: 1fr; }
}

.glass-panel {
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

.preview-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-label {
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-secondary);
  padding: 0.6rem 1rem;
  border-bottom: 1px solid var(--glass-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-action-btn {
  background: transparent;
  border: 1px solid var(--glass-border);
  color: var(--text-secondary);
  width: 26px;
  height: 26px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.header-action-btn:hover {
  color: #4ade80;
  border-color: #4ade80;
  background: rgba(74, 222, 128, 0.1);
}

.tab-group {
  display: flex;
  gap: 0.4rem;
}

.tab-btn {
  background: transparent;
  border: 1px solid transparent;
  color: var(--text-secondary);
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-size: 0.65rem;
  font-weight: 800;
  cursor: pointer;
}

.tab-btn.active {
  background: rgba(var(--primary-rgb, 99, 102, 241), 0.15);
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.gcode-simulator-container {
  width: 100%;
  height: 100%;
  background: #111;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.gcode-simulator-container canvas {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.gcode-large-view {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #111;
}

.img-box {
  flex: 1;
  min-height: 220px;
  max-height: 300px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0.75rem;
  overflow: hidden;
  position: relative;
}

.img-box.empty {
  color: var(--text-secondary);
  text-align: center;
  gap: 0.5rem;
  cursor: pointer;
}

.drop-icon {
  font-size: 2.5rem;
  opacity: 0.35;
  margin-bottom: 0.5rem;
}

.fmt-badges {
  display: flex;
  gap: 0.3rem;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 0.5rem;
}

.badge {
  background: var(--glass-bg-secondary, rgba(255,255,255,0.07));
  border: 1px solid var(--glass-border);
  border-radius: 4px;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 2px 6px;
  letter-spacing: 0.04em;
  color: var(--text-secondary);
}

.preview-img {
  max-width: 100%;
  max-height: 260px;
  object-fit: contain;
  border-radius: 4px;
}

.preview-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  opacity: 0.5;
  color: var(--text-secondary);
}

.img-meta {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
  color: var(--text-secondary);
  border-top: 1px solid var(--glass-border);
}

.svg-stats { gap: 0.5rem; }
.svg-stats span { display: flex; flex-direction: column; align-items: center; }
.stat-num { color: #4ade80; font-weight: 700; font-size: 1rem; }

.btn-download-svg {
  margin: 0 1rem 0.75rem;
  padding: 0.5rem;
  background: transparent;
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
  letter-spacing: 0.05em;
  transition: all 0.2s;
}

.btn-download-svg:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.spinner-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid var(--glass-border);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.svg-holder {
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: white;
  border-radius: 6px;
  cursor: grab;
  position: relative;
}

.svg-holder:active { cursor: grabbing; }

.svg-render-scale {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  transform-origin: 0 0;
  transition: transform 0.05s linear;
}

.svg-render-scale :deep(svg) {
  max-width: 100%;
  max-height: 100%;
  display: block;
}

/* Zoom Controls */
.zoom-controls {
  position: absolute;
  right: 0.75rem;
  bottom: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  z-index: 100;
}

.zoom-btn {
  width: 32px;
  height: 32px;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  transition: all 0.2s;
}

.zoom-btn:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.zoom-level {
  background: rgba(0,0,0,0.4);
  color: white;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  text-align: center;
}

.gcode-box {
  background: rgba(0,0,0,0.25);
  justify-content: flex-start;
}

.gcode-text {
  width: 100%;
  height: 100%;
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  font-size: 0.7rem;
  color: #a3e635;
  line-height: 1.5;
  overflow: auto;
  white-space: pre;
  margin: 0;
  padding: 0.5rem;
}

.gcode-meta {
  align-items: center;
}

.gcode-stats {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.time-estimate {
  color: #60a5fa;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.time-estimate i {
  font-size: 0.8rem;
}

.gcode-actions {
  display: flex;
  gap: 0.4rem;
}

.btn-icon {
  background: var(--glass-bg-secondary, rgba(255,255,255,0.07));
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-secondary);
  width: 30px;
  height: 30px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
}

.btn-icon:hover { color: var(--primary-color); border-color: var(--primary-color); }

/* Settings Row */
.settings-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  padding: 10px;
}

.gcode-generator-disabled {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 100px);
  padding: 2rem;
}

.disabled-message {
  text-align: center;
  padding: 3rem;
  max-width: 600px;
  border-radius: 1rem;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
}

.disabled-message h2 {
  font-size: 2rem;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.disabled-message p {
  color: var(--text-secondary);
  line-height: 1.6;
  font-size: 1.1rem;
}

@media (max-width: 1024px) {
  .preview-row, .settings-row {
    flex-direction: column;
  }
}

.settings-card {
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.settings-header {
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--glass-border);
  padding-bottom: 0.6rem;
  margin-bottom: 0.25rem;
}

.setting-section-title {
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #4ade80;
  margin-top: 0.25rem;
}

.generate-btn {
  width: 100%;
  padding: 0.75rem;
  background: #22c55e;
  border: none;
  border-radius: 8px;
  color: white;
  font-weight: 800;
  font-size: 0.9rem;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.generate-btn:hover:not(:disabled) { filter: brightness(1.1); }
.generate-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.gcode-gen-btn { background: var(--primary-color); }

/* Presets */
.preset-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}

.preset-btn {
  display: flex;
  flex-direction: column;
  padding: 0.6rem 0.75rem;
  border: 1px solid var(--glass-border);
  border-radius: 8px;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
}

.preset-btn:hover {
  border-color: var(--primary-color);
  background: rgba(var(--primary-rgb, 99, 102, 241), 0.08);
}

.preset-btn.active {
  border-color: #22c55e;
  background: rgba(34, 197, 94, 0.1);
  color: var(--text-primary);
}

.preset-name {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text-primary);
}

.preset-desc {
  font-size: 0.68rem;
  line-height: 1.3;
  margin-top: 0.2rem;
  color: var(--text-secondary);
}

/* Sliders & Settings */
.setting-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.setting-group.mt-1 { margin-top: 0.25rem; }
.setting-group.mt-2 { margin-top: 0.5rem; }
.mb-2 { margin-bottom: 0.5rem; }

.setting-label {
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-secondary);
}

.slider-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.slider-val {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--primary-color);
}

.slider {
  width: 100%;
  accent-color: #22c55e;
  cursor: pointer;
}

.setting-select,
.setting-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  background: var(--glass-bg-secondary, rgba(255,255,255,0.05));
  border: 1px solid var(--glass-border);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 0.85rem;
  box-sizing: border-box;
}

.setting-select:focus, .setting-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

/* Checkboxes */
.check-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.check-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.82rem;
  color: var(--text-secondary);
}

.check-item input[type="checkbox"] {
  accent-color: #22c55e;
  width: 14px;
  height: 14px;
}

/* Toggle Group */
.toggle-group {
  display: flex;
  gap: 0.5rem;
}

.toggle-btn {
  flex: 1;
  padding: 0.5rem;
  border-radius: 6px;
  border: 1px solid var(--glass-border);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.78rem;
  font-weight: 600;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
}

.toggle-btn.active {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

/* Save to Drive */
.save-drive-area {
  border-top: 1px solid var(--glass-border);
  padding-top: 0.85rem;
  margin-top: 0.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.save-hint {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.save-hint code {
  color: var(--primary-color);
  background: rgba(var(--primary-rgb, 99,102,241), 0.12);
  padding: 1px 5px;
  border-radius: 4px;
}

.save-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.save-input { flex: 1; }

.ext {
  font-weight: 700;
  color: var(--text-secondary);
  font-size: 0.85rem;
  white-space: nowrap;
}

.btn-save {
  padding: 0.5rem 1rem;
  background: var(--primary-color);
  border: none;
  border-radius: 6px;
  color: white;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-save:hover:not(:disabled) { filter: brightness(1.15); }
.btn-save:disabled { opacity: 0.45; cursor: not-allowed; }

.save-ok { color: #4ade80; font-size: 0.82rem; margin: 0; }
.save-err { color: #f87171; font-size: 0.82rem; margin: 0; }

/* Toast */
.toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  padding: 0.8rem 1.5rem;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.9rem;
  z-index: 9999;
  animation: slideIn 0.3s ease;
  box-shadow: 0 8px 32px rgba(0,0,0,0.35);
}

.toast.success { background: #22c55e; color: white; }
.toast.error { background: #ef4444; color: white; }

@keyframes slideIn {
  from { transform: translateY(14px); opacity: 0; }
  to   { transform: translateY(0); opacity: 1; }
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0,0,0,0.85);
  backdrop-filter: blur(8px);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.full-preview-modal {
  width: 100%;
  max-width: 1200px;
  height: 90vh;
  display: flex;
  flex-direction: column;
  background: var(--glass-bg-primary);
  border: 1px solid var(--glass-border);
  box-shadow: 0 24px 64px rgba(0,0,0,0.5);
  overflow: hidden;
}

.modal-header {
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--glass-border);
}

.modal-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 800;
  color: #4ade80;
  letter-spacing: 0.05em;
}

.close-btn {
  background: transparent;
  border: 1px solid var(--glass-border);
  color: var(--text-secondary);
  width: 34px;
  height: 34px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
}

.close-btn:hover {
  background: #ef4444;
  color: white;
  border-color: #ef4444;
}

.modal-body {
  flex: 1;
  overflow: hidden;
  display: flex;
  position: relative;
}

.simulator-body {
  padding: 0;
  background: #000;
}

.fullscreen-svg-holder {
  width: 100%;
  height: 100%;
  border-radius: 0;
}

.modal-footer {
  padding: 1rem;
  display: flex;
  justify-content: center;
  border-top: 1px solid var(--glass-border);
}

.static-zoom {
  position: static;
  flex-direction: row;
  align-items: center;
  background: rgba(255,255,255,0.05);
  padding: 0.5rem 1rem;
  border-radius: 12px;
}
</style>