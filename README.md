# GameControllerTester
```
Support 4 joystick at once (compatibe PS3, PS4, XBOX)
Please report any bugs (project in development).
Compatible with pygame 2.0
```

### Visual checks of game controller's inputs (e.g PS3, PS4, XBOX). .

The Game controller must be connected to the PC via a USB key (bluetooth) or directly with a usb cable.

1. Connect your Joystick(s) via USB  
2. DOWNLOAD PS3 DRIVER FROM A SAFE SITE (SCP-DS-Driver-Package-1.2.0.160) and install the drivers for windows

![alt text](https://github.com/yoyoberenguer/GameControllerTester/blob/master/screenshot1468.png)


## REQUIREMENT:
```
pip install pygame cython numpy==1.19.3

- python > 3.0
- numpy
- pygame 
- Cython
- A compiler such visual studio, MSVC, CGYWIN setup correctly
  on your system.
  - a C compiler for windows (Visual Studio, MinGW etc) install on your system 
  and linked to your windows environment.
  Note that some adjustment might be needed once a compiler is install on your system, 
  refer to external documentation or tutorial in order to setup this process.
  e.g https://devblogs.microsoft.com/python/unable-to-find-vcvarsall-bat/
```
## BUILDING PROJECT:
```
In a command prompt and under the directory containing the source files
C:\>python setup_project.py build_ext --inplace

If the compilation fail, refers to the requirement section and make sure cython 
and a C-compiler are correctly install on your system. 
```
## DEMO
```
Edit the file joystick.py in your favorite python IDE and run it 
Or run C:\>python joystick.py 
