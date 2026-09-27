@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo 正在启动后端和前端，请勿关闭弹出的两个窗口...
echo.

start "后端 - Automated-stocks" cmd /k "cd /d "%~dp0backend" && pip install -q -r requirements.txt && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

start "前端 - Automated-stocks" cmd /k "cd /d "%~dp0" && npm run dev"

echo.
echo 后端与前端已在两个新窗口中启动。
echo 后端 API: http://localhost:8000   前端页面: http://localhost:5174
echo.
pause
