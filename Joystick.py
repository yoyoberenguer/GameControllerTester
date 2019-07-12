# encoding: utf-8
"""

                   GNU GENERAL PUBLIC LICENSE

                       Version 3, 29 June 2007


 Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>

 Everyone is permitted to copy and distribute verbatim copies

 of this license document, but changing it is not allowed.
 """
from SoundServer import SoundControl

__author__ = "Yoann Berenguer"
__copyright__ = "Copyright 2007, Cobra Project"
__credits__ = ["Yoann Berenguer"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Yoann Berenguer"
__email__ = "yoyoberenguer@hotmail.com"
__status__ = "Joystick Demo"

import pygame
from pygame import freetype
import numpy
import _pickle as pickle

CONTROLLER_LAYOUT = {
    # Motion sensing(3 axes, 6 degrees of freedom)
    # 2× Analog
    # sticks(10 - bit
    # precision)
    # 2× Analog
    # triggers
    # (L2, R2)
    # 6× Pressure - sensitive
    # buttons
    # (Triangle, Circle, Cross, Square, L1, R1)
    # Pressure - sensitive
    # directional
    # buttons
    # 5× Digital
    # buttons
    # (Start, Select, "PS", L3, R3)

    # DUALSHOCK 3 PS3 layout connected with USB cable or using bluethooth
    # with XBOX 360 drivers emulation
    # Buttons x 10 (11 with PS button)

    'Controller (XBOX 360 For Windows)':
    # |----- NAME ------------| NUMBER
        {'buttons':
             [{'A          :': (575, 327)},  # 0
              {'B          :': (617, 300)},  # 1
              {'X          :': (535, 300)},  # 2
              {'Y          :': (578, 273)},  # 3
              {'LBUMPER    :': (265, 230)},  # 4
              {'RBUMPER    :': (576, 230)},  # 5
              {'BACK       :': (380, 300)},  # 6
              {'START      :': (467, 300)},  # 7
              {'STICK LEFT :': (270, 300)},  # 8
              {'STICK RIGHT:': (500, 361)},  # 9
              {'XBOX       :': (423, 253)}],  # 10
         'axis':
         # ---------------------------------
         # AXIS ( 2 axis + 2 pads left right
         # Left / right same axis but values differs,
         # left side (0, 1) right side (0, -1)
             [{'8 AXIS X   :': (270, 300)},  # 0  range X(-1, 1)
              {'8 AXIS Y   :': (270, 300)},  # 1  range Y(-1, 1)
              {'LEFT/RIGHT :': [(265, 230), (576, 230)]},  # 2  left side (0, 1) right side (0, -1)
              {'9 AXIS X   :': (500, 361)},  # 9  range X(-1, 1)
              {'9 AXIS Y   :': (500, 361)}],  # 9  range Y(-1, 1)
         # ----------------------------------
         # HATS return a tuple (0, 0)
         'hats':
             [{'D-PAD RIGHT   :': (375, 363)},  # tuple[1] range 0 or 1
              {'D-PAD LEFT    :': (320, 363)},  # tuple[1] range 0 or -1
              {'D-PAD UP      :': (346, 344)},  # tuple[0] range 0 or 1
              {'D-PAD DOWN    :': (346, 384)}  # tuple[0] range 0 or -1
              ]},

    # GIOTECK VX2 2.4G Wireless PS3 controller layout connected
    # with USB cable or using bluethooth
    # with XBOX 360 drivers emulation
    # Buttons x 13
    'Gioteck VX2 2.4G Wireless Controller':
        {'buttons':
             [{'TRIANGLE   :': (530, 326)},  # 0
              {'CIRCLE     :': (559, 355)},  # 1
              {'X          :': (530, 385)},  # 2
              {'SQUARE     :': (498, 356)},  # 3
              {'L1         :': (310, 272)},  # 4
              {'R1         :': (530, 272)},  # 5
              {'L2         :': (310, 272)},  # 6
              {'R2         :': (530, 272)},  # 7
              {'SELECT     :': (387, 356)},  # 8
              {'START      :': (451, 356)},  # 9
              {'L3 PRESSED :': (362, 411)},  # 10
              {'R3 PRESSED :': (474, 411)},  # 11
              {'PS         :': (420, 376)}],  # 12
         'axis':
         # -------------------------------
         # AXIS x 4 detected (axis 2 controlling right pad and left pad)
             [{'L3 X       : ': (362, 411)},  # 0  range -1, 1
              {'L3 Y       : ': (362, 411)},  # 1  range -1, 1
              {'R3 X       : ': (474, 411)},  # 2  range -1, 1
              {'R3 Y       : ': (474, 411)}],  # 3  range -1, 1
         'hats':
         # ----------------------------------
         # HATS return a tuple (0, 0)
             [{'D-PAD UP      :': (330, 355)},  # tuple[1] range 0 or 1
              {'D-PAD DOWN    :': (287, 355)},  # tuple[1] range 0 or -1
              {'D-PAD RIGHT   :': (309, 336)},  # tuple[0] range 0 or 1
              {'D-PAD LEFT    :': (309, 375)}  # tuple[0] range 0 or -1
              ]},

    # DUALSHOCK 4 PS3 layout connected with USB cable or using bluethooth
    # with XBOX 360 drivers emulation
    # 6 axis motion sensing (3 axis accelerometer, 3 axis gyroscope)
    # 2× Analog sticks
    # 2× Analog triggers
    # (L2, R2)
    # 2× Pressure-sensitive buttons
    # (L1, R1)
    # 10× Digital buttons
    # (Triangle, Circle, Cross, Square, L3, R3, "PS", SHARE, OPTIONS, touchpad click)
    # Digital directional buttons
    # 2 point capacitive touchpad with click mechanism (see buttons)[24]
    'Wireless Controller':
    # Buttons x 14
        {'buttons':
             [{'SQUARE   :': (528, 307)},  # 0
              {'X        :': (560, 333)},  # 1
              {'CIRCLE   :': (590, 306)},  # 2
              {'TRIANGLE :': (560, 281)},  # 3
              {'L1       :': (295, 245)},  # 4
              {'R1       :': (555, 245)},  # 5
              {'L2       :': (295, 245)},  # 6 duplicate with axis
              {'R2       :': (555, 245)},  # 7 duplicate with axis
              {'SHARE    :': (340, 270)},  # 8
              {'OPTIONS  :': (515, 270)},  # 9
              {'L3       :': (358, 355)},  # 10
              {'R3       :': (495, 355)},  # 11
              {'PS       :': (425, 355)},  # 12
              {'TRIGGER  :': (430, 288)}],  # 13
         'axis':
         # -------------------------------
         # AXIS x 6 detected (axis 2 controlling right pad and left pad)
             [{'L3 X     :': (358, 355)},  # 0  range -1, 1
              {'L3 Y     :': (358, 355)},  # 1  range -1, 1
              {'R3 X     :': (495, 355)},  # 2  range -1, 1
              {'R3 Y     :': (495, 355)},  # 3  range -1, 1
              {'R2       :': (555, 245)},  # 4  right side (-1, 1)
              {'L2       :': (295, 245)}],  # 5  left side (-1, 1)
         'hats':
         # ----------------------------------
         # HATS return a tuple (0, 0)
             [{'D-PAD UP   :': (317, 305)},  # tuple[1] range 0 or 1
              {'D-PAD DOWN :': (269, 305)},  # tuple[1] range 0 or -1
              {'D-PAD RIGHT:': (293, 286)},  # tuple[0] range 0 or 1
              {'D-PAD LEFT :': (293, 323)}  # tuple[0] range 0 or -1
              ]}
}

"""
        {'buttons': [
            {'TRIANGLE :': (0, 0)},  # 0
            {'CIRCLE   :': (0, 0)},  # 1
            {'X        :': (0, 0)},  # 2
            {'SQUARE   :': (0, 0)},  # 3
            {'L1       :': (0, 0)},  # 4
            {'R1       :': (0, 0)},  # 5
            {'SELECT   :': (0, 0)},  # 6
            {'START    :': (0, 0)},  # 7
            {'L3 CLICK :': (0, 0)},  # 8
            {'R3 CLICK :': (0, 0)},  # 9
            {'PS       :': (0, 0)}],  # 10  # not detected when connected with USB cable using XBOX 360 drivers
            'axis': [
                # -------------------------------
                # AXIS x 4 detected (axis 2 controlling right pad and left pad)
                {'L3 X     :': (0, 0)},  # 0  range -1, 1
                {'L3 Y     :': (0, 0)},  # 1  range -1, 1
                {'L2       :': (0, 0)},  # 2  left side (0, 1)
                {'R2       :': (0, 0)},  # 2  right side (0, -1)
                {'R3 X     :': (0, 0)},  # 3  range -1, 1
                {'R3 Y     :': (0, 0)}],  # 4  range -1, 1
            'hats':
                 # ----------------------------------
                 # HATS return a tuple (0, 0)
                     [{'D-PAD UP      :': (330, 355)},  # tuple[1] range 0 or 1
                      {'D-PAD DOWN    :': (287, 355)},  # tuple[1] range 0 or -1
                      {'D-PAD RIGHT   :': (309, 336)},  # tuple[0] range 0 or 1
                      {'D-PAD LEFT    :': (309, 375)}  # tuple[0] range 0 or -1
                      ]
        },
    
    # XBOX 360 LAYOUT
    # Input
    # Digital D-Pad
    # 2× Analog triggers (LT, RT)
    # 2× Analog sticks
    # 11× Digital buttons
    # (Y, B, A, X, LB, RB, left stick click, right stick click, Menu, View, Xbox)
    # Wireless pairing button
    # Connectivity
    # Wireless
    # Micro USB
    # 3.5 mm stereo audio jack (after 2nd revision)
    # Bluetooth 4.0 (third revision)
    # USB-C (Elite Series 2)
    
    'XBOX 360 For Windows':
    #  |----- NAME ------------| NUMBER
        {'buttons':
             ['A          :',  # 0
              'B          :',  # 1
              'X          :',  # 2
              'Y          :',  # 3
              'LBUMPER    :',  # 4
              'RBUMPER    :',  # 5
              'BACK       :',  # 6
              'START      :',  # 7
              'STICK LEFT :',  # 8
              'STICK RIGHT:',  # 9
              'XBOX       :'],  # 10
         'axis':
         # ---------------------------------
         # AXIS ( 2 axis + 2 pads left right
         # Left / right same axis but values differs,
         # left side (0, 1) right side (0, -1)
             ['8 AXIS X   :',  # 0  range X(-1, 1)
              '8 AXIS Y   :',  # 1  range Y(-1, 1)
              'LEFT/RIGHT :',  # 2  left side (0, 1) right side (0, -1)
              '9 AXIS X   :',  # 9  range X(-1, 1)
              '9 AXIS Y   :'],  # 9  range Y(-1, 1)
         # ----------------------------------
         # HATS return a tuple (0, 0)
         'hats':
             ['D-PAD UP      :',  # tuple[1] range 0 or 1
              'D-PAD DOWN    :',  # tuple[1] range 0 or -1
              'D-PAD RIGHT   :',  # tuple[0] range 0 or 1
              'D-PAD LEFT    :'  # tuple[0] range 0 or -1
              ]},
"""

OPTIONS_MENU_JOYSTICK = {
    1: {'TEXT': 'Disconnected', 'SIZE': 16,
        'FOREGROUND': pygame.Color(220, 198, 218), 'BACKGROUND': pygame.Color(10, 10, 36),
        'SELECT_COLOR': pygame.Color(220, 198, 10), 'ACTIVE': False, 'EXPLAIN': 'JOYSTICK STATUS',
        'POSITION': (400, 100),
        'FUNCTION': None, 'STYLE': freetype.STYLE_NORMAL}
}
OPTIONS_OPTIONS = [OPTIONS_MENU_JOYSTICK]


class GL:
    All = None
    TIME_PASSED_SECONDS = None
    MOUSE_POS = pygame.math.Vector2(0, 0)
    SOUND_SERVER = None
    JOYSTICK = None
    MAIN_MENU_FONT = None


def make_array(rgb_array_: numpy.ndarray, alpha_: numpy.ndarray) -> numpy.ndarray:
    """
    This function is used for 24-32 bit pygame surface with pixel alphas transparency layer

    make_array(RGB array, alpha array) -> RGBA array

    Return a 3D numpy (numpy.uint8) array representing (R, G, B, A)
    values of all pixels in a pygame surface.

    :param rgb_array_: 3D array that directly references the pixel values in a Surface.
                       Only work on Surfaces that have 24-bit or 32-bit formats.
    :param alpha_:     2D array that directly references the alpha values (degree of transparency) in a Surface.
                       alpha_ is created from a 32-bit Surfaces with a per-pixel alpha value.
    :return:           Return a numpy 3D array (numpy.uint8) storing a transparency value for every pixel
                       This allow the most precise transparency effects, but it is also the slowest.
                       Per pixel alphas cannot be mixed with pygame method set_colorkey (this will have
                       no effect).
    """
    return numpy.dstack((rgb_array_, alpha_))


def make_surface(rgba_array: numpy.ndarray) -> pygame.Surface:
    """
    This function is used for 24-32 bit pygame surface with pixel alphas transparency layer

    make_surface(RGBA array) -> Surface

    Argument rgba_array is a 3d numpy array like (width, height, RGBA)
    This method create a 32 bit pygame surface that combines RGB values and alpha layer.

    :param rgba_array: 3D numpy array created with the method surface.make_array.
                       Combine RGB values and alpha values.
    :return:           Return a pixels alpha surface.This surface contains a transparency value
                       for each pixels.
    """
    return pygame.image.frombuffer((rgba_array.transpose([1, 0, 2])).copy(order='C').astype(numpy.uint8),
                                   (rgba_array.shape[:2][0], rgba_array.shape[:2][1]), 'RGBA').convert_alpha()


def blend_texture(surface_, interval_, color_) -> pygame.Surface:
    """
    Compatible with 24-32 bit pixel alphas texture.
    Blend two colors together to produce a third color.
    Alpha channel of the source image will be transfer to the destination surface (no alteration
    of the alpha channel)

    :param surface_: pygame surface
    :param interval_: number of steps or intervals, int value
    :param color_: Destination color. Can be a pygame.Color or a tuple
    :return: return a pygame.surface supporting per-pixels transparency only if the surface passed
                    as an argument has been created with convert_alpha() method.
                    Pixel transparency of the source array will be unchanged.
    """

    source_array = pygame.surfarray.pixels3d(surface_)
    alpha_channel = pygame.surfarray.pixels_alpha(surface_)
    diff = (numpy.full_like(source_array.shape, color_[:3]) - source_array) * interval_
    rgba_array = numpy.dstack((numpy.add(source_array, diff), alpha_channel)).astype(dtype=numpy.uint8)
    return pygame.image.frombuffer(rgba_array.transpose([1, 0, 2]).copy(order='C').astype(numpy.uint8),
                                   (rgba_array.shape[:2][0], rgba_array.shape[:2][1]), 'RGBA').convert_alpha()


# Add transparency value to all pixels including black pixels
def add_transparency_all(rgb_array: numpy.ndarray, alpha_: numpy.ndarray, value: int) -> pygame.Surface:
    """
    Increase transparency of a surface
    This method is equivalent to pygame.Surface.set_alpha() but conserve the per-pixel properties of a texture
    All pixels will be update with a new transparency value.
    If you need to increase transparency on visible pixels only, prefer the method add_transparency instead.
    :param rgb_array:
    :param alpha_:
    :param value:
    :return:
    """
    # if not 0 <= value <= 255:
    #     raise ERROR('\n[-] invalid value for argument value, should be 0 < value <=255 got %s '
    #                 % value)
    # method 1
    """
    mask = (alpha_ >= value)
    mask_zero = (alpha_ < value)
    alpha_[:][mask_zero] = 0
    alpha_[:][mask] -= value
    return make_surface(make_array(rgb_array, alpha_.astype(numpy.uint8)))
    """
    # method 2
    alpha_ = alpha_.astype(numpy.int16)
    alpha_ -= value
    numpy.putmask(alpha_, alpha_ < 0, 0)

    return make_surface(make_array(rgb_array, alpha_.astype(numpy.uint8))).convert_alpha()


def load_per_pixel(file: str) -> pygame.Surface:
    """ Not compatible with 8 bit depth color surface"""

    assert isinstance(file, str), 'Expecting path for argument <file> got %s: ' % type(file)
    try:
        surface_ = pygame.image.load(file)
        buffer_ = surface_.get_view('2')
        w, h = surface_.get_size()
        source_array = numpy.frombuffer(buffer_, dtype=numpy.uint8).reshape((w, h, 4))

        surface_ = pygame.image.frombuffer(source_array.copy(order='C'),
                                           (tuple(source_array.shape[:2])), 'RGBA').convert_alpha()
        return surface_
    except pygame.error:
        raise SystemExit('\n[-] Error : Could not load image %s %s ' % (file, pygame.get_error()))


class Halo(pygame.sprite.Sprite):
    """
    Create a Halo sprite
    """

    images = []
    containers = None
    inventory = []

    def __init__(self,
                 rect_,
                 timing_,
                 id_=0,
                 layer_: int = 0
                 ):
        """
        :param rect_  : pygame.Rect representing the coordinates and sprite center
        :param timing_: integer representing the sprite refreshing time in ms
        :param layer_ : Layer to use, default 0
        """
        pygame.sprite.Sprite.__init__(self, self.containers)

        if isinstance(GL.All, pygame.sprite.LayeredUpdates):
            GL.All.change_layer(self, layer_)

        self.images_copy = self.images.copy()
        self.image = self.images_copy[0]
        self.center = rect_.center
        self.rect = self.image.get_rect(center=self.center)
        self._blend = None  # blend mode
        self.dt = 0  # time constant
        self.index = 0  # list index
        self.timing = timing_
        self.id_ = id_

    def update(self):

        if self.dt > self.timing:

            self.image = self.images_copy[self.index]
            self.rect = self.image.get_rect(center=self.center)

            if self.index < len(self.images_copy) - 1:
                self.index += 1
            else:
                if self.id_ in self.inventory:
                    self.inventory.remove(self.id_)
                self.kill()

            self.dt = 0

        self.dt += GL.TIME_PASSED_SECONDS


class JoystickEmulator(pygame.sprite.Sprite, GL):
    images = None

    def __init__(self,  joystickid_, menu_position_, offset_, layer_=0, timing_=120):

        assert isinstance(GL.All, LayeredUpdatesModified), 'GL.All should be a LayeredUpdatesModified class.'
        super(GL, self).__init__()
        pygame.sprite.Sprite.__init__(self, pygame.sprite.GroupSingle(), self.All)

        assert isinstance(menu_position_, tuple), 'Argument menu_position_ should be a tuple.'
        assert isinstance(layer_, int), 'Argument layer_ should be an integer.'
        assert isinstance(timing_, int), 'Argument timing_ should be an integer.'
        assert isinstance(JoystickEmulator.images,
                          (list, pygame.Surface)), 'Images should be defined as a list of pygame.Surfaces'
        assert isinstance(self.SOUND_SERVER, SoundControl), 'Sound Server is not initialised.'
        assert isinstance(MOUSE_CLICK_SOUND, pygame.mixer.Sound), 'MOUSE_CLICK_SOUND should be a pygame.mixer.Sound.'
        self.layer = layer_

        if isinstance(self.All, pygame.sprite.LayeredUpdates):
            self.All.change_layer(self, layer_)

        if self.images:
            self.images_copy = self.images.copy()
            self.image = self.images_copy[0] if isinstance(self.images_copy, list) else self.images_copy
            self.rect = self.image.get_rect(center=(menu_position_[0], menu_position_[1]))

        self.force_kill = False  # Variable used for killing the active window
        self.dt = 0  # Time constant
        self.timing = timing_  # Refreshing time used by the method update
        self.menu_position = menu_position_  # Window position into the screen, represent the topleft corner
        self.index = 0  # Iteration variable

        width, height = self.image.get_size()

        self.canw, self.canh = (700, 500)
        self.canw2, self.canh2 = (700 >> 1, 500 >> 1)
        self.canvas = pygame.Surface((700, 500), depth=32,
                                     flags=(pygame.SWSURFACE | pygame.SRCALPHA))

        assert isinstance(FRAME_BORDER_LEFT, pygame.Surface), \
            'FRAME_BORDER_LEFT is not defined or is not a pygame.Surface.'

        bw, bh = FRAME_BORDER_LEFT.get_size()
        self.transparent = pygame.Surface((self.canw - bw, self.canh),
                                          depth=32, flags=(pygame.SWSURFACE | pygame.SRCALPHA))
        self.transparent.fill((50, 80, 138, 220))
        self.canvas.blit(self.transparent, (bw, 0))
        self.canvas.blit(self.image, (self.canw2 - (width >> 1) + 25, self.canh2 - 80))
        self.canvas.blit(FRAME_BORDER_LEFT, (0, 0))

        self.image = self.canvas
        self.rect = self.image.get_rect(center=(menu_position_[0], menu_position_[1]))
        self.image_copy = self.image.copy()

        self.menu_position = (menu_position_[0] - self.canw2 + offset_[0],
                              menu_position_[1] - self.canh2 + offset_[1])

        # RED BUTTON
        assert isinstance(RED_SWITCH1, pygame.Surface), \
            'RED_SWITCH1 is not defined or is not a pygame.Surface.'

        self.exit_rect = RED_SWITCH1.get_rect(
            topleft=(self.menu_position[0] + self.canw - RED_SWITCH1.get_width(),
                     self.menu_position[1]))

        self.exit_rect = self.exit_rect.inflate(-15, -17)
        self.canvas.blit(RED_SWITCH1, self.exit_rect.topleft)

        self.joystickid = joystickid_
        self.avtive = True
        self.offset = offset_

    def highlight(self, coordinates_, id_):
        # create a colorful halo where the button is pressed
        rect = pygame.Rect(0, 0, 10, 10)
        rect.center = coordinates_
        Halo(rect_=rect, timing_=1, layer_=self.layer, id_=id_)

    def tick(self):
        # play the sound MOUSE_CLICK_SOUND
        self.SOUND_SERVER.play(sound_=MOUSE_CLICK_SOUND, loop_=False, priority_=0,
                                   volume_=0.1, fade_out_ms=0, panning_=True,
                                   name_='MOUSE CLICK', x_=self.MOUSE_POS[0])

    def connection(self):

        # Check the joystick status connected | disconnected 
        for key, value in OPTIONS_OPTIONS[0].items():

            if pygame.joystick.get_count() > 0:
                value['TEXT'] = 'Joystick %s Connected.' % pygame.joystick.Joystick(self.joystickid).get_name()
                value['FOREGROUND'] = (128, 220, 98, 255)
                rect = self.MAIN_MENU_FONT.get_rect(value['TEXT'],
                                                    style=freetype.STYLE_NORMAL, size=10)
                self.image.blit(self.MAIN_MENU_FONT.render(value['TEXT'],
                                                           fgcolor=(128, 220, 98, 255),
                                                           style=freetype.STYLE_NORMAL,
                                                           size=10)[0], ((self.canw - rect.w + 25) // 2, 10))
            else:
                value['TEXT'] = 'Joystick Disconnected'
                value['FOREGROUND'] = (218, 25, 18, 255)
                rect = self.MAIN_MENU_FONT.get_rect(value['TEXT'],
                                                    style=freetype.STYLE_NORMAL, size=10)
                self.image.blit(self.MAIN_MENU_FONT.render(value['TEXT'],
                                                           fgcolor=(218, 25, 18, 255),
                                                           style=freetype.STYLE_NORMAL,
                                                           size=10)[0], ((self.canw - rect.w + 25) // 2, 10))

    def layout(self):
        style = freetype.STYLE_NORMAL
        size_ = 8
        x = 80
        y = 50
        red = (255, 0, 0, 255)
        white = (255, 255, 255, 255)
        color_ = white
        lx = 160
        ly = 20
        rows = 7
        try:
            joystick_bind = pygame.joystick.Joystick(self.joystickid)
        except pygame.error as error:
            print('\n[-]ERROR - %s ' % error)
            raise SystemExit

        if not joystick_bind.get_init():
            joystick_bind.init()

        joystick_name = joystick_bind.get_name()

        if isinstance(CONTROLLER_LAYOUT, dict):
            layouts = CONTROLLER_LAYOUT.keys()
        else:
            raise AssertionError('\n[-]ERROR - CONTROLLER_LAYOUT is not a python dictionary')

        if joystick_name not in layouts:
            print('\n[-]INFO - No layout associated to joystick device %s ' % joystick_name)
        else:

            layout = CONTROLLER_LAYOUT[joystick_name]
            buttons = layout['buttons']
            axes = layout['axis']
            hats = layout['hats']
            i = 0

            button_number = joystick_bind.get_numbuttons()

            if len(buttons) >= button_number:

                for b in range(0, button_number):
                    color_ = white
                    pressed = joystick_bind.get_button(b)
                    if b == 0:
                        Halo.images = HALO_SPRITE_PURPLE
                    elif b == 1:
                        Halo.images = HALO_SPRITE_BLUE
                    elif b in (2, 6, 7):
                        Halo.images = HALO_SPRITE_RED
                    elif b == 3:
                        Halo.images = HALO_SPRITE_GREEN

                    else:
                        Halo.images = HALO_SPRITE_GREEN

                    if pressed:
                        xx, yy = list(*buttons[b].values())

                        self.highlight((xx + self.offset[0], yy + self.offset[1]), id_=0)
                        input_ = str(list(buttons[i].keys())[0]) + 'pressed'
                        color_ = red
                        self.tick()  # if b not in (6, 7) else None
                    else:
                        input_ = str(list(buttons[i].keys())[0]) + 'n/a'

                    if i != 0 and i % rows == 0:
                        y = 50
                        x += lx

                    self.image.blit(self.MAIN_MENU_FONT.render(input_,
                                                               fgcolor=color_,
                                                               style=style,
                                                               size=size_)[0], (x, y))
                    i += 1
                    y += ly

            x += lx
            y = 50
            axes_number = joystick_bind.get_numaxes()
            i = 0
            if len(axes) >= axes_number:

                for ax in range(0, axes_number):
                    input_ = str(axes[i])

                    if i != 0 and i % rows == 0:
                        y = 50
                        x += lx

                    pressed = joystick_bind.get_axis(ax)
                    if abs(pressed) > 0.1:

                        if joystick_name in ('Wireless Controller',
                                             'Gioteck VX2 2.4G Wireless Controller',
                                             'Generic'):

                            if ax in (4, 5):

                                if abs(pressed) < 1:
                                    xx, yy = list(list(axes[ax].values()))[0]
                                    Halo.images = HALO_SPRITE_PURPLE
                                    self.highlight((xx + self.offset[0], yy + self.offset[1]), id_=0)
                                    color_ = red
                                    input_ = str(list(axes[ax].keys())[0]) + str(round(pressed, 3))
                                else:
                                    color_ = white
                                    input_ = str(list(axes[ax].keys())[0]) + '0.0'

                            else:

                                xx, yy = list(list(axes[ax].values()))[0]
                                Halo.images = HALO_SPRITE_RED
                                self.highlight((xx + self.offset[0], yy + self.offset[1]), id_=0)
                                input_ = str(list(axes[ax].keys())[0]) + str(round(pressed, 3))
                                color_ = red

                        elif joystick_name == 'Controller (XBOX 360 For Windows)':
                            if ax == 2:
                                values = list(*axes[ax].values())
                                left, right = values[0], values[1]
                                if pressed > 0:
                                    xx, yy = left
                                else:
                                    xx, yy = right
                                Halo.images = HALO_SPRITE_RED
                                self.highlight((xx + self.offset[0], yy + self.offset[1]), id_=0)
                                color_ = red
                                input_ = str(list(axes[ax].keys())[0]) + str(round(pressed, 3))
                            else:
                                xx, yy = list(list(axes[ax].values()))[0]
                                Halo.images = HALO_SPRITE_PURPLE
                                self.highlight((xx + self.offset[0], yy + self.offset[1]), id_=0)
                                color_ = red
                                input_ = str(list(axes[ax].keys())[0]) + str(round(pressed, 3))

                        else:
                            print('\n[-]INFO - Joystick not recognized...')

                    else:
                        input_ = str(list(axes[ax].keys())[0]) + '0.0'
                        color_ = white

                    self.image.blit(self.MAIN_MENU_FONT.render(input_, fgcolor=color_, style=style,
                                                               size=size_)[0], (x, y))
                    i += 1
                    y += ly

            x += lx
            y = 50
            hats_number = joystick_bind.get_numhats()
            if len(hats) >= hats_number:
                for h in range(0, hats_number):
                    hat = joystick_bind.get_hat(h)
                    if any(hat):
                        color_ = red
                    else:
                        color_ = white
                    input_ = 'D-PAD   ' + str(hat)  # str(list(hats[0].keys())[0]) + str(hat)

                    if any(hat) != 0:
                        xx = 0
                        yy = 0
                        Halo.images = HALO_SPRITE_BLUE
                        if hat[0] == 1:
                            xx, yy = list(*hats[0].values())
                        if hat[0] == -1:
                            xx, yy = list(*hats[1].values())
                        if hat[1] == 1:
                            xx, yy = list(*hats[2].values())
                        if hat[1] == -1:
                            xx, yy = list(*hats[3].values())

                        self.highlight((xx + self.offset[0], yy + self.offset[1]), id_=0)
                        self.tick()
                    self.image.blit(self.MAIN_MENU_FONT.render(input_, fgcolor=color_, style=style,
                                                               size=size_)[0], (x, y))

                    y += ly

    def update(self):

        # self.menu_position = JoystickEmulator._menu_position

        if self.force_kill:
            self.force_kill = False
            self.active = False
            self.kill()
            return

        if self.dt > self.timing:

            self.image = self.image_copy.copy()

            self.active = True

            self.connection()

            if pygame.joystick.get_count() > 0:
                self.layout()

            self.image.blit(RED_SWITCH1, (615, 0))

            # collision detection with the red switch
            if self.exit_rect.collidepoint(self.MOUSE_POS):

                self.image.blit(RED_SWITCH2, (615, 0))
                # user pressed left click to confirm exit
                if pygame.mouse.get_pressed()[0]:
                    self.image.blit(RED_SWITCH3, (615, 0))
                    self.force_kill = True

            if isinstance(self.images_copy, list):
                if self.index < len(self.images_copy) - 1:
                    self.index += 1

            self.rect = self.image.get_rect(topleft=self.menu_position)
            self.rect.clamp_ip(SCREENRECT)
            self.dt = 0

        self.dt += self.TIME_PASSED_SECONDS


class LayeredUpdatesModified(pygame.sprite.LayeredUpdates):

    def __init__(self):
        pygame.sprite.LayeredUpdates.__init__(self)

    def draw(self, surface_):
        """draw all sprites in the right order onto the passed surface

        LayeredUpdates.draw(surface): return Rect_list

        """
        spritedict = self.spritedict
        surface_blit = surface_.blit
        dirty = self.lostsprites
        self.lostsprites = []
        dirty_append = dirty.append
        init_rect = self._init_rect
        for spr in self.sprites():
            rec = spritedict[spr]

            if hasattr(spr, '_blend') and spr._blend is not None:
                newrect = surface_blit(spr.image, spr.rect, special_flags=spr._blend)
            else:
                newrect = surface_blit(spr.image, spr.rect)

            if rec is init_rect:
                dirty_append(newrect)
            else:
                if newrect.colliderect(rec):
                    dirty_append(newrect.union(rec))
                else:
                    dirty_append(newrect)
                    dirty_append(rec)
            spritedict[spr] = newrect
        return dirty


if __name__ == '__main__':

    pygame.init()
    pygame.mixer.init()

    freetype.init(cache_size=64, resolution=72)
    MAIN_MENU_FONT = freetype.Font('Assets\\ARCADE_R.ttf', size=14)
    MAIN_MENU_FONT.antialiased = True
    GL.MAIN_MENU_FONT = MAIN_MENU_FONT

    SCREENRECT = pygame.Rect(0, 0, 800, 600)
    screen = pygame.display.set_mode(SCREENRECT.size, pygame.HWSURFACE, 32)
    BACKGROUND = pygame.image.load('Assets\\ps3-logo2.png').convert()
    BACKGROUND = pygame.transform.smoothscale(BACKGROUND, SCREENRECT.size)

    PS3_SCHEME = pygame.image.load('Assets\\PS3_Layout.png').convert_alpha()
    PS3_SCHEME = pygame.transform.smoothscale(PS3_SCHEME, (600, 272))

    XBOX_SCHEME = pygame.image.load('Assets\\xbox1.png').convert_alpha()
    XBOX_SCHEME = pygame.transform.smoothscale(XBOX_SCHEME, (600, 272))

    DUALSHOCK4 = pygame.image.load('Assets\\PS4.png')
    DUALSHOCK4 = pygame.transform.smoothscale(DUALSHOCK4, (600, 272))
    DUALSHOCK4.set_colorkey((255, 255, 255, 255))

    FRAME_BORDER_LEFT = pygame.image.load('Assets\\dModScreens06.png').convert_alpha()
    FRAME_BORDER_LEFT = pygame.transform.smoothscale(FRAME_BORDER_LEFT, (FRAME_BORDER_LEFT.get_width(), 500))

    RED_SWITCH1 = pygame.image.load('Assets\\switchRed01.png').convert_alpha()
    RED_SWITCH2 = pygame.image.load('Assets\\switchRed02.png').convert_alpha()
    RED_SWITCH3 = pygame.image.load('Assets\\switchRed03.png').convert_alpha()

    GRAY_BUTTON0 = pygame.image.load('Assets\\modGrayBtn02.png').convert_alpha()
    GRAY_BUTTON0_SELECT = pygame.image.load('Assets\\modGrayBtn03.png').convert_alpha()

    GREEN_SWITCH1 = pygame.image.load('Assets\\switchGreen01.png').convert_alpha()
    GREEN_SWITCH2 = pygame.image.load('Assets\\switchGreen02.png').convert_alpha()
    GREEN_SWITCH3 = pygame.image.load('Assets\\switchGreen03.png').convert_alpha()

    TEXTPREV = pygame.image.load('Assets\\txtPrev01.png').convert_alpha()
    TEXTNEXT = pygame.image.load('Assets\\txtPrev02.png').convert_alpha()

    # WHITE HALO
    HALO_SPRITE = []
    HALO_SPRITE_ = load_per_pixel('Assets\\WhiteHalo.png')
    steps = numpy.array([0., 0.03333333, 0.06666667, 0.1, 0.13333333,
                         0.16666667, 0.2, 0.23333333, 0.26666667, 0.3,
                         0.33333333, 0.36666667, 0.4, 0.43333333, 0.46666667,
                         0.5, 0.53333333, 0.56666667, 0.6, 0.63333333,
                         0.66666667, 0.7, 0.73333333, 0.76666667, 0.8,
                         0.83333333, 0.86666667, 0.9, 0.93333333, 0.96666667])

    for number in range(30):
        surface = blend_texture(HALO_SPRITE_, steps[number], pygame.Color(128, 255, 255, 255))
        rgb = pygame.surfarray.pixels3d(surface)
        alpha = pygame.surfarray.array_alpha(surface)
        surface = add_transparency_all(rgb, alpha, int(255 * steps[number] / 8))
        size = pygame.math.Vector2(surface.get_size())
        size *= (number / 60)
        surface1 = pygame.transform.smoothscale(surface, (int(size.x), int(size.y)))
        HALO_SPRITE.append(surface1)

    # RED HALO
    HALO_SPRITE_RED = []
    HALO_SPRITE_RED_ = load_per_pixel('Assets\\WhiteHalo.png')

    for number in range(30):
        surface = blend_texture(HALO_SPRITE_RED_, steps[number], pygame.Color(255, 0, 0, 255))
        rgb = pygame.surfarray.pixels3d(surface)
        alpha = pygame.surfarray.array_alpha(surface)
        surface = add_transparency_all(rgb, alpha, int(255 * steps[number] / 8))
        size = pygame.math.Vector2(surface.get_size())
        size *= (number / 60)
        surface1 = pygame.transform.smoothscale(surface, (int(size.x), int(size.y)))
        HALO_SPRITE_RED.append(surface1)

    # GREEN HALO
    HALO_SPRITE_GREEN = []
    HALO_SPRITE_GREEN_ = load_per_pixel('Assets\\WhiteHalo.png')

    for number in range(30):
        surface = blend_texture(HALO_SPRITE_GREEN_, steps[number], pygame.Color(25, 255, 18, 255))
        rgb = pygame.surfarray.pixels3d(surface)
        alpha = pygame.surfarray.array_alpha(surface)
        surface = add_transparency_all(rgb, alpha, int(255 * steps[number] / 8))
        size = pygame.math.Vector2(surface.get_size())
        size *= (number / 60)
        surface1 = pygame.transform.smoothscale(surface, (int(size.x), int(size.y)))
        HALO_SPRITE_GREEN.append(surface1)

    # BLUE HALO
    HALO_SPRITE_BLUE = []
    HALO_SPRITE_BLUE_ = load_per_pixel('Assets\\WhiteHalo.png')

    for number in range(30):
        # Blend red
        surface = blend_texture(HALO_SPRITE_BLUE_, steps[number], pygame.Color(15, 25, 255, 255))
        rgb = pygame.surfarray.pixels3d(surface)
        alpha = pygame.surfarray.array_alpha(surface)
        surface = add_transparency_all(rgb, alpha, int(255 * steps[number] / 8))
        size = pygame.math.Vector2(surface.get_size())
        size *= (number / 60)
        surface1 = pygame.transform.smoothscale(surface, (int(size.x), int(size.y)))
        HALO_SPRITE_BLUE.append(surface1)

    # PURPLE HALO
    HALO_SPRITE_PURPLE = []
    HALO_SPRITE_PURPLE_ = load_per_pixel('Assets\\WhiteHalo.png')

    for number in range(30):
        # Blend red
        surface = blend_texture(HALO_SPRITE_PURPLE_, steps[number], pygame.Color(120, 15, 255, 255))
        rgb = pygame.surfarray.pixels3d(surface)
        alpha = pygame.surfarray.array_alpha(surface)
        surface = add_transparency_all(rgb, alpha, int(255 * steps[number] / 8))
        size = pygame.math.Vector2(surface.get_size())
        size *= (number / 60)
        surface1 = pygame.transform.smoothscale(surface, (int(size.x), int(size.y)))
        HALO_SPRITE_PURPLE.append(surface1)

    SoundControl.SCREENRECT = SCREENRECT
    GL.SOUND_SERVER = SoundControl(10)

    MOUSE_CLICK_SOUND = pygame.mixer.Sound('Assets\\MouseClick.ogg')

    GL.All = LayeredUpdatesModified()
    GL.TIME_PASSED_SECONDS = 0

    Halo.images = HALO_SPRITE_RED
    Halo.containers = GL.All

    count = pygame.joystick.get_count()
    if not count > 0:
        print('\n[-]INFO - Joystick not connected...')
        raise SystemExit

    for id in range(count):
        jjobject = pygame.joystick.Joystick(id)
        jjobject.init()
        if jjobject.get_name() == 'Controller (XBOX 360 For Windows)':
            SCHEME = XBOX_SCHEME
        elif jjobject.get_name() == 'Wireless Controller':
            SCHEME = DUALSHOCK4
        else:
            SCHEME = PS3_SCHEME
        JoystickEmulator.containers = GL.All
        JoystickEmulator.images = SCHEME
        JoystickEmulator(id, SCREENRECT.center, offset_=(id * 50, id * 50), layer_=id, timing_=100)

    clock = pygame.time.Clock()
    STOP_GAME = False

    FRAME = 0
    while not STOP_GAME:

        for event in pygame.event.get():
            keys = pygame.key.get_pressed()

            if keys[pygame.K_F8]:
                pygame.image.save(screen, 'screenshot' + str(FRAME) + '.png')

            if event.type == pygame.QUIT:
                print('Quitting')
                STOP_GAME = True

            if event.type == pygame.MOUSEMOTION:
                GL.MOUSE_POS = pygame.math.Vector2(event.pos)
                # print(GL.MOUSE_POS)

        screen.blit(BACKGROUND, (0, 0))
        GL.All.update()
        GL.All.draw(screen)
        GL.TIME_PASSED_SECONDS = clock.tick(60)

        pygame.display.flip()
        FRAME += 1
        GL.SOUND_SERVER.update()

    pygame.quit()
