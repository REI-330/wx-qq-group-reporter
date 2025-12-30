# 模板图片样式自定义指南

#### ❗本文档由 AI 生成，暂未人工校验

## 概述

当用户点击"生成分享图"按钮时，后端会使用 Playwright 访问当前报告页面并截图。在这个过程中，后端会在 URL 中添加 `?mode=share` 参数，模板可以检测这个参数来应用专门的分享版样式。

## 工作流程

```
用户点击"生成分享图"
    ↓
前端调用 POST /api/reports/{id}/generate-image
    ↓
后端构建 URL: /report/{template}/{id}?mode=share
    ↓
Playwright 访问该 URL
    ↓
模板检测到 mode=share 参数
    ↓
应用分享版专属样式
    ↓
Playwright 截图并返回
```

## 在模板中实现

### 1. 检测分享模式

在模板组件中添加检测逻辑：

```vue
<script setup>
import { ref, onMounted, computed } from 'vue'

// 检测是否为分享模式
const isShareMode = ref(false)

onMounted(() => {
  const urlParams = new URLSearchParams(window.location.search)
  isShareMode.value = urlParams.get('mode') === 'share'
})

// 或者使用 computed
const isShareMode = computed(() => {
  return window.location.search.includes('mode=share')
})
</script>
```

### 2. 应用条件样式

#### 方法 A：使用 v-if 控制元素显示

```vue
<template>
  <div class="report-container">
    <!-- 分享版隐藏操作按钮 -->
    <div v-if="!isShareMode" class="share-section">
      <button @click="$emit('generate-image')">
        生成分享图
      </button>
    </div>
    
    <!-- 分享版显示水印 -->
    <div v-if="isShareMode" class="watermark">
      由 XX 工具生成
    </div>
  </div>
</template>
```

#### 方法 B：使用动态 class

```vue
<template>
  <div :class="['report-container', { 'share-mode': isShareMode }]">
    <!-- 内容 -->
  </div>
</template>

<style scoped>
/* 普通显示模式 */
.share-section {
  display: block;
}

/* 分享模式：隐藏按钮 */
.share-mode .share-section {
  display: none;
}

/* 分享模式：添加水印 */
.share-mode::after {
  content: '由 XX 工具生成';
  position: fixed;
  bottom: 10px;
  right: 10px;
  font-size: 12px;
  opacity: 0.5;
}
</style>
```

#### 方法 C：使用动态样式对象

```vue
<template>
  <div class="report-container">
    <div 
      class="header"
      :style="headerStyle"
    >
      <!-- 内容 -->
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const isShareMode = computed(() => {
  return window.location.search.includes('mode=share')
})

const headerStyle = computed(() => {
  if (isShareMode.value) {
    return {
      padding: '40px 20px',  // 分享版更大的内边距
      fontSize: '18px'        // 分享版更大的字体
    }
  }
  return {
    padding: '30px 20px',
    fontSize: '16px'
  }
})
</script>
```

### 3. 完整示例

```vue
<template>
  <div :class="containerClasses">
    <!-- 报告头部 -->
    <div class="header">
      <h1>{{ report.chat_name }}</h1>
      <p>年度报告</p>
    </div>
    
    <!-- 报告内容 -->
    <div class="content">
      <!-- 热词、榜单等 -->
    </div>
    
    <!-- 分享按钮区域 - 仅在非分享模式显示 -->
    <div v-if="!isShareMode" class="share-section">
      <button 
        @click="$emit('generate-image')"
        :disabled="generatingImage"
      >
        <span v-if="!generatingImage">📸 生成分享图</span>
        <span v-else class="loading-dots">生成中</span>
      </button>
      
      <div v-if="imageError" class="share-error">
        {{ imageError }}
      </div>
    </div>
    
    <!-- 水印 - 仅在分享模式显示 -->
    <div v-if="isShareMode" class="watermark">
      <p>扫码查看完整报告</p>
      <!-- 可以添加二维码等 -->
    </div>
    
    <!-- 页脚 -->
    <div class="footer">
      <p>{{ new Date().getFullYear() }} 年度报告</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Props
const props = defineProps({
  report: {
    type: Object,
    required: true
  },
  generatingImage: {
    type: Boolean,
    default: false
  },
  imageError: {
    type: String,
    default: ''
  }
})

// Emits
defineEmits(['generate-image'])

// 检测分享模式
const isShareMode = ref(false)

onMounted(() => {
  const urlParams = new URLSearchParams(window.location.search)
  isShareMode.value = urlParams.get('mode') === 'share'
  
  if (isShareMode.value) {
    console.log('📸 分享模式已激活')
  }
})

// 动态容器类名
const containerClasses = computed(() => ({
  'report-container': true,
  'share-mode': isShareMode.value,
  'display-mode': !isShareMode.value
}))
</script>

<style scoped>
/* 基础样式 */
.report-container {
  width: 450px;
  background: #1a1a1a;
}

/* 分享模式特殊样式 */
.share-mode .header {
  padding: 40px 20px 70px;  /* 更大的内边距 */
}

.share-mode .content {
  /* 分享版可能需要调整间距 */
}

/* 水印样式 */
.watermark {
  background: rgba(0, 0, 0, 0.8);
  padding: 20px;
  text-align: center;
  color: #d4af37;
}

/* 显示模式下隐藏水印 */
.display-mode .watermark {
  display: none;
}
</style>
```

## 常见的分享版自定义需求

### 1. 隐藏交互元素

```vue
<!-- 分享版隐藏所有按钮 -->
<div v-if="!isShareMode" class="interactive-elements">
  <button>生成图片</button>
  <button>重新生成</button>
</div>
```

### 2. 添加水印或署名

```vue
<div v-if="isShareMode" class="attribution">
  <p>由 XX 工具生成</p>
  <p>扫码查看完整报告</p>
  <img v-if="qrCodeUrl" :src="qrCodeUrl" alt="二维码">
</div>
```

### 3. 调整布局和间距

```css
/* 分享版：更紧凑的布局 */
.share-mode .section {
  margin-bottom: 15px;  /* 原本是 20px */
}

.share-mode .word-card {
  padding: 15px;  /* 原本是 18px */
}
```

### 4. 优化字体大小

```css
/* 分享版：更大的字体以便截图后清晰 */
.share-mode .header h1 {
  font-size: 42px;  /* 原本是 38px */
}

.share-mode .word-card-title {
  font-size: 26px;  /* 原本是 24px */
}
```

### 5. 添加背景装饰

```css
/* 分享版：添加特殊背景 */
.share-mode::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    linear-gradient(45deg, rgba(212,175,55,0.05) 0%, transparent 100%);
  pointer-events: none;
}
```

## 测试分享模式

### 在浏览器中测试

在浏览器中访问报告页面时，手动添加 `?mode=share` 参数：

```
http://localhost:5173/report/classic/your-report-id?mode=share
```

### 使用开发者工具

1. 打开报告页面
2. 打开浏览器开发者工具（F12）
3. 在控制台执行：
   ```javascript
   window.location.href = window.location.href + '?mode=share'
   ```

## 注意事项

1. **Playwright 截图分辨率**
   - 宽度：450px
   - 设备像素比：2（即实际 900px）
   - 确保样式在这个尺寸下良好显示

2. **CSS 兼容性**
   - Playwright 使用 Chromium，支持所有现代 CSS 特性
   - `repeating-linear-gradient`、`backdrop-filter` 等都完美支持

3. **字体加载**
   - 确保自定义字体已加载完成
   - Playwright 会等待 `networkidle` 事件
   - 如需额外等待，可以在模板中添加：
     ```javascript
     onMounted(() => {
       if (isShareMode.value) {
         // 等待字体加载
         document.fonts.ready.then(() => {
           console.log('✅ 字体已加载')
         })
       }
     })
     ```

4. **性能优化**
   - 分享模式下移除不必要的动画
   - 避免大量的 DOM 操作
   - 使用 CSS 而非 JavaScript 实现样式变化

## 调试技巧

### 在模板中添加调试信息

```vue
<div v-if="isShareMode" style="position: fixed; top: 0; left: 0; background: red; color: white; padding: 5px; z-index: 9999;">
  SHARE MODE ACTIVE
</div>
```

### 查看后端生成的 URL

后端会在控制台打印访问的 URL：

```
🖼️ 开始生成图片: report-id (模板: classic, 格式: for_share)
   🌐 访问: http://localhost:5173/report/classic/report-id?mode=share
```

## 最佳实践

1. **保持简洁**：分享图应该去除所有交互元素，只保留内容
2. **添加标识**：添加水印或来源标识，但不要太显眼
3. **优化可读性**：适当增大字体和间距
4. **测试截图**：在实际生成前测试 `?mode=share` 的显示效果
5. **考虑分享场景**：社交媒体分享时，图片会被缩小显示，确保关键信息清晰

## 示例：Classic 模板的分享版改造

```vue
<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps(['report', 'generatingImage', 'imageError'])
defineEmits(['generate-image'])

const isShareMode = ref(false)

onMounted(() => {
  isShareMode.value = new URLSearchParams(window.location.search).get('mode') === 'share'
})
</script>

<template>
  <div :class="['report-container', { 'for-share': isShareMode }]">
    <!-- 内容保持不变 -->
    
    <!-- 分享按钮：仅显示模式显示 -->
    <div v-if="!isShareMode" class="share-section">
      <!-- 按钮 -->
    </div>
    
    <!-- 底部标识：仅分享模式显示 -->
    <div v-if="isShareMode" class="share-footer">
      <p>📊 QQ群年度报告 · 2024</p>
    </div>
  </div>
</template>

<style scoped>
.for-share {
  /* 分享版特殊样式 */
}
</style>
