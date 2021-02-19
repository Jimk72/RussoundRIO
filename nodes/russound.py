#!/usr/bin/env python3
"""
Polyglot v2 node server Russound status and control via RIO protocol
Copyright (C) 2020 Robert Paauwe
"""

try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
import sys
import time
import datetime
import requests
import threading
import socket
import math
import re
import russound_main
import node_funcs
from nodes import zone

LOGGER = polyinterface.LOGGER

@node_funcs.add_functions_as_methods(node_funcs.functions)
class Controller(polyinterface.Controller):
    id = 'russound'
    hint = [0,0,0,0]

    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'RussoundRIO'
        self.address = 'rio'
        self.primary = self.address
        self.configured = False
        self.rio = None
        self.sock = None
        self.mesg_thread = None
        self.source_status = 0x00 # assume all sources are inactive

        self.params = node_funcs.NSParameters([{
            'name': 'IP Address',
            'default': 'IP of MCA Controller',
            'isRequired': True,
            'notice': 'IP Address of serial network interface must be set',
            },
            {
            'name': 'Port',
            'default': '9621',
            'isRequired': False,
            'notice': '',
            },
            {
            'name': 'Number of Controllers',
            'default': '1',
            'isRequired': False,
            'notice': '',
            },
            {
            'name': 'Zones per Controller',
            'default': '6',
            'isRequired': False,
            'notice': '',
            },
            ])

        self.poly.onConfig(self.process_config)

    # Process changes to customParameters
    def process_config(self, config):
        (valid, changed) = self.params.update_from_polyglot(config)
        if changed and not valid:
            LOGGER.debug('-- configuration not yet valid')
            self.removeNoticesAll()
            self.params.send_notices(self)
        elif changed and valid:
            LOGGER.debug('-- configuration is valid')
            self.removeNoticesAll()
            self.configured = True
            
        elif valid:
            LOGGER.debug('-- configuration not changed, but is valid')
            # is this necessary
            #self.configured = True

    def start(self):
        LOGGER.info('Starting node server')
        self.set_logging_level()
        self.check_params()
                
        
        # Open a connection to the Russound
        if self.configured:
            LOGGER.info('Initializing TCP to Russound')
            self.rio = russound_main.RIOConnection(self.params.get('IP Address'), self.params.get('Port'), False)
            
            self.rio.Connect()
            #self.discover()
            
            if self.rio.connected:
                LOGGER.info('Connected to Russound')
                # Start a thread that listens for messages from the russound.
                self.mesg_thread = threading.Thread(target=self.rio.MessageLoop, args=(self.processCommand,))
                self.mesg_thread.daemon = True
                self.mesg_thread.start()

                # Query each zone name
                LOGGER.info('Getting Zone Names!')
                for x in range(int(self.params.get('Number of Controllers'))):
                    for z in range(int(self.params.get('Zones per Controller'))):
                        self.rio.get_info('C[' + str(x+1) + '].Z[' + str(z+1) + ']', 'name')
                        time.sleep(1)
                    time.sleep(4)
                time.sleep(5)
                
                # Query each zone
                for x in range(int(self.params.get('Number of Controllers'))):
                    for z in range(int(self.params.get('Zones per Controller'))):
                        self.rio.get_info('C['+str(x+1)+'].Z['+str(z+1)+']', 'all')
                        time.sleep(2)
                time.sleep(5)
                self.rio.get_info('System', 'all')
               
            LOGGER.info('Node server started')
        else:
            LOGGER.info('Waiting for configuration to be complete')

    def longPoll(self):
        pass

    def shortPoll(self):
        pass

    def query(self):
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def discover(self, rioNode, nodeName):
        node = zone.Zone(self, self.address, rioNode, nodeName)
        node.setRIO(self.rio)
        try:
            LOGGER.debug('Compare old name to new name:' + self.poly.getNode(rioNode)['name'] +'=' + nodeName + '?')
            if self.poly.getNode(rioNode)['name'] != nodeName:
                self.delNode(rioNode)
                time.sleep(1)  # give it time to remove from database
        except:
            LOGGER.warning('Failed to delete node for zone ' + rioNode)
        self.addNode(node)

    # Delete the node server from Polyglot
    def delete(self):
        LOGGER.info('Removing node server')

    def stop(self):
        LOGGER.info('Stopping node server')

    def update_profile(self, command):
        st = self.poly.installprofile()
        return st

    def check_params(self):
        # NEW code, try this:
        self.removeNoticesAll()

        if self.params.get_from_polyglot(self):
            LOGGER.debug('All required parameters are set!')
            self.configured = True
        else:
            LOGGER.debug('Configuration required.')
            LOGGER.debug('IP Address = ' + self.params.get('IP Address'))
            self.params.send_notices(self)

    def remove_notices_all(self, command):
        self.removeNoticesAll()

    def processCommand(self, msg):
        if msg != 'S':
            if msg[0:13] == 'N System.time':
                LOGGER.debug('Russound Time received')
                self.rio.get_info('System', 'status')
            if msg[0] == 'N' or msg[0] == 'S':
                if msg[2] == 'C' and msg[10] == ']':
                    curZone = 'zone_' +msg[4]+ msg[9]
                    curCommand = msg[12: msg.find('=')]
                    curValue = msg[msg.find('=')+2:-1]
                    LOGGER.debug('From Russound: ' + msg)
                    #Change ON/OFF to 1/0
                    if curValue == 'OFF' : 
                        curValue = 0
                    if curValue == 'ON' : 
                        curValue = 1
                    if curCommand == 'status' :
                        self.nodes[curZone].set_power(curValue)
                    # This is where we get the name info from a zone and add the node
                    elif curCommand == 'name' and msg[0] == 'S':
                        if curValue == '':
                            curValue = 'Unused'
                        self.discover(curZone, curValue)
                    elif curCommand == 'volume' :
                        self.nodes[curZone].set_volume(int(curValue))
                    elif curCommand == 'turnOnVolume' :
                        LOGGER.debug('Turn on valume not setup yet')
                    elif curCommand == 'mute' :
                        self.nodes[curZone].set_mute(curValue)
                    elif curCommand == 'page' :
                        self.nodes[curZone].set_page(curValue)
                    elif curCommand == 'sharedSource' :
                        self.nodes[curZone].set_shared_source(curValue)
                    elif curCommand == 'treble' :
                        self.nodes[curZone].set_treble(int(curValue)+10)
                    elif curCommand == 'bass' :
                        self.nodes[curZone].set_bass(int(curValue)+10)
                    elif curCommand == 'balance' :
                        self.nodes[curZone].set_balance(int(curValue)+10)
                    elif curCommand == 'currentSource' :
                        self.nodes[curZone].set_source(int(curValue)-1)
                    elif curCommand == 'loudness' :
                        self.nodes[curZone].set_loudness(curValue)
                    elif curCommand == 'partyMode' :
                        self.nodes[curZone].set_party_mode(curValue)
                    elif curCommand == 'doNotDisturb' :
                        self.nodes[curZone].set_dnd(curValue)

    def set_logging_level(self, level=None):
        if level is None:
            try:
                level = self.get_saved_log_level()
            except:
                LOGGER.error('set_logging_level: get saved level failed.')

            if level is None:
                level = 10
            level = int(level)
        else:
            level = int(level['value'])

        self.save_log_level(level)

        LOGGER.info('set_logging_level: Setting log level to %d' % level)
        LOGGER.setLevel(10)


    commands = {
            'UPDATE_PROFILE': update_profile,
            'REMOVE_NOTICES_ALL': remove_notices_all,
            'DEBUG': set_logging_level,
            }

    # For this node server, all of the info is available in the single
    # controller node.
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},   # node server status
            ]

