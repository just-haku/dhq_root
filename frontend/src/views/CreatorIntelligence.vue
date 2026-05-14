<template>
  <div class="ci-page">
    <header class="ci-header">
      <div>
        <p class="eyebrow">Creator Intelligence</p>
        <h1>Digital Creator Research</h1>
      </div>
      <div class="header-actions">
        <button class="icon-btn" title="Refresh" @click="refreshAll" :disabled="loading">
          <i class="fas fa-sync-alt" :class="{ spinning: loading }"></i>
        </button>
        <button class="primary-btn" @click="enqueueDefaultJob">
          <i class="fas fa-play"></i>
          Queue Analysis
        </button>
      </div>
    </header>

    <section class="metric-grid">
      <div class="metric-tile">
        <span>Workers</span>
        <strong>{{ overview.workers?.online || 0 }}/{{ overview.workers?.total || 0 }}</strong>
      </div>
      <div class="metric-tile">
        <span>Queued</span>
        <strong>{{ overview.queues?.jobs?.queued || 0 }}</strong>
      </div>
      <div class="metric-tile">
        <span>Creators</span>
        <strong>{{ overview.creators || 0 }}</strong>
      </div>
      <div class="metric-tile" :class="{ muted: !overview.qdrant?.healthy }">
        <span>Qdrant</span>
        <strong>{{ overview.qdrant?.healthy ? 'Healthy' : 'Offline' }}</strong>
      </div>
    </section>

    <nav class="module-tabs" aria-label="Creator Intelligence modules">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        type="button"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        <i :class="tab.icon"></i>
        <span>{{ tab.label }}</span>
      </button>
    </nav>

    <section v-if="activeTab === 'dashboard'" class="ci-section">
      <div class="section-title">
        <h2>Creator Dashboard</h2>
        <span>{{ creators.length }} tracked</span>
      </div>
      <div class="creator-grid">
        <article v-for="creator in creators" :key="creator.id" class="creator-row">
          <div>
            <strong>@{{ creator.handle }}</strong>
            <span>{{ creator.platform }} / {{ creator.creator_type }}</span>
          </div>
          <div class="tag-row">
            <small v-for="tag in creator.tags" :key="tag">{{ tag }}</small>
          </div>
        </article>
        <p v-if="creators.length === 0" class="empty-state">No creators tracked yet.</p>
      </div>
    </section>

    <section v-if="activeTab === 'video'" class="ci-section">
      <div class="section-title">
        <h2>Video Explorer</h2>
        <span>{{ jobs.length }} recent jobs</span>
      </div>
      <div class="job-list">
        <article v-for="job in jobs" :key="job.job_id" class="job-row">
          <div>
            <strong>{{ job.job_type }}</strong>
            <span>{{ job.job_id }}</span>
          </div>
          <span class="status-pill" :class="job.status">{{ job.status }}</span>
          <button class="icon-btn" title="Cancel" @click="cancelJob(job.job_id)" :disabled="!['queued', 'running'].includes(job.status)">
            <i class="fas fa-ban"></i>
          </button>
        </article>
      </div>
    </section>

    <section v-if="activeTab === 'competitors'" class="ci-section split">
      <div>
        <div class="section-title">
          <h2>Competitor Intelligence</h2>
          <span>Low priority</span>
        </div>
        <JobComposer
          job-type="compare_competitor"
          priority="low"
          :toggles="analysisToggles"
          @submit="enqueueJob"
        />
      </div>
      <MemoryPanel :memory="memory" namespace-prefix="competitor:" />
    </section>

    <section v-if="activeTab === 'trends'" class="ci-section split">
      <div>
        <div class="section-title">
          <h2>Trend Radar</h2>
          <span>Namespaces</span>
        </div>
        <JobComposer job-type="trend_scan" priority="low" :toggles="analysisToggles" @submit="enqueueJob" />
      </div>
      <MemoryPanel :memory="memory" namespace-prefix="trend:" />
    </section>

    <section v-if="activeTab === 'draft'" class="ci-section">
      <div class="section-title">
        <h2>Draft Critic</h2>
        <span>High priority</span>
      </div>
      <JobComposer job-type="draft_critique" priority="high" :toggles="analysisToggles" @submit="enqueueJob" />
    </section>

    <section v-if="activeTab === 'chat'" class="ci-section">
      <div class="section-title">
        <h2>AI Chat with Gemma</h2>
        <span>Typed actions only</span>
      </div>
      <textarea v-model="chatPrompt" rows="5" placeholder="Analyze this creator, compare hooks, or request a supervised scrape."></textarea>
      <button class="primary-btn" @click="enqueueChatJob">
        <i class="fas fa-brain"></i>
        Route Request
      </button>
    </section>

    <section v-if="activeTab === 'strategy'" class="ci-section">
      <div class="section-title">
        <h2>Strategy Planner</h2>
        <span>External model route optional</span>
      </div>
      <JobComposer job-type="strategic_synthesis" priority="normal" :toggles="analysisToggles" @submit="enqueueJob" />
    </section>

    <section v-if="activeTab === 'ontology'" class="ci-section">
      <div class="section-title">
        <h2>Ontology Registry</h2>
        <span>{{ ontologyRegistries.length }} canonical domains</span>
      </div>
      <div class="ontology-grid">
        <article v-for="registry in ontologyRegistries" :key="registry.domain" class="ontology-panel">
          <div class="panel-heading">
            <strong>{{ registry.domain.replaceAll('_', ' ') }}</strong>
            <span>{{ registry.label_count }} labels</span>
          </div>
          <div class="label-list">
            <span v-for="label in registry.labels" :key="label.id" class="ontology-label" :title="label.description">
              {{ label.id }}
            </span>
          </div>
        </article>
      </div>
    </section>

    <section v-if="activeTab === 'explainability'" class="ci-section split">
      <div>
        <div class="section-title">
          <h2>Lineage & Evidence</h2>
          <span>Inspectable recommendations</span>
        </div>
        <div class="explain-list">
          <article v-for="job in jobs.slice(0, 8)" :key="`e-${job.job_id}`" class="explain-row">
            <strong>{{ job.job_type }}</strong>
            <span>{{ job.trace_id || job.job_id }}</span>
            <small>{{ evidenceCount(job) }} evidence refs / {{ Object.keys(job.result || {}).length }} result fields</small>
          </article>
        </div>
      </div>
      <div>
        <div class="section-title">
          <h2>Semantic Consensus</h2>
          <span>{{ consensusRecords.length }} records</span>
        </div>
        <div class="explain-list">
          <article v-for="item in consensusRecords" :key="item.consensus_id" class="explain-row">
            <strong>{{ item.resolution }}</strong>
            <span>{{ Math.round((item.agreement_score || 0) * 100) }}% agreement</span>
            <small>{{ (item.disagreements || []).length }} disagreements</small>
          </article>
          <p v-if="consensusRecords.length === 0" class="empty-state">No semantic consensus records yet.</p>
        </div>
      </div>
    </section>

    <section v-if="activeTab === 'feedback'" class="ci-section split">
      <div>
        <div class="section-title">
          <h2>Human Feedback</h2>
          <span>Reinforcement memory boundary</span>
        </div>
        <div class="feedback-form">
          <select v-model="feedbackForm.feedback_type">
            <option value="confirm_recommendation">Confirm recommendation</option>
            <option value="reject_interpretation">Reject interpretation</option>
            <option value="label_resonance">Label resonance</option>
            <option value="performance_mismatch">Performance mismatch</option>
            <option value="manual_override">Manual override</option>
          </select>
          <input v-model="feedbackForm.target_ref.ref_id" placeholder="Target ref id" />
          <label class="check-line">
            Rating
            <input type="range" min="-1" max="1" step="0.1" v-model.number="feedbackForm.rating" />
            <span>{{ feedbackForm.rating.toFixed(1) }}</span>
          </label>
          <textarea v-model="feedbackForm.comment" rows="3" placeholder="Correction, confirmation, or performance note."></textarea>
          <button class="primary-btn" @click="submitFeedback">
            <i class="fas fa-check"></i>
            Record Feedback
          </button>
        </div>
      </div>
      <div class="explain-list">
        <article v-for="event in feedbackEvents" :key="event.event_id" class="explain-row">
          <strong>{{ event.feedback_type.replaceAll('_', ' ') }}</strong>
          <span>{{ event.target_ref?.ref_id }}</span>
          <small>{{ event.comment || 'No comment' }}</small>
        </article>
        <p v-if="feedbackEvents.length === 0" class="empty-state">No feedback events yet.</p>
      </div>
    </section>

    <section v-if="activeTab === 'audience'" class="ci-section">
      <div class="section-title">
        <h2>Audience Psychology</h2>
        <span>Confidence scoped</span>
      </div>
      <ToggleMatrix v-model="analysisToggles" />
    </section>

    <section v-if="activeTab === 'embeddings'" class="ci-section">
      <div class="section-title">
        <h2>Embedding Maps</h2>
        <span>{{ overview.qdrant?.healthy ? 'Vector service ready' : 'Vector service offline' }}</span>
      </div>
      <JobComposer job-type="embed_content" priority="normal" :toggles="analysisToggles" @submit="enqueueJob" />
    </section>

    <section v-if="activeTab === 'hooks'" class="ci-section">
      <div class="section-title">
        <h2>Hook Explorer</h2>
        <span>Taxonomy and similarity</span>
      </div>
      <JobComposer job-type="analyze_video" priority="normal" :toggles="{ ...analysisToggles, hook_explorer: true }" @submit="enqueueJob" />
    </section>

    <section v-if="activeTab === 'memory'" class="ci-section">
      <div class="section-title">
        <h2>Memory Graph</h2>
        <span>{{ memory.length }} records</span>
      </div>
      <MemoryPanel :memory="memory" />
    </section>

    <section v-if="activeTab === 'workers'" class="ci-section">
      <div class="section-title">
        <h2>Worker Management</h2>
        <button class="secondary-btn" @click="createWorkerToken">Create Token</button>
      </div>
      <div v-if="workerToken" class="token-box">{{ workerToken }}</div>
      <div class="data-table">
        <div class="table-head">
          <span>Worker</span>
          <span>Role</span>
          <span>Status</span>
          <span>Capabilities</span>
        </div>
        <div v-for="worker in workers" :key="worker.worker_id" class="table-row">
          <span>{{ worker.worker_name }}</span>
          <span>{{ worker.machine_role }}</span>
          <span class="status-pill" :class="worker.status">{{ worker.status }}</span>
          <span>{{ compactCapabilities(worker.capabilities) }}</span>
        </div>
      </div>
    </section>

    <section v-if="activeTab === 'stability'" class="ci-section split">
      <div>
        <div class="section-title">
          <h2>Resource Pressure</h2>
          <span>{{ pressureSnapshots.length }} snapshots</span>
        </div>
        <div class="explain-list">
          <article v-for="snapshot in pressureSnapshots" :key="snapshot.id" class="pressure-row">
            <div>
              <strong>{{ snapshot.worker_id }}</strong>
              <span>{{ snapshot.thermal_state }}</span>
            </div>
            <meter min="0" max="1" :value="snapshot.gpu_pressure || 0"></meter>
            <small>{{ snapshot.scheduling?.reason || 'unclassified' }}</small>
          </article>
          <p v-if="pressureSnapshots.length === 0" class="empty-state">No resource pressure snapshots yet.</p>
        </div>
      </div>
      <div>
        <div class="section-title">
          <h2>Default Policies</h2>
          <span>Deterministic guardrails</span>
        </div>
        <div class="policy-grid">
          <div class="metric-tile">
            <span>High confidence</span>
            <strong>{{ formatPercent(policyDefaults.confidence?.high_confidence_threshold) }}</strong>
          </div>
          <div class="metric-tile">
            <span>Reasoning depth</span>
            <strong>{{ policyDefaults.reasoning_depth?.max_reasoning_depth || 0 }}</strong>
          </div>
          <div class="metric-tile">
            <span>Trend 14d weight</span>
            <strong>{{ formatPercent(policyDefaults.temporal_weights?.trend_14_days) }}</strong>
          </div>
          <div class="metric-tile">
            <span>Identity 14d weight</span>
            <strong>{{ formatPercent(policyDefaults.temporal_weights?.creator_identity_14_days) }}</strong>
          </div>
        </div>
      </div>
    </section>

    <section v-if="activeTab === 'queues'" class="ci-section">
      <div class="section-title">
        <h2>Queue Monitor</h2>
        <span>Redis Streams</span>
      </div>
      <div class="queue-grid">
        <div v-for="(value, key) in queues.streams" :key="key" class="metric-tile">
          <span>{{ key }}</span>
          <strong>{{ value }}</strong>
        </div>
      </div>
    </section>

    <section v-if="activeTab === 'models'" class="ci-section">
      <div class="section-title">
        <h2>Local Model Manager</h2>
        <button class="secondary-btn" @click="scanModels">Scan GGUF</button>
      </div>
      <label class="check-line">
        <input type="checkbox" v-model="validateHashes" />
        Validate hashes
      </label>
      <div class="data-table">
        <div class="table-head">
          <span>Model</span>
          <span>Worker</span>
          <span>Status</span>
          <span>Size</span>
        </div>
        <div v-for="model in models" :key="model.id" class="table-row">
          <span>{{ model.model_name }}</span>
          <span>{{ model.worker_id }}</span>
          <span class="status-pill" :class="model.validation_status">{{ model.validation_status }}</span>
          <span>{{ formatBytes(model.size_bytes) }}</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, defineComponent, h, onMounted, ref } from 'vue'
import { apiGet, apiPost } from '@/utils/api'

const tabs = [
  { key: 'dashboard', label: 'Creator Dashboard', icon: 'fas fa-gauge-high' },
  { key: 'video', label: 'Video Explorer', icon: 'fas fa-film' },
  { key: 'competitors', label: 'Competitor Intelligence', icon: 'fas fa-user-secret' },
  { key: 'trends', label: 'Trend Radar', icon: 'fas fa-signal' },
  { key: 'draft', label: 'Draft Critic', icon: 'fas fa-pen-nib' },
  { key: 'chat', label: 'AI Chat with Gemma', icon: 'fas fa-comments' },
  { key: 'strategy', label: 'Strategy Planner', icon: 'fas fa-chess' },
  { key: 'ontology', label: 'Ontology Registry', icon: 'fas fa-tags' },
  { key: 'explainability', label: 'Explainability', icon: 'fas fa-sitemap' },
  { key: 'feedback', label: 'Human Feedback', icon: 'fas fa-user-check' },
  { key: 'audience', label: 'Audience Psychology', icon: 'fas fa-users-viewfinder' },
  { key: 'embeddings', label: 'Embedding Maps', icon: 'fas fa-project-diagram' },
  { key: 'hooks', label: 'Hook Explorer', icon: 'fas fa-fish-hook' },
  { key: 'memory', label: 'Memory Graph', icon: 'fas fa-diagram-project' },
  { key: 'workers', label: 'Worker Management', icon: 'fas fa-network-wired' },
  { key: 'stability', label: 'Stability Layer', icon: 'fas fa-shield-alt' },
  { key: 'queues', label: 'Queue Monitor', icon: 'fas fa-stream' },
  { key: 'models', label: 'Local Model Manager', icon: 'fas fa-microchip' }
]

const activeTab = ref('dashboard')
const loading = ref(false)
const overview = ref({})
const workers = ref([])
const queues = ref({})
const jobs = ref([])
const models = ref([])
const memory = ref([])
const creators = ref([])
const ontology = ref({})
const feedbackEvents = ref([])
const consensusRecords = ref([])
const pressureSnapshots = ref([])
const policyDefaults = ref({})
const workerToken = ref('')
const validateHashes = ref(false)
const chatPrompt = ref('')
const feedbackForm = ref({
  feedback_type: 'confirm_recommendation',
  target_ref: { ref_type: 'recommendation', ref_id: '' },
  rating: 0,
  comment: ''
})

const ontologyRegistries = computed(() => Object.values(ontology.value || {}))

const analysisToggles = ref({
  ocr_timeline: true,
  emotional_analysis: true,
  visual_fatigue: true,
  competitor_comparison: false,
  audience_psychology: true,
  shot_boundary_detection: true,
  pacing_graph: true,
  embedding_search: true,
  trend_comparison: false,
  draft_critique: false
})

async function refreshAll() {
  loading.value = true
  try {
    const [
      overviewRes,
      workersRes,
      queuesRes,
      jobsRes,
      modelsRes,
      memoryRes,
      creatorsRes,
      ontologyRes,
      feedbackRes,
      consensusRes,
      pressureRes,
      policiesRes
    ] = await Promise.all([
      apiGet('/creator-intelligence/overview'),
      apiGet('/creator-intelligence/workers'),
      apiGet('/creator-intelligence/queues'),
      apiGet('/creator-intelligence/jobs?limit=50'),
      apiGet('/creator-intelligence/models'),
      apiGet('/creator-intelligence/memory?limit=100'),
      apiGet('/creator-intelligence/creators'),
      apiGet('/creator-intelligence/ontology'),
      apiGet('/creator-intelligence/feedback?limit=30'),
      apiGet('/creator-intelligence/consensus?limit=30'),
      apiGet('/creator-intelligence/pressure?limit=30'),
      apiGet('/creator-intelligence/policies/defaults')
    ])
    overview.value = overviewRes
    workers.value = workersRes.workers || []
    queues.value = queuesRes || {}
    jobs.value = jobsRes.jobs || []
    models.value = modelsRes.models || []
    memory.value = memoryRes.memory || []
    creators.value = creatorsRes.creators || []
    ontology.value = ontologyRes.registries || {}
    feedbackEvents.value = feedbackRes.feedback || []
    consensusRecords.value = consensusRes.consensus || []
    pressureSnapshots.value = pressureRes.pressure || []
    policyDefaults.value = policiesRes || {}
  } finally {
    loading.value = false
  }
}

async function enqueueJob(payload) {
  await apiPost('/creator-intelligence/jobs', payload)
  await refreshAll()
}

async function enqueueDefaultJob() {
  await enqueueJob({
    job_type: 'analyze_video',
    priority: 'normal',
    payload: { analysis_toggles: analysisToggles.value },
    capability_requirements: { multimodal: true, gguf_runtime: true }
  })
}

async function enqueueChatJob() {
  await enqueueJob({
    job_type: 'strategic_synthesis',
    priority: 'high',
    payload: {
      prompt: chatPrompt.value,
      analysis_toggles: analysisToggles.value,
      route: 'gemma_first'
    },
    capability_requirements: {}
  })
  chatPrompt.value = ''
}

async function cancelJob(jobId) {
  await apiPost(`/creator-intelligence/jobs/${jobId}/cancel`, {})
  await refreshAll()
}

async function createWorkerToken() {
  const response = await apiPost('/creator-intelligence/workers/register-token', {})
  workerToken.value = response.token
}

async function scanModels() {
  await apiPost('/creator-intelligence/models/scan', {
    roots: [],
    validate_hashes: validateHashes.value
  })
  await refreshAll()
}

async function submitFeedback() {
  if (!feedbackForm.value.target_ref.ref_id) return
  await apiPost('/creator-intelligence/feedback', feedbackForm.value)
  feedbackForm.value = {
    feedback_type: 'confirm_recommendation',
    target_ref: { ref_type: 'recommendation', ref_id: '' },
    rating: 0,
    comment: ''
  }
  await refreshAll()
}

function compactCapabilities(capabilities = {}) {
  return Object.entries(capabilities)
    .filter(([, value]) => value === true)
    .map(([key]) => key)
    .slice(0, 5)
    .join(', ') || 'basic'
}

function formatBytes(value) {
  if (!value) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let size = value
  let index = 0
  while (size >= 1024 && index < units.length - 1) {
    size /= 1024
    index += 1
  }
  return `${size.toFixed(size >= 10 ? 0 : 1)} ${units[index]}`
}

function formatPercent(value) {
  return `${Math.round((value || 0) * 100)}%`
}

function evidenceCount(job) {
  return (job.progress || []).reduce((total, event) => total + (event.evidence || []).length, 0)
}

const ToggleMatrix = defineComponent({
  props: { modelValue: { type: Object, required: true } },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const labels = computed(() => Object.keys(props.modelValue))
    const toggle = (key) => {
      emit('update:modelValue', { ...props.modelValue, [key]: !props.modelValue[key] })
    }
    return () => h('div', { class: 'toggle-grid' }, labels.value.map((key) =>
      h('button', {
        class: ['toggle-chip', props.modelValue[key] ? 'on' : ''],
        onClick: () => toggle(key)
      }, [
        h('i', { class: props.modelValue[key] ? 'fas fa-check-square' : 'far fa-square' }),
        h('span', key.replaceAll('_', ' '))
      ])
    ))
  }
})

const JobComposer = defineComponent({
  props: {
    jobType: { type: String, required: true },
    priority: { type: String, required: true },
    toggles: { type: Object, required: true }
  },
  emits: ['submit'],
  setup(props, { emit }) {
    const target = ref('')
    const platform = ref('tiktok')
    const requireGpu = ref(false)
    const submit = () => {
      emit('submit', {
        job_type: props.jobType,
        priority: props.priority,
        payload: {
          target: target.value,
          platform: platform.value,
          analysis_toggles: props.toggles
        },
        capability_requirements: {
          platform: platform.value,
          gpu: requireGpu.value || undefined,
          multimodal: ['analyze_video', 'draft_critique'].includes(props.jobType) || undefined,
          playwright: props.jobType.includes('scrape') || undefined
        }
      })
      target.value = ''
    }
    return () => h('div', { class: 'job-composer' }, [
      h('input', {
        value: target.value,
        onInput: event => { target.value = event.target.value },
        placeholder: 'Creator handle, content URL, trend namespace, or draft reference'
      }),
      h('select', {
        value: platform.value,
        onChange: event => { platform.value = event.target.value }
      }, [
        h('option', { value: 'tiktok' }, 'TikTok'),
        h('option', { value: 'instagram' }, 'Instagram')
      ]),
      h('label', { class: 'check-line' }, [
        h('input', {
          type: 'checkbox',
          checked: requireGpu.value,
          onChange: event => { requireGpu.value = event.target.checked }
        }),
        ' GPU'
      ]),
      h('button', { class: 'primary-btn', onClick: submit }, [
        h('i', { class: 'fas fa-plus' }),
        ' Queue Job'
      ])
    ])
  }
})

const MemoryPanel = defineComponent({
  props: {
    memory: { type: Array, required: true },
    namespacePrefix: { type: String, default: '' }
  },
  setup(props) {
    const filtered = computed(() => props.namespacePrefix
      ? props.memory.filter(item => item.namespace?.startsWith(props.namespacePrefix))
      : props.memory
    )
    return () => h('div', { class: 'memory-list' }, filtered.value.length
      ? filtered.value.map(item => h('article', { class: 'memory-row', key: item.id }, [
        h('div', [
          h('strong', item.namespace),
          h('p', item.statement)
        ]),
        h('span', { class: ['status-pill', item.validation_status] }, `${Math.round((item.confidence || 0) * 100)}%`)
      ]))
      : [h('p', { class: 'empty-state' }, 'No memory records yet.')]
    )
  }
})

onMounted(refreshAll)
</script>

<style scoped>
.ci-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: clamp(1rem, 2vw, 2rem);
  color: var(--text-primary);
}

.ci-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.eyebrow {
  margin: 0 0 0.25rem;
  color: var(--text-secondary);
  font-size: 0.85rem;
  text-transform: uppercase;
}

h1,
h2 {
  margin: 0;
  letter-spacing: 0;
}

.header-actions,
.section-title,
.job-composer {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.section-title {
  justify-content: space-between;
  margin-bottom: 1rem;
}

.section-title span {
  color: var(--text-secondary);
}

.primary-btn,
.secondary-btn,
.icon-btn,
.module-tabs button,
.toggle-chip {
  border: 1px solid var(--glass-border);
  background: var(--bg-secondary);
  color: var(--text-primary);
  min-height: 42px;
  cursor: pointer;
  transition: transform 0.15s ease, border-color 0.15s ease, background 0.15s ease;
}

.primary-btn,
.secondary-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0 1rem;
  border-radius: 8px;
}

.primary-btn {
  background: #0f766e;
  border-color: #14b8a6;
}

.secondary-btn {
  background: #374151;
}

.icon-btn {
  width: 42px;
  height: 42px;
  border-radius: 8px;
}

.primary-btn:hover,
.secondary-btn:hover,
.icon-btn:hover,
.module-tabs button:hover,
.toggle-chip:hover {
  transform: translateY(-1px);
  border-color: #60a5fa;
}

.metric-grid,
.queue-grid,
.ontology-grid,
.policy-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.75rem;
}

.metric-tile,
.ci-section,
.creator-row,
.job-row,
.memory-row,
.ontology-panel,
.explain-row,
.pressure-row,
.token-box {
  border: 1px solid var(--glass-border);
  background: var(--bg-secondary);
  border-radius: 8px;
}

.metric-tile {
  padding: 1rem;
}

.metric-tile span {
  display: block;
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.metric-tile strong {
  display: block;
  margin-top: 0.35rem;
  font-size: 1.5rem;
}

.metric-tile.muted strong {
  color: #f97316;
}

.module-tabs {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 0.5rem;
}

.module-tabs button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  justify-content: flex-start;
  padding: 0.65rem 0.75rem;
  border-radius: 8px;
  text-align: left;
}

.module-tabs button.active {
  background: #1d4ed8;
  border-color: #60a5fa;
}

.ci-section {
  padding: 1rem;
}

.ci-section.split {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 0.8fr);
  gap: 1rem;
}

.creator-grid,
.job-list,
.memory-list,
.explain-list {
  display: grid;
  gap: 0.75rem;
}

.creator-row,
.job-row,
.memory-row,
.table-row,
.table-head {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
}

.creator-row span,
.job-row span,
.memory-row p {
  color: var(--text-secondary);
}

.memory-row {
  grid-template-columns: minmax(0, 1fr) auto;
}

.memory-row p {
  margin: 0.25rem 0 0;
}

.ontology-grid {
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
}

.ontology-panel,
.explain-row,
.pressure-row,
.feedback-form {
  display: grid;
  gap: 0.65rem;
  padding: 0.75rem;
}

.panel-heading,
.pressure-row > div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.panel-heading span,
.explain-row span,
.explain-row small,
.pressure-row span,
.pressure-row small {
  color: var(--text-secondary);
}

.label-list {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.ontology-label {
  border-radius: 999px;
  padding: 0.25rem 0.5rem;
  background: rgba(20, 184, 166, 0.14);
  color: #99f6e4;
  font-size: 0.78rem;
}

.feedback-form input,
.feedback-form select {
  border: 1px solid var(--glass-border);
  background: var(--bg-primary);
  color: var(--text-primary);
  border-radius: 8px;
  padding: 0.75rem;
}

.pressure-row meter {
  width: 100%;
  height: 0.75rem;
}

.policy-grid {
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.tag-row {
  display: flex;
  gap: 0.35rem;
  flex-wrap: wrap;
}

.tag-row small,
.status-pill {
  border-radius: 999px;
  padding: 0.25rem 0.55rem;
  background: rgba(96, 165, 250, 0.16);
  color: #bfdbfe;
}

.status-pill.running,
.status-pill.online,
.status-pill.validated,
.status-pill.accepted {
  background: rgba(20, 184, 166, 0.18);
  color: #99f6e4;
}

.status-pill.failed,
.status-pill.dead,
.status-pill.offline,
.status-pill.error,
.status-pill.rejected {
  background: rgba(239, 68, 68, 0.18);
  color: #fecaca;
}

.status-pill.queued,
.status-pill.stale,
.status-pill.detected,
.status-pill.quarantined {
  background: rgba(245, 158, 11, 0.18);
  color: #fde68a;
}

.job-composer {
  align-items: stretch;
}

.job-composer input,
.job-composer select,
textarea {
  border: 1px solid var(--glass-border);
  background: var(--bg-primary);
  color: var(--text-primary);
  border-radius: 8px;
  padding: 0.75rem;
}

.job-composer input {
  min-width: min(100%, 420px);
  flex: 1;
}

textarea {
  width: 100%;
  resize: vertical;
  margin-bottom: 0.75rem;
}

.check-line {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  color: var(--text-secondary);
}

.toggle-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 0.5rem;
}

.toggle-chip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  justify-content: flex-start;
  border-radius: 8px;
  padding: 0.7rem 0.8rem;
}

.toggle-chip.on {
  border-color: #14b8a6;
}

.data-table {
  display: grid;
  gap: 0.25rem;
  overflow-x: auto;
}

.table-head,
.table-row {
  grid-template-columns: minmax(160px, 1.3fr) minmax(120px, 0.8fr) minmax(100px, 0.5fr) minmax(160px, 1fr);
  min-width: 680px;
}

.table-head {
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.table-row {
  border-top: 1px solid var(--glass-border);
}

.token-box {
  padding: 0.75rem;
  margin-bottom: 0.75rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  overflow-wrap: anywhere;
}

.empty-state {
  color: var(--text-secondary);
  margin: 0;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 820px) {
  .ci-header,
  .section-title {
    align-items: flex-start;
    flex-direction: column;
  }

  .ci-section.split {
    grid-template-columns: 1fr;
  }

  .creator-row,
  .job-row {
    grid-template-columns: 1fr;
  }
}
</style>
