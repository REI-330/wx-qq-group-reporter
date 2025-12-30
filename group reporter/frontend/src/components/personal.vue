<template>
  <div class="v-personal-container">
    <div class="v-report-tab-content">
      <div v-if="!generated" class="v-report-card">
        <div class="v-report-header">
          <h2 class="v-report-main-title">个人年度报告</h2>
          <p class="v-report-desc-text">上传群聊 JSON 文件，输入要分析的用户名称，生成您的专属年度回忆。</p>
        </div>

        <div class="v-report-sub-card">
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
        </div>

        <div class="v-report-sub-card">
          <label class="v-report-toggle-row">
            <input type="checkbox" v-model="useStopwords" class="v-report-checkbox" />
            <div class="v-report-toggle-info">
              <strong class="v-report-strong">使用智能停用词库</strong>
              <p class="v-report-small-text">自动屏蔽“的”、“了”、“哈”等无意义词汇，使报告更精准。</p>
            </div>
          </label>
        </div>

        <div class="v-report-sub-card">
          <h3 class="v-report-sub-title">👤 用户识别</h3>
          <input type="text" v-model="userName" placeholder="请输入您的群名片（支持模糊匹配）" class="v-report-text-input" />
          <p class="v-report-hint-text">💡 系统会自动匹配该名称在聊天记录中的所有发言。</p>
        </div>

        <div class="v-report-action-area">
          <div class="v-report-file-wrapper">
            <input type="file" accept=".json" @change="onFileChange" id="v-personal-file" class="v-report-hidden-input" />
            <label for="v-personal-file" class="v-report-file-label">
              {{ file ? '📄 ' + file.name : '📎 点击选取聊天记录 JSON' }}
            </label>
          </div>
          <button class="v-report-btn-main" :disabled="loading || !file || !userName" @click="generate">
            {{ loading ? '⏳ 正在拼命分析中...' : '生成我的个人报告' }}
          </button>
        </div>

        <div v-if="error" class="v-report-error-box">
          <p>❌ {{ error }}</p>
        </div>
      </div>

      <div v-else class="v-report-card v-report-finish-card">
        <div class="v-report-success-icon">✨</div>
        <h2 class="v-report-main-title">报告已就绪</h2>
        
        <div class="v-report-result-box">
          <p class="v-report-status-text">您的年度回忆录已生成，快去看看吧！</p>

          <div class="v-report-info-grid">
            <div class="v-report-badge">🆔 {{ result.report_id }}</div>
            <div class="v-report-badge">👤 {{ result.user_name }}</div>
            <div class="v-report-badge">💬 {{ result.chat_name }}</div>
          </div>

          <div class="v-report-url-section">
            <p class="v-report-section-label">🔗 报告访问链接</p>
            <div class="v-report-url-display">{{ reportUrl }}</div>
            
            <div class="v-report-btn-group">
              <button class="v-report-btn-primary" @click="$emit('open-report', result.report_id)">预览报告</button>
              <button class="v-report-btn-secondary" @click="$emit('copy-url', result.report_id)">复制链接</button>
            </div>
          </div>

          <div class="v-report-bottom-nav">
            <button class="v-report-btn-text" @click="reset">创建下一份</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  loading: { type: Boolean, default: false }
})

const emit = defineEmits(['generate', 'open-report', 'copy-url'])

const file = ref(null)
const userName = ref('')
const startDate = ref('')
const endDate = ref('')
const useStopwords = ref(true)
const result = ref(null)
const error = ref('')

const generated = computed(() => !!result.value)
const reportUrl = computed(() =>
  result.value ? `${window.location.origin}/personal-report/personal-classic/${result.value.report_id}` : ''
)

function onFileChange(e) {
  const [f] = e.target.files || []
  file.value = f || null
  error.value = ''
}

function generate() {
  if (!file.value || !userName.value) return
  error.value = ''
  emit('generate', {
    file: file.value,
    userName: userName.value,
    startDate: startDate.value,
    endDate: endDate.value,
    useStopwords: useStopwords.value
  })
}

function reset() {
  file.value = null
  userName.value = ''
  startDate.value = ''
  endDate.value = ''
  useStopwords.value = true
  result.value = null
  error.value = ''
}

function setResult(data) { result.value = data }
function setError(msg) { error.value = msg }

defineExpose({ setResult, setError })
</script>

<style scoped>
/* ========== QQ 风格变量系统 ========== */
.v-personal-container {
  --qq-blue: #0099FF;
  --qq-blue-light: #F0F9FF;
  --qq-bg: #F2F5F8;
  --card-bg: #FFFFFF;
  --text-main: #333333;
  --text-sub: #888888;
  --border-color: #E0E6ED;
  background: var(--qq-bg);
  min-height: 100vh;
  padding: 20px 15px;
  font-family: -apple-system, "PingFang SC", sans-serif;
}

/* ========== 卡片组件 (高圆角 & 柔和阴影) ========== */
.v-report-card {
  background: var(--card-bg);
  border-radius: 24px;
  padding: 30px;
  max-width: 600px;
  margin: 0 auto;
  box-shadow: 0 8px 24px rgba(0, 153, 255, 0.08);
  animation: fadeIn 0.4s ease-out;
}

.v-report-sub-card {
  background: #F9FBFF;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 16px;
  border: 1px solid var(--border-color);
}

/* ========== 标题与文本 ========== */
.v-report-main-title {
  font-size: 24px;
  font-weight: bold;
  color: #000;
  margin: 0 0 10px 0;
}

.v-report-desc-text {
  font-size: 14px;
  color: var(--text-sub);
  line-height: 1.6;
  margin-bottom: 25px;
}

.v-report-sub-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #444;
}

/* ========== 表单输入控组件 ========== */
.v-report-time-range-group {
  display: flex;
  gap: 15px;
}

.v-report-time-field {
  flex: 1;
}

.v-report-label {
  font-size: 12px;
  color: var(--text-sub);
  display: block;
  margin-bottom: 6px;
}

.v-report-date-input, .v-report-text-input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.v-report-date-input:focus, .v-report-text-input:focus {
  border-color: var(--qq-blue);
}

.v-report-hint-text {
  font-size: 12px;
  color: var(--text-sub);
  margin-top: 8px;
}

/* ========== 自定义 Checkbox (核心修复：解决变黑) ========== */
.v-report-toggle-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  cursor: pointer;
}

.v-report-checkbox {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-color);
  border-radius: 6px;
  background: #FFF;
  cursor: pointer;
  position: relative;
  flex-shrink: 0;
  margin-top: 2px;
}

.v-report-checkbox:checked {
  background-color: var(--qq-blue);
  border-color: var(--qq-blue);
}

.v-report-checkbox:checked::after {
  content: '';
  position: absolute;
  width: 5px;
  height: 9px;
  border: 2px solid #FFF;
  border-top: 0;
  border-left: 0;
  left: 6px;
  top: 2px;
  transform: rotate(45deg);
}

.v-report-strong {
  font-size: 15px;
  color: #333;
  display: block;
}

.v-report-small-text {
  font-size: 12px;
  color: var(--text-sub);
  margin-top: 4px;
}

/* ========== 按钮与上传区域 ========== */
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
  border: 2px dashed var(--border-color);
  border-radius: 18px;
  text-align: center;
  color: var(--qq-blue);
  background: var(--qq-blue-light);
  cursor: pointer;
  transition: all 0.2s;
}

.v-report-btn-main {
  padding: 16px;
  background: var(--qq-blue);
  color: #FFF;
  border: none;
  border-radius: 30px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 153, 255, 0.2);
  transition: transform 0.2s;
}

.v-report-btn-main:active { transform: scale(0.98); }
.v-report-btn-main:disabled { background: #D0DDE9; box-shadow: none; cursor: not-allowed; }

/* ========== 成功界面展示 ========== */
.v-report-finish-card { text-align: center; }
.v-report-success-icon { font-size: 50px; margin-bottom: 15px; }
.v-report-status-text { color: var(--text-sub); margin-bottom: 25px; }

.v-report-info-grid {
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 30px;
}

.v-report-badge {
  padding: 6px 14px;
  background: var(--qq-blue-light);
  color: var(--qq-blue);
  border-radius: 20px;
  font-size: 13px;
  border: 1px solid rgba(0, 153, 255, 0.1);
}

.v-report-url-display {
  padding: 15px;
  background: #F5F7FA;
  border-radius: 12px;
  color: var(--qq-blue);
  font-family: monospace;
  font-size: 13px;
  word-break: break-all;
  margin: 15px 0;
}

.v-report-btn-group {
  display: flex;
  gap: 12px;
}

.v-report-btn-primary {
  flex: 2;
  background: var(--qq-blue);
  color: white;
  border: none;
  padding: 12px;
  border-radius: 20px;
  font-weight: bold;
  cursor: pointer;
}

.v-report-btn-secondary {
  flex: 1;
  background: #EEE;
  border: none;
  padding: 12px;
  border-radius: 20px;
  cursor: pointer;
}

.v-report-btn-text {
  background: none;
  border: none;
  color: var(--text-sub);
  text-decoration: underline;
  margin-top: 25px;
  cursor: pointer;
}

.v-report-error-box {
  margin-top: 20px;
  padding: 12px;
  background: #FFF0F0;
  border-radius: 10px;
  color: #FF4D4F;
  font-size: 14px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>