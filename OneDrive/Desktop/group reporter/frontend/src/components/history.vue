<template>
    <div class="v-history-container">
        <div class="v-report-tab-content">
            <div class="v-report-card main-card">
                <h2 class="v-history-title">历史报告</h2>

                <div class="report-type-toggle">
                    <div class="toggle-track">
                        <button :class="['tab-btn', { active: innerType === 'group' }]" @click="switchType('group')">
                            群聊报告
                        </button>
                        <button :class="['tab-btn', { active: innerType === 'personal' }]" @click="switchType('personal')">
                            个人报告
                        </button>
                    </div>
                </div>

                <div class="search-box">
                    <div class="search-input-wrapper">
                        <span class="search-icon">🔍</span>
                        <input v-model="keyword" :placeholder="placeholder" @keyup.enter="search" />
                    </div>
                    <button class="search-btn" @click="search">搜索</button>
                </div>

                <div v-if="loading" class="state-container">
                    <div class="v-report-spinner"></div>
                    <p>正在拉取记录...</p>
                </div>

                <div v-else-if="list.length" class="reports-list">
                    <div v-for="r in list" :key="r.report_id" class="report-item">
                        <div class="report-main-info">
                            <div class="report-header">
                                <h3 v-if="innerType === 'group'">{{ r.chat_name }}</h3>
                                <h3 v-else>{{ r.user_name }} <small>@ {{ r.chat_name }}</small></h3>
                                <span class="report-date">{{ fmt(r.created_at) }}</span>
                            </div>
                            
                            <div class="report-tags">
                                <span class="badge">📊 {{ innerType === 'group' ? r.message_count : r.total_messages }} 条消息</span>
                                <span class="badge id-badge">🆔 {{ r.report_id }}</span>
                            </div>

                            <div class="report-url-box">
                                <code class="url-text">{{ innerType === 'group' ? groupUrl(r.report_id) : personalUrl(r.report_id) }}</code>
                            </div>
                        </div>

                        <div class="report-actions">
                            <button class="btn-action btn-view" @click="$emit('open-' + innerType, r.report_id)">查看</button>
                            <button class="btn-action btn-copy" @click="$emit('copy-' + innerType, r.report_id)">复制</button>
                            <button class="btn-action btn-del" @click="$emit('delete-' + innerType, r.report_id)">删除</button>
                        </div>
                    </div>

                    <div v-if="total > pageSize" class="pagination">
                        <button class="page-btn" :disabled="page === 1" @click="changePage(page - 1)">上一页</button>
                        <div class="page-indicator">第 {{ page }} / {{ pageTotal }} 页</div>
                        <button class="page-btn" :disabled="page === pageTotal" @click="changePage(page + 1)">下一页</button>
                    </div>
                </div>

                <div v-else class="state-container empty-state">
                    <div class="empty-icon">📁</div>
                    <p>暂时没有发现相关报告记录</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
    type: { type: String, default: 'group' },
    list: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false },
    total: { type: Number, default: 0 },
    page: { type: Number, default: 1 },
    pageSize: { type: Number, default: 20 }
})

const emit = defineEmits([
    'update:type', 'update:page', 'search',
    'open-group', 'copy-group', 'delete-group',
    'open-personal', 'copy-personal', 'delete-personal'
])

const keyword = ref('')
const innerType = computed({
    get: () => props.type,
    set: v => emit('update:type', v)
})

const placeholder = computed(() =>
    innerType.value === 'group' ? '搜索群聊名称...' : '搜索群聊或用户名...'
)
const pageTotal = computed(() => Math.ceil(props.total / props.pageSize))

const switchType = t => {
    innerType.value = t
    emit('search', { keyword: keyword.value, page: 1 })
}
const search = () => emit('search', { keyword: keyword.value, page: 1 })
const changePage = p => emit('search', { keyword: keyword.value, page: p })

const groupUrl = id => `${window.location.origin}/report/${id}`
const personalUrl = id => `${window.location.origin}/personal-report/personal-classic/${id}`
const fmt = d => {
    const date = new Date(d);
    return `${date.getMonth() + 1}月${date.getDate()}日 ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
}
</script>

<style scoped>
/* ========== QQ 风格基础变量 ========== */
.v-history-container {
    --qq-blue: #0099FF;
    --qq-blue-light: #F0F9FF;
    --qq-bg: #F2F5F8;
    --card-bg: #FFFFFF;
    --text-main: #333333;
    --text-sub: #888888;
    --border-color: #E0E6ED;
    --danger-red: #FF5A5A;
    
    background: var(--qq-bg);
    min-height: 100vh;
    padding: 20px 15px;
    font-family: -apple-system, "PingFang SC", sans-serif;
}

.v-report-tab-content {
    max-width: 800px;
    margin: 0 auto;
}

/* ========== 主卡片样式 ========== */
.v-report-card {
    background: var(--card-bg);
    border-radius: 24px;
    padding: 30px;
    box-shadow: 0 8px 30px rgba(0, 153, 255, 0.05);
}

.v-history-title {
    font-size: 22px;
    font-weight: bold;
    color: #000;
    margin-bottom: 25px;
}

/* ========== QQ 胶囊式切换按钮 ========== */
.report-type-toggle {
    display: flex;
    justify-content: center;
    margin-bottom: 25px;
}

.toggle-track {
    background: #F0F2F5;
    padding: 4px;
    border-radius: 12px;
    display: flex;
    gap: 4px;
}

.tab-btn {
    border: none;
    padding: 8px 24px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    background: transparent;
    color: var(--text-sub);
}

.tab-btn.active {
    background: #FFF;
    color: var(--qq-blue);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* ========== 搜索框样式 ========== */
.search-box {
    display: flex;
    gap: 12px;
    margin-bottom: 30px;
}

.search-input-wrapper {
    flex: 1;
    position: relative;
    display: flex;
    align-items: center;
}

.search-icon {
    position: absolute;
    left: 15px;
    color: var(--text-sub);
    font-size: 14px;
}

.search-input-wrapper input {
    width: 100%;
    padding: 12px 12px 12px 40px;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    font-size: 15px;
    background: #F9FBFF;
    outline: none;
    transition: all 0.2s;
}

.search-input-wrapper input:focus {
    border-color: var(--qq-blue);
    background: #FFF;
    box-shadow: 0 0 0 3px rgba(0, 153, 255, 0.1);
}

.search-btn {
    background: var(--qq-blue);
    color: white;
    border: none;
    padding: 0 25px;
    border-radius: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: opacity 0.2s;
}

.search-btn:hover { opacity: 0.9; }

/* ========== 报告列表项 ========== */
.reports-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.report-item {
    background: #FFF;
    border: 1px solid var(--border-color);
    border-radius: 20px;
    padding: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: transform 0.2s, box-shadow 0.2s;
}

.report-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(0, 153, 255, 0.08);
    border-color: #BEE3FF;
}

.report-main-info { flex: 1; }

.report-header {
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 8px;
}

.report-header h3 {
    margin: 0;
    font-size: 17px;
    color: #000;
}

.report-header h3 small {
    font-weight: normal;
    font-size: 13px;
    color: var(--text-sub);
}

.report-date {
    font-size: 12px;
    color: var(--text-sub);
}

.report-tags {
    display: flex;
    gap: 8px;
    margin-bottom: 12px;
}

.badge {
    padding: 4px 10px;
    background: var(--qq-blue-light);
    color: var(--qq-blue);
    border-radius: 6px;
    font-size: 12px;
    font-weight: 500;
}

.badge.id-badge {
    background: #F0F2F5;
    color: var(--text-sub);
}

.report-url-box {
    max-width: 400px;
}

.url-text {
    display: block;
    background: #F5F7FA;
    padding: 6px 10px;
    border-radius: 8px;
    font-size: 12px;
    color: var(--qq-blue);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    border: 1px solid #EDF1F5;
}

/* ========== 操作按钮 ========== */
.report-actions {
    display: flex;
    gap: 8px;
    margin-left: 20px;
}

.btn-action {
    border: none;
    padding: 8px 16px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-view { background: var(--qq-blue); color: #FFF; }
.btn-copy { background: #F0F2F5; color: var(--text-main); }
.btn-del { background: #FFF; color: var(--danger-red); border: 1px solid #FFE0E0; }

.btn-del:hover { background: var(--danger-red); color: #FFF; }

/* ========== 分页与空状态 ========== */
.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid var(--border-color);
}

.page-btn {
    padding: 8px 16px;
    border-radius: 10px;
    border: 1px solid var(--border-color);
    background: #FFF;
    cursor: pointer;
}

.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.page-indicator { font-size: 14px; color: var(--text-sub); }

.state-container {
    text-align: center;
    padding: 60px 0;
    color: var(--text-sub);
}

.empty-icon { font-size: 40px; margin-bottom: 15px; opacity: 0.5; }

/* 加载动画 */
.v-report-spinner {
    width: 30px;
    height: 30px;
    border: 3px solid var(--qq-blue-light);
    border-top-color: var(--qq-blue);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin: 0 auto 15px;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* 响应式调整 */
@media (max-width: 600px) {
    .report-item { flex-direction: column; align-items: flex-start; }
    .report-actions { margin-left: 0; margin-top: 15px; width: 100%; justify-content: space-between; }
    .btn-action { flex: 1; text-align: center; }
}
</style>