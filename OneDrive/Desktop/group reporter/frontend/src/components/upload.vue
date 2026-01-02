<template>
  <div class="v-report-tab-content">
    <div v-if="step === 1" class="v-report-card">
      <div class="v-report-header-box">
        <h2 class="v-report-main-title">QQ群年度报告分析器</h2>
        <p class="v-report-desc-text">
          上传
          <a href="https://github.com/shuakami/qq-chat-exporter" target="_blank" class="v-report-link">qq-chat-exporter</a>
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

    <div v-if="step === 2" class="v-report-step2-container">
      <div class="v-report-sticky-header">
        <h2 class="v-report-main-title">选择年度关键词</h2>
        <div class="v-report-badge-container">
          <div class="v-report-badge">📍 {{ currentReport.chat_name }}</div>
          <div :class="['v-report-counter', { 'is-full': selectedWords.length === 10 }]">
            已选 {{ selectedWords.length }} / 10
          </div>
        </div>
      </div>

      <div class="v-report-word-grid">
        <div v-for="word in paginatedWords" :key="word.word"
          :class="['v-report-word-card', { 'v-report-is-selected': isWordSelected(word.word) }]"
          @click="toggleWord(word.word)">
          <div class="v-report-word-main">
            <span class="v-report-word-text">{{ word.word }}</span>
            <span class="v-report-word-freq">{{ word.freq }}次</span>
          </div>
          <div class="v-report-word-details">
            <span class="v-report-contributor">🏆 {{ word.contributors[0]?.name }}</span>
            <div class="v-report-select-dot"></div>
          </div>
        </div>
      </div>

      <div v-if="totalWordPages > 1" class="v-report-pagination">
        <button class="v-report-page-btn" :disabled="currentWordPage <= 1" @click="currentWordPage--">上一页</button>
        <span class="v-report-page-num">{{ currentWordPage }} / {{ totalWordPages }}</span>
        <button class="v-report-page-btn" :disabled="currentWordPage >= totalWordPages" @click="currentWordPage++">下一页</button>
      </div>

      <div class="v-report-floating-actions">
        <button class="v-report-btn-secondary" @click="backToStep1">返回重新上传</button>
        <button :disabled="selectedWords.length !== 10 || loading" class="v-report-btn-main" @click="finalizeReport">
          {{ loading ? '生成中...' : '确认，生成报告' }}
        </button>
      </div>
    </div>

    <div v-if="step === 3" class="v-report-step3-container">
      <div class="v-report-success-header">
        <div class="v-report-success-icon-wrap">
          <span class="v-report-sparkle">✨</span>
        </div>
        <h2 class="v-report-main-title">年度回忆录已生成</h2>
        <p class="v-report-desc-text">属于你们群的 2024 精彩时刻已封装完毕</p>
      </div>

      <div class="v-report-result-card">
        <div class="v-report-tmpl-section">
          <div class="v-report-section-header">
            <span class="v-report-section-dot"></span>
            <span class="v-report-section-title">选择展示模板</span>
          </div>
          <div class="v-report-tmpl-grid">
            <div v-for="tmpl in availableTemplates" :key="tmpl.id"
              :class="['v-report-tmpl-card', { 'active': selectedTemplate === tmpl.id }]"
              @click="selectedTemplate = tmpl.id">
              <div class="v-report-tmpl-preview">🎨</div>
              <span class="v-report-tmpl-name">{{ tmpl.name }}</span>
            </div>
          </div>
        </div>

        <div class="v-report-url-section">
          <div class="v-report-section-header">
            <span class="v-report-section-dot"></span>
            <span class="v-report-section-title">报告链接</span>
          </div>
          <div class="v-report-url-box">
            <input readonly class="v-report-url-display" :value="templateReportUrl" />
            <div class="v-report-btn-row">
              <button class="v-report-btn-main" @click="$emit('openReport', finalResult.report_id, selectedTemplate)">🔗 立即预览</button>
              <button class="v-report-btn-outline" @click="$emit('copyUrl', finalResult.report_id, selectedTemplate)">📋 复制</button>
            </div>
          </div>
        </div>

        <div class="v-report-nav-footer">
          <button class="v-report-btn-ghost" @click="resetFlow">创建下一份报告</button>
          <button class="v-report-btn-ghost" @click="$emit('jumpHistory')">查看历史记录</button>
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
const wordsPerPage = 12 // 改为12，在网格中更整齐
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

    const { data } = await axios.post('/api/upload', fd)
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
/* ========== 全局变量 ========== */
.v-report-tab-content {
  --qq-blue: #0099FF;
  --qq-blue-hover: #0088EE;
  --qq-blue-light: #F0F9FF;
  --qq-bg: #F2F5F8;
  --card-bg: #FFFFFF;
  --text-main: #333333;
  --text-sub: #888888;
  --border-color: #E0E6ED;
  --success-color: #07C160;

  max-width: 800px;
  margin: 0 auto;
  padding: 15px;
  background: var(--qq-bg);
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif;
  color: var(--text-main);
}

/* ========== 通用组件样式 ========== */
.v-report-card {
  background: var(--card-bg);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 4px 15px rgba(0, 153, 255, 0.05);
}

.v-report-sub-card {
  background: #F8FAFC;
  padding: 20px;
  border-radius: 16px;
  border: 1px solid var(--border-color);
}

.v-report-main-title { font-size: 22px; font-weight: 700; margin-bottom: 8px; color: #000; }
.v-report-sub-title { font-size: 16px; font-weight: 600; margin-bottom: 12px; color: #444; }
.v-report-desc-text { font-size: 14px; color: var(--text-sub); line-height: 1.5; }

/* ========== Step 1 特有样式 ========== */
.v-report-time-range-group { display: flex; gap: 12px; margin: 15px 0; }
.v-report-time-field { flex: 1; display: flex; flex-direction: column; }
.v-report-label { font-size: 12px; color: var(--text-sub); margin-bottom: 6px; }
.v-report-date-input { background: #fff; border: 1px solid var(--border-color); border-radius: 10px; padding: 10px; }
.v-report-mode-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 15px; }
.v-report-mode-item { background: #fff; padding: 16px; border-radius: 15px; border: 2px solid var(--border-color); cursor: pointer; display: flex; }
.v-report-mode-item:has(.v-report-radio:checked) { border-color: var(--qq-blue); background: var(--qq-blue-light); }
.v-report-btn-main { width: 100%; padding: 16px; border-radius: 30px; font-size: 16px; font-weight: bold; border: none; cursor: pointer; background: var(--qq-blue); color: #fff; }
.v-report-btn-main:disabled { background: #D0DDE9; cursor: not-allowed; }

/* ========== Step 2: 选词界面 (重构) ========== */
.v-report-step2-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.v-report-sticky-header {
  position: sticky;
  top: 0;
  z-index: 10;
  background: var(--card-bg);
  padding: 20px;
  border-radius: 0 0 20px 20px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

.v-report-badge-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.v-report-counter {
  font-weight: bold;
  color: var(--text-sub);
  font-size: 14px;
}
.v-report-counter.is-full { color: var(--qq-blue); }

.v-report-word-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
  padding: 0 5px;
}

.v-report-file-label {
  display: block;
  padding: 20px;
  border: 2px dashed var(--border-color);
  border-radius: 20px;
  text-align: center;
  color: var(--qq-blue);
  cursor: pointer;
  background: #FFFFFF;
  transition: background 0.2s;
}

.v-report-word-card {
  background: #fff;
  border-radius: 16px;
  padding: 15px;
  border: 1px solid var(--border-color);
  transition: all 0.2s;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.v-report-word-card:hover { border-color: var(--qq-blue); transform: translateY(-2px); }

.v-report-word-card.v-report-is-selected {
  background: var(--qq-blue-light);
  border-color: var(--qq-blue);
}

.v-report-word-main {
  display: flex;
  flex-direction: column;
  margin-bottom: 10px;
}

.v-report-word-text { font-size: 16px; font-weight: 600; color: #000; }
.v-report-word-freq { font-size: 12px; color: var(--text-sub); }

.v-report-word-details {
  border-top: 1px solid #f0f0f0;
  padding-top: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  color: var(--text-sub);
}

.v-report-select-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 1px solid var(--border-color);
}
.v-report-is-selected .v-report-select-dot {
  background: var(--qq-blue);
  border-color: var(--qq-blue);
}

.v-report-pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin: 10px 0;
}
.v-report-page-btn { padding: 8px 16px; border-radius: 20px; border: 1px solid var(--border-color); background: #fff; cursor: pointer; }

.v-report-floating-actions {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 12px;
  padding: 20px;
  background: #fff;
  border-radius: 20px;
}

/* ========== Step 3: 完成界面 (重构) ========== */
.v-report-step3-container {
  text-align: center;
  animation: fadeIn 0.5s ease-out;
}

.v-report-success-header {
  padding: 40px 0 30px;
}

.v-report-success-icon-wrap {
  width: 80px;
  height: 80px;
  background: var(--qq-blue-light);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}
.v-report-sparkle { font-size: 40px; }

.v-report-result-card {
  background: #fff;
  border-radius: 24px;
  padding: 24px;
  text-align: left;
}

.v-report-section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}
.v-report-section-dot { width: 4px; height: 16px; background: var(--qq-blue); border-radius: 2px; }
.v-report-section-title { font-weight: bold; font-size: 15px; }

.v-report-tmpl-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 30px;
}

.v-report-tmpl-card {
  border: 2px solid #f0f0f0;
  border-radius: 12px;
  padding: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}
.v-report-tmpl-card.active { border-color: var(--qq-blue); background: var(--qq-blue-light); }
.v-report-tmpl-preview { font-size: 24px; margin-bottom: 4px; }
.v-report-tmpl-name { font-size: 12px; font-weight: 500; }

.v-report-url-box {
  background: #F8FAFC;
  border-radius: 16px;
  padding: 16px;
  border: 1px dashed var(--border-color);
}

.v-report-url-display {
  width: 100%;
  border: none;
  background: transparent;
  color: var(--qq-blue);
  text-align: center;
  padding: 10px;
  font-size: 13px;
  margin-bottom: 16px;
  word-break: break-all;
}

.v-report-btn-row {
  display: grid;
  grid-template-columns: 1fr 80px;
  gap: 10px;
}

.v-report-btn-outline {
  border: 1px solid var(--qq-blue);
  background: transparent;
  color: var(--qq-blue);
  border-radius: 30px;
  cursor: pointer;
  font-weight: 500;
}

.v-report-nav-footer {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 30px;
}

.v-report-btn-ghost {
  background: transparent;
  border: none;
  color: var(--text-sub);
  font-size: 14px;
  cursor: pointer;
  padding: 8px;
}
.v-report-btn-ghost:hover { color: var(--qq-blue); }

.v-report-btn-secondary {
  border: 1px solid var(--border-color);
  background: #fff;
  border-radius: 30px;
  cursor: pointer;
}

/* ========== 辅助样式 ========== */
.v-report-hidden-input { display: none; }
.v-report-spinner { width: 32px; height: 32px; border: 3px solid var(--qq-blue-light); border-top-color: var(--qq-blue); border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 15px; }

@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 600px) {
  .v-report-word-grid { grid-template-columns: 1fr 1fr; }
  .v-report-tmpl-grid { grid-template-columns: 1fr 1fr 1fr; }
}
</style>