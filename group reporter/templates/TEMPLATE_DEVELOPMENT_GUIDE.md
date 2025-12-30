# 模板开发指南

本指南说明如何为 QQ 群年度报告系统创建新的报告模板。

## 📋 目录

1. [快速开始](#快速开始)
2. [模板基本结构](#模板基本结构)
3. [必需的 Props](#必需的-props)
4. [可用的工具函数](#可用的工具函数)
5. [样式指南](#样式指南)
6. [完整示例](#完整示例)
7. [测试和调试](#测试和调试)

---

## 快速开始

### 1. 创建模板文件

在 `frontend/src/templates/` 目录下创建你的模板文件：

```bash
frontend/src/templates/mytemplate.vue
```

### 2. 注册模板

在 `frontend/src/templates/templates.json` 中添加你的模板信息：

```json
{
  "templates": [
    {
        "id": "classic",
        "name": "模板1",
        "description": "最初的模板",
        "component": "classic.vue"
    }
  ]
}
```

### 3. 访问模板

启动开发服务器后，通过以下 URL 访问：

```
http://localhost:5173/report/mytemplate/{reportId}
```

---

## 模板基本结构

每个模板都是一个独立的 Vue 单文件组件，基本结构如下：

```vue
<template>
  <div class="my-template">
    <!-- 你的模板 HTML -->
    <div class="report-container">
      <h1>{{ report.chat_name }}</h1>
      <!-- 更多内容 -->
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useReportUtils } from '../composables/useReportUtils'

// 1. 定义 Props
const props = defineProps({
  report: { type: Object, required: true },
  generatingImage: { type: Boolean, default: false },
  imageUrl: { type: String, default: '' },
  imageError: { type: String, default: '' }
})

// 2. 定义 Emits
defineEmits(['generate-image'])

// 3. 使用工具函数（可选）
const { formatNumber, truncateText } = useReportUtils()

// 4. 自定义逻辑
const myCustomData = computed(() => {
  // 你的计算逻辑
  return '...'
})
</script>

<style scoped>
/* 你的样式 */
.my-template {
  /* ... */
}
</style>
```

---

## 必需的 Props

### 核心 Props（必须接收）

```javascript
const props = defineProps({
  // 报告数据对象（必需）
  report: {
    type: Object,
    required: true
  },
  
  // 图片生成相关（如果需要图片分享功能）
  generatingImage: {
    type: Boolean,
    default: false
  },
  imageUrl: {
    type: String,
    default: ''
  },
  imageError: {
    type: String,
    default: ''
  }
})
```

### 必需的 Emit

如果你的模板支持图片分享功能，需要定义这个事件：

```javascript
defineEmits(['generate-image'])
```

### report 对象结构

`report` prop 包含以下数据：

```javascript
{
  chat_name: "群聊名称",
  message_count: 12345,
  
  // 精选热词（最多10个）
  selected_words: [
    {
      word: "词语",
      freq: 123,
      bar_height: 80,  // 柱状图高度百分比
      ai_comment: "AI 生成的评论",
      contributors_text: "主要贡献者文本",
      samples: ["示例消息1", "示例消息2"],
      segments: [
        { percent: 60, color: "#ff0000" },
        { percent: 40, color: "#00ff00" }
      ],
      legend: [
        { name: "用户1", color: "#ff0000" },
        { name: "用户2", color: "#00ff00" }
      ]
    }
  ],
  
  // 各类排行榜
  rankings: [
    {
      title: "最活跃成员",
      icon: "🏆",
      unit: "条",
      first: {
        name: "用户名",
        value: 1234,
        avatar: "avatar_url"
      },
      others: [
        {
          name: "用户名",
          value: 567,
          avatar: "avatar_url"
        }
      ]
    }
  ],
  
  // 统计数据
  statistics: {
    hourDistribution: {
      "0": 10,
      "1": 5,
      // ... 24小时的分布
      "23": 15
    }
  }
}
```

---

## 可用的工具函数

### 使用 useReportUtils

系统提供了一套通用工具函数，你可以选择性使用：

```javascript
import { useReportUtils } from '../composables/useReportUtils'

const {
  formatNumber,      // 格式化数字
  truncateText,      // 截断文本
  getTitleClass,     // 获取标题样式类
  handleImageError,  // 处理图片加载错误
  getHourHeight,     // 获取时段高度百分比
  getPeakHour        // 获取最活跃时段
} = useReportUtils()
```

### 函数说明

#### `formatNumber(num)`
格式化数字，添加千位分隔符。

```javascript
formatNumber(12345)  // "12,345"
formatNumber(0)      // "0"
```

#### `truncateText(text, maxLength)`
截断文本，超出部分用 "..." 替代。

```javascript
truncateText("这是一段很长的文本", 5)  // "这是一段很..."
```

#### `getTitleClass(chatName)`
根据聊天名称长度返回合适的样式类。

```javascript
getTitleClass("短名")      // "short-title"
getTitleClass("中等长度名称")  // "medium-title"
getTitleClass("非常非常长的群组名称")  // "long-title"
```

#### `handleImageError(event)`
处理头像图片加载失败，隐藏错误图片。

```html
<img :src="avatar" @error="handleImageError">
```

#### `getHourHeight(hour, hourDistribution)`
计算时段柱状图高度百分比。

```javascript
const height = getHourHeight(
  report.statistics.hourDistribution['12'],
  report.statistics.hourDistribution
)
// 返回 0-100 之间的数字
```

#### `getPeakHour(hourDistribution)`
获取最活跃的小时。

```javascript
const peak = getPeakHour(report.statistics.hourDistribution)
// 返回 0-23 之间的小时数
```

### 自定义工具函数

你也可以在模板中定义自己的工具函数：

```javascript
// 自定义格式化函数
const customFormat = (value) => {
  return `自定义: ${value}`
}

// 使用计算属性
const processedData = computed(() => {
  return props.report.selected_words.map(word => ({
    ...word,
    customField: customFormat(word.freq)
  }))
})
```

---

## 样式指南

### 使用现有样式

你可以导入系统提供的基础样式：

```vue
<style scoped>
@import '../report-styles.css';

/* 你的自定义样式 */
.my-template {
  /* ... */
}
</style>
```

### 重要 CSS 类

系统样式提供了以下常用类：

- `.report-container` - 报告主容器（必需，用于图片生成）
- `.header` - 页头区域
- `.section` - 内容区块
- `.word-cards` - 热词卡片容器
- `.rankings-grid` - 排行榜网格

### 自定义主题

创建完全自定义的样式：

```vue
<style scoped>
.my-template {
  /* 主题颜色 */
  --primary-color: #yourcolor;
  --secondary-color: #yourcolor;
  
  /* 背景 */
  background: linear-gradient(135deg, #color1, #color2);
  
  /* 布局 */
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.my-template .report-container {
  /* 确保图片生成正确 */
  background: #ffffff;
  padding: 40px;
  border-radius: 10px;
}
</style>
```

---

## 完整示例

### 简单模板示例

```vue
<template>
  <div class="simple-template">
    <div class="report-container">
      <!-- 标题 -->
      <header class="header">
        <h1>{{ report.chat_name }}</h1>
        <p class="subtitle">年度总结报告</p>
        <div class="stats">
          <span>总消息数: {{ formatNumber(report.message_count) }}</span>
        </div>
      </header>

      <!-- 热词列表 -->
      <section class="hot-words">
        <h2>热门话题</h2>
        <div class="word-list">
          <div 
            v-for="(word, index) in report.selected_words" 
            :key="word.word"
            class="word-item">
            <span class="rank">#{{ index + 1 }}</span>
            <span class="word">{{ word.word }}</span>
            <span class="freq">{{ word.freq }}次</span>
          </div>
        </div>
      </section>

      <!-- 排行榜 -->
      <section class="rankings">
        <h2>成员排行</h2>
        <div 
          v-for="ranking in report.rankings" 
          :key="ranking.title"
          class="ranking-section">
          <h3>{{ ranking.icon }} {{ ranking.title }}</h3>
          <div v-if="ranking.first" class="top-user">
            <img :src="ranking.first.avatar" @error="handleImageError">
            <span>{{ ranking.first.name }}</span>
            <span>{{ ranking.first.value }}{{ ranking.unit }}</span>
          </div>
        </div>
      </section>

      <!-- 分享按钮 -->
      <div class="share-section">
        <button 
          @click="$emit('generate-image')"
          :disabled="generatingImage"
          class="share-btn">
          {{ generatingImage ? '生成中...' : '📸 生成图片' }}
        </button>
        <div v-if="imageUrl" class="share-success">
          <a :href="imageUrl" :download="imageFileName">下载图片</a>
        </div>
        <div v-if="imageError" class="share-error">
          {{ imageError }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useReportUtils } from '../composables/useReportUtils'

const props = defineProps({
  report: { type: Object, required: true },
  generatingImage: { type: Boolean, default: false },
  imageUrl: { type: String, default: '' },
  imageError: { type: String, default: '' }
})

defineEmits(['generate-image'])

const { formatNumber, handleImageError } = useReportUtils()

const imageFileName = computed(() => {
  return `${props.report.chat_name}_报告.png`
})
</script>

<style scoped>
.simple-template {
  background: #f5f5f5;
  min-height: 100vh;
  padding: 20px;
}

.report-container {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  border-radius: 10px;
  padding: 40px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.header {
  text-align: center;
  margin-bottom: 40px;
}

.header h1 {
  font-size: 32px;
  color: #333;
  margin-bottom: 10px;
}

.hot-words, .rankings {
  margin-bottom: 40px;
}

.word-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px;
  border-bottom: 1px solid #eee;
}

.share-btn {
  width: 100%;
  padding: 15px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
}

.share-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
```

---

## 测试和调试

### 本地测试

1. 启动开发服务器：
```bash
cd frontend
npm run dev
```

2. 访问你的模板：
```
http://localhost:5173/report/mytemplate/{reportId}
```

### 获取测试数据

使用现有的报告 ID 进行测试，或通过 API 获取报告列表：

```bash
curl http://localhost:8000/api/reports
```

### 调试技巧

1. **使用 Vue DevTools**：安装浏览器扩展进行组件调试

2. **查看 report 数据**：
```vue
<pre>{{ JSON.stringify(report, null, 2) }}</pre>
```

3. **测试图片生成**：确保 `.report-container` 类存在且可见

4. **样式调试**：使用浏览器开发者工具检查样式应用

---

## 最佳实践

### ✅ 推荐做法

1. **使用语义化的 CSS 类名**
2. **保持 `.report-container` 作为主容器**（图片生成需要）
3. **处理数据缺失情况**：使用 `v-if` 和默认值
4. **优化大数据渲染**：使用 `v-show` 或虚拟滚动
5. **提供加载状态反馈**
6. **支持响应式设计**

### ❌ 避免的做法

1. **不要修改 report 数据**（props 是只读的）
2. **不要依赖全局变量**
3. **不要使用内联样式过多**
4. **不要忘记错误处理**

### 性能优化

```vue
<script setup>
// 使用 computed 缓存计算结果
const processedData = computed(() => {
  return props.report.selected_words.map(word => ({
    ...word,
    displayText: truncateText(word.word, 20)
  }))
})

// 避免在模板中进行复杂计算
// ❌ 不好
// <div>{{ complexCalculation(report.data) }}</div>

// ✅ 好
// <div>{{ cachedResult }}</div>
</script>
```

---


## 发布模板

完成开发后，确保：

1. ✅ 模板文件在 `frontend/src/templates/` 目录
2. ✅ 在 `templates.json` 中注册
3. ✅ 提供模板预览图（可选）
4. ✅ 测试所有功能正常工作
5. ✅ 编写简单的说明文档

---

## 获取帮助

- 📖 查看 `classic.vue` 作为参考示例
- 🔧 查看 `useReportUtils.js` 了解可用工具
- 💬 在 Issues 中提问

祝你创作出精彩的模板！🎨
