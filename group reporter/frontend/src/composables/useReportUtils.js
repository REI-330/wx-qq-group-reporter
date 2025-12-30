/**
 * 报告工具函数 Composable
 * 提供通用的数据处理和格式化函数
 * 模板可以选择性使用这些函数
 */

export function useReportUtils() {
  // 格式化数字
  const formatNumber = (num) => {
    if (!num) return '0'
    return num.toLocaleString('zh-CN')
  }

  // 截断文本
  const truncateText = (text, maxLength) => {
    if (!text) return ''
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + '...'
  }

  // 获取标题样式类
  const getTitleClass = (chatName) => {
    const length = chatName ? chatName.length : 0
    if (length <= 6) return 'short-title'
    if (length <= 15) return 'medium-title'
    if (length <= 24) return 'long-title'
    return 'ultra-long-title'
  }

  // 处理图片加载错误
  const handleImageError = (e) => {
    e.target.style.display = 'none'
  }

  // 获取时段高度百分比
  const getHourHeight = (hour, hourDistribution) => {
    if (!hour || !hourDistribution) return 0
    const maxHour = Math.max(...Object.values(hourDistribution))
    return maxHour > 0 ? (hour / maxHour) * 100 : 0
  }

  // 获取最活跃时段
  const getPeakHour = (hourDistribution) => {
    if (!hourDistribution) return 0
    let maxHour = 0
    let maxValue = 0
    for (const [hour, value] of Object.entries(hourDistribution)) {
      if (value > maxValue) {
        maxValue = value
        maxHour = parseInt(hour)
      }
    }
    return maxHour
  }

  return {
    formatNumber,
    truncateText,
    getTitleClass,
    handleImageError,
    getHourHeight,
    getPeakHour
  }
}
