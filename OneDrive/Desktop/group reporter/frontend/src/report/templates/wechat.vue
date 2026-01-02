<template>
  <div class="report-page-wrapper wechat-template">
    <div class="report-container" v-if="report">
      <div class="stripe"></div>
      
      <div class="header">
        <div class="header-badge">Annual Report</div>
        <div class="header-star-group">★ ★ ★</div>
        <h1 :class="getTitleClass(report.chat_name)">{{ report.chat_name }}</h1>
        <div class="subtitle">年度报告</div>
        <div class="header-stats">
          <div class="stat-box">
            <div class="stat-value">{{ formatNumber(report.message_count) }}</div>
            <div class="stat-label">消息总数</div>
          </div>
        </div>
      </div>
      
      <div class="stripe-diagonal"></div>
      
      <div class="chart-section">
        <div class="section-header">
          <div class="section-title">✨ 热词热度排行榜</div>
        </div>
        
        <div class="bar-chart-container">
          <div class="bar-chart">
            <div v-for="(word, index) in report.selected_words" :key="word.word" class="bar-item">
              <div class="bar-value">{{ word.freq }}</div>
              
              <div class="bar-wrapper">
                <div class="bar" :style="{ height: word.bar_height + '%' }">
                  <template v-if="word.segments && word.segments.length">
                    <div v-for="(seg, segIndex) in word.segments" :key="segIndex"
                         class="bar-segment" 
                         :style="{ height: seg.percent + '%', backgroundColor: seg.color || '#07C160' }">
                    </div>
                  </template>
                  <div v-else class="bar-segment-default"></div>
                </div>
              </div>

              <div class="bar-info">
                <div class="bar-label">{{ word.word }}</div>
                <div class="bar-rank">TOP {{ index + 1 }}</div>
              </div>

              <div class="bar-contributors">
                <div v-for="(item, itemIndex) in word.legend?.slice(0, 3)" :key="itemIndex"
                     :class="['bar-contributor-item', { empty: !item.name }]">
                  <div class="bar-contributor-dot" :style="{ background: item.color || '#07C160' }"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="divider">
        <div class="divider-line"></div>
      </div>
      
      <div class="section">
        <div class="section-header">
          <div class="section-title">热词档案</div>
        </div>
        
        <div class="word-cards">
          <div v-for="(word, index) in report.selected_words" :key="word.word" 
               :class="['word-card', `color-${index + 1}`]">
            <div class="word-card-header">
              <div class="word-card-left">
                <div class="word-card-rank">#{{ index + 1 }}</div>
                <div class="word-card-title">{{ word.word }}</div>
              </div>
              <div class="word-card-freq">{{ word.freq }}次</div>
            </div>
            
            <div v-if="word.ai_comment" class="word-card-comment">{{ word.ai_comment }}</div>
            
            <div class="word-card-contributors">
              {{ word.contributors_text }}
            </div>
            
            <ul class="word-card-samples">
              <li v-for="(sample, sampleIndex) in word.samples.slice(0, 3)" :key="sampleIndex">
                {{ truncateText(sample, 40) }}
              </li>
            </ul>
          </div>
        </div>
      </div>
      
      <div class="stripe"></div>
      
      <div class="section rankings-section">
        <div class="section-header">
          <div class="section-title">荣誉殿堂</div>
        </div>
        
        <div class="rankings-grid">
          <div v-for="ranking in report.rankings" :key="ranking.title" class="ranking-card">
            <div class="ranking-card-header">
              {{ ranking.icon }} {{ ranking.title }}
            </div>
            
            <div v-if="ranking.first" class="ranking-first">
              <div class="ranking-first-crown">👑</div>
              <img class="ranking-first-avatar" 
                   :src="ranking.first.avatar" 
                   :alt="ranking.first.name"
                   @error="handleImageError">
              <div class="ranking-first-name">{{ ranking.first.name }}</div>
              <div class="ranking-first-value">{{ ranking.first.value }}{{ ranking.unit }}</div>
            </div>
            
            <div v-if="ranking.others" class="ranking-others">
              <div v-for="(item, itemIndex) in ranking.others" :key="itemIndex" class="ranking-item">
                <div class="ranking-item-pos">{{ itemIndex + 2 }}</div>
                <img class="ranking-item-avatar" 
                     :src="item.avatar" 
                     :alt="item.name"
                     @error="handleImageError">
                <div class="ranking-item-name">{{ item.name }}</div>
                <div class="ranking-item-value">{{ item.value }}{{ ranking.unit }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="section hour-section">
        <div class="section-header">
          <div class="section-title">活跃时段</div>
        </div>
        
        <div class="hour-chart-container">
          <div class="hour-chart">
            <div v-for="(hour, index) in report.statistics?.hourDistribution || {}" :key="index"
                 class="hour-bar" :style="{ height: getHourHeightPercent(hour) + '%' }"></div>
          </div>
          <div class="hour-labels">
            <span>0时</span>
            <span>6时</span>
            <span>12时</span>
            <span>18时</span>
            <span>24时</span>
          </div>
          <div class="hour-peak">
            ⭐ 最活跃时段
            <div class="hour-peak-badge">{{ peakHourText }}</div>
          </div>
        </div>
      </div>
      
      <div class="stripe-diagonal"></div>
      
      <div class="share-section">
        <div class="share-container">
          <button 
            v-if="!imageUrl || imageError"
            class="share-button" 
            @click="$emit('generate-image')"
            :disabled="generatingImage">
            <span v-if="!generatingImage">
              {{ imageError ? '🔄 重新生成' : '📸 生成图片分享' }}
            </span>
            <span v-else>生成中...</span>
          </button>
          
          <div v-if="imageUrl && !imageError" class="share-result">
            <div class="share-success">✅ 图片已生成并下载</div>
            <div class="share-actions">
              <a :href="imageUrl" :download="imageFileName" class="download-button">💾 下载图片</a>
              <button class="regenerate-button" @click="$emit('generate-image')">🔄 重新生成</button>
            </div>
          </div>
          <div v-if="imageError" class="share-error">❌ {{ imageError }}</div>
        </div>
      </div>
      
      <div class="footer">
        <div class="footer-text">微信风格群聊年度报告</div>
      </div>
      
      <div class="stripe-thin"></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useReportUtils } from '../../composables/useReportUtils'

const props = defineProps({
  report: { type: Object, required: true },
  generatingImage: { type: Boolean, default: false },
  imageUrl: { type: String, default: '' },
  imageError: { type: String, default: '' }
})

defineEmits(['generate-image'])

const {
  formatNumber,
  truncateText,
  getTitleClass,
  handleImageError,
  getHourHeight,
  getPeakHour
} = useReportUtils()

const getHourHeightPercent = (hour) => getHourHeight(hour, props.report.statistics?.hourDistribution)
const peakHourText = computed(() => {
  const peak = getPeakHour(props.report.statistics?.hourDistribution)
  return `${peak}:00 - ${peak + 1}:00`
})
const imageFileName = computed(() => `${props.report?.chat_name}_年度报告.png`)
</script>

<style scoped>
/* ========== 微信暗绿风格定义 ========== */
.wechat-template {
  background-color: #111111; /* 纯黑背景 */
  padding: 20px 0;
}

.report-container {
  max-width: 600px;
  margin: 0 auto;
  background: #191919; /* 深灰色背景 */
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 30px rgba(0,0,0,0.5);
}

/* 装饰条纹 */
.stripe { height: 8px; background: #07C160; } /* 微信绿 */
.stripe-thin { height: 4px; background: #07C160; opacity: 0.6; }
.stripe-diagonal {
  height: 12px;
  background-image: repeating-linear-gradient(45deg, #07C160, #07C160 10px, transparent 10px, transparent 20px);
  opacity: 0.15;
}

/* 头部 */
.header {
  padding: 40px 20px;
  text-align: center;
  background: linear-gradient(135deg, #191919 0%, #111111 100%);
  color: #FFFFFF;
}
.header-badge { display: inline-block; padding: 4px 12px; background: rgba(7, 193, 96, 0.2); border: 1px solid #07C160; color: #07C160; border-radius: 4px; font-size: 12px; margin-bottom: 10px; }
.header-star-group { color: #07C160; margin-bottom: 10px; letter-spacing: 5px; }
.header h1 { font-size: 26px; margin-bottom: 5px; font-weight: 800; color: #07C160; }
.stat-value { font-size: 42px; font-weight: 900; color: #FFFFFF; }
.stat-label { color: #888; }

/* 排行榜 (Chart Section) */
.chart-section {
  padding: 25px 15px;
  background: #191919;
}

.bar-chart-container {
  width: 100%;
  overflow-x: auto;
  padding-bottom: 10px;
}

.bar-chart {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 220px;
  min-width: 450px;
}

.bar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 50px;
}

.bar-value {
  font-size: 11px;
  color: #07C160;
  font-weight: bold;
  margin-bottom: 5px;
}

.bar-wrapper {
  width: 18px;
  height: 120px;
  background: #2c2c2c;
  border-radius: 2px; /* 微信偏向直角方块感 */
  overflow: hidden;
  display: flex;
  flex-direction: column-reverse;
}

.bar {
  width: 100%;
  display: flex;
  flex-direction: column-reverse;
  transition: height 1s ease-out;
}

.bar-segment-default {
  height: 100%;
  background: #07C160;
}

.bar-segment {
  width: 100%;
}

.bar-info {
  margin-top: 8px;
  text-align: center;
}

.bar-label {
  font-size: 12px;
  font-weight: 700;
  color: #FFFFFF;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 45px;
}

.bar-rank {
  font-size: 10px;
  color: #555;
}

.bar-contributors {
  display: flex;
  gap: 2px;
  margin-top: 5px;
}

.bar-contributor-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

/* 通用 Section */
.section { padding: 25px 20px; color: #FFFFFF; }
.section-header { border-left: 4px solid #07C160; padding-left: 12px; margin-bottom: 20px; }
.section-title { font-size: 18px; font-weight: bold; color: #FFFFFF; }

/* 热词卡片 - 微信对话气泡感 */
.word-cards { display: grid; gap: 15px; }
.word-card { 
  background: #2c2c2c; 
  border-radius: 8px; 
  padding: 18px; 
  border: 1px solid #333;
}
.word-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.word-card-rank { color: #07C160; font-weight: 900; font-style: italic; font-size: 18px; margin-right: 10px; }
.word-card-title { font-size: 18px; font-weight: 700; color: #FFFFFF; }
.word-card-freq { font-size: 12px; color: #888; background: #191919; padding: 2px 8px; border-radius: 4px; border: 1px solid #333; }
.word-card-comment { background: #353535; padding: 10px; border-radius: 4px; font-size: 13px; color: #bbb; margin-bottom: 10px; line-height: 1.5; }
.word-card-contributors { font-size: 12px; color: #07C160; font-weight: 600; margin-bottom: 8px; }
.word-card-samples li { font-size: 12px; color: #888; margin-bottom: 4px; font-style: italic; }

/* 排行榜网格 */
.rankings-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 0 10px;
}

.ranking-card {
  border: 1px solid #333;
  border-radius: 8px;
  padding: 15px 10px;
  text-align: center;
  background-color: #2c2c2c;
}

.ranking-card-header {
  font-weight: bold;
  font-size: 14px;
  color: #FFFFFF;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px dashed #444;
}

.ranking-first-avatar { width: 52px; height: 52px; border-radius: 26px; border: 2.5px solid #07C160; background: #191919; }
.ranking-first-name { font-size: 13px; font-weight: bold; margin-top: 5px; color: #FFFFFF; }
.ranking-first-value { color: #07C160; font-weight: 900; font-size: 16px; }

.ranking-item {
  display: flex;
  align-items: center;
  padding: 6px 8px;
  background-color: #191919; 
  border: 1px solid #333; 
  border-radius: 4px; 
}

.ranking-item-pos { color: #555; }
.ranking-item-avatar { width: 24px; height: 24px; border-radius: 12px; margin-left: 3px;}
.ranking-item-name { color: #bbb; font-size: 10px; }
.ranking-item-value { color: #07C160; font-size: 10px; margin-left: auto;}

/* 时段分布 */
.hour-chart { display: flex; align-items: flex-end; gap: 2px; height: 80px; margin-bottom: 10px; }
.hour-bar { flex: 1; background: #07C160; opacity: 0.6; }
.hour-labels { color: #555; display: flex; justify-content: space-between; font-size: 10px; }
.hour-peak-badge { display: inline-block; background: #07C160; color: white; padding: 2px 10px; border-radius: 4px; }

/* 按钮区 */
.share-section { padding: 30px 20px; }
.share-button { width: 100%; padding: 15px; background: #07C160; color: white; border: none; border-radius: 8px; font-weight: bold; }
.download-button { display: block; text-decoration: none; background: #2c2c2c; border: 1px solid #07C160; color: #07C160; padding: 12px; border-radius: 8px; margin-bottom: 10px; text-align: center; }
.regenerate-button { width: 100%; padding: 10px; background: transparent; border: 1px solid #555; color: #888; border-radius: 8px; }
.footer { padding: 20px; text-align: center; color: #555; font-size: 12px; }
</style>