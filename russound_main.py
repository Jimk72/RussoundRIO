#
# Russound support functions.
#
#  Open a connection to the Russound device
#  Wait for messages from the Russound device

from polyinterface import LOGGER
import time
import socket
import threading

russound_connected = False

class RIOConnection:
    LOGGER = None
    def __init__(self, ipaddress, port, udp):
        self.ip = ipaddress
        self.port = int(port)
        self.udp = udp
        self.connected = False
        self.sock = None

    ## Connect to the Russound via IP address 
    def __russound_connect_tcp(self, ip, port):
        global russound_connected
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((ip, int(port)))
            russound_connected = True
            self.connected = True
        except socket.error as msg:
            LOGGER.error('Error trying to connect to russound controller.')
            LOGGER.error(msg)
            self.sock = None
        
        return self.sock

    def Connect(self):
        self.__russound_connect_tcp(self.ip, self.port)


    def Send(self, data):
        self.sock.send(data.encode())

    # Main loop waits for messages from Russound and then processes them
    def __russound_loop_tcp(self, processCommand):
        while self.connected:
            try:
                data = self.sock.recv(4096)
                if data == b'':
                    LOGGER.debug('Connection Closed by Russound!')
                riocmd = data.splitlines()
                for x in riocmd:
                    processCommand(x.decode())

            except BlockingIOError:
                LOGGER.info('waiting on data')
                pass
            except ConnectionResetError as msg:
                LOGGER.error('Connection error: ' + str(msg))
                self.connected = False

    def MessageLoop(self, processCommand):
        self.__russound_loop_tcp(processCommand)

    

    # Send a request to the controller to send various types of information
    # about a specific zone.
    #  name - Zone name
    #  volume - current volume
    #  currentSource - selected source
    #  status - current on/off state
    #  all - all info
    #  bass - current bass level
    #  treble- current treble level
    #  loudness - current loudness level
    #  balance - current balance
    #  turnOnVolume - current turn on volume
    #  doNotDisturb - current do not distrub
    #  partyMode - current party mode
    def get_info(self, rioZone, info_type):
        data = ''
        if info_type == 'all':
            data = 'WATCH ' + rioZone + ' ON\r\n'
        else:
            data = 'GET ' + rioZone + '.' + info_type + '\r\n'
        if data != '':
            self.Send(data)
        else:
            LOGGER.debug('Unkown request!')
        

    # params 0 = bass, 1 = treble, 2 = loudness, 3 = balance,
    #        4 = turn on vol, 5 = mute, 6 = do no disturb, 7 = party mode
    def set_param(self, rioZone, param, level):
        LOGGER.debug('sending Zone:' + rioZone + ' level:' + str(level) )
        if param == 0:
            data = 'SET ' + rioZone + '.bass="' + str(level-10) + '"\r\n'
        if param == 1:
            data = 'SET ' + rioZone + '.treble="' + str(level-10) + '"\r\n'
        if param == 2:
            if level == 0:
                data = 'SET ' + rioZone + '.loudness="OFF"\r\n'
            else:
                data = 'SET ' + rioZone + '.loudness="ON"\r\n'
        if param == 3:
            data = 'SET ' + rioZone + '.balance="' + str(level-10) + '"\r\n'
        if param == 4:
            data = 'SET ' + rioZone + '.turnOnVolume="' + str(level) + '"\r\n'
        if param == 5:
            if level == 0:
                data = 'EVENT ' + rioZone + '!ZoneMuteOff\r\n'
            else:
                data = 'EVENT ' + rioZone + '!ZoneMuteOn\r\n'
        if param == 6:
            if level == 0:
                data = 'EVENT ' + rioZone + '!DoNotDisturb OFF\r\n'
            else:
                data = 'EVENT ' + rioZone + '!doNotDisturb ON\r\n'
        if param == 7:
            if level == 0:
                data = 'EVENT ' + rioZone + '!PartyMode OFF\r\n'
            else:
                data = 'EVENT ' + rioZone + '!PartyMode ON\r\n'
        self.Send(data)

    def set_source(self, rioZone, source):
        data = 'EVENT ' + rioZone + '!KeyRelease SelectSource ' + str(source+1) + '\r\n'
        self.Send(data)

    def set_state(self, rioZone, state):
        if state == 1:
            data = 'EVENT ' + rioZone + '!ZoneOn\r\n'
            self.Send(data)
        else:
            data = 'EVENT ' + rioZone + '!ZoneOff\r\n'
            self.Send(data)

    def volume(self, rioZone, level):
        data = 'EVENT ' + rioZone + '!KeyPress Volume ' + str(level) + '\r\n'
        self.Send(data)

    
