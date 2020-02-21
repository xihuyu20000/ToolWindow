# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['SpiderTool_win10_64.py'],
             pathex=['E:\\workspace\\workspace-python\\ToolWindow'],
             binaries=[],
             datas=[],
             hiddenimports=['PyQt5.QtWebKit'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='SpiderTool_win10_64',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='SpiderTool_win10_64')
