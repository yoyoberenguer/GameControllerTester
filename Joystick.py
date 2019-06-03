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

# PS3 layout (buttons, axes, hats)
# todo screen shot ?
PS3_BUTTONS = [
    # config 1
    ['TRIANGLE   : %s' % 'N/A',  # 0
     'CIRCLE     : %s' % 'N/A',  # 1
     'X          : %s' % 'N/A',  # 3
     'SQUARE     : %s' % 'N/A',  # 4
     'L1         : %s' % 'N/A',  # 5
     'R1         : %s' % 'N/A',  # 6
     'L2         : %s' % 'N/A',  # 7
     'R2         : %s' % 'N/A',  # 8
     # next column
     'SELECT     : %s' % 'N/A',  # 9
     'START      : %s' % 'N/A',  # 10
     'L3 PRESSED : %s' % 'N/A',  # 11
     'R3 PRESSED : %s' % 'N/A',  # 12
     'PS         : %s' % 'N/A',  # 13
     # ----- end of buttons ------------------
     'L3 LATERAL : %s' % 'RIGHT/LEFT',  # 14
     'L3 VERTICAL: %s' % 'UP/DOWN',     # 15
     'R3 LATERAL : %s' % 'RIGHT/LEFT',  # 16
     'R3 VERTICAL: %s' % 'UP/DOWN',     # 17

     'D-PAD UP      : %s' % 'N/A',  # 18
     'D-PAD DOWN    : %s' % 'N/A',  # 19
     'D-PAD RIGHT   : %s' % 'N/A',  # 20
     'D-PAD LEFT    : %s' % 'N/A'   # 21
     ],
    # config 2
    ['TRIANGLE   : %s' % 'N/A',  # 0
     'CIRCLE     : %s' % 'N/A',  # 1
     'X          : %s' % 'N/A',  # 3
     'SQUARE     : %s' % 'N/A',  # 4
     'L1         : %s' % 'N/A',  # 5
     'R1         : %s' % 'N/A',  # 6
     'L2         : %s' % 'N/A',  # 7
     'R2         : %s' % 'N/A',  # 8
     # next column
     'SELECT     : %s' % 'N/A',  # 9
     'START      : %s' % 'N/A',  # 10
     'L3 PRESSED : %s' % 'N/A',  # 11
     'R3 PRESSED : %s' % 'N/A',  # 12
     'PS         : %s' % 'N/A',  # 13
     # ----- end of buttons ------------------
     'L3 LATERAL : %s' % 'RIGHT/LEFT',  # 14
     'L3 VERTICAL: %s' % 'UP/DOWN',     # 15
     'R3 LATERAL : %s' % 'RIGHT/LEFT',  # 16
     'R3 VERTICAL: %s' % 'UP/DOWN',     # 17

     'D-PAD UP      : %s' % 'N/A',  # 18
     'D-PAD DOWN    : %s' % 'N/A',  # 19
     'D-PAD RIGHT   : %s' % 'N/A',  # 20
     'D-PAD LEFT    : %s' % 'N/A'   # 21
     ]
]


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
    return pygame.image.frombuffer((rgba_array.transpose(1, 0, 2)).copy(order='C').astype(numpy.uint8),
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
    return pygame.image.frombuffer((rgba_array.transpose(1, 0, 2)).copy(order='C').astype(numpy.uint8),
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
        surface = pygame.image.load(file)
        buffer_ = surface.get_view('2')
        w, h = surface.get_size()
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
        self._blend = None      # blend mode
        self.dt = 0             # time constant
        self.index = 0          # list index
        self.timing = timing_
        self.id_ = id_
        if id_ in self.inventory:
            self.kill()
        else:
            self.inventory.append(id_)

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


class PS3Scheme(pygame.sprite.Sprite, GL):
    images = None
    active = False
    _force_kill = False
    _menu_position = None

    def __new__(cls, menu_position_, layer_=0, timing_=120, *args, **kwargs):
        # return if an instance already exist.
        if PS3Scheme.active:
            return
        else:
            return super().__new__(cls, *args, **kwargs)

    def __init__(self, menu_position_, layer_=0, timing_=120):

        assert isinstance(GL.All, LayeredUpdatesModified), 'GL.All should be a LayeredUpdatesModified class.'
        super(GL, self).__init__()
        pygame.sprite.Sprite.__init__(self, pygame.sprite.GroupSingle(), self.All)

        assert isinstance(menu_position_, tuple), 'Argument menu_position_ should be a tuple.'
        assert isinstance(layer_, int), 'Argument layer_ should be an integer.'
        assert isinstance(timing_, int), 'Argument timing_ should be an integer.'
        assert isinstance(PS3Scheme.images, (list, pygame.Surface)), 'Images should be defined as a list of pygame.Surfaces'
        assert isinstance(self.SOUND_SERVER, SoundControl), 'Sound Server is not initialised.'
        assert isinstance(MOUSE_CLICK_SOUND, pygame.mixer.Sound), 'MOUSE_CLICK_SOUND should be a pygame.mixer.Sound.'
        self._layer = layer_

        if isinstance(self.All, pygame.sprite.LayeredUpdates):
            self.All.change_layer(self, layer_)

        if self.images:
            self.images_copy = self.images.copy()
            self.image = self.images_copy[0] if isinstance(self.images_copy, list) else self.images_copy
            self.rect = self.image.get_rect(center=(menu_position_[0], menu_position_[1]))
        
        
        PS3Scheme._force_kill = False           # Variable used for killing the active window
        self.dt = 0                             # Time constant
        self.timing = timing_                   # Refreshing time used by the method update
        self.menu_position = menu_position_     # Window position into the screen, represent the topleft corner
        self.index = 0                          # Iteration variable

        width, height = PS3Scheme.images.get_size()
        self.canw, self.canh = (700, 500)
        self.canw2, self.canh2 = (700 >> 1, 500 >> 1)
        self.canvas = pygame.Surface((700, 500), depth=32,
                                     flags=(pygame.SWSURFACE | pygame.SRCALPHA))

        assert isinstance(FRAME_BORDER_LEFT, pygame.Surface),\
                            'FRAME_BORDER_LEFT is not defined or is not a pygame.Surface.'
                            
        bw, bh = FRAME_BORDER_LEFT.get_size()
        self.transparent = pygame.Surface((self.canw - bw, self.canh),
                                          depth=32, flags=(pygame.SWSURFACE | pygame.SRCALPHA))
        self.transparent.fill((50, 80, 138, 220))
        self.canvas.blit(self.transparent, (bw, 0))
        self.canvas.blit(PS3Scheme.images, (self.canw2 - (width >> 1) + 25,
                                            self.canh2 - 80))
        self.canvas.blit(FRAME_BORDER_LEFT, (0, 0))

        self.image = self.canvas
        self.rect = self.image.get_rect(center=(menu_position_[0], menu_position_[1]))
        self.image_copy = self.image.copy()

        PS3Scheme._menu_position = (menu_position_[0] - self.canw2,
                                    menu_position_[1] - self.canh2)

        # RED BUTTON
        assert isinstance(RED_SWITCH1, pygame.Surface),\
                            'RED_SWITCH1 is not defined or is not a pygame.Surface.'
        self.canvas.blit(RED_SWITCH1, (615, 0))
        self.exit_rect = RED_SWITCH1.get_rect(
            topleft=(self.menu_position[0] + self.canw2 - RED_SWITCH1.get_width(),
                     self.menu_position[1] - self.canh2))
        self.exit_rect = self.exit_rect.inflate(-15, -17)

        assert isinstance(self.JOYSTICK, JJoystick), 'Joystick is not instanciated.'
        # ---- remove the joystick bind -------
        # 1) remove the bind
        # 2) create the bind again to know if the joystick
        #    is still present
        pygame.joystick.quit()
        # Create the bind again
        self.JOYSTICK.init_joystick()
        # ---------------------------------------
        self.configuration = 0

    @staticmethod
    def highlight(coordinates_, id_):
        # create a colorful halo where the button is pressed
        rect = pygame.Rect(0, 0, 10, 10)
        rect.center = coordinates_
        Halo(rect_=rect, timing_=1, layer_=0, id_=id_)

    @staticmethod
    def tick():
        # play the sound MOUSE_CLICK_SOUND
        if not self.SOUND_SERVER.get_identical_id(id(MOUSE_CLICK_SOUND)):
            self.SOUND_SERVER.play(sound_=MOUSE_CLICK_SOUND, loop_=False, priority_=0,
                                 volume_=0.1, fade_out_ms=0, panning_=True,
                                 name_='MOUSE CLICK', x_=self.MOUSE_POS[0],
                                 object_id_=id(MOUSE_CLICK_SOUND))

    def connection(self):
        # Check the joystick status connected | disconnected 
        for key, value in OPTIONS_OPTIONS[0].items():
            if self.JOYSTICK.PRESENT:
                value['TEXT'] = 'Joystick Connected'
                value['FOREGROUND'] = (128, 220, 98, 255)
                rect = self.MAIN_MENU_FONT.get_rect('Joystick Connected',
                                                  style=freetype.STYLE_NORMAL, size=15)
                self.image.blit(self.MAIN_MENU_FONT.render('Joystick Connected',
                                fgcolor=(128, 220, 98, 255),
                                style=freetype.STYLE_NORMAL,
                                size=15)[0], ((self.canw - rect.w + 25) // 2, 10))
            else:
                value['TEXT'] = 'Joystick Disconnected'
                value['FOREGROUND'] = (218, 25, 18, 255)
                rect = self.MAIN_MENU_FONT.get_rect('Joystick Disconnected',
                                                  style=freetype.STYLE_NORMAL, size=15)
                self.image.blit(self.MAIN_MENU_FONT.render('Joystick Disconnected',
                                fgcolor=(218, 25, 18, 255),
                                style=freetype.STYLE_NORMAL,
                                size=15)[0], ((self.canw - rect.w + 25) // 2, 10))

    def layout(self):
        # Draw on the the status of buttons and joystick hats
        style = freetype.STYLE_NORMAL
        size = 8
        x = 100
        y = 50
        element_ = 0

        for button in PS3_BUTTONS[self.configuration]:
            Halo.images = HALO_SPRITE_RED
            color_ = (255, 255, 255, 255)
            xx, yy = self.menu_position[0] + self.canw2, self.menu_position[1] + self.canh2
            # BUTTONS
            if element_ <= self.JOYSTICK.button - 1 and self.JOYSTICK.button_status[element_]:
                
                # Triangle
                if self.JOYSTICK.button_status[0] and element_ == 0:
                    Halo.images = HALO_SPRITE_GREEN
                    self.highlight(( xx + 130, yy + 25), id_=0)
                    self.tick()
                    PS3_BUTTONS[self.configuration][0] = 'TRIANGLE   : %s' % 'pressed'
                    
                # Circle
                elif self.JOYSTICK.button_status[1] and element_ == 1:
                    Halo.images = HALO_SPRITE_RED
                    self.highlight((xx + 158, yy + 55), id_=1)
                    self.tick()
                    PS3_BUTTONS[self.configuration][1] = 'CIRCLE     : %s' % 'pressed'
                # X
                elif self.JOYSTICK.button_status[2] and element_ == 2:
                    Halo.images = HALO_SPRITE_BLUE
                    self.highlight((xx + 130, yy + 85 ), id_=2)
                    self.tick()
                    PS3_BUTTONS[self.configuration][2] = 'X          : %s' % 'pressed'
                    
                # Square
                elif self.JOYSTICK.button_status[3] and element_ == 3:
                    Halo.images = HALO_SPRITE_PURPLE
                    self.highlight((xx + 102, yy + 55), id_=3)
                    self.tick()
                    PS3_BUTTONS[self.configuration][3] = 'SQUARE     : %s' % 'pressed'
                    
                # L1
                elif self.JOYSTICK.button_status[4] and element_ == 4:
                    Halo.images = HALO_SPRITE_GREEN
                    self.highlight((xx - 90, yy - 25), id_=4)
                    self.tick()
                    PS3_BUTTONS[self.configuration][4] = 'L1         : %s' % 'pressed'
                    
                # R1
                elif self.JOYSTICK.button_status[5] and element_ == 5:
                    Halo.images = HALO_SPRITE_GREEN
                    self.highlight((x + 130, yy - 25), id_=5)
                    self.tick()
                    PS3_BUTTONS[self.configuration][5] = 'R1         : %s' % 'pressed'
                    
                # L2
                elif self.JOYSTICK.button_status[6] and element_ == 6:
                    self.highlight((xx - 90, yy - 25), id_=6)
                    self.tick()
                    PS3_BUTTONS[self.configuration][6] = 'L2         : %s' % 'pressed'
                # R2
                elif self.JOYSTICK.button_status[7] and element_ == 7:
                    self.highlight((xx + 130 , self.menu_position[1] - 25 + self.h2), id_=7)
                    self.tick()
                    PS3_BUTTONS[self.configuration][7] = 'R2         : %s' % 'pressed'
                    
                # select
                elif self.JOYSTICK.button_status[8] and element_ == 8:
                    self.highlight((xx - 15, yy + 55), id_=8)
                    self.tick()
                    PS3_BUTTONS[self.configuration][8] = 'SELECT     : %s' % 'pressed'
                    
                # start
                elif self.JOYSTICK.button_status[9] and element_ == 9:
                    self.highlight((xx + 50, yy + 55), id_=9)
                    self.tick()
                    PS3_BUTTONS[self.configuration][9] = 'START      : %s' % 'pressed'
                    
                # L3 PRESSED
                elif self.JOYSTICK.button_status[10] and element_ == 10:
                    self.highlight((xx - 38, yy + 110), id_=10)
                    self.tick()
                    PS3_BUTTONS[self.configuration][10] = 'L3 PRESSED : %s' % 'pressed'
                    

                # R3 PRESSED
                elif self.JOYSTICK.button_status[11] and element_ == 11:
                    self.highlight((xx + 75, yy + 110), id_=11)
                    self.tick()
                    PS3_BUTTONS[self.configuration][11] = 'L3 PRESSED : %s' % 'pressed'


                # ps
                elif self.JOYSTICK.button_status[12] and element_ == 12:
                    self.highlight((xx + 20, yy + 75), id_=12)
                    self.tick()
                    PS3_BUTTONS[self.configuration][12] = 'PS         : %s' % 'pressed'
                color_ = (255, 0, 0, 255)

            # AXES
            elif 12 < element_ < 17:
                if self.JOYSTICK.axes_status[(element_ - self.JOYSTICK.button) % len(self.JOYSTICK.axes_status)] != 0.0:
                    
                    if element_ == 13:
                        button = 'L3 LATERAL : %s' % 'RIGHT/LEFT ' + str(round(self.JOYSTICK.axes_status[0], 3))
                        Halo.images = HALO_SPRITE
                        self.highlight((xx - 38, yy + 110), id_=13)
                        
                    elif element_ == 14:
                        button = 'L3 VERTICAL: UP/DOWN ' + str(round(self.JOYSTICK.axes_status[1], 3))
                        Halo.images = HALO_SPRITE
                        self.highlight((xx - 38, yy + 110), id_=14)
                        
                    elif element_ == 15:
                        button = 'R3 LATERAL : %s' % 'RIGHT/LEFT ' + str(round(self.JOYSTICK.axes_status[2], 3))
                        Halo.images = HALO_SPRITE
                        self.highlight((xx + 75, yy + 110), id_=15)
                        
                    else:
                        button = 'R3 VERTICAL: UP/DOWN ' + str(round(self.JOYSTICK.axes_status[3], 3))
                        Halo.images = HALO_SPRITE
                        self.highlight((xx + 75, yy + 110), id_=16)
                    color_ = (255, 0, 0, 255)
            # D-PAD
            else:
                # D-PAD UP
                if element_ == 17 and self.JOYSTICK.hats_status[0][1] == 1:
                    color_ = (255, 0, 0, 255)
                    self.highlight((xx - 90,  yy + 35), id_=17)
                    self.tick()
                    PS3_BUTTONS[self.configuration][17] = 'D-PAD UP      : %s' % 'pressed'
                    
                # D-PAD DOWN
                elif element_ == 18 and self.JOYSTICK.hats_status[0][1] == -1:
                    # item highlighted
                    color_ = (255, 0, 0, 255)
                    self.highlight((xx - 90, yy + 75), id_=18)
                    self.tick()
                    PS3_BUTTONS[self.configuration][18] = 'D-PAD DOWN    : %s' % 'pressed'
                    
                # D-PAD RIGHT
                elif element_ == 19 and self.JOYSTICK.hats_status[0][0] == 1:
                    color_ = (255, 0, 0, 255)
                    self.highlight((xx - 70, yy + 55), id_=19)
                    self.tick()
                    PS3_BUTTONS[self.configuration][19] = 'D-PAD RIGHT   : %s' % 'pressed'
                    
                # D-PAD LEFT
                else:
                    if element_ == 20 and self.JOYSTICK.hats_status[0][0] == -1:
                        # item highlighted
                        color_ = (255, 0, 0, 255)
                        self.highlight((xx - 110, yy + 55), id_=20)
                        self.tick()
                        PS3_BUTTONS[self.configuration][20] = 'D-PAD LEFT    : %s' % 'pressed'

            self.image.blit(self.MAIN_MENU_FONT.render(button,
                                                     fgcolor=color_,
                                                     style=style,
                                                     size=size)[0], (x, y))

            if element_ == 8 or element_ == 17:
                x += 200  # next column
                y = 50    # first row

            else:
                y += 15

            element_ += 1

    def update(self):

        self.menu_position = PS3Scheme._menu_position

        if PS3Scheme._force_kill:
            PS3Scheme._force_kill = False
            PS3Scheme.active = False
            self.kill()
            return

        if self.dt > self.timing:

            self.image = self.image_copy.copy()

            PS3Scheme.active = True

            self.connection()

            if self.JOYSTICK.PRESENT:
                self.layout()

            self.image.blit(RED_SWITCH1, (615, 0))

            # collision detection with the red switch
            if self.exit_rect.collidepoint(self.MOUSE_POS):
                self.image.blit(RED_SWITCH2, (615, 0))
                # user pressed left click to confirm exit
                if pygame.mouse.get_pressed()[0]:
                    self.image.blit(RED_SWITCH3, (615, 0))
                    PS3Scheme._force_kill = True
                    self.SOUND_SERVER.stop_object(id(MOUSE_CLICK_SOUND))
                    self.SOUND_SERVER.play(sound_=MOUSE_CLICK_SOUND, loop_=False, priority_=0,
                                         volume_=1, fade_out_ms=0, panning_=True,
                                         name_='MOUSE CLICK', x_=self.MOUSE_POS[0],
                                         object_id_=id(MOUSE_CLICK_SOUND))

            if isinstance(self.images_copy, list):
                if self.index < len(self.images_copy) - 1:
                    self.index += 1

            self.rect = self.image.get_rect(topleft=self.menu_position)
            self.rect.clamp_ip(SCREENRECT)
            self.dt = 0

        self.dt += self.TIME_PASSED_SECONDS


class JoystickObject:
    """ Create a Joystick player referencing the device """

    def __init__(self, id_: int = None,
                 name_: str = None,
                 axes_: int = None,
                 buttons_: int = None,
                 hats_: int = None,
                 balls_: int = None):
        """
        :param id_:         get the Joystick ID
        :param name_:       get the Joystick system name
        :param axes_:       get the number of axes on a Joystick
        :param buttons_:    get the number of buttons on a Joystick
        :param hats_:       get the number of hat controls on a Joystick
        :param balls_:      get the number of trackballs on a Joystick
        """
        self.id = id_
        self.name = name_
        self.axes = axes_
        self.button = buttons_
        self.hats = hats_
        self.balls = balls_
        self.button_status = [False for i in range(self.button)]
        self.axes_status = [0 for i in range(self.axes)]
        self.hats_status = [(0, 0) for i in range(self.hats)]


class JJoystick(JoystickObject):
    
    """ prior testing the Joystick 
        1) The pygame display has to be initialised 
        2) The event loop has to be setup 
        
    """
    PRESENT = False  # Confirm if a joystick is connected
    QUANTITY = 0  # How many joystick(s) are connected
    OBJECT = None  # Bind to the device

    def __init__(self, joystick_id_: int = 0, sensitivity_: float = 0.01, verbosity_: bool = False):

        assert isinstance(joystick_id_, int), \
            'Expecting int for argument joystick_id_ got %s ' % type(joystick_id_)
        assert isinstance(sensitivity_, float), \
            'Expecting float for argument sensitivity_ got %s ' % type(sensitivity_)
        assert isinstance(verbosity_, bool), \
            'Expecting bool for argument verbosity_ got %s ' % type(verbosity_)

        self.verbosity = verbosity_
        self.id = joystick_id_
        # axis sensitivity_.
        # Below this value the changes are ignored
        self.sensitivity = sensitivity_

        self.init_joystick()

    def init_joystick(self):
        if not pygame.joystick.get_init():
            pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            self.joystick_not_present()
        else:
            if self.verbosity:
                print('Joystick detected')
            JJoystick.PRESENT = True
            self.check_joystick_quantity()
            args = self.create_joystick_object(self.id)
            if args is not None:
                JoystickObject.__init__(self, *args)
            else:
                self.joystick_not_present()

    def joystick_not_present(self):
        """ Check if joystick(s) exist """
        JJoystick.PRESENT = False  # Confirmation
        JJoystick.QUANTITY = 0
        print('Joystick with id %s is not detected' % self.id)

    def check_joystick_quantity(self):
        """ Check the number of joystick connected  """
        try:
            JJoystick.QUANTITY = pygame.joystick.get_count()

        except pygame.error as e:
            JJoystick.QUANTITY = 0
            JJoystick.PRESENT = False
            if self.verbosity:
                print(e)

    def create_joystick_object(self, joystick_id_: int = 0) -> tuple:
        """ Create a new joystick to access a physical device. """
        try:
            arguments = None

            assert isinstance(joystick_id_, int), \
                'Expecting int for argument joystick_id_ got %s ' % type(joystick_id_)

            if JJoystick.PRESENT:
                JJoystick.OBJECTS = None
                JJoystick.OBJECT = pygame.joystick.Joystick(joystick_id_)
                JJoystick.OBJECT.init()

                if self.verbosity:
                    print(JJoystick.OBJECT.get_id(), \
                          JJoystick.OBJECT.get_name(), \
                          JJoystick.OBJECT.get_numaxes(), \
                          JJoystick.OBJECT.get_numbuttons(), \
                          JJoystick.OBJECT.get_numhats(), \
                          JJoystick.OBJECT.get_numballs)

                arguments = JJoystick.OBJECT.get_id(), \
                            JJoystick.OBJECT.get_name(), \
                            JJoystick.OBJECT.get_numaxes(), \
                            JJoystick.OBJECT.get_numbuttons(), \
                            JJoystick.OBJECT.get_numhats(), \
                            JJoystick.OBJECT.get_numballs

        except (pygame.error, AssertionError) as err:
            JJoystick.QUANTITY = 0
            JJoystick.PRESENT = False
            if self.verbosity:
                print('\n[-] %s ' % err)

        finally:
            return arguments

    def check_all_buttons_status(self):
        """
            Goes through all the joystick buttons
        """
        try:
            if self.button > 0:
                for i in range(self.button):
                    self.button_status[i] = True if JJoystick.OBJECT.get_button(i) else False

        except Exception as e:
            JJoystick.QUANTITY = 0
            JJoystick.PRESENT = False
            if self.verbosity:
                print(e)

    def check_button_status(self, button_: int = 0):
        """ return the button number being pressed, otherwise return None"""
        argument = None
        try:
            if self.button > 0:
                assert isinstance(button_, int), \
                    'Expecting int for argument button_ got %s ' % type(button_)
                argument = JJoystick.OBJECT.get_button(button_)
        except (pygame.error, AssertionError) as e:
            JJoystick.QUANTITY = 0
            JJoystick.PRESENT = False
            if self.verbosity:
                print(e)

        finally:
            return argument

    def check_axes_position(self):
        """ Check all joystick axes and store the positions into a list call self.axes_status.
            The position is rounded to zero (0.0) if the value is in between (-self.sensitivity...+sensitivity)
            By default self.sensitivity is set to 0.01
        """
        try:
            if self.axes > 0:
                for axis in range(self.axes):
                    axis_response = JJoystick.OBJECT.get_axis(axis)
                    self.axes_status[axis] = axis_response if axis_response > self.sensitivity \
                                                              or axis_response < -self.sensitivity else 0.0
        except Exception as e:
            JJoystick.QUANTITY = 0
            JJoystick.PRESENT = False
            if self.verbosity:
                print(e)

    def check_axis_position(self, axis_number_: int = 0):
        """ Check a given axis number and return its value """
        try:
            argument = None
            if self.axes > 0:
                assert isinstance(axis_number_, int), \
                    'Expecting int for argument axis_number_ got %s ' % type(axis_number_)
                axis_response = JJoystick.OBJECT.get_axis(axis_number_)
                argument = axis_response if axis_response > self.sensitivity \
                                            or axis_response < -self.sensitivity else 0.0
        except (pygame.error, AssertionError) as e:
            JJoystick.QUANTITY = 0
            JJoystick.PRESENT = False
            if self.verbosity:
                print(e)

        finally:
            return argument

    def check_hats_status(self):
        """ Check all joystick axes and store the positions into a list.
            The position is rounded to zero (0.0) if the value is in between (-self.sensitivity...+sensitivity)
            By default self.sensitivity is set to 0.01
        """
        try:
            if self.hats > 0:
                for hat in range(self.hats):
                    self.hats_status[hat] = JJoystick.OBJECT.get_hat(hat)
        except Exception as e:
            JJoystick.QUANTITY = 0
            JJoystick.PRESENT = False
            if self.verbosity:
                print(e)

    def check_hat_status(self, hat_number_: int = 0):
        """ Check a given hat and return its value """
        argument = None
        try:
            if self.hats > 0:
                assert isinstance(hat_number_, int), \
                    'Expecting int for argument hat got %s ' % type(hat_number_)
                argument = JJoystick.OBJECT.get_hat(hat_number_)

        except (pygame.error, AssertionError) as e:
            JJoystick.QUANTITY = 0
            JJoystick.PRESENT = False
            if self.verbosity:
                print(e)

        finally:
            return argument

    def check_ball_position(self, ball_number_: int = 0):
        argument = None
        try:
            if self.balls > 0:
                assert isinstance(ball_number_, int), \
                    'Expecting int for argument ball_number_ got %s ' % type(ball_number_)
                argument = JJoystick.OBJECT.get_ball(ball_number_)

        except (pygame.error, AssertionError) as e:
            JJoystick.QUANTITY = 0
            JJoystick.PRESENT = False
            if self.verbosity:
                print(e)

        finally:
            return argument


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

    SCREENRECT = pygame.Rect(0, 0, 800, 1024)
    screen = pygame.display.set_mode(SCREENRECT.size, pygame.HWSURFACE, 32)
    BACKGROUND = pygame.image.load('Assets\\ps3-logo2.png').convert()
    BACKGROUND = pygame.transform.smoothscale(BACKGROUND, SCREENRECT.size)

    PS3_SCHEME = pygame.image.load('Assets\\PS3_Layout.png').convert_alpha()
    PS3_SCHEME = pygame.transform.smoothscale(PS3_SCHEME, (600, 272))

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

    GL.JOYSTICK = JJoystick(0, 0.01, verbosity_=False)

    Halo.images = HALO_SPRITE_RED
    Halo.containers = GL.All

    PS3Scheme.containers = GL.All
    PS3Scheme.images = PS3_SCHEME
    ps3 = PS3Scheme(SCREENRECT.center, layer_=0, timing_=100)

    clock = pygame.time.Clock()
    STOP_GAME = False

    FRAME = 0
    while not STOP_GAME:

        for event in pygame.event.get():
            keys = pygame.key.get_pressed()

            if event.type == pygame.QUIT:
                print('Quitting')
                STOP_GAME = True

            if event.type == pygame.MOUSEMOTION:
                GL.MOUSE_POS = pygame.math.Vector2(event.pos)

        screen.blit(BACKGROUND, (0, 0))
        GL.All.update()
        GL.All.draw(screen)
        GL.TIME_PASSED_SECONDS = clock.tick(60)

        # update list of all joystick buttons
        GL.JOYSTICK.check_all_buttons_status()
        GL.JOYSTICK.check_axes_position()
        GL.JOYSTICK.check_hats_status()
        pygame.display.flip()
        FRAME += 1
        GL.SOUND_SERVER.update()

    pygame.quit()
