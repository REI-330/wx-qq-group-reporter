<template>
  <div class="v-report-tab-content">
    <div v-if="step === 1" class="v-report-card">
      <div class="v-report-header-box">
        <h2 class="v-report-main-title">微信群年度报告分析器</h2>
        <p class="v-report-desc-text">
          上传
          <a href="https://github.com/shuakami/qq-chat-exporter" target="_blank" class="v-report-link">chatlog</a>
          导出的 JSON，生成您的专属年度回忆。
        </p>
      </div>

      <div class="v-report-card v-report-sub-card">
        <h3 class="v-report-sub-title">🗓️ 时间范围设置</h3>
        <div class="v-report-time-range-group">
          <div class="v-report-time-field">
            <label class="v-report-label">起始日期</label>
            <input type="date" v-model="startDate" class="v-report-date-input" />
          </div>
          <div class="v-report-time-field">
            <label class="v-report-label">结束日期</label>
            <input type="date" v-model="endDate" class="v-report-date-input" />
          </div>
        </div>
        <p class="v-report-hint">💡 建议选择一整年以获得最精准的分析结果</p>
      </div>

      <div class="v-report-card v-report-sub-card">
        <label class="v-report-toggle-row">
          <input type="checkbox" v-model="useStopwords" class="v-report-checkbox" />
          <div class="v-report-toggle-info">
            <strong class="v-report-strong">使用智能停用词库</strong>
            <p class="v-report-small-text">自动屏蔽“的”、“了”、“哈”等无意义词汇</p>
          </div>
        </label>
      </div>

      <div class="v-report-card v-report-sub-card">
        <h3 class="v-report-sub-title">🤖 选词模式</h3>
        <div class="v-report-mode-grid">
          <label class="v-report-mode-item">
            <input type="radio" v-model="autoSelect" :value="false" class="v-report-radio" />
            <div class="v-report-mode-body">
              <strong class="v-report-strong">🎯 手动选词</strong>
              <p class="v-report-tiny-text">从词云中亲手挑选 10 个词</p>
            </div>
          </label>
          <label class="v-report-mode-item">
            <input type="radio" v-model="autoSelect" :value="true" class="v-report-radio" />
            <div class="v-report-mode-body">
              <strong class="v-report-strong">{{ aiFeatures.ai_word_selection_enabled ? '🤖 AI 语义分析' : '📋 词频 Top 10'
                }}</strong>
              <p class="v-report-tiny-text">{{ aiFeatures.ai_word_selection_enabled ? '基于大模型深度分析' : '按聊天热度自动排序' }}</p>
            </div>
          </label>
        </div>
      </div>

      <div class="v-report-action-area">
        <div class="v-report-file-wrapper">
          <input type="file" accept=".json" @change="onFileChange" id="v-report-file-input"
            class="v-report-hidden-input" />
          <label for="v-report-file-input" class="v-report-file-label">
            {{ file ? '📄 ' + file.name : '📎 点击选取聊天记录 JSON' }}
          </label>
        </div>
        <button class="v-report-btn-primary v-report-btn-main" :disabled="loading || !file" @click="uploadAndAnalyze">
          {{ loading ? '⏳ 正在拼命分析中...' : '开始分析我的年度报告' }}
        </button>
      </div>

      <div v-if="loading" class="v-report-loading-status">
        <div class="v-report-spinner"></div>
        <p class="v-report-loading-msg">{{ loadingMessage }}</p>
      </div>
    </div>

    <div v-if="step === 2" class="v-report-card">
      <div class="v-report-sticky-header">
        <h2 class="v-report-main-title">选择年度关键词</h2>
        <div class="v-report-badge-container">
          <div class="v-report-badge">群聊：{{ currentReport.chat_name }}</div>
          <div class="v-report-badge">已选：{{ selectedWords.length }} / 10</div>
        </div>
      </div>

      <div class="v-report-word-grid">
        <div v-for="word in paginatedWords" :key="word.word"
          :class="['v-report-word-item', { 'v-report-is-selected': isWordSelected(word.word) }]"
          @click="toggleWord(word.word)">
          <div class="v-report-word-header">
            <div class="v-report-word-info">
              <span class="v-report-word-name">{{ word.word }}</span>
              <span class="v-report-word-count">{{ word.freq }} 次</span>
            </div>
            <div class="v-report-word-check">
              {{ isWordSelected(word.word) ? '✓' : '选择' }}
            </div>
          </div>

          <div class="v-report-word-footer">
            <strong class="v-report-strong">🏆 领跑者：</strong>
            <span>{{ word.contributors[0]?.name }} ({{ word.contributors[0]?.count }}次)</span>
          </div>
        </div>
      </div>

      <div v-if="currentReport.available_words?.length > wordsPerPage" class="v-report-pagination">
        <button class="v-report-page-btn" :disabled="currentWordPage <= 1" @click="currentWordPage--">←</button>
        <span class="v-report-page-info">第 {{ currentWordPage }} / {{ totalWordPages }} 页</span>
        <button class="v-report-page-btn" :disabled="currentWordPage >= totalWordPages"
          @click="currentWordPage++">→</button>
      </div>

      <div class="v-report-footer-actions">
        <button class="v-report-btn-text" @click="backToStep1">重新上传文件</button>
        <button :disabled="selectedWords.length !== 10 || loading" class="v-report-btn-primary v-report-btn-full"
          @click="finalizeReport">
          {{ loading ? '生成中...' : '确定，生成年度报告' }}
        </button>
      </div>
    </div>

    <div v-if="step === 3" class="v-report-card v-report-finish-card">
      <div class="v-report-success-icon">✨</div>
      <h2 class="v-report-main-title">报告已就绪</h2>

      <div class="v-report-result-box">
        <p class="v-report-status-text">{{ finalResult.message || '回忆录已生成，请选择模板预览' }}</p>

        <div class="v-report-tmpl-section">
          <p class="v-report-section-label">🎨 展示方案</p>
          <div class="v-report-tmpl-selector">
            <div v-for="tmpl in availableTemplates" :key="tmpl.id"
              :class="['v-report-tmpl-item', { 'v-report-tmpl-selected': selectedTemplate === tmpl.id }]"
              @click="selectedTemplate = tmpl.id">
              {{ tmpl.name }}
            </div>
          </div>
        </div>

        <div class="v-report-url-group">
          <input readonly class="v-report-url-input" :value="templateReportUrl" />
          <div class="v-report-btn-group">
            <button class="v-report-btn-primary"
              @click="$emit('openReport', finalResult.report_id, selectedTemplate)">🔗 预览报告</button>
            <button class="v-report-btn-secondary" @click="$emit('copyUrl', finalResult.report_id, selectedTemplate)">📋
              复制链接</button>
          </div>
        </div>

        <div class="v-report-bottom-nav">
          <button class="v-report-btn-text" @click="resetFlow">创建下一份</button>
          <button class="v-report-btn-text" @click="$emit('jumpHistory')">查看历史</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'

const props = defineProps({
  aiFeatures: { type: Object, required: true },
  availableTemplates: { type: Array, default: () => [] }
})

const emit = defineEmits(['openReport', 'copyUrl', 'jumpHistory', 'loadingChange'])

const step = ref(1)
const file = ref(null)
const loading = ref(false)
const loadingMessage = ref('')
const startDate = ref('')
const endDate = ref('')
const useStopwords = ref(true)
const autoSelect = ref(false)
const currentReport = ref(null)
const selectedWords = ref([])
const currentWordPage = ref(1)
const wordsPerPage = 10
const finalResult = ref({})
const selectedTemplate = ref('classic')

const paginatedWords = computed(() => {
  if (!currentReport.value?.available_words) return []
  const start = (currentWordPage.value - 1) * wordsPerPage
  return currentReport.value.available_words.slice(start, start + wordsPerPage)
})
const totalWordPages = computed(() => Math.ceil((currentReport.value?.available_words?.length || 0) / wordsPerPage))
const templateReportUrl = computed(() => {
  if (!finalResult.value.report_id) return ''
  return `${window.location.origin}/report/${selectedTemplate.value}/${finalResult.value.report_id}`
})

function onFileChange(e) {
  const [f] = e.target.files || []
  file.value = f || null
}

async function uploadAndAnalyze() {
  if (!file.value) return
  loading.value = true
  emit('loadingChange', true)
  loadingMessage.value = `正在深度扫描数据...`

  try {
    const fd = new FormData()
    fd.append('file', file.value)
    fd.append('auto_select', autoSelect.value ? 'true' : 'false')
    fd.append('use_stopwords', useStopwords.value ? 'true' : 'false')
    if (startDate.value) fd.append('start_date', startDate.value)
    if (endDate.value) fd.append('end_date', endDate.value)

    const { data } = await axios.post('/api/wechat-upload', fd)
    if (autoSelect.value && data.success) {
      finalResult.value = data
      step.value = 3
    } else {
      currentReport.value = data
      selectedWords.value = []
      currentWordPage.value = 1
      step.value = 2
    }
  } catch (e) { alert('分析失败') }
  finally { loading.value = false; emit('loadingChange', false) }
}

function isWordSelected(w) { return selectedWords.value.includes(w) }
function toggleWord(w) {
  const idx = selectedWords.value.indexOf(w)
  if (idx > -1) selectedWords.value.splice(idx, 1)
  else if (selectedWords.value.length < 10) selectedWords.value.push(w)
}

async function finalizeReport() {
  if (selectedWords.value.length !== 10) return
  loading.value = true
  emit('loadingChange', true)
  try {
    const freqMap = {}
    currentReport.value.available_words.forEach(v => (freqMap[v.word] = v.freq))
    const sorted = [...selectedWords.value].sort((a, b) => (freqMap[b] || 0) - (freqMap[a] || 0))
    const { data } = await axios.post('/api/finalize', {
      report_id: currentReport.value.report_id,
      selected_words: sorted,
      oss_key: currentReport.value.oss_key
    })
    finalResult.value = data
    step.value = 3
  } catch (e) { alert('生成失败') }
  finally { loading.value = false; emit('loadingChange', false) }
}

function backToStep1() { file.value = null; step.value = 1 }
function resetFlow() {
  file.value = null; currentReport.value = null; selectedWords.value = []
  finalResult.value = {}; step.value = 1; currentWordPage.value = 1
}
</script>

<style scoped>
/* ========== 样式命名空间隔离 (v-report-) ========== */
.v-report-tab-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 15px;
  color: #FFFFFF;
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif;
}

.v-report-card {
  background: #191919;
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 20px;
  border: 1px solid #2c2c2c;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.v-report-sub-card {
  background: #232323;
  padding: 20px;
  border-radius: 16px;
  border: none;
}

.v-report-main-title {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #07c160;
}

.v-report-sub-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #eee;
}

.v-report-desc-text {
  font-size: 14px;
  color: #888;
  line-height: 1.5;
}

.v-report-link {
  color: #07c160;
  text-decoration: none;
}

/* ========== 表单元素 ========== */
.v-report-time-range-group {
  display: flex;
  gap: 12px;
  margin: 15px 0;
}

.v-report-time-field {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.v-report-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 6px;
}

.v-report-date-input {
  background: #2c2c2c;
  border: 1px solid #333;
  border-radius: 10px;
  padding: 10px;
  color: white;
  color-scheme: dark;
}

/* Checkbox 微信绿 */
.v-report-checkbox {
  accent-color: #07c160;
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.v-report-toggle-row {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.v-report-strong {
  font-size: 15px;
  display: block;
  color: #eee;
}

.v-report-small-text {
  font-size: 12px;
  color: #666;
  margin-top: 2px;
}

/* Radio 微信绿 */
.v-report-mode-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 15px;
}

.v-report-mode-item {
  background: #2c2c2c;
  padding: 16px;
  border-radius: 15px;
  border: 2px solid transparent;
  cursor: pointer;
  display: flex;
  transition: all 0.2s ease;
}

/* 选中状态隔离样式 */
.v-report-mode-item:has(.v-report-radio:checked) {
  border-color: #07c160;
  background: rgba(7, 193, 96, 0.1);
}

.v-report-radio {
  margin-right: 10px;
  accent-color: #07c160;
}

.v-report-tiny-text {
  font-size: 11px;
  color: #666;
  margin: 0;
}

/* ========== 上传区域 ========== */
.v-report-action-area {
  margin-top: 30px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.v-report-hidden-input {
  display: none;
}

.v-report-file-label {
  display: block;
  padding: 20px;
  border: 2px dashed #333;
  border-radius: 20px;
  text-align: center;
  color: #07c160;
  cursor: pointer;
  background: #232323;
}

.v-report-btn-main {
  width: 100%;
  padding: 16px;
  border-radius: 30px;
  font-size: 16px;
  font-weight: bold;
  border: none;
  transition: transform 0.2s;
  cursor: pointer;
}

.v-report-btn-main:active {
  transform: scale(0.97);
}

.v-report-btn-primary {
  background: #07c160;
  color: white;
}

.v-report-btn-primary:disabled {
  background: #333;
  color: #555;
}

/* ========== 选词界面 ========== */
.v-report-badge-container {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.v-report-badge {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  background: #2c2c2c;
  border: 1px solid #444;
}

.v-report-word-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin: 20px 0;
}

.v-report-word-item {
  background: #232323;
  padding: 16px;
  border-radius: 16px;
  border: 1px solid #333;
  cursor: pointer;
}

.v-report-word-item.v-report-is-selected {
  border-color: #07c160;
  background: rgba(7, 193, 96, 0.1);
}

.v-report-word-check {
  float: right;
  color: #07c160;
  font-weight: bold;
}

.v-report-word-footer {
  margin-top: 10px;
  font-size: 11px;
  color: #888;
  border-top: 1px solid #333;
  padding-top: 8px;
}

.v-report-pagination {
  display: flex;
  justify-content: center;
  gap: 20px;
  align-items: center;
  color: #666;
}

.v-report-page-btn {
  background: none;
  border: none;
  color: #888;
  cursor: pointer;
  font-size: 18px;
}

/* ========== 完成页 ========== */
.v-report-finish-card {
  text-align: center;
}

.v-report-success-icon {
  font-size: 60px;
  margin-bottom: 20px;
  color: #07c160;
}

.v-report-tmpl-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
  justify-content: center;
}

.v-report-tmpl-item {
  padding: 8px 18px;
  background: #2c2c2c;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  border: 1px solid #444;
}

.v-report-tmpl-selected {
  background: #07c160;
  color: white;
  border-color: #07c160;
}

.v-report-url-input {
  width: 100%;
  background: #111;
  border: 1px solid #333;
  padding: 14px;
  border-radius: 12px;
  color: #07c160;
  font-family: monospace;
  margin: 15px 0;
}

.v-report-btn-group {
  display: flex;
  gap: 12px;
}

.v-report-btn-group button {
  flex: 1;
  padding: 12px;
  border-radius: 25px;
  border: none;
  cursor: pointer;
}

.v-report-btn-secondary {
  background: #333;
  color: #eee;
}

.v-report-bottom-nav {
  margin-top: 30px;
  display: flex;
  justify-content: center;
  gap: 40px;
}

.v-report-btn-text {
  background: none;
  color: #666;
  text-decoration: underline;
  font-size: 14px;
  border: none;
  cursor: pointer;
}

/* 动画 */
.v-report-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(7, 193, 96, 0.1);
  border-top-color: #07c160;
  border-radius: 50%;
  animation: v-report-spin 0.8s linear infinite;
  margin: 0 auto 15px;
}

@keyframes v-report-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>