# GameControllerTester

### Visual checks of game controller's inputs (e.g PS3, PS4, XBOX). .

The Game controller must be connected to the PC via a USB key (bluetooth) or directly with a usb cable.

1. Connect you usb Joystick 
2. Download Assets directory and start Joystick.exe 

![alt text](https://github.com/yoyoberenguer/python-Fire-Effect-/blob/main/screenshot101.png)

```
DOWNLOAD PS3 DRIVER FROM A SAFE SITE (SCP-DS-Driver-Package-1.2.0.160)
```

## REQUIREMENT:
```
- python > 3.0
- Platform
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
Edit the file fire_demo.py in your favorite python IDE and run it 
Or run joystick.py 
