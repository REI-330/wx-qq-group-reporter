<template>
  <div class="report-page-wrapper">
    <component 
      v-if="report && templateComponent" 
      :is="templateComponent"
      :report="report"
      :generating-image="generatingImage"
      :image-url="imageUrl"
      :image-error="imageError"
      @generate-image="generateImage"
    />
    
    <div v-else-if="report && !templateComponent" class="template-error-container">
      <div class="template-error">
        <h2>⚠️ 模板加载失败</h2>
        <p>无法加载模板文件，请检查模板配置</p>
        <div class="template-info">
          <p>模板ID: <code>{{ currentTemplateId }}</code></p>
          <p>报告ID: <code>{{ currentReportId }}</code></p>
        </div>
        <button @click="loadReport">重新加载</button>
      </div>
    </div>
    
    <div v-else-if="loading" class="loading-container">
      <div class="loading">
        <div class="loading-spinner"></div>
        <p>正在拉取年度回忆...</p>
      </div>
    </div>
    
    <div v-else-if="error" class="error-container">
      <div class="error-message">
        <h2>❌ 加载失败</h2>
        <p>{{ error }}</p>
      </div>
      <button @click="loadReport">重新加载</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, shallowRef } from 'vue'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'
const templateModules = import.meta.glob('./templates/*.vue')

const report = ref(null)
const loading = ref(true)
const error = ref(null)
const templateComponent = shallowRef(null)
const currentTemplateId = ref('')
const currentReportId = ref('')
const generatingImage = ref(false)
const imageUrl = ref('')
const imageError = ref('')

const getRouteParams = () => {
  const path = window.location.pathname
  let match = path.match(/\/personal-report\/([^/]+)\/([^/]+)/)
  if (match) return { templateId: match[1], reportId: match[2], isPersonal: true }
  match = path.match(/\/report\/([^/]+)\/([^/]+)/)
  if (match) return { templateId: match[1], reportId: match[2], isPersonal: false }
  match = path.match(/\/report\/([^/]+)/)
  if (match) return { templateId: 'classic', reportId: match[1], isPersonal: false }
  return null
}

const getReportId = () => {
  const params = getRouteParams()
  return params ? params.reportId : null
}

const loadTemplate = async (templateId) => {
  const path = `./templates/${templateId}.vue`
  const mod = templateModules[path]
  if (!mod) {
    templateComponent.value = null
    return
  }
  const esModule = await mod()
  templateComponent.value = esModule.default
}

const loadReport = async () => {
  loading.value = true
  error.value = null
  try {
    const reportId = getReportId()
    if (!reportId) throw new Error('报告ID不存在')
    const params = getRouteParams()
    const isPersonal = params?.isPersonal || false
    const apiEndpoint = isPersonal 
      ? `${API_BASE}/personal-reports/${reportId}`
      : `${API_BASE}/reports/${reportId}`
    const { data } = await axios.get(apiEndpoint)
    if (data.error) throw new Error(data.error)
    report.value = data
  } catch (err) {
    error.value = err.message || '加载报告失败'
  } finally {
    loading.value = false
  }
}

const generateImage = async () => {
  if (generatingImage.value) return
  generatingImage.value = true
  imageError.value = ''
  try {
    const reportId = getReportId()
    const params = getRouteParams()
    const templateId = params?.templateId || 'classic'
    const isPersonal = params?.isPersonal || false
    const apiEndpoint = isPersonal
      ? `${API_BASE}/personal-reports/${reportId}/generate-image`
      : `${API_BASE}/reports/${reportId}/generate-image`
    const { data } = await axios.post(apiEndpoint, {
      template: templateId,
      format: 'for_share',
      force: false
    })
    if (data.success) {
      imageUrl.value = data.image_url
      const link = document.createElement('a')
      link.href = data.image_url
      link.download = `年度报告_${new Date().getTime()}.png`
      link.click()
    } else {
      throw new Error(data.error || '图片生成失败')
    }
  } catch (err) {
    imageError.value = err.response?.data?.error || err.message || '生成图片失败'
  } finally {
    generatingImage.value = false
  }
}

onMounted(async () => {
  const params = getRouteParams()
  if (params) {
    currentTemplateId.value = params.templateId
    currentReportId.value = params.reportId
    await loadTemplate(params.templateId)
  }
  loadReport()
})
</script>

<style scoped>
/* ========== QQ 风格基础背景 ========== */
.report-page-wrapper {
  background-color: #F2F5F8; /* QQ NT 版标准的淡灰色背景 */
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 0;
  margin: 0;
  font-family: -apple-system, "PingFang SC", "Helvetica Neue", Arial, sans-serif;
}

/* ========== 加载与错误容器 ========== */
.loading-container, .error-container, .template-error-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  width: 100%;
  color: #333;
  text-align: center;
  padding: 20px;
}

/* ========== 加载动画 (QQ 蓝旋转) ========== */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(0, 153, 255, 0.1);
  border-top-color: #0099FF; /* QQ Blue */
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading p {
  font-size: 16px;
  color: #888;
  margin: 0;
}

/* ========== 错误卡片 (QQ 风格大圆角) ========== */
.error-message, .template-error {
  background: #FFFFFF;
  padding: 40px 30px;
  border-radius: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  max-width: 400px;
  width: 90%;
}

.error-message h2, .template-error h2 {
  color: #333;
  margin: 0 0 12px 0;
  font-size: 20px;
}

.error-message p, .template-error p {
  color: #888;
  margin: 10px 0;
  font-size: 15px;
  line-height: 1.5;
}

.template-info {
  margin: 20px 0;
  padding: 15px;
  background: #F7F9FC;
  border-radius: 12px;
  text-align: left;
}

.template-info p {
  margin: 5px 0;
  font-size: 13px;
  color: #666;
}

.template-info code {
  background: #E0E6ED;
  padding: 2px 6px;
  border-radius: 4px;
  color: #0099FF;
  font-family: monospace;
}

/* ========== 按钮美化 ========== */
.error-container button, .template-error-container button {
  margin-top: 10px;
  padding: 12px 40px;
  background: #0099FF;
  color: #FFF;
  border: none;
  border-radius: 25px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.error-container button:hover, .template-error-container button:hover {
  background: #007ACC;
  transform: scale(1.02);
}

.error-container button:active {
  transform: scale(0.98);
}
</style>