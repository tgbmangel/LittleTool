# -*- mode: python -*-

block_cipher = None


a = Analysis(['buildcloudlittletool.py'],
             pathex=['D:\\python_code\\mywork\\US66\\CloudUserAdd'],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=True,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [('wisonic-cloud.pem','wisonic-cloud.pem','DATA')],
          name='CloudLittleTool',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='wisonic.ico')
