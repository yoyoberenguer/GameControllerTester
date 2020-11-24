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
__status__ = "Joystick Client"

import pygame
import socket
import _pickle as pickle
import threading


class JoystickClientSocket(threading.Thread):
    """
        Open a socket and listen for incoming data
        Here is the data layout (JoystickObject class)

        self.id = id_
        self.name = name_
        self.axes = axes_
        self.axes_status = axes_status_
        self.buttons = buttons_
        self.button_status = buttons_status_
        self.hat = hat_
        self.hats_status = hats_status
        self.balls = balls_
        self.balls_status = balls_status_

    """

    def __init__(self,
                 host_,  # host address
                 port_,  # port value
                 ):

        """
        Create a socket to received Joystick pickle objects
        :param host_: String corresponding to the server address
        :param port_: Integer used for the port.
                      Port to listen on (non-privileged ports are > 1023) and 0 < port_ < 65535
        """

        assert isinstance(host_, str), \
            'Expecting string for argument host_, got %s instead.' % type(host_)
        assert isinstance(port_, int), \
            'Expecting integer for argument port_, got %s instead.' % type(port_)
        # Port to listen on (non-privileged ports are > 1023)
        assert 0 < port_ < 65535, \
            'Incorrect value assign to port_, 0 < port_ < 65535, got %s ' % port_

        threading.Thread.__init__(self)
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Bind the socket to the port
            self.sock.bind((host_, port_))
        except socket.error as error:
            print('\n[-] Error : %s ' % error)
            raise SystemExit

        try:
            # Listen for incoming connections
            self.sock.listen(1)
        except socket.error as error:
            print('\n[-] Error : %s ' % error)
            raise SystemExit

    def run(self):

        print('\n[+] Info : Client socket is listning...')
        while not GL.STOP.isSet():
            try:
                buffer = b''
                # Wait for a connection
                connection, client_address = self.sock.accept()

                # Receive the data in small chunks
                while not GL.STOP.isSet():
                    data = connection.recv(1024)
                    pyobject = pickle.loads(data)
                    if data == b'quit':
                        print('\n[-] WARNING : Client socket is aborting')
                        GL.STOP.set()
                        break

                    else:
                        if isinstance(pyobject, JoystickObject):
                            # print('data received : ', data)
                            # print('data decoded  : ', pyobject)
                            print('\n')
                            print('Joystick id %s ' % pyobject.id)
                            print('Joystick name %s ' % pyobject.name)
                            print('Joystick axes %s ' % pyobject.axes)
                            print('Joystick axes_status %s ' % pyobject.axes_status)
                            print('Joystick button %s ' % pyobject.buttons)
                            print('Joystick button_status %s ' % pyobject.button_status)
                            print('Joystick hats %s ' % pyobject.hat)
                            print('Joystick hats_status %s ' % pyobject.hats_status)
                            print('Joystick balls %s ' % pyobject.balls)
                            print('Joystick balls_status %s ' % pyobject.balls_status)

            except:
                pass

            finally:
                connection.close()
        print('\n[-] Info : Client thread is now terminated.')


def JoystickServerSocket(host_, port_, data_):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host_, port_))
        s.sendall(pickle.dumps(data_))
        s.close()
        return True


class JoystickAttributes:
    """
    Create a Joystick object with formatted attributes

    """

    def __init__(self,
                 id_: int = 0,
                 name_: str = '',
                 axes_: int = 0,
                 buttons_: int = 0,
                 hats_: int = 0,
                 balls_: int = 0,
                 ):
        """
        :param id_:         get the Joystick ID
        :param name_:       get the Joystick system name
        :param axes_:       get the number of axes
        :param buttons_:    get the number of buttons
        :param hats_:       get the number of hat controls
        :param balls_:      get the number of trackballs
        """
        """
        assert isinstance(id_, int), 'Expecting integer for argument id_, got %s ' % type(id_)
        assert isinstance(name_, str), 'Expecting string for argument name_, got %s ' % type(name_)
        assert isinstance(axes_, int), 'Expecting integer for argument axes_, got %s ' % type(axes_)
        assert isinstance(buttons_, int), 'Expecting integer for argument buttons_, got %s ' % type(buttons_)
        assert isinstance(hats_, int), 'Expecting integer for argument hats_, got %s ' % type(hats_)
        assert isinstance(balls_, int), 'Expecting integer for argument balls_, got %s ' % type(balls_)
        """
        self.id = id_
        self.name = name_
        self.axes = axes_
        self.button = buttons_
        self.hats = hats_
        self.balls = balls_
        try:
            self.button_status = [False] * self.button                  # init the buttons status
            self.axes_status = [0] * self.axes                          # init the axes status
            self.hats_status = [(0, 0)] * self.hats                     # init hats status
            self.balls_status = [pygame.math.Vector2()] * self.balls    # init the trackballs

        except IndexError as e:
            print('\n[-] ERROR Joystick Object cannot be instantiated. ', e)


class JoystickObject:
    """
    Create a Joystick object referencing all attributes
    """

    def __init__(self,
                 id_: int = 0,
                 name_: str = '',
                 axes_: int = 0,
                 axes_status_: int = 0,
                 buttons_: int = 0,
                 buttons_status_: int = 0,
                 hat_: int = 0,
                 hats_status: int = 0,
                 balls_: int = 0,
                 balls_status_: int = 0
                 ):
        """
        :param id_:             get the Joystick ID
        :param name_:           get the Joystick system name
        :param axes_:           get the number of axes
        :param axes_status_:    get the axes status
        :param buttons_:        get the number of buttons
        :param buttons_status_: get the buttons status
        :param hats_:           get the number of hat controls
        :param hats_status:     get the status of hat controls
        :param balls_:          get the number of trackballs
        :param balls_status_:   get the trackballs status
        """
        self.id = id_
        self.name = name_
        self.axes = axes_
        self.axes_status = axes_status_
        self.buttons = buttons_
        self.button_status = buttons_status_
        self.hat = hat_
        self.hats_status = hats_status
        self.balls = balls_
        self.balls_status = balls_status_


class JJoystick(JoystickAttributes):
    """
        Prior testing the Joystick
        1) The pygame display has to be initialised pygame.init()
    """
    PRESENT = False  # Confirm if a joystick is present (bool)
    QUANTITY = 0  # How many joystick(s) are connected (int)
    OBJECT = []  # Bind to the joystick(s) device(s)-> pygame.joystick.Joystick object

    def __init__(self,
                 joystick_id_: int = 0,
                 sensitivity_: float = 0.01,
                 verbosity_: bool = False
                 ):

        """
        :joystick_id_ id_: get the Joystick ID integer
        :sensitivity_ name_: Joystick sensitivity threshold default float 0.01, any variation below
        the threshold will be ignored.
        :param verbosity_: verbosity (bool False | True)

        """

        assert isinstance(joystick_id_, int), \
            'Expecting int for argument joystick_id_ got %s ' % type(joystick_id_)
        assert isinstance(sensitivity_, float), \
            'Expecting float for argument sensitivity_ got %s ' % type(sensitivity_)
        assert isinstance(verbosity_, bool), \
            'Expecting bool for argument verbosity_ got %s ' % type(verbosity_)
        assert isinstance(JJoystick.OBJECT, list), \
            'Expecting list for argument OBJECT got %s ' % type(JJoystick.OBJECT)

        self.verbosity = verbosity_  # default False
        self.sensitivity = sensitivity_  # axis sensitivity_
        self.init_joystick()
        self.args = None
        JoystickAttributes.__init__(self)

    def init_joystick(self):

        if not bool(pygame.joystick.get_init()):  # return bool
            # Initialize the joystick module.
            # This will scan the system for all joystick devices.
            pygame.joystick.init()

        JJoystick.QUANTITY = self.get_joystick_number()  # returns the number of joystick available

        if JJoystick.QUANTITY == 0:
            self.no_joystick()

        # at least one Joystick is present
        else:

            if self.verbosity:
                print('\n[+] Info %s joystick(s) detected...' % JJoystick.QUANTITY)

            for joystick_id in range(JJoystick.QUANTITY):

                JJoystick.PRESENT = True

                # Reference object into a python list
                JJoystick.OBJECT.append(pygame.joystick.Joystick(joystick_id))
                JJoystick.OBJECT[joystick_id].init()

                self.args = self.get_overall_status(joystick_id)

                if self.args is not None:
                    JoystickAttributes.__init__(self, *list(self.args))
                else:
                    self.no_joystick(joystick_id)

    @staticmethod
    def pickle_data(data):
        """
            Pickle all the joystick buttons including hats and axes before
            sending the data through the network
        """
        return pickle.dumps(data)

    @staticmethod
    def adjust_quantity():
        """
        Current tested joystick failed to respond.
        Decrement quantity.
        """
        JJoystick.QUANTITY -= 1

        # None of the joystick are responding
        # Flag PRESENT is set to False (no joystick present)
        if JJoystick.QUANTITY < 0:
            JJoystick.QUANTITY = 0
            JJoystick.PRESENT = False
        else:
            JJoystick.PRESENT = True

    def no_joystick(self, id_=None):
        """ No joystick present """
        if id_ is None:
            JJoystick.QUANTITY = 0
            JJoystick.OBJECT = []
            print('\n[-] Info No Joystick available...')
        else:
            assert isinstance(id_, int), 'Expecting int for argument id_, got %s ' % type(id_)
            self.adjust_quantity()
            if isinstance(JJoystick.OBJECT, list):
                JJoystick.OBJECT[id_] = None
            else:
                raise Exception

    @staticmethod
    def get_joystick_number() -> int:
        """
            Return the number of joysticks connected to the interface (int).
            Returns 0 if no joystick available
        """
        quantity = 0
        try:
            quantity = pygame.joystick.get_count()
        except Exception as e:
            JJoystick.QUANTITY = 0
            JJoystick.PRESENT = False
            JJoystick.OBJECT = []
            print('\n[-] Error: ', e)
            quantity = 0

        finally:
            return quantity

    def get_overall_status(self, joystick_id_=0):

        """
            Fetch number of buttons, hats and axes.
            Joystick_id_ (int) select the joystick object from all joysticks that have been detected
            If an error occurred during the checks None is return otherwise return a tuple.
        """

        args = None
        try:
            assert isinstance(joystick_id_, int), \
                'Expecting int for argument joystick_id_ got %s ' % type(joystick_id_)

            obj = JJoystick.OBJECT[joystick_id_]

            args = obj.get_id(), \
                obj.get_name(), \
                obj.get_numaxes(), \
                obj.get_numbuttons(), \
                obj.get_numhats(), \
                obj.get_numballs()

            if self.verbosity:
                print('\n id %s, \n name %s, \n number of axes  %s, '
                      '\n number of button %s, \n number of hats %s, \n number of balls %s' 
                      '\n number of trackball %s ' % (tuple(args)))
            return args

        except (pygame.error, AssertionError, AttributeError) as err:
            self.adjust_quantity()
            args = None
            print('\n[-] Joystick id, %s Error: %s' % (joystick_id_, err))

        finally:
            return args

    def get_all_status(self, joystick_id_=0):
        """
            Returns all the Joysticks attributes values (button's status, axes position and hats value.
            Returns None if an error occurred.
        """

        jobject = None
        try:
            assert len(JJoystick.OBJECT) >= joystick_id_ + 1, 'Argument Joystick_id is incorrect.'

            obj = JJoystick.OBJECT[joystick_id_]
            if JJoystick.PRESENT and isinstance(obj, pygame.joystick.JoystickType):

                JoystickAttributes.__init__(self, *list(self.get_overall_status(joystick_id_)))

                # buttons status
                for i in range(self.button):
                    self.button_status[i] = True if \
                        obj.get_button(i) else False

                # Axis status
                for axis in range(self.axes):
                    axis_response = round(obj.get_axis(axis), 4)
                    self.axes_status[axis] = axis_response if axis_response > self.sensitivity \
                        or axis_response < -self.sensitivity else 0.0

                # hats status
                if self.hats > 0:
                    for hat in range(self.hats):
                        self.hats_status[hat] = obj.get_hat(hat)

                # trackball
                if self.balls > 0:
                    for balls in range(self.balls):
                        self.balls_status[balls] = obj.get_ball(balls)

                jobject = JoystickObject(obj.get_id(), obj.get_name(), self.button, self.button_status, self.axes,
                                        self.axes_status, self.hats, self.hats_status, self.balls, self.balls_status)

            return jobject

        except (AssertionError, AttributeError) as err:
            print('\n[-] Joystick id, %s Error: %s' % (joystick_id_, err))
            return jobject

    def check_ball_position(self, ball_number_: int = 0, joystick_id_=0):
        """
            Get the relative position of a trackball.
            Return None if an error occurred

        """
        argument = None
        try:

            if JJoystick.PRESENT and len(JJoystick.OBJECT) > 0 and \
                    isinstance(JJoystick.OBJECT[joystick_id_], pygame.joystick.JoystickType):

                obj = JJoystick.OBJECT[joystick_id_]

                if hasattr(obj, 'balls'):
                    if obj.balls > 0:
                        assert isinstance(ball_number_, int), \
                            'Expecting int for argument ball_number_ got %s ' % type(ball_number_)
                        argument = obj.get_ball(ball_number_)
                else:
                    if obj.verbosity:
                        print('\n[-] Error JJoystick missing attribute balls.')
                    raise AssertionError

        except (pygame.error, AssertionError, AttributeError) as e:
            self.adjust_quantity()
            print('\n[-] Joystick id %s, Error %s ' % (joystick_id_, e))

        finally:
            return argument


class GL:
    STOP = threading.Event()


if __name__ == '__main__':

    host = '127.0.0.1'
    port = 81

    socket.setdefaulttimeout(60)

    pygame.init()
    pygame.mixer.init()

    SCREENRECT = pygame.Rect(0, 0, 800, 600)
    import os
    os.environ['SDL_VIDEODRIVER'] = ''
    screen = pygame.display.set_mode(SCREENRECT.size, pygame.HWSURFACE, 32)

    GL.All = pygame.sprite.Group()
    GL.TIME_PASSED_SECONDS = 0

    GL.JOYSTICK = JJoystick(0, 0.01, verbosity_=False)

    clock = pygame.time.Clock()
    STOP_GAME = False

    FRAME = 0

    # JoystickClientSocket(host, port).start()

    while not STOP_GAME:

        for event in pygame.event.get():
            keys = pygame.key.get_pressed()

            if event.type == pygame.QUIT:
                print('Quitting')
                STOP_GAME = True

            if keys[pygame.K_ESCAPE]:
                STOP_GAME = True

            if event.type == pygame.MOUSEMOTION:
                GL.MOUSE_POS = pygame.math.Vector2(event.pos)

        GL.All.update()
        GL.All.draw(screen)
        GL.TIME_PASSED_SECONDS = clock.tick(60)

        JoystickServerSocket(host, port, GL.JOYSTICK.get_all_status(0))
        pygame.display.flip()
        FRAME += 1

    pygame.quit()
