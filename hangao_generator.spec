# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec — 函告生成系统"""

import sys
from pathlib import Path

ROOT = Path(".").resolve()

# 需要额外声明的隐藏导入，确保 PyInstaller 不会遗漏
HIDDEN_IMPORTS = [
    # Excel 处理链
    "openpyxl",
    "openpyxl.cell._writer",
    "openpyxl.styles",
    "openpyxl.utils",
    "xlrd",
    "xlrd.compdoc",
    "et_xmlfile",
    # pandas 全家桶
    "pandas",
    "pandas.io.excel._openpyxl",
    "pandas.io.excel._xlrd",
    "numpy",
    # Word 模板
    "docxtpl",
    "docx",
    "docx.opc.constants",
    "jinja2",
    "jinja2.ext",
    "lxml",
    "lxml.etree",
    # HTTP
    "requests",
    "urllib3",
    "urllib3.exceptions",
    "certifi",
    "charset_normalizer",
    "idna",
    # HTML 解析（downloader 用）
    "bs4",
    "html.parser",
    # 日期处理
    "dateutil",
    "dateutil.tz",
    "dateutil.parser",
    "dateutil.zoneinfo",
    # Qt 主题
    "qdarktheme",
    # PySide6 可能遗漏的子模块
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "PySide6.QtNetwork",
]

# 禁止自动收集整个 site-packages，
# 只保留项目自身和明确的第三方包
EXCLUDES = [
    "tkinter",
    "test",
    "unittest",
    "pytest",
    "setuptools",
    "pip",
    "wheel",
    "IPython",
    "jupyter",
    "notebook",
    "matplotlib",
    "scipy",
    "PIL",
    "cv2",
    "sqlalchemy",
]

DATAS = [
    # 如果存在 card_mapping.json，也一起打进包
    ("card_mapping.json", ".") if Path("card_mapping.json").exists() else None,
]
DATAS = [d for d in DATAS if d is not None]

a = Analysis(
    ["main.py"],
    pathex=[str(ROOT)],
    binaries=[],
    datas=DATAS,
    hiddenimports=HIDDEN_IMPORTS,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=EXCLUDES,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="函告生成系统",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,        # 如果 upx 在 PATH 里会自动调用
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,   # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,       # 如果需要图标，填 .ico 路径
)