# 📊 QQ & WeChat 群聊年度报告分析器 (Web 版)

> **这是一个专为群聊爱好者设计的年度数据可视化工具。**
> 它能够将 QQ (通过 `QQChatExporter`) 或 微信 (通过 `Chatlog`) 导出的聊天记录，转化为精美的、充满仪式感的年度回忆报告。

---

## ✨ 项目核心特性

### 1. 双平台深度兼容
* **QQ 模式**：原生支持 `QQChatExporter` 导出的 JSON 标准格式。
* **微信转换模式**：内置 `Wechat2QQ` 转换引擎，自动识别微信导出格式并智能重构为标准数据集，解决微信群聊中发送者 ID 混杂的问题。

### 2. 多维度数据分析
* **群聊全景报告**：分析活跃度趋势、年度发言榜、高频词云、深夜活跃时段等。
* **个人专属报告**：根据发言习惯自动生成“人格化标签”（如：深夜诗人、复读机、表情包达人），并统计与群友的互动程度。

### 3. AI 驱动的深度洞察
* **智能总结**：结合 AI 分析年度关键词。
* **AI 评语**：为你的年度表现生成独一无二的 AI 幽默评语。

### 4. 极致交互与性能
* **响应式 UI**：采用 Apple 风格与微信原生风格切换的现代化设计。
* **大文件流式处理**：后端针对 GB 级 JSON 文件进行了优化，转换过程低内存占用。
* **隐私保护**：采用 CRC32 对用户身份进行脱敏处理，确保分析过程不泄露隐私。

---

## 🛠️ 技术栈

* **前端**：`Vue 3` + `Vite` + `Axios` (响应式组件化开发)
* **后端**：`Flask` + `Flask-CORS` + `Flask-Limiter` (高并发限流保护)
* **数据库**：`MySQL` / `MariaDB` (存储历史报告元数据)
* **处理库**：`zlib` (身份脱敏), `jieba` (分词), `PIL/Pillow` (图片生成)

---

## 🚀 快速开始（3步启动）

### 📋 第 1 步：安装必需软件

请确保已安装以下软件：

1.  **Python 3.8+** （必需）
    * 下载：[python.org](https://www.python.org/downloads/)
    * 安装时勾选 **"Add Python to PATH"**
2.  **Node.js 16+** （必需）
    * 下载：[nodejs.org](https://nodejs.org/)
3.  **MySQL 5.7+** （可选）
    * 下载：[mysql.com](https://dev.mysql.com/downloads/mysql/)
    * ⚡ 默认使用 JSON 文件存储，**无需安装 MySQL**
4.  **qq-chat-exporter** （必需）
    * 下载：[qq-chat-exporter](https://github.com/shuakami/qq-chat-exporter)
    * 使用该项目导出 QQ 群聊天记录为 JSON
5.  **wechatlog** （可选）
    * 下载：[wechatlog](https://github.com/REI-330/wechat-exporter)
    * 使用该项目导出微信群聊天记录为 JSON

### 🎯 第 2 步：启动服务

#### Windows 用户（推荐使用一键启动）

**首次运行：**
1.  双击运行 `start.bat`
2.  脚本会自动创建配置文件并提示你配置
3.  编辑配置文件（默认配置即可用，无需 MySQL）
    * *(注：也可自己获取对应的 API 后开启 AI 分析、AI 选词，默认关闭。可以在这里配置，也可以开启后在 `backend\envs` 配置，配置后重启后端即可)*
4.  再次运行 `start.bat` 即可启动
5.  可能会遇到的问题: start.bat无法启动,这个时候进行编辑器检查,用 VS Code 或 Notepad++ 打开 start.bat,确保状态栏显示的是 CRLF

**后续运行：**
直接双击 `start.bat` 即可启动所有服务。

---

## ⚙️ 配置说明

首次运行时会自动创建两个配置文件。

## 🖼️ 使用截图

<img width="998" height="1179" alt="image" src="https://github.com/user-attachments/assets/0984120c-3141-401e-ae14-fb32ac6f233f" />
<img width="972" height="1064" alt="image" src="https://github.com/user-attachments/assets/393d32b9-0ef3-4959-81d7-a01e85c429e7" />
<img width="981" height="876" alt="image" src="https://github.com/user-attachments/assets/09980187-dffc-4034-965c-040e71067679" />
<img width="629" height="1079" alt="image" src="https://github.com/user-attachments/assets/4eb42e85-150e-4583-aac3-a5f9bae0f499" />


---

## 📅 数据来源与流程

1.  **数据导出**：
    * **QQ**：使用 `QQChatExporter` 导出 JSON 文件。
    * **微信**：使用 `Chatlog` 等工具导出原始 JSON。
2.  **上传分析**：
    * 访问 Web 页面，选择对应的平台标签。
    * 微信用户上传后，系统会自动触发 `is_wechat_file` 校验并完成格式重组。
3.  **生成报告**：
    * 设定时间范围（如 2023-01-01 至 2023-12-31）。
    * 点击生成，获取专属的网页版或图片版年度报告。

---

## 🛡️ 隐私声明

本项目非常重视用户信息安全：
* 所有聊天记录仅在处理请求时加载，**不进行原始聊天文本的永久存储**。
* 数据库仅存储经过统计后的聚合数据（如发言次数、排名、报告链接）。

---

## 🤝 贡献指南

### 💡 开发计划 (Roadmap)
* [x] 微信 JSON 格式流式转换
* [x] 个人报告人格化标签生成
* [ ] 导出 PDF 格式报告
* [ ] 支持更多主流 AI 模型 API 自定义评语
