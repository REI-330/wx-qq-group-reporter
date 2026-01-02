@echo off
cd /d "%~dp0"

:: 1. 简单暴力的环境配置（跳过检查，直接执行）
if not exist "backend\.env" (
    echo F | xcopy /y "backend\.env.example" "backend\.env" >nul 2>&1
    if not exist "backend\.env" type nul > "backend\.env"
)

:: 2. 安装/更新 Python 依赖
if not exist "venv" python -m venv venv
echo 正在安装依赖，请稍候...
venv\Scripts\python -m pip install -r backend\requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
venv\Scripts\python -m pip install flask flask-cors flask-limiter gunicorn jinja2 requests python-dotenv ijson pymysql httpx openai jieba -i https://pypi.tuna.tsinghua.edu.cn/simple

:: 3. 安装前端依赖
cd frontend
if not exist "node_modules" call npm install
cd ..

:: 4. 启动服务（双开窗口）
echo 正在启动...
start "Backend" cmd /k "venv\Scripts\python backend\app.py"
start "Frontend" cmd /k "cd frontend && npm run dev"

echo 启动成功！请稍后访问 http://localhost:5173
pause
