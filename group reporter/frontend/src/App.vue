<template>
  <div :class="['container', { 'theme-wechat': activeTab === 'wechat' }]">

    <div v-if="isReportPage">
      <Report />
    </div>

    <div v-else>
      <div class="tabs">
        <button :class="['tab', { active: activeTab === 'upload' }]" @click="activeTab = 'upload'">
          上传分析
        </button>
        <button :class="['tab', { active: activeTab === 'personal' }]" @click="activeTab = 'personal'">
          个人报告
        </button>
        <button :class="['tab', { active: activeTab === 'wechat' }]" @click="activeTab = 'wechat'">
          微信转换
        </button>
        <button :class="['tab', { active: activeTab === 'history' }]" @click="activeTab = 'history'; loadReports()">
          历史记录
        </button>
      </div>

      <div class="tab-content-wrapper">
        <div v-if="activeTab === 'upload'">
          <upload :ai-features="aiFeatures" :available-templates="availableTemplates" @open-report="openReportWindow"
            @copy-url="copyReportUrl" @jump-history="activeTab = 'history'; loadReports()"
            @loading-change="val => loading = val" />
        </div>

        <div v-if="activeTab === 'history'">
          <history v-model:type="reportType" v-model:page="reports.page" :list="reports.data" :loading="loadingReports"
            :total="reports.total" :page-size="reports.page_size" @search="loadReports" @open-group="openReportWindow"
            @copy-group="copyReportUrl" @delete-group="deleteReport" @open-personal="openPersonalReport"
            @copy-personal="copyPersonalReportUrl" @delete-personal="deletePersonalReport" />
        </div>

        <div v-if="activeTab === 'personal'">
          <personal ref="personalPanel" :loading="personalLoading" @generate="generatePersonalReport"
            @open-report="openPersonalReport" @copy-url="copyPersonalReportUrl" />
        </div>

        <div v-if="activeTab === 'wechat'">
          <WechatVerifier :ai-features="aiFeatures" :available-templates="availableTemplates"
            @open-report="openReportWindow" @copy-url="copyReportUrl"
            @jump-history="activeTab = 'history'; loadReports()" @loading-change="val => loading = val" />
        </div>
      </div>
    </div>

    <!-- <footer class="copyright-footer">
      <div class="copyright-content">
        <p>
          <span>© 2025 QQ群年度报告分析器</span>
          <span class="separator">|</span>
          <span>作者：<a href="https://github.com/ZiHuixi" target="_blank">Huixi</a> & <a
              href="https://github.com/yujingkun1" target="_blank">Jingkun</a></span>
          <span class="separator">|</span>
          <span>开源协议：<a href="https://www.gnu.org/licenses/agpl-3.0.html" target="_blank">AGPL-3.0</a></span>
        </p>
        <p class="copyright-warning">
          ⚠️ 本软件为开源软件，<strong>严禁用于任何商业用途</strong>。仅供个人学习、研究和非商业用途使用。
        </p>
        <p class="copyright-links">
          <a href="https://github.com/ZiHuixi/QQgroup-annual-report-analyzer" target="_blank">GitHub 仓库</a>
        </p>
      </div>
    </footer> -->
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'

// 导入你的所有子组件
import Report from './report/Report.vue'
import upload from './components/upload.vue'
import history from './components/history.vue'
import personal from './components/personal.vue'
import WechatVerifier from './components/WechatVerifier.vue' // 确保路径和文件名大小写正确

/* ===== 全局变量 ===== */
const activeTab = ref('upload')
const API_BASE = import.meta.env.VITE_API_BASE || '/api'
const SITE_URL = window.location.origin
const aiFeatures = ref({ ai_comment_enabled: false, ai_word_selection_enabled: false })
const availableTemplates = ref([])
const loading = ref(false)
const personalLoading = ref(false)
const personalPanel = ref(null)
/* ===== 路由与历史记录相关 ===== */
const isReportPage = computed(() =>
  window.location.pathname.startsWith('/report/') ||
  window.location.pathname.startsWith('/personal-report/')
)
const reportType = ref('group')
const loadingReports = ref(false)
const reports = ref({ data: [], total: 0, page: 1, page_size: 20 })
const searchQuery = ref('')

/* ===== 核心逻辑：主题切换监听 ===== */
watch(activeTab, (newTab) => {
  if (newTab === 'wechat') {
    document.body.style.backgroundColor = '#111111'
  } else {
    document.body.style.backgroundColor = '#f5f5f7'
  }
}, { immediate: true })

/* ===== 方法定义 ===== */
const fetchAIFeatures = async () => {
  try { const { data } = await axios.get(`${API_BASE}/health`); aiFeatures.value = data.features || {} } catch { }
}
const loadTemplates = async () => {
  try {
    const { data } = await axios.get(`${API_BASE}/templates`)
    availableTemplates.value = data.templates || []
  } catch {
    availableTemplates.value = [{ id: 'classic', name: '经典模板', description: '最初的模板' }]
  }
}
const loadReports = async (page = 1) => {
  loadingReports.value = true
  try {
    const api = reportType.value === 'group' ? `${API_BASE}/reports` : `${API_BASE}/personal-reports`
    const { data } = await axios.get(api, {
      params: { page, page_size: 20, [reportType.value === 'group' ? 'chat_name' : 'user_name']: searchQuery.value }
    })
    reports.value = data
  } catch (e) { console.error(e) } finally { loadingReports.value = false }
}

const openReportWindow = (rid, tid) => window.open(`/report/${tid}/${rid}`, '_blank')
const copyReportUrl = async (rid, tid) => {
  const url = `${SITE_URL}/report/${tid}/${rid}`
  try { await navigator.clipboard.writeText(url); alert('链接已复制') } catch { prompt('请手动复制：', url) }
}
const openPersonalReport = (rid) => window.open(`/personal-report/personal-classic/${rid}`, '_blank')
const copyPersonalReportUrl = async (rid) => {
  const url = `${SITE_URL}/personal-report/personal-classic/${rid}`
  try { await navigator.clipboard.writeText(url); alert('链接已复制') } catch { prompt('请手动复制：', url) }
}

// 删除群聊报告
const deleteReport = async (rid) => {
  if (!confirm('确定要删除这份群聊报告吗？')) return
  try {
    // 调用后端 @app.route('/api/reports/<report_id>', methods=['DELETE']) 接口
    const { data } = await axios.delete(`${API_BASE}/reports/${rid}`)
    if (data.success) {
      alert('删除成功')
      loadReports(reports.value.page) // 刷新当前列表
    }
  } catch (e) {
    console.error("删除报错:", e)
    alert(e.response?.data?.error || '删除失败')
  }
}

// 删除个人报告
const deletePersonalReport = async (rid) => {
  if (!confirm('确定要删除这份个人报告吗？')) return
  try {
    // 调用后端 @app.route('/api/personal-reports/<report_id>', methods=['DELETE']) 接口
    const { data } = await axios.delete(`${API_BASE}/personal-reports/${rid}`)
    if (data.success) {
      alert('删除成功')
      loadReports(reports.value.page) // 刷新当前列表
    }
  } catch (e) {
    console.error("删除报错:", e)
    alert(e.response?.data?.error || '删除失败')
  }
}

async function generatePersonalReport(params) {
    const { file, userName, startDate, endDate, useStopwords } = params
    
    personalLoading.value = true
    try {
        const fd = new FormData()
        fd.append('file', file)
        // 1. 修改参数名：后端用的是 'target_name'
        fd.append('target_name', userName) 
        fd.append('use_stopwords', useStopwords ? 'true' : 'false')
        
        // 如果你的后端 PersonalAnalyzer 还没有写日期过滤逻辑，
        // 暂时传过去也没关系，但后端代码目前主要接收上面三个参数
        if (startDate) fd.append('start_date', startDate)
        if (endDate) fd.append('end_date', endDate)

        // 2. 修改接口地址：后端定义的是 '/api/personal-report'
        const { data } = await axios.post('/api/personal-report', fd)
        
        if (data.success) {
            // 注意：后端返回的对象里，报告数据在 data.report 中
            // 且 report_id 在 data.report_id
            personalPanel.value.setResult({
                ...data.report,
                report_id: data.report_id
            })
        } else {
            personalPanel.value.setError(data.error || '生成失败')
        }
    } catch (e) {
        console.error("请求报错详情:", e);
        const errorMsg = e.response?.data?.error || '网络请求失败，请稍后重试';
        personalPanel.value.setError(errorMsg)
    } finally {
        personalLoading.value = false
    }
}

onMounted(async () => {
  await fetchAIFeatures()
  loadTemplates()
})
</script>

<style scoped>
/* ========== 全局基础容器 ========== */
.container {
  min-height: 100vh;
  padding: 20px;
  /* 关键：设置背景色过渡动画 */
  transition: background-color 0.6s cubic-bezier(0.4, 0, 0.2, 1), 
              color 0.6s ease;
}

/* ========== 标签栏样式 ========== */
.tabs {
  display: flex;
  margin-bottom: 32px;
  background: #f5f5f7;
  border-radius: 12px;
  padding: 4px;
  border: 1px solid #e5e5e7;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  transition: all 0.5s ease;
}

.tab {
  flex: 1;
  padding: 12px 16px;
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #6e6e73;
}

.tab.active {
  background: white;
  color: #1d1d1f;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* ========== 微信暗色模式样式 ========== */
.theme-wechat {
  background-color: #111111;
  color: #e5e5e5;
}

.theme-wechat .tabs {
  background: #1c1c1e;
  border-color: #2c2c2e;
}

.theme-wechat .tab.active {
  background: #2c2c2e;
  color: #07c160; /* 标志性微信绿 */
}

/* ========== 内容切换动画 (Fade-Slide) ========== */
.tab-content-wrapper {
  max-width: 800px;
  margin: 0 auto;
  position: relative;
}

/* 进入前状态 */
.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

/* 离开后状态 */
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 动画过程 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ========== 页脚样式 ========== */
.copyright-footer {
  margin-top: 60px;
  padding: 24px 0;
  border-top: 1px solid #e5e5e7;
  text-align: center;
  transition: all 0.5s ease;
}

.theme-wechat .copyright-footer {
  border-top-color: #2c2c2e;
  color: #444;
}

.theme-wechat .copyright-footer a {
  color: #07c160;
}
</style>
