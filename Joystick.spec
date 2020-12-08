# -*- mode: python -*-

block_cipher = None


a = Analysis(['Joystick.py'],
             pathex=['C:\\Users\\yoann\\PycharmProjects\\Joystick_module'],
             binaries=[],
             datas=[('*.pyd', '.'),
                    ('*.pxd', '.'),
                    ('Assets/*.png', './Assets'),
                    ('Assets/*.wav', './Assets'),
                    ('Assets/*.ttf', './Assets'),
                    ('Assets/*.jpg', './Assets'),
                   ],

             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='JoystickController',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
