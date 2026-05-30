$ErrorActionPreference = "Stop"
$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8

Write-Host "============================================"
Write-Host "  函告生成系统 — PyInstaller 打包脚本"
Write-Host "============================================"
Write-Host ""

# ========== 可配置项 ==========
$UPXDir     = "C:\tools\upx"
$OutputDir  = "dist"
$SpecFile   = "hangao_generator.spec"
# ==============================

# 检测 UPX
$UPXExe = $null
if (Test-Path "$UPXDir\upx.exe") {
    $UPXExe = "$UPXDir\upx.exe"
}
elseif (Test-Path "$UPXDir\upx") {
    $UPXExe = "$UPXDir\upx"
}

if ($UPXExe) {
    Write-Host "[OK] UPX found: $UPXExe" -ForegroundColor Green
    $UPXArg = "--upx-dir=$UPXDir"
}
else {
    Write-Host "[WARN] UPX not found at '$UPXDir', skip UPX compression" -ForegroundColor Yellow
    $UPXArg = ""
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# 需要显式声明的隐藏导入
$hiddenImports = @(
    # Excel 处理链
    "openpyxl", "openpyxl.cell._writer", "openpyxl.styles", "openpyxl.utils",
    "xlrd", "xlrd.compdoc", "et_xmlfile",
    # pandas 全家桶
    "pandas", "pandas.io.excel._openpyxl", "pandas.io.excel._xlrd", "numpy",
    # Word 模板
    "docxtpl", "docx", "docx.opc.constants", "jinja2", "jinja2.ext",
    "lxml", "lxml.etree",
    # HTTP
    "requests", "urllib3", "urllib3.exceptions",
    "certifi", "charset_normalizer", "idna",
    # HTML 解析 (downloader)
    "bs4", "html.parser",
    # 日期处理
    "dateutil", "dateutil.tz", "dateutil.parser", "dateutil.zoneinfo",
    # Qt 主题
    "qdarktheme",
    # PySide6
    "PySide6.QtCore", "PySide6.QtGui", "PySide6.QtWidgets", "PySide6.QtNetwork"
)

# 排除无关模块，缩小体积
$excludes = @(
    "tkinter", "test", "unittest", "pytest", "setuptools", "pip", "wheel",
    "matplotlib", "scipy", "PIL", "cv2", "sqlalchemy",
    "IPython", "jupyter", "notebook"
)

Write-Host "[1/2] Cleaning old build artifacts..." -ForegroundColor Cyan
if (Test-Path "build")       { Remove-Item "build" -Recurse -Force }
if (Test-Path $OutputDir)    { Remove-Item $OutputDir -Recurse -Force }

Write-Host "[2/2] Running PyInstaller..." -ForegroundColor Cyan
Write-Host ""

# 构建命令行参数
$args = @(
    "--distpath=`"$OutputDir`"",
    "--workpath=build",
    "--noconfirm",
    "--clean",
    "--onedir",
    "--name=函告生成系统",
    "--console"
)

# 添加 --add-data
if (Test-Path "card_mapping.json") {
    $args += "--add-data=card_mapping.json;."
}

# 添加隐藏导入
foreach ($imp in $hiddenImports) {
    $args += "--hidden-import=$imp"
}

# 添加排除项
foreach ($ex in $excludes) {
    $args += "--exclude-module=$ex"
}

# UPX
if ($UPXArg) {
    $args += $UPXArg
}

$args += "main.py"

# 执行
$pyinstallerCmd = "pyinstaller $args"
Write-Host "pyinstaller $args" -ForegroundColor DarkGray

$proc = Start-Process -FilePath "pyinstaller" -ArgumentList $args -NoNewWindow -Wait -PassThru

if ($proc.ExitCode -ne 0) {
    Write-Host ""
    Write-Host "[FAIL] Packaging failed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "============================================"
Write-Host "  Packaging complete!"
Write-Host "  Output: $OutputDir\函告生成系统\"
Write-Host "============================================"

# 可选：自动打开输出目录
# Invoke-Item "$OutputDir"

Read-Host "Press Enter to exit"
