# encoding: utf-8
"""

                   GNU GENERAL PUBLIC LICENSE

                       Version 3, 29 June 2007


 Copyright (C) 2007 Free Software Foundation, Inc. <http://fsf.org/>

 Everyone is permitted to copy and distribute verbatim copies

 of this license document, but changing it is not allowed.
 """

__author__ = "Yoann Berenguer"
__copyright__ = "Copyright 2007, Cobra Project"
__credits__ = ["Yoann Berenguer"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Yoann Berenguer"
__email__ = "yoyoberenguer@hotmail.com"
__status__ = "Joystick Server"


import pygame
import socket
import _pickle as pickle
import time


def send_to_client(host_, port_, data_):
    
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((host_, port_))
                compress_data = pickle.dumps(data_)
                s.sendall(compress_data)

            except (Exception, socket.error) as error:
                print('\n[-]JoystickServer Error %s ' % error)
                
            finally:
                s.close()
            

class JoystickObject:
    """ Create a Joystick object referencing the device """

    def __init__(self,
                 id_: int = None,
                 name_: str = None,
                 axes_: int = None,
                 buttons_: int = None,
                 hats_: int = None,
                 balls_: int = None
                 ):
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
    PRESENT = False    # Confirm if a joystick is connected
    QUANTITY = 0       # How many joystick(s) are connected
    OBJECT = None      # Bind to the device

    def __init__(self,
                 joystick_id_: int = 0,
                 sensitivity_: float = 0.01,
                 verbosity_: bool = False
                 ):

        assert isinstance(joystick_id_, int), \
            'Expecting int for argument joystick_id_ got %s ' % type(joystick_id_)
        assert isinstance(sensitivity_, float), \
            'Expecting float for argument sensitivity_ got %s ' % type(sensitivity_)
        assert isinstance(verbosity_, bool), \
            'Expecting bool for argument verbosity_ got %s ' % type(verbosity_)

        self.verbosity = verbosity_        # default False 
        self.id = joystick_id_             # default 0
        self.sensitivity = sensitivity_    # axis sensitivity_.

        self.init_joystick()
        
        print('\n')
        print('\n Joystick id %s ' % self.id)
        print('\n Joystick name %s ' % self.name)
        print('\n Joystick axes %s ' % self.axes)
        print('\n Joystick button %s ' % self.button)
        print('\n Joystick hats %s ' % self.hats)
        print('\n Joystick balls %s ' % self.balls)
        print('\n Joystick button_status %s ' % self.button_status)
        print('\n Joystick axes_status %s ' % self.axes_status)
        print('\n Joystick hats_status %s ' % self.hats_status)

    def init_joystick(self):
        if not pygame.joystick.get_init():
            pygame.joystick.init()

        # Checking how many joysticks are connected
        if pygame.joystick.get_count() == 0:
            self.joystick_not_present()
        # at least one
        else:
            if self.verbosity:
                print('Joystick(s) detected...')
            # Show at least one joystick available
            JJoystick.PRESENT = True

            # todo if finding more than one should we
            # iterate them ? and add the object into a python list to reference the objects??
            # self.id need to be incremented
            self.check_joystick_quantity()

            # todo last joystick will override the first one if more than one joystick
            self.args = self.create_joystick_object(self.id)
            if self.args is not None:
                JoystickObject.__init__(self, *list(self.args))
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
                print('Error while checking the number of joystick connected: ', e)

    def create_joystick_object(self, joystick_id_: int = 0) -> tuple:
        """ Create a new joystick to access a physical device. """
        try:
            arguments = None

            assert isinstance(joystick_id_, int), \
                'Expecting int for argument joystick_id_ got %s ' % type(joystick_id_)

            if JJoystick.PRESENT:
                JJoystick.OBJECT = pygame.joystick.Joystick(joystick_id_)
                JJoystick.OBJECT.init()

                if self.verbosity:
                    print(JJoystick.OBJECT.get_id(), \
                          JJoystick.OBJECT.get_name(), \
                          JJoystick.OBJECT.get_numaxes(), \
                          JJoystick.OBJECT.get_numbuttons(), \
                          JJoystick.OBJECT.get_numhats(), \
                          JJoystick.OBJECT.get_numballs())

                arguments = JJoystick.OBJECT.get_id(), \
                            JJoystick.OBJECT.get_name(), \
                            JJoystick.OBJECT.get_numaxes(), \
                            JJoystick.OBJECT.get_numbuttons(), \
                            JJoystick.OBJECT.get_numhats(), \
                            JJoystick.OBJECT.get_numballs()

        except (pygame.error, AssertionError) as err:
            # todo quantity zero ? what about two joysticks connected
            JJoystick.QUANTITY = 0
            JJoystick.PRESENT = False
            arguments = None
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


if __name__ == '__main__':

    host = '127.0.0.1'
    port = 81

    socket.setdefaulttimeout(60)

    pygame.init()
    pygame.mixer.init()

    SCREENRECT = pygame.Rect(0, 0, 800, 600)
    screen = pygame.display.set_mode(SCREENRECT.size, pygame.HWSURFACE, 32)

    All = pygame.sprite.Group()
    TIME_PASSED_SECONDS = 0

    JOYSTICK = JJoystick(0, 0.01, verbosity_=True)

    # JOYSTICK.OBJECT = JoystickAttributes(0, 'Joystick 0', 4, 4, 4, 4)

    clock = pygame.time.Clock()
    STOP_GAME = False

    FRAME = 0

    while not STOP_GAME:

        for event in pygame.event.get():
            keys = pygame.key.get_pressed()

            if event.type == pygame.QUIT:
                print('Quitting')
                STOP_GAME = True

            if keys[pygame.K_ESCAPE]:
                STOP_GAME = True

        All.update()
        All.draw(screen)
        TIME_PASSED_SECONDS = clock.tick(60)

        # update list of all joystick buttons
        JOYSTICK.check_all_buttons_status()
        JOYSTICK.check_axes_position()
        JOYSTICK.check_hats_status()
        pygame.display.flip()
        FRAME += 1
        time.sleep(0.1)
        print(JOYSTICK.button_status)
        send_to_client(host, port, JOYSTICK)

    pygame.quit()
