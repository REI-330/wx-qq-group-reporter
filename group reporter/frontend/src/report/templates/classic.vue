<template>

  <div class="report-page-wrapper classic-template">

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

                         :style="{ height: seg.percent + '%', backgroundColor: seg.color || '#0099FF' }">

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

                  <div class="bar-contributor-dot" :style="{ background: item.color || '#0099FF' }"></div>

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

        <div class="footer-text">QQ 群聊年度报告分析器</div>

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

/* ========== 全局容器与颜色定义 ========== */

.classic-template {

  background-color: #f2f5f8;

  padding: 20px 0;

}



.report-container {

  max-width: 600px;

  margin: 0 auto;

  background: white;

  border-radius: 12px;

  overflow: hidden; /* 关键：防止子元素溢出 */

  box-shadow: 0 4px 20px rgba(0,0,0,0.08);

}



/* 顶部与条纹 */

.stripe { height: 8px; background: #0099ff; }

.stripe-thin { height: 4px; background: #0099ff; opacity: 0.6; }

.stripe-diagonal {

  height: 12px;

  background-image: repeating-linear-gradient(45deg, #0099ff, #0099ff 10px, transparent 10px, transparent 20px);

  opacity: 0.1;

}



/* 头部 */

.header {

  padding: 40px 20px;

  text-align: center;

  background: linear-gradient(135deg, #0099ff 0%, #007acc 100%);

  color: white;

}

.header-badge { display: inline-block; padding: 4px 12px; background: rgba(255,255,255,0.2); border-radius: 20px; font-size: 12px; margin-bottom: 10px; }

.header-star-group { color: #ffd700; margin-bottom: 10px; letter-spacing: 5px; }

.header h1 { font-size: 26px; margin-bottom: 5px; font-weight: 800; }

.stat-value { font-size: 42px; font-weight: 900; }



/* ========== 重构：蓝色排行榜 (Chart Section) ========== */

.chart-section {

  padding: 25px 15px;

  background: #ffffff;

}



.bar-chart-container {

  width: 100%;

  overflow-x: auto; /* 手机端如果挤不下可以横向滑动 */

  padding-bottom: 10px;

}



.bar-chart {

  display: flex;

  justify-content: space-around;

  align-items: flex-end;

  height: 220px;

  min-width: 450px; /* 保证柱子不会太细 */

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

  color: #0099ff;

  font-weight: bold;

  margin-bottom: 5px;

}



.bar-wrapper {

  width: 18px;

  height: 120px; /* 柱状图总高度 */

  background: #f0f2f5;

  border-radius: 9px;

  overflow: hidden;

  display: flex;

  flex-direction: column-reverse; /* 让柱子从下往上长 */

}



.bar {

  width: 100%;

  display: flex;

  flex-direction: column-reverse;

  transition: height 1s ease-out;

}



.bar-segment-default {

  height: 100%;

  background: #0099ff;

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

  color: #333;

  white-space: nowrap;

  overflow: hidden;

  text-overflow: ellipsis;

  max-width: 45px;

}



.bar-rank {

  font-size: 10px;

  color: #999;

  font-family: Arial;

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

.section { padding: 25px 20px; }

.section-header { border-left: 4px solid #0099ff; padding-left: 12px; margin-bottom: 20px; }

.section-title { font-size: 18px; font-weight: bold; }



/* 热词卡片 - QQ 气泡感 */

.word-cards { display: grid; gap: 15px; }

.word-card { 

  background: #f8fbff; 

  border-radius: 16px; 

  padding: 18px; 

  border: 1px solid #e1e9f5;

}

.word-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }

.word-card-rank { color: #0099ff; font-weight: 900; font-style: italic; font-size: 18px; margin-right: 10px; }

.word-card-title { font-size: 18px; font-weight: 700; color: #1a1a1a; }

.word-card-freq { font-size: 12px; color: #888; background: #eee; padding: 2px 8px; border-radius: 10px; }

.word-card-comment { background: #eef6ff; padding: 10px; border-radius: 8px; font-size: 13px; color: #444; margin-bottom: 10px; line-height: 1.5; }

.word-card-contributors { font-size: 12px; color: #0099ff; font-weight: 600; margin-bottom: 8px; }

.word-card-samples { list-style: none; padding: 0; margin: 0; }

.word-card-samples li { font-size: 12px; color: #666; margin-bottom: 4px; font-style: italic; }



.rankings-grid {

  display: grid;

  grid-template-columns: 1fr 1fr; /* 保持两列布局 */

  gap: 12px;

  padding: 0 10px;

}



.ranking-card {

  border: 1px solid #eee;

  border-radius: 14px;

  padding: 15px 10px;

  text-align: center;

  background-color: #fff;

}



.ranking-card-header {

  font-weight: bold;

  font-size: 14px;

  color: #333;

  margin-bottom: 12px;

  padding-bottom: 8px;

  border-bottom: 1px dashed #eee;

}



/* 第一名特殊样式 */

.ranking-first {

  margin-bottom: 15px;

  position: relative;

}

.ranking-first-crown { font-size: 18px; margin-bottom: -5px; }

.ranking-first-avatar { width: 52px; height: 52px; border-radius: 50%; border: 2.5px solid #ffd700; background: #f9f9f9; }

.ranking-first-name { font-size: 13px; font-weight: bold; margin-top: 5px; }

.ranking-first-value { color: #0099ff; font-weight: 900; font-size: 16px; }

.ranking-first-value small { font-size: 10px; opacity: 0.7; }



/* 其他排行项：每一条分开并带边框 */

.ranking-others {

  display: flex;

  flex-direction: column;

  gap: 6px; /* 每一项之间的间距 */

}



.ranking-item {

  display: flex;

  align-items: center;

  padding: 6px 8px;

  background-color: #f8fbff; /* 浅蓝色背景 */

  border: 1px solid #eef2f8; /* 边框 */

  border-radius: 8px; /* 圆角 */

  font-size: 11px;

}



.ranking-item-pos {

  font-weight: 900;

  color: #abbac7;

  width: 14px;

  font-style: italic;

  margin-right: 4px;

}



.ranking-item-avatar {

  width: 24px;

  height: 24px;

  border-radius: 50%;

  margin-right: 8px;

  border: 1px solid #fff;

}



.ranking-item-name {

  flex: 1;

  text-align: left;

  color: #555;

  white-space: nowrap;

  overflow: hidden;

  text-overflow: ellipsis;

}



.ranking-item-value {

  font-weight: bold;

  color: #78909c;

  margin-left: 4px;

}



/* 时段分布 */

.hour-chart { display: flex; align-items: flex-end; gap: 2px; height: 80px; margin-bottom: 10px; }

.hour-bar { flex: 1; background: #0099ff; opacity: 0.4; }

.hour-peak-badge { display: inline-block; background: #0099ff; color: white; padding: 2px 10px; border-radius: 12px; }



/* 按钮区 */

.share-section { padding: 30px 20px; }

.share-button { width: 100%; padding: 15px; background: #0099ff; color: white; border: none; border-radius: 30px; font-weight: bold; }

.download-button { display: block; text-decoration: none; background: #07c160; color: white; padding: 12px; border-radius: 10px; margin-bottom: 10px; text-align: center; }

.footer { padding: 20px; text-align: center; opacity: 0.4; font-size: 12px; }

</style>