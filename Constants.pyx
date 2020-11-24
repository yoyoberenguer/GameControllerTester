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


from multiprocessing import Event, Queue

# SCREEN RESOLUTION
W = 1440
H = 1080

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cdef class CONSTANTS:

    """
    DEFINE YOUR GUI VARIABLES AND CONSTANT

    To access your variables
    1) Create first an instance of the class
        GL = CONSTANTS()
    2) Access the variable
        GL.MAX_FPS      -> point to MAX_FPS VAR

    PS: TO MAKE YOUR VARIABLE VISIBLE FROM AN EXTERNAL ACCESS USE
        cdef public
        If the variable is not public, an attribute error will be raised
    """

    cdef public object SOUND_SERVER, ALL, CLOCK, JOYSTICK, SCREEN, SCREENRECT, EVENT, FONT

    cdef public dict MIXER_SETTINGS

    cdef public int TIME_PASSED_SECONDS, MAX_FPS, SCREENRECT_W2, SCREENRECT_H2,\
        SCREENRECT_W, SCREENRECT_H, SCREENRECT_CENTERX, SCREENRECT_CENTERY, SCREEN_BIT_DEPTH, VIDEO_FLAGS

    cdef public tuple MOUSE_POS
    cdef public long long int FRAME
    cdef public str PATH_TEXTURE, PATH_SOUND, SCREEN_POSITION, PATH_SCREENSHOT, VIDEO_DRIVER_NAME
    cdef public float SFX_VOLUME_VALUE, SOUND_LEVEL, MUSIC_LEVEL, FPS_VALUE, RATIO_X, RATIO_Y
    cdef public bint TICK_SOUND

    def __cinit__(self):

        self.FRAME                   = 0
        self.ALL                     = None
        self.CLOCK                   = Clock()
        self.EVENT                   = None
        self.MOUSE_POS               = (0, 0)
        self.TIME_PASSED_SECONDS     = 0
        self.JOYSTICK                = None

        self.SCREENRECT              = Rect(0, 0, W , H)
        self.RATIO_X                 = W / 1280.0
        self.RATIO_Y                 = H / 1024.0
        self.SCREENRECT_CENTERX      = self.SCREENRECT.centerx
        self.SCREENRECT_CENTERY      = self.SCREENRECT.centery
        self.SCREENRECT_W            = self.SCREENRECT.w
        self.SCREENRECT_H            = self.SCREENRECT.h
        self.SCREENRECT_W2           = self.SCREENRECT.w >> 1
        self.SCREENRECT_H2           = self.SCREENRECT.h >> 1
        self.SCREEN                  = None
        self.SCREEN_POSITION         = "0, 0"
        self.SCREEN_BIT_DEPTH        = 32   # SCREEN VIDEO MODE IN 32 BIT
        self.VIDEO_DRIVER_NAME       = 'windib' # directx
        self.VIDEO_FLAGS             = SWSURFACE # | FULLSCREEN

        self.FPS_VALUE               = 60.0  # CAP THE FRAME RATE TO 60 FPS

        self.PATH_TEXTURE            = 'Assets\\'
        self.PATH_SOUND              = 'Assets\\Sounds\\'
        self.PATH_SCREENSHOT         = 'Assets\\Screenshots\\'

        self.MIXER_SETTINGS          = {"frequency":44100, "size":-16, "channels":2, "buffer":512,
                                        "allowedchanges": "pygame.AUDIO_ALLOW_FREQUENCY_CHANGE | pygame."
                                                          "AUDIO_ALLOW_CHANNELS_CHANGE"}
        self.SOUND_SERVER            = None

        self.SFX_VOLUME_VALUE        = 50.0  # VOLUME AT 50%
        self.SOUND_LEVEL             = self.SFX_VOLUME_VALUE / 100.0  # EQUIVALENT TO 0.5 (VOLUME at 50%)

        self.FONT                    = None
        self.TICK_SOUND              = True    # TICK SOUND EACH TIME A JOYSTICK BUTTON IS PRESSED ?


    def __copy__(self):
        return CONSTANTS
