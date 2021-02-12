# Node definition for a Russound zone
# 

try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
import json
import time
import datetime
import russound
import node_funcs

LOGGER = polyinterface.LOGGER

@node_funcs.add_functions_as_methods(node_funcs.functions)
class Zone(polyinterface.Node):
    id = 'zone'
    power_state = False
    """
    What makes up a zone? 
        Power
        Source
        Volume
        Bass
        Treble
        Party Mode
        Do Not Disturb
    """

    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 25},       # zone power
            {'driver': 'GV0', 'value': 0, 'uom': 25},      # zone source
            {'driver': 'SVOL', 'value': 0, 'uom': 12},     # zone volume
            {'driver': 'GV2', 'value': 0, 'uom': 56},      # zone treble
            {'driver': 'GV3', 'value': 0, 'uom': 56},      # zone bass
            {'driver': 'GV4', 'value': 0, 'uom': 56},      # zone balance
            {'driver': 'GV5', 'value': 0, 'uom': 25},       # loudness
            {'driver': 'GV6', 'value': 0, 'uom': 25},       # do not disturb
            {'driver': 'GV7', 'value': 0, 'uom': 25},       # party mode
            {'driver': 'GV8', 'value': 0, 'uom': 25},       # mute
            {'driver': 'GV9', 'value': 0, 'uom': 25},       # page
            {'driver': 'GV10', 'value': 0, 'uom': 25},       # shared source
            ]

    def setRIO(self, rio):
        self.rio = rio
   
    def set_power(self, power):
        self.setDriver('ST', power, True, True, 25)
        if power == 0:
            self.power_state = False
        else:
            self.power_state = True

    def set_source(self, source):
        self.setDriver('GV0', source + 1, True, True, 25)

    def set_volume(self, vol):
        self.setDriver('SVOL', vol, True, True, 12)

    def set_treble(self, vol):
        # display is -10 to +10
        self.setDriver('GV2', vol - 10, True, True, 56)

    def set_bass(self, vol):
        # display is -10 to +10
        self.setDriver('GV3', vol - 10, True, True, 56)

    def set_balance(self, vol):
        self.setDriver('GV4', vol - 10, True, True, 56)

    def set_loudness(self, toggle):
        self.setDriver('GV5', toggle, True, True, 25)

    def set_dnd(self, toggle):
        self.setDriver('GV6', toggle, True, True, 25)

    def set_party_mode(self, toggle):
        self.setDriver('GV7', toggle, True, True, 25)
    
    def set_mute(self, toggle):
        self.setDriver('GV8', toggle, True, True, 25)

    def set_page(self, toggle):
        self.setDriver('GV9', toggle, True, True, 25)

    def set_shared_source(self, toggle):
        self.setDriver('GV10', toggle, True, True, 25)

    def get_power(self):
        return self.power_state

    def process_cmd(self, cmd=None):
        # {'address': 'zone_11', 'cmd': 'VOLUME', 'value': '28', 'uom': '56', 'query': {}}
        isyZone = cmd['address']
        RioZone = 'C[' + isyZone[5] + '].Z[' + isyZone[6] + ']'
        LOGGER.debug('ISY sent: ' + str(cmd))
        if cmd['cmd'] == 'VOLUME':
            self.rio.volume(RioZone, int(cmd['value']))
        elif cmd['cmd'] == 'BASS':
            self.rio.set_param(RioZone, 0, int(cmd['value'])+10)
            
        elif cmd['cmd'] == 'TREBLE':
            self.rio.set_param(RioZone, 1, int(cmd['value'])+10)
            
        elif cmd['cmd'] == 'BALANCE':
            self.rio.set_param(RioZone, 3, int(cmd['value'])+10)

        elif cmd['cmd'] == 'MUTE':
            self.rio.set_param(RioZone, 5, int(cmd['value']))
            
        elif cmd['cmd'] == 'LOUDNESS':
            self.rio.set_param(RioZone, 2, int(cmd['value']))
            
        elif cmd['cmd'] == 'DND':
            self.rio.set_param(RioZone, 6, int(cmd['value']))
            
        elif cmd['cmd'] == 'PARTY':
            self.rio.set_param(RioZone, 7, int(cmd['value']))
            
        elif cmd['cmd'] == 'SOURCE':
            self.rio.set_source(RioZone, int(cmd['value'])-1)
            
        elif cmd['cmd'] == 'DFON':
            self.rio.set_state(RioZone, 1)
        elif cmd['cmd'] == 'DFOF':
            self.rio.set_state(RioZone, 0)

    commands = {
            'VOLUME': process_cmd,
            'SOURCE': process_cmd,
            'BASS': process_cmd,
            'TREBLE': process_cmd,
            'BALANCE': process_cmd,
            'LOUDNESS': process_cmd,
            'DND': process_cmd,
            'PARTY': process_cmd,
            'DFON': process_cmd,
            'DFOF': process_cmd,
            'MUTE': process_cmd,
            }

