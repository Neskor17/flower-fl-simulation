@echo off
chcp 65001 >nul
title 🌸 Flower Streamlit Dashboard (Local Test)

echo =======================================================
echo   🌸 Flower FL Simulation on Streamlit
echo =======================================================
echo.

cd /d "%~dp0"

echo Menjalankan Streamlit secara lokal...
python -m streamlit run app.py

pause
