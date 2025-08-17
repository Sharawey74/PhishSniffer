@echo off
echo ====================================
echo   PhishSniffer Dashboard Launcher
echo ====================================
echo Starting tabbed dashboard interface...
echo.
echo Access your dashboard at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo ====================================

cd /d "%~dp0"
streamlit run streamlit_app.py
