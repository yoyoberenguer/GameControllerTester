# encoding: utf-8
###cython: boundscheck=False, wraparound=False, nonecheck=False, optimize.use_switch=True

from numpy import linspace, newaxis, repeat, dstack, uint8, arange, putmask, asarray, array

from Constants import CONSTANTS
import time
import pygame
from pygame.rect import Rect
from pygame import mask, image, transform, RLEACCEL, Surface, SWSURFACE, SRCALPHA, BLEND_RGBA_ADD, BLEND_RGBA_MULT, \
    BLEND_RGBA_SUB, BLEND_RGBA_MAX, HWSURFACE
from pygame.surfarray import pixels3d, pixels_alpha, array_alpha
from pygame.image import frombuffer
from pygame.transform import smoothscale, rotozoom, flip
from pygame.math import Vector2

if not pygame.display.get_init():
    raise Exception('\nPygame video mode is not initialized!')

GL = CONSTANTS()
cdef str PATH
PATH          = GL.PATH_TEXTURE
RATIO_X       = GL.RATIO_X
RATIO_Y       = GL.RATIO_Y

try:
    cimport cython
    from cython.parallel cimport prange
    from cpython cimport PyObject_CallFunctionObjArgs, PyObject, \
        PyList_SetSlice, PyObject_HasAttr, PyObject_IsInstance, \
        PyObject_CallMethod, PyObject_CallObject
    from cpython.dict cimport PyDict_DelItem, PyDict_Clear, PyDict_GetItem, PyDict_SetItem, \
        PyDict_Values, PyDict_Keys, PyDict_Items
    from cpython.list cimport PyList_Append, PyList_GetItem, PyList_Size
    from cpython.object cimport PyObject_SetAttr
except ImportError:
    raise ImportError("\n<cython> library is missing on your system."
          "\nTry: \n   C:\\pip install cython on a window command prompt.")

from SpriteSheet import sprite_sheet_per_pixel, sprite_sheet_fs8_numpy
from Surface_tools import smooth_reshape, low_pixel_value_filter_m, black_blanket, reshape, blend_texture, \
    add_transparency_all
from os import path
path_join = path.join

PS3_BACKGROUND = image.load(path_join(PATH, 'PS3_BACKGROUND.jpg')).convert()
PS3_BACKGROUND = transform.smoothscale(PS3_BACKGROUND, GL.SCREENRECT.size)

PS4_BACKGROUND = image.load(path_join(PATH, 'PS4_BACKGROUND.jpg')).convert()
PS4_BACKGROUND = transform.smoothscale(PS4_BACKGROUND, GL.SCREENRECT.size)

XBOX_BACKGROUND = image.load(path_join(PATH,'XBOX_BACKGROUND.jpg')).convert()
XBOX_BACKGROUND = transform.smoothscale(XBOX_BACKGROUND, GL.SCREENRECT.size)

PS3_IMAGE = image.load(path_join(PATH, 'PS3.png')).convert_alpha()
PS3_IMAGE = transform.smoothscale(PS3_IMAGE, (600, 272))

XBOX_IMAGE = image.load(path_join(PATH, 'xbox1.png')).convert_alpha()
XBOX_IMAGE = transform.smoothscale(XBOX_IMAGE, (600, 272)) # (600, 272))

PS4_IMAGE = image.load(path_join(PATH, 'PS4.png'))
PS4_IMAGE = transform.smoothscale(PS4_IMAGE, (600, 272))
PS4_IMAGE.set_colorkey((255, 255, 255, 255))

FRAME_BORDER_LEFT = image.load(path_join(PATH,'dModScreens06.png')).convert_alpha()
FRAME_BORDER_LEFT = transform.smoothscale(FRAME_BORDER_LEFT, (FRAME_BORDER_LEFT.get_width(), 500))

RED_SWITCH1 = image.load(path_join(PATH,'switchRed01.png')).convert_alpha()
RED_SWITCH2 = image.load(path_join(PATH,'switchRed02.png')).convert_alpha()
RED_SWITCH3 = image.load(path_join(PATH,'switchRed03.png')).convert_alpha()

GRAY_BUTTON0 = image.load(path_join(PATH,'modGrayBtn02.png')).convert_alpha()
GRAY_BUTTON0_SELECT = image.load(path_join(PATH,'modGrayBtn03.png')).convert_alpha()

GREEN_SWITCH1 = image.load(path_join(PATH,'switchGreen01.png')).convert_alpha()
GREEN_SWITCH2 = image.load(path_join(PATH,'switchGreen02.png')).convert_alpha()
GREEN_SWITCH3 = image.load(path_join(PATH,'switchGreen03.png')).convert_alpha()

TEXTPREV = image.load(path_join(PATH,'txtPrev01.png')).convert_alpha()
TEXTNEXT = image.load(path_join(PATH,'txtPrev02.png')).convert_alpha()


steps = linspace(0, 1, 30)

cdef blend(int r, object texture_, tuple color_):
    cdef:
        list spritelist = []
        int number

    for number in range(r):
        surface = blend_texture(texture_, steps[number]*100, color_)
        rgb     = pixels3d(surface)
        alpha   = array_alpha(surface)
        surface = add_transparency_all(rgb, alpha, <int>(255.0 * steps[number] / 8.0))
        size    = Vector2(surface.get_size())
        size    *= (number / 60.0)
        surface1 = smoothscale(surface, (<int> size.x, <int> size.y))
        spritelist.append(surface1)
    return spritelist

# WHITE HALO
IMAGE = image.load('Assets\\WhiteHalo.png').convert_alpha()
WHITE_FLAG  = blend(30, IMAGE, (128, 255, 255, 255))
# RED HALO
RED_FLAG    = blend(30, IMAGE, (255, 0, 0, 255))
# GREEN HALO
GREEN_FLAG  = blend(30, IMAGE, (25, 255, 18, 255))
# BLUE HALO
BLUE_FLAG   = blend(30, IMAGE, (15, 25, 255, 255))
# PURPLE HALO
PURPLE_FLAG = blend(30, IMAGE, (120, 15, 255, 255))
