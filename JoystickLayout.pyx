###cython: boundscheck=False, wraparound=False, nonecheck=False, optimize.use_switch=True
# encoding: utf-8

from pygame._freetype import STYLE_STRONG, STYLE_NORMAL

try:
    cimport cython
    from cython.parallel cimport prange
    from cpython cimport PyObject, PyObject_HasAttr, PyObject_IsInstance
    from cpython.list cimport PyList_Append, PyList_GetItem, PyList_Size
except ImportError:
    print("\n<cython> library is missing on your system."
          "\nTry: \n   C:\\pip install cython on a window command prompt.")
    raise SystemExit

try:
    import pygame
    from pygame.math import Vector2
    from pygame import Rect, BLEND_RGB_ADD, HWACCEL, BLEND_RGB_MAX, BLEND_RGB_MULT, HWSURFACE, DOUBLEBUF, FULLSCREEN, \
    SWSURFACE
    from pygame import Surface, SRCALPHA, mask, event
    from pygame.transform import rotate, scale, smoothscale
    from pygame.rect import Rect
    from pygame import freetype
    from pygame.time import Clock
except ImportError as e:
    raise ImportError("\n<Pygame> library is missing on your system."
          "\nTry: \n   C:\\pip install pygame on a window command prompt.")

try:
    from numpy import array
except ImportError as e:
    raise ImportError("\n<numpy> library is missing on your system."
          "\nTry: \n   C:\\pip install numpy on a window command prompt.")

try:
    from Textures import XBOX_IMAGE, PS3_IMAGE, PS4_IMAGE
except ImportError as e:
    raise ImportError("\nlibrary Textures is missing on your system or not cynthonized!.")

cdef int xbox_width, xbox_height
xbox_width, xbox_height = XBOX_IMAGE.get_size()

"""
Motion sensing(3 axes, 6 degrees of freedom)
2× Analog sticks(10 - bit precision)
2× Analog triggers (L2, R2)
6× Pressure - sensitive buttons (Triangle, Circle, Cross, Square, L1, R1)
Pressure - sensitive directional buttons
5× Digital buttons (Start, Select, "PS", L3, R3)

DUALSHOCK 3 PS3 layout connected with USB cable or using bluethooth
with XBOX 360 drivers emulation Buttons x 10 (11 with PS button)
"""

# POSITION OF EACH BUTTONS FOR ORIGINAL TEXTURE 600 x 272
XBOX_BUTTON_VERTICES = array([(451, 106), (491, 80), (410, 80), (450, 56), \
                              (139, 9), (450, 9), (257, 79), (340, 79), \
                              (145, 80), (374, 140), (298, 33)])

XBOX_AXES_VERTICES = array([(145, 80), (145, 80), (139, 9), (374, 140), (450, 9), (450, 9)])
XBOX_DPAD_VERTICES = array([(250, 144), (188, 144), (220, 126), (220, 165)])

cdef float ratio_x, ratio_y

if xbox_width!=600 or xbox_height !=272:
    ratio_x = <float>(xbox_width / 600.0)
    ratio_y = <float>(xbox_height / 272.0)
    print(ratio_x, ratio_y)
    XBOX_BUTTON_VERTICES[:, 0] = XBOX_BUTTON_VERTICES[:, 0] * ratio_x
    XBOX_BUTTON_VERTICES[:, 1] = XBOX_BUTTON_VERTICES[:, 1] * ratio_y
    XBOX_AXES_VERTICES[:, 0] = XBOX_AXES_VERTICES[:, 0] * ratio_x
    XBOX_AXES_VERTICES[:, 1] = XBOX_AXES_VERTICES[:, 1] * ratio_y
    XBOX_DPAD_VERTICES[:, 0] = XBOX_DPAD_VERTICES[:, 0] * ratio_x
    XBOX_DPAD_VERTICES[:, 1] = XBOX_DPAD_VERTICES[:, 1] * ratio_y



# POSITION OF EACH BUTTONS FOR ORIGINAL TEXTURE 600 x 272
PS3_BUTTON_VERTICES = array([(476, 75), (524, 109), (475, 140), (425, 109),
                             (119, 9), (472, 9), (119, 9), (472, 9),
                             (244, 110), (349, 110), (207, 173), (388, 173), (300, 134)])
PS3_AXES_VERTICES = array([(207, 173), (207, 173), (388, 173), (388, 173)])
PS3_DPAD_VERTICES = array([(125, 85), (125, 136), (159, 110), (87, 110)])
cdef int ps3_width, ps3_height
ps3_width, ps3_height = PS3_IMAGE.get_size()
if ps3_width!=600 or ps3_height !=272:
    ratio_x = <float>(ps3_width / 600.0)
    ratio_y = <float>(ps3_height / 272.0)
    print(ratio_x, ratio_y)
    PS3_BUTTON_VERTICES[:, 0] = PS3_BUTTON_VERTICES[:, 0] * ratio_x
    PS3_BUTTON_VERTICES[:, 1] = PS3_BUTTON_VERTICES[:, 1] * ratio_y
    PS3_AXES_VERTICES[:, 0] = PS3_AXES_VERTICES[:, 0] * ratio_x
    PS3_AXES_VERTICES[:, 1] = PS3_AXES_VERTICES[:, 1] * ratio_y
    PS3_DPAD_VERTICES[:, 0] = PS3_DPAD_VERTICES[:, 0] * ratio_x
    PS3_DPAD_VERTICES[:, 1] = PS3_DPAD_VERTICES[:, 1] * ratio_y



# POSITION OF EACH BUTTONS FOR ORIGINAL TEXTURE 600 x 272
PS4_BUTTON_VERTICES = array([(487, 114), (531, 82), (443, 82), (487, 48), (177, 38), (300, 140),
               (425, 40), (202, 138), (395, 136), (118, 7), (487, 7),  (115, 55), (115, 110), (75, 80),
              (145, 80), (296, 58)])
PS4_AXES_VERTICES = array([(202, 138), (202, 138), (395, 138), (395, 138), (118, 7), (487, 7)])
PS4_DPAD_VERTICES = array([(115, 55), (115, 110), (145, 80), (75, 80)])
cdef int ps4_width, ps4_height
ps4_width, ps4_height = PS4_IMAGE.get_size()
if ps4_width!=600 or ps4_height !=272:
    ratio_x = <float>(ps4_width / 600.0)
    ratio_y = <float>(ps4_height / 272.0)
    print(ratio_x, ratio_y)
    PS4_BUTTON_VERTICES[:, 0] = PS4_BUTTON_VERTICES[:, 0] * ratio_x
    PS4_BUTTON_VERTICES[:, 1] = PS4_BUTTON_VERTICES[:, 1] * ratio_y
    PS4_AXES_VERTICES[:, 0] = PS4_AXES_VERTICES[:, 0] * ratio_x
    PS4_AXES_VERTICES[:, 1] = PS4_AXES_VERTICES[:, 1] * ratio_y
    PS4_DPAD_VERTICES[:, 0] = PS4_DPAD_VERTICES[:, 0] * ratio_x
    PS4_DPAD_VERTICES[:, 1] = PS4_DPAD_VERTICES[:, 1] * ratio_y


CONTROLLER_LAYOUT = {

# 11 BUTTONS
'XBOX 360 CONTROLLER':
    {'buttons':
         [{'A          :': XBOX_BUTTON_VERTICES[0]},
          {'B          :': XBOX_BUTTON_VERTICES[1]},
          {'X          :': XBOX_BUTTON_VERTICES[2]},
          {'Y          :': XBOX_BUTTON_VERTICES[3]},
          {'LBUMPER    :': XBOX_BUTTON_VERTICES[4]},
          {'RBUMPER    :': XBOX_BUTTON_VERTICES[5]},
          {'BACK       :': XBOX_BUTTON_VERTICES[6]},
          {'START      :': XBOX_BUTTON_VERTICES[7]},
          {'STICK LEFT :': XBOX_BUTTON_VERTICES[8]},
          {'STICK RIGHT:': XBOX_BUTTON_VERTICES[9]},
          {'XBOX       :': XBOX_BUTTON_VERTICES[10]}],
    'axis':

         [{'8 AXIS X   :': XBOX_AXES_VERTICES[0]},  # 0  range X(-1, 1)
          {'8 AXIS Y   :': XBOX_AXES_VERTICES[1]},  # 1  range Y(-1, 1)
          {'LEFT       :': XBOX_AXES_VERTICES[2]},  # 2  left side (0, 1)
          {'9 AXIS X   :': XBOX_AXES_VERTICES[3]},  #
          {'9 AXIS Y   :': XBOX_AXES_VERTICES[4]},  #
          {'RIGHT      :': XBOX_AXES_VERTICES[5]}],  # right side (0, -1)

    'hats':
         [{'D-PAD RIGHT   :': XBOX_DPAD_VERTICES[0]},  # tuple[1] range 0 or 1
          {'D-PAD LEFT    :': XBOX_DPAD_VERTICES[1]},  # tuple[1] range 0 or -1
          {'D-PAD UP      :': XBOX_DPAD_VERTICES[2]},  # tuple[0] range 0 or 1
          {'D-PAD DOWN    :': XBOX_DPAD_VERTICES[3]}  # tuple[0] range 0 or -1
          ]},

    # # GIOTECK VX2 2.4G Wireless PS3 controller layout connected
    # # with USB cable or using bluethooth
    # # with XBOX 360 drivers emulation
    # # Buttons x 13
    # 'GIOTECK VX2 2.4G WIRELESS CONTROLLER':
    #     {'buttons':
    #          [{'TRIANGLE   :': PS3_BUTTON_VERTICES[0]},  # 0
    #           {'CIRCLE     :': PS3_BUTTON_VERTICES[1]},  # 1
    #           {'X          :': PS3_BUTTON_VERTICES[2]},  # 2
    #           {'SQUARE     :': PS3_BUTTON_VERTICES[3]},  # 3
    #           {'L1         :': PS3_BUTTON_VERTICES[4]},  # 4
    #           {'R1         :': PS3_BUTTON_VERTICES[5]},  # 5
    #           {'L2         :': PS3_BUTTON_VERTICES[6]},  # 6
    #           {'R2         :': PS3_BUTTON_VERTICES[7]},  # 7
    #           {'SELECT     :': PS3_BUTTON_VERTICES[8]},  # 8
    #           {'START      :': PS3_BUTTON_VERTICES[9]},  # 9
    #           {'L3 PRESSED :': PS3_BUTTON_VERTICES[10]},  # 10
    #           {'R3 PRESSED :': PS3_BUTTON_VERTICES[11]},  # 11
    #           {'PS         :': PS3_BUTTON_VERTICES[12]}],  # 12
    #      'axis':
    #      # -------------------------------
    #      # AXIS x 4 detected (axis 2 controlling right pad and left pad)
    #          [{'L3 X       : ': PS3_AXES_VERTICES[0]},  # 0  range -1, 1
    #           {'L3 Y       : ': PS3_AXES_VERTICES[1]},  # 1  range -1, 1
    #           {'R3 X       : ': PS3_AXES_VERTICES[2]},  # 2  range -1, 1
    #           {'R3 Y       : ': PS3_AXES_VERTICES[3]}],  # 3  range -1, 1
    #      'hats':
    #
    #      # HATS return a tuple (0, 0)
    #          [{'D-PAD UP      :': PS3_DPAD_VERTICES[2]},  # tuple[1] range 0 or 1
    #           {'D-PAD DOWN    :': PS3_DPAD_VERTICES[3]},  # tuple[1] range 0 or -1
    #           {'D-PAD RIGHT   :': PS3_DPAD_VERTICES[0]},  # tuple[0] range 0 or 1
    #           {'D-PAD LEFT    :': PS3_DPAD_VERTICES[1]}  # tuple[0] range 0 or -1
    #           ]},

    # 13 BUTTONS
    "PLAYSTATION 3 CONTROLLER":
        {'buttons':
             [{'TRIANGLE   :': PS3_BUTTON_VERTICES[0]},  # 0
              {'CIRCLE     :': PS3_BUTTON_VERTICES[1]},  # 1
              {'X          :': PS3_BUTTON_VERTICES[2]},  # 2
              {'SQUARE     :': PS3_BUTTON_VERTICES[3]},  # 3
              {'L1         :': PS3_BUTTON_VERTICES[4]},  # 4
              {'R1         :': PS3_BUTTON_VERTICES[5]},  # 5
              {'L2         :': PS3_BUTTON_VERTICES[6]},  # 6
              {'R2         :': PS3_BUTTON_VERTICES[7]},  # 7
              {'SELECT     :': PS3_BUTTON_VERTICES[8]},  # 8
              {'START      :': PS3_BUTTON_VERTICES[9]},  # 9
              {'L3 PRESSED :': PS3_BUTTON_VERTICES[10]},  # 10
              {'R3 PRESSED :': PS3_BUTTON_VERTICES[11]},  # 11
              {'PS         :': PS3_BUTTON_VERTICES[12]}],  # 12
        'axis':
         # -------------------------------
         # AXIS x 4 detected (axis 2 controlling right pad and left pad)
             [{'L3 X       : ': PS3_AXES_VERTICES[0]},  # 0  range -1, 1
              {'L3 Y       : ': PS3_AXES_VERTICES[1]},  # 1  range -1, 1
              {'R3 X       : ': PS3_AXES_VERTICES[2]},  # 2  range -1, 1
              {'R3 Y       : ': PS3_AXES_VERTICES[3]}],  # 3  range -1, 1
        'hats':

         # HATS return a tuple (0, 0)
             [{'D-PAD UP      :': PS3_DPAD_VERTICES[2]},  # tuple[1] range 0 or 1
              {'D-PAD DOWN    :': PS3_DPAD_VERTICES[3]},  # tuple[1] range 0 or -1
              {'D-PAD RIGHT   :': PS3_DPAD_VERTICES[0]},  # tuple[0] range 0 or 1
              {'D-PAD LEFT    :': PS3_DPAD_VERTICES[1]}  # tuple[0] range 0 or -1
              ]},


    "PLAYSTATION 4 CONTROLLER":
        # Buttons x 16
        {'buttons':
             [{'X        :': PS4_BUTTON_VERTICES[0]},  # 0
              {'CIRCLE   :': PS4_BUTTON_VERTICES[1]},  # 1
              {'SQUARE   :': PS4_BUTTON_VERTICES[2]},  # 2
              {'TRIANGLE :': PS4_BUTTON_VERTICES[3]},  # 3
              {'SHARE    :': PS4_BUTTON_VERTICES[4]},  # 4
              {'PS       :': PS4_BUTTON_VERTICES[5]},  # 5
              {'OPTIONS  :': PS4_BUTTON_VERTICES[6]},  # 6 duplicate with axis
              {'L3       :': PS4_BUTTON_VERTICES[7]},  # 7 duplicate with axis
              {'R3       :': PS4_BUTTON_VERTICES[8]},  # 8
              {'L2       :': PS4_BUTTON_VERTICES[9]},  # 9
              {'R2       :': PS4_BUTTON_VERTICES[10]},  # 10
              {'UP       :': PS4_BUTTON_VERTICES[11]},  # 11
              {'DOWN     :': PS4_BUTTON_VERTICES[12]},  # 12
              {'LEFT     :': PS4_BUTTON_VERTICES[13]},  # 13
              {'RIGHT    :': PS4_BUTTON_VERTICES[14]}, #14
              {'TOUCHPAD :': PS4_BUTTON_VERTICES[15]}], #15
        'axis':
         # -------------------------------
         # AXIS x 6 detected (axis 2 controlling right pad and left pad)
             [{'L3 X     :': PS4_AXES_VERTICES[0]},  # 0  range -1, 1
              {'L3 Y     :': PS4_AXES_VERTICES[1]},  # 1  range -1, 1
              {'R3 X     :': PS4_AXES_VERTICES[2]},  # 2  range -1, 1
              {'R3 Y     :': PS4_AXES_VERTICES[3]},  # 3  range -1, 1
              {'L2       :': PS4_AXES_VERTICES[4]},  # 4  right side (-1, 1)
              {'R2       :': PS4_AXES_VERTICES[5]}],  # 5  left side (-1, 1)
        'hats':
         # HATS return a tuple (0, 0)
             [{'D-PAD UP      :': PS4_DPAD_VERTICES[0]},  # tuple[1] range 0 or 1
              {'D-PAD DOWN    :': PS4_DPAD_VERTICES[1]},  # tuple[1] range 0 or -1
              {'D-PAD RIGHT   :': PS4_DPAD_VERTICES[2]},  # tuple[0] range 0 or 1
              {'D-PAD LEFT    :': PS4_DPAD_VERTICES[3]}  # tuple[0] range 0 or -1
              ]}

}

OPTIONS_MENU_JOYSTICK = {
    1: {'TEXT': 'Disconnected', 'SIZE': 16,
        'FOREGROUND': pygame.Color(220, 198, 218), 'BACKGROUND': pygame.Color(10, 10, 36),
        'SELECT_COLOR': pygame.Color(220, 198, 10), 'ACTIVE': False, 'EXPLAIN': 'JOYSTICK STATUS',
        'POSITION': (400, 100),
        'FUNCTION': None, 'STYLE': freetype.STYLE_NORMAL}
}