@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================
echo   函告生成系统 — PyInstaller 打包脚本
echo ============================================
echo.

REM ---------- 可配置项 ----------
REM UPX 目录（用户自行下载后修改此处路径）
set "UPX_DIR=C:\tools\upx"
REM 输出目录
set "OUTPUT_DIR=dist"
REM ---------------------------------

REM 检测 UPX
if exist "%UPX_DIR%\upx.exe" (
    echo [OK] UPX found: %UPX_DIR%\upx.exe
    set "UPX_ARG=--upx-dir=%UPX_DIR%"
) else if exist "%UPX_DIR%\upx" (
    echo [OK] UPX found: %UPX_DIR%\upx
    set "UPX_ARG=--upx-dir=%UPX_DIR%"
) else (
    echo [WARN] UPX not found at "%UPX_DIR%", skip UPX compression
    set "UPX_ARG="
)

echo.
echo [1/2] Cleaning old build artifacts...
if exist build rmdir /s /q build
if exist "%OUTPUT_DIR%" rmdir /s /q "%OUTPUT_DIR%"
if exist "*.spec" (
    REM keep our spec, but delete old auto-generated ones in case of name collision
)

echo [2/2] Running PyInstaller...
echo.

pyinstaller ^
    --distpath="%OUTPUT_DIR%" ^
    --workpath=build ^
    --noconfirm ^
    --clean ^
    --onedir ^
    --name="函告生成系统" ^
    --add-data="card_mapping.json;." ^
    --hidden-import=openpyxl ^
    --hidden-import=openpyxl.cell._writer ^
    --hidden-import=openpyxl.styles ^
    --hidden-import=openpyxl.utils ^
    --hidden-import=xlrd ^
    --hidden-import=xlrd.compdoc ^
    --hidden-import=et_xmlfile ^
    --hidden-import=pandas ^
    --hidden-import=pandas.io.excel._openpyxl ^
    --hidden-import=pandas.io.excel._xlrd ^
    --hidden-import=numpy ^
    --hidden-import=docxtpl ^
    --hidden-import=docx ^
    --hidden-import=docx.opc.constants ^
    --hidden-import=jinja2 ^
    --hidden-import=jinja2.ext ^
    --hidden-import=lxml ^
    --hidden-import=lxml.etree ^
    --hidden-import=requests ^
    --hidden-import=urllib3 ^
    --hidden-import=urllib3.exceptions ^
    --hidden-import=certifi ^
    --hidden-import=charset_normalizer ^
    --hidden-import=idna ^
    --hidden-import=bs4 ^
    --hidden-import=html.parser ^
    --hidden-import=dateutil ^
    --hidden-import=dateutil.tz ^
    --hidden-import=dateutil.parser ^
    --hidden-import=dateutil.zoneinfo ^
    --hidden-import=qdarktheme ^
    --hidden-import=PySide6.QtCore ^
    --hidden-import=PySide6.QtGui ^
    --hidden-import=PySide6.QtWidgets ^
    --hidden-import=PySide6.QtNetwork ^
    --exclude-module=tkinter ^
    --exclude-module=test ^
    --exclude-module=unittest ^
    --exclude-module=pytest ^
    --exclude-module=setuptools ^
    --exclude-module=pip ^
    --exclude-module=matplotlib ^
    --exclude-module=scipy ^
    --exclude-module=PIL ^
    --exclude-module=cv2 ^
    --exclude-module=sqlalchemy ^
    --console ^
    %UPX_ARG% ^
    main.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [FAIL] Packaging failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Packaging complete!
echo   Output: %OUTPUT_DIR%\函告生成系统\
echo ============================================

REM 可选：打开输出目录
REM explorer "%OUTPUT_DIR%"

endlocal
pause
