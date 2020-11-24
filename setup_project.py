# distutils: extra_compile_args = -fopenmp
# distutils: extra_link_args = -fopenmp

# USE :
# python setup_Project.py build_ext --inplace

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy

ext_modules = [

    Extension("Sprites",        ["Sprites.pyx"]),
    Extension("SpriteSheet",    ["SpriteSheet.pyx"]),
    Extension("Textures",       ["Textures.pyx"]),
    Extension("Constants",      ["Constants.pyx"]),
    Extension("SoundServer",    ["SoundServer.pyx"]),
    Extension("Surface_tools",  ["Surface_tools.pyx"]),
    Extension("JoystickLayout", ["JoystickLayout.pyx"])
]

setup(
    name="JOYSTICK",
    cmdclass={"build_ext": build_ext},
    ext_modules=ext_modules,
    include_dirs=[numpy.get_include()],
    version='1.00',
    packages=[''],
    author='Yoann Berenguer',
    author_email='yoann.berenguer@hotmail.com',
    description='Joystick Tester'
)
