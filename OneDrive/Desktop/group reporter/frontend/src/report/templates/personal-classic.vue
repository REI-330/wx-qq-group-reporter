<template>
  <div class="report-page-wrapper qq-style-template">
    <div class="report-container" v-if="report">
      
      <div class="qq-header-card">
        <div class="qq-header-content">
          <div class="qq-header-left">
            <h1 :class="getTitleClass(report.user_name)">{{ report.user_name }}</h1>
            <div class="qq-annual-badge">Personal Annual Report 2024</div>
            <div class="qq-chat-source">{{ report.chat_name }} · 个人回忆录</div>
          </div>
          <div class="qq-header-right">
            <div class="qq-total-stats">
              <span class="qq-stat-num">{{ formatNumber(report.total_messages) }}</span>
              <div class="qq-stat-info">
                <span class="qq-stat-unit">条年度总发言</span>
                <span class="qq-stat-sub">ANNUAL TOTAL</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="qq-section" v-if="report.personality_tags && report.personality_tags.length > 0">
        <div class="qq-section-title">🎭 我的专属标签</div>
        <div class="qq-tags-container">
          <span v-for="tag in report.personality_tags" :key="tag" class="qq-personality-tag">
            {{ tag }}
          </span>
        </div>
      </div>

      <div class="qq-section">
        <div class="qq-section-title">📊 活跃数据概览</div>
        <div class="qq-stats-grid">
          <div class="qq-stat-card">
            <div class="qq-stat-card-label">平均每日发言</div>
            <div class="qq-stat-card-value">{{ (report.avg_daily_messages || 0).toFixed(1) }}</div>
          </div>
          <div class="qq-stat-card">
            <div class="qq-stat-card-label">活跃天数</div>
            <div class="qq-stat-card-value">{{ report.active_days }}<span class="qq-small-unit">/{{ report.total_days }}</span></div>
          </div>
          <div class="qq-stat-card">
            <div class="qq-stat-card-label">活跃率</div>
            <div class="qq-stat-card-value">{{ (report.active_ratio || 0).toFixed(1) }}%</div>
          </div>
          <div class="qq-stat-card" v-if="report.most_active_date">
            <div class="qq-stat-card-label">单日巅峰 ({{ report.most_active_date.date }})</div>
            <div class="qq-stat-card-value">{{ report.most_active_date.count }}<span class="qq-small-unit">条</span></div>
          </div>
        </div>
      </div>

      <div class="qq-section">
        <div class="qq-section-title">⏰ 活跃脉搏</div>
        <div class="qq-hour-box">
          <div class="qq-hour-chart">
            <div v-for="hour in 24" 
                 :key="hour"
                 class="qq-hour-dot" 
                 :style="{ 
                   height: getHourHeight(hour) + '%',
                   backgroundColor: getHourColor(getHourHeight(hour))
                 }">
            </div>
          </div>
          <div class="qq-hour-labels">
            <span>00:00</span>
            <span>06:00</span>
            <span>12:00</span>
            <span>18:00</span>
            <span>24:00</span>
          </div>
          <div class="qq-peak-footer">
             夜猫子指数：<span class="qq-blue-text">{{ (report.night_ratio || 0).toFixed(1) }}%</span>
             <span class="qq-peak-divider">|</span>
             高峰时段：<span class="qq-blue-text">{{ report.peak_hour }}:00</span>
          </div>
        </div>
      </div>

      <div class="qq-section">
        <div class="qq-section-title">🎨 消息偏好占比</div>
        <div class="qq-type-list">
          <div class="qq-bar-item">
            <div class="qq-bar-label-group">
              <span class="qq-bar-word">纯文字</span>
              <span class="qq-bar-freq">{{ (report.message_type_ratios?.text || 0).toFixed(1) }}%</span>
            </div>
            <div class="qq-bar-track">
              <div class="qq-bar-fill" :style="{ width: (report.message_type_ratios?.text || 0) + '%', backgroundColor: '#0099FF' }"></div>
            </div>
          </div>
          <div class="qq-bar-item">
            <div class="qq-bar-label-group">
              <span class="qq-bar-word">表情包</span>
              <span class="qq-bar-freq">{{ (report.message_type_ratios?.emoji || 0).toFixed(1) }}%</span>
            </div>
            <div class="qq-bar-track">
              <div class="qq-bar-fill" :style="{ width: (report.message_type_ratios?.emoji || 0) + '%', backgroundColor: '#2BB5FF' }"></div>
            </div>
          </div>
          <div class="qq-bar-item">
            <div class="qq-bar-label-group">
              <span class="qq-bar-word">图片</span>
              <span class="qq-bar-freq">{{ (report.message_type_ratios?.image || 0).toFixed(1) }}%</span>
            </div>
            <div class="qq-bar-track">
              <div class="qq-bar-fill" :style="{ width: (report.message_type_ratios?.image || 0) + '%', backgroundColor: '#56C5FF' }"></div>
            </div>
          </div>
        </div>
      </div>

      <div class="qq-section" v-if="report.most_interact_user || report.most_at_target">
        <div class="qq-section-title">🤝 年度社交羁绊</div>
        <div class="qq-interaction-flex">
          <div class="qq-rank-wide-card" v-if="report.most_interact_user">
            <div class="qq-rank-inner">
              <div class="qq-avatar-side"><div class="qq-avatar-placeholder">🤝</div></div>
              <div class="qq-rank-info">
                <div class="qq-rank-type">最常互动对象</div>
                <div class="qq-rank-name">{{ report.most_interact_user.name }}</div>
                <div class="qq-rank-val">{{ report.most_interact_user.count }} 次回复</div>
              </div>
            </div>
          </div>
          <div class="qq-rank-wide-card" v-if="report.most_at_target">
            <div class="qq-rank-inner">
              <div class="qq-avatar-side"><div class="qq-avatar-placeholder">@</div></div>
              <div class="qq-rank-info">
                <div class="qq-rank-type">最常 @ 的人</div>
                <div class="qq-rank-name">{{ report.most_at_target.name }}</div>
                <div class="qq-rank-val">呼唤了 {{ report.most_at_target.count }} 次</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="qq-section" v-if="report.top_words && report.top_words.length > 0">
        <div class="qq-section-title">✨ 我的高频词 Top 10</div>
        <div class="qq-bar-chart">
          <div v-for="(word, index) in report.top_words.slice(0, 10)" :key="word.word" class="qq-bar-item">
            <div class="qq-bar-label-group">
              <span class="qq-bar-rank">#{{ index + 1 }}</span>
              <span class="qq-bar-word">{{ word.word }}</span>
              <span class="qq-bar-freq">{{ word.freq }}次</span>
            </div>
            <div class="qq-bar-track">
              <div class="qq-bar-fill" :style="{ width: getBarWidth(word), backgroundColor: getQQColor(index) }"></div>
            </div>
          </div>
        </div>
      </div>

      <div class="qq-footer-actions">
        <div class="share-container">
          <button v-if="!imageUrl || imageError" class="qq-btn-primary-wide" @click="$emit('generate-image')" :disabled="generatingImage">
            {{ generatingImage ? '⏳ 正在生成个人报告...' : '📸 生成图片分享' }}
          </button>
          
          <div v-if="imageUrl && !imageError" class="qq-share-result">
            <p class="qq-success-tip">✅ 报告已生成</p>
            <div class="qq-btn-group-wide">
              <a :href="imageUrl" :download="imageFileName" class="qq-btn-secondary">下载至设备</a>
              <button class="qq-btn-text" @click="$emit('generate-image')">重新生成</button>
            </div>
          </div>
        </div>
        <p class="qq-copyright">QQ 群聊年度报告分析器 · ZiHuixi</p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useReportUtils } from '../../composables/useReportUtils'

const props = defineProps({
  report: Object,
  generatingImage: Boolean,
  imageUrl: String,
  imageError: String
})

defineEmits(['generate-image'])

const { formatNumber, getTitleClass, handleImageError, getPeakHour } = useReportUtils()

// 基础工具函数
const getHourHeight = (hour) => {
  if (!props.report.hour_distribution) return 0
  const values = Object.values(props.report.hour_distribution)
  const maxCount = Math.max(...values, 1)
  return ((props.report.hour_distribution[hour] || 0) / maxCount) * 100
}

const getBarWidth = (word) => {
  const topFreq = props.report.top_words[0]?.freq || 1;
  return Math.max((word.freq / topFreq) * 100, 2) + '%';
}

const getQQColor = (i) => ['#0099FF', '#2BB5FF', '#56C5FF', '#82D5FF', '#ADDFFF'][i] || '#D7EFFF';
const getHourColor = (h) => h > 70 ? '#0099FF' : '#D0E9FF';
const imageFileName = computed(() => `${props.report?.user_name}_个人年度报告.png`);
</script>

<style scoped>
/* ========== QQ 宽屏风格适配器 ========== */
.qq-style-template {
  background-color: #F2F5F8;
  padding: 30px 20px;
  width: 100%;
  box-sizing: border-box;
}

.report-container {
  max-width: 650px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 头部卡片 */
.qq-header-card {
  background: linear-gradient(110deg, #0099FF 0%, #007ACC 100%);
  border-radius: 28px;
  padding: 35px;
  color: white;
  box-shadow: 0 10px 30px rgba(0, 153, 255, 0.15);
}

.qq-header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.qq-header-left h1 { font-size: 26px; margin: 0; font-weight: 800; }
.qq-chat-source { font-size: 14px; opacity: 0.8; margin-top: 5px; }

.qq-annual-badge {
  display: inline-block;
  background: rgba(255, 255, 255, 0.15);
  padding: 4px 12px;
  border-radius: 10px;
  font-size: 12px;
  margin-top: 10px;
  backdrop-filter: blur(8px);
}

.qq-stat-num { font-size: 46px; font-weight: 900; line-height: 1; }
.qq-stat-info { display: flex; flex-direction: column; }
.qq-stat-unit { font-size: 14px; font-weight: 600; }
.qq-stat-sub { font-size: 10px; opacity: 0.5; }

/* 模块通用 */
.qq-section {
  background: white;
  border-radius: 24px;
  padding: 24px 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
}

.qq-section-title {
  font-size: 18px;
  font-weight: 800;
  color: #1F1F1F;
  margin-bottom: 22px;
}

/* 标签样式 */
.qq-tags-container { display: flex; flex-wrap: wrap; gap: 10px; }
.qq-personality-tag {
  background: #F0F7FF;
  color: #0099FF;
  padding: 8px 18px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  border: 1px solid #E1EFFF;
}

/* 数据网格 */
.qq-stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}
.qq-stat-card {
  background: #F9FBFF;
  padding: 20px;
  border-radius: 18px;
  border: 1px solid #EEF2F6;
}
.qq-stat-card-label { font-size: 13px; color: #8F959E; margin-bottom: 8px; }
.qq-stat-card-value { font-size: 24px; font-weight: 800; color: #1F1F1F; }
.qq-small-unit { font-size: 14px; font-weight: 400; margin-left: 2px; }

/* 进度条通用 */
.qq-bar-item { margin-bottom: 18px; }
.qq-bar-label-group { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 14px; }
.qq-bar-word { font-weight: 600; color: #333; }
.qq-bar-rank { color: #D1D9E0; font-weight: 900; margin-right: 10px; }
.qq-bar-track { height: 10px; background: #F5F7F9; border-radius: 5px; overflow: hidden; }
.qq-bar-fill { height: 100%; border-radius: 5px; transition: width 1s ease-in-out; }

/* 活跃图表 */
.qq-hour-chart { height: 100px; display: flex; align-items: flex-end; gap: 4px; margin-bottom: 15px; }
.qq-hour-dot { flex: 1; border-radius: 4px 4px 2px 2px; min-height: 2px; }
.qq-hour-labels { display: flex; justify-content: space-between; color: #ABB3BD; font-size: 11px; }
.qq-peak-footer { margin-top: 20px; background: #F0F9FF; padding: 12px; border-radius: 12px; font-size: 13px; text-align: center; }
.qq-peak-divider { margin: 0 15px; color: #D0E9FF; }
.qq-blue-text { color: #0099FF; font-weight: bold; }

/* 互动卡片 */
.qq-interaction-flex { display: flex; flex-direction: column; gap: 12px; }
.qq-rank-wide-card { background: #F9FBFF; border-radius: 18px; padding: 16px 24px; border: 1px solid #EEF2F6; }
.qq-rank-inner { display: flex; align-items: center; gap: 20px; }
.qq-avatar-placeholder { width: 50px; height: 50px; background: #E1EFFF; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; }
.qq-rank-info { flex: 1; display: grid; grid-template-columns: 1fr 1fr 1fr; align-items: center; }
.qq-rank-type { font-size: 13px; color: #8F959E; }
.qq-rank-name { font-size: 16px; color: #1F1F1F; font-weight: 700; }
.qq-rank-val { font-size: 13px; color: #0099FF; text-align: right; font-weight: 700; }

/* 底部操作 */
.qq-footer-actions { padding: 20px 0 60px; text-align: center; }
.qq-btn-primary-wide { background: #0099FF; color: white; border: none; width: 100%; padding: 18px; border-radius: 18px; font-size: 16px; font-weight: 800; cursor: pointer; box-shadow: 0 10px 20px rgba(0,153,255,0.2); }
.qq-btn-group-wide { display: flex; flex-direction: column; gap: 10px; align-items: center; margin-top: 15px; }
.qq-btn-secondary { background: white; color: #333; width: 100%; max-width: 300px; padding: 14px; border-radius: 14px; text-decoration: none; font-weight: 600; border: 1px solid #E0E6ED; }
.qq-btn-text { background: none; border: none; color: #8F959E; text-decoration: underline; cursor: pointer; }
.qq-copyright { margin-top: 30px; opacity: 0.4; font-size: 11px; }

@media (max-width: 480px) {
  .qq-header-content { flex-direction: column; text-align: center; gap: 15px; }
  .qq-rank-info { grid-template-columns: 1fr; gap: 5px; text-align: left; }
  .qq-rank-val { text-align: left; }
  .qq-stats-grid { grid-template-columns: 1fr; }
}
</style>