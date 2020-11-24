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


import socket
import threading
import _pickle as pickle
from JoystickServer import JoystickObject, JJoystick


class GL:
    STOP = threading.Event()


class SocketClient(threading.Thread):

    def __init__(self,
                 host_,     # host address
                 port_,     # port value
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
     
        print('\n[+] INFO : Client socket is listning...')
        while not GL.STOP.isSet():
            try:
                
                # Wait for a connection
                connection, client_address = self.sock.accept()
                
                # Receive the data in small chunks
                while not GL.STOP.isSet():
                        
                    data = connection.recv(1024) 
                    
                    if len(data) > 0:
                        # unpickle_data = pickle.loads(data)
                        unpickle_data = pickle.loads(data)
                        if unpickle_data == b'quit':
                            GL.STOP.set()
                        else:

                            print('\n')
                            print('\n Joystick id %s ' % unpickle_data.id)
                            print('\n Joystick name %s ' % unpickle_data.name)
                            print('\n Joystick axes %s ' % unpickle_data.axes)
                            print('\n Joystick button %s ' % unpickle_data.button)
                            print('\n Joystick hats %s ' % unpickle_data.hats)
                            print('\n Joystick balls %s ' % unpickle_data.balls)
                            print('\n Joystick button_status %s ' % unpickle_data.button_status)
                            print('\n Joystick axes_status %s ' % unpickle_data.axes_status)
                            print('\n Joystick hats_status %s ' % unpickle_data.hats_status)

                    else:
                        break                 
                
            except (Exception, socket.error) as error:
                print('\n[-]JoystickClient Error %s ' % error)
                GL.STOP.set()
                
            finally:            
                connection.close()
                
        print('\n[-] Client socket thread is dead.')


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 81
    SocketClient(host, port).start()
