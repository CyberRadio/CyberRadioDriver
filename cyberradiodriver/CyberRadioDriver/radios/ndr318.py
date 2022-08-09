#!/usr/bin/env python
##################################################################
# \package CyberRadioDriver.radios.ndr318
# \brief NDR318 Support
# \author NH
# \author DA
# \author MN
# \copyright Copyright (c) 2014-2022 CyberRadio Solutions, Inc.
#    All rights reserved.
##################################################################

# Imports from other modules in this package
from CyberRadioDriver import command
from CyberRadioDriver import configKeys
from CyberRadioDriver.radios.ndr308 import \
    ndr308_tuner, \
    ndr308_wbddc, \
    ndr308_nbddc, \
    ndr308_wbddc_group, \
    ndr308_nbddc_group, \
    ndr308_ifSpec, \
    ndr308
# Imports from external modules
# Python standard library imports

## TODO: Enhanced Wideband DDC Support

##
# \internal
# \brief Tuner component class for the NDR318 (all flavors).
#
class ndr318_tuner(ndr308_tuner):
    _name = "Tuner(NDR318)"


##
# \internal
# \brief WBDDC component class for the NDR318.
#
class ndr318_wbddc(ndr308_wbddc):
    _name = "WBDDC(NDR318)"


##
# \internal
# \brief NBDDC component class for the NDR318.
#
class ndr318_nbddc(ndr308_nbddc):
    _name = "NBDDC(NDR318)"


##
# \internal
# \brief WBDDC group component class specific to the NDR318.
#
# A WBDDC group component object maintains one WBDDC group on the radio.
#
class ndr318_wbddc_group(ndr308_wbddc_group):
    _name = "WBDDCGroup(NDR318)"


##
# \internal
# \brief NBDDC group component class specific to the NDR318.
#
# A NBDDC group component object maintains one NBDDC group on the radio.
#
class ndr318_nbddc_group(ndr308_nbddc_group):
    _name = "NBDDCGroup(NDR318)"


##
# \internal
# \brief VITA 49 interface specification class for the NDR318.
#
class ndr318_ifSpec(ndr308_ifSpec):
    headerSizeWords = 9
    payloadSizeWords = 1024
    tailSizeWords = 1
    byteOrder = "little"
    iqSwapped = True


##
# \brief Radio handler class for the NDR318.
#
# This class implements the CyberRadioDriver.IRadio interface.
#
# \section ConnectionModes_NDR318 Connection Modes
#
# "tcp"
#
# \section RadioConfig_NDR318 Radio Configuration Options
#
# \code
# configDict = {
#      "configMode": [0, 1],
#      "referenceMode": [0, 1, 2, 3, 4],
#      "bypassMode": [0, 1],
#      "freqNormalization": [0, 1],
#      "gpsEnable": [0, 1],
#      "referenceTuningVoltage": [0-65535],
#      "tunerConfiguration": {
#            1: {
#               "frequency": [20000000.0-6000000000.0, step 1000000.0],
#               "attenuation": [0.0-30.0, step 1.0],
#               "enable": [0, 1],
#               "filter": [0, 1],
#               "timingAdjustment": [-200000 - 200000, step 1],
#            },
#         ...8 (repeat for each tuner)
#      },
#      "ddcConfiguration": {
#         "wideband": {
#              1: {
#                 "enable": [0, 1],
#                 "rateIndex": [0, 1, 2],
#                 "udpDest": [DIP table index],
#                 "vitaEnable": [0, 1, 2, 3],
#                 "streamId": [stream ID],
#                 "dataPort": [1, 2],
#              },
#           ...8 (repeat for each WBDDC)
#         },
#         "narrowband": {
#              1: {
#                 "enable": [0, 1],
#                 "frequency": [-25600000.0-25600000.0, step 1],
#                 "rateIndex": [0, 1, 2, 3, 4, 5, 6],
#                 "udpDest": [DIP table index],
#                 "vitaEnable": [0, 1, 2, 3],
#                 "streamId": [stream ID],
#                 "rfIndex": [1, 2, 3, 4, 5, 6, 7, 8],
#                 "dataPort": [1, 2],
#              },
#           ...32 (repeat for each NBDDC)
#         },
#      },
#      "ddcGroupConfiguration": {
#         "wideband": {
#              1: {
#                 "enable": [0, 1],
#                 "members": [None, single DDC, or iterable with multiple DDCs],
#              },
#           ...4 (repeat for each WBDDC group)
#         },
#         "narrowband": {
#              1: {
#                 "enable": [0, 1],
#                 "members": [None, single DDC, or iterable with multiple DDCs],
#              },
#           ...8 (repeat for each NBDDC group)
#         },
#      },
#      "ipConfiguration": {
#            1: {
#               "sourceIP": [IP address],
#               "destIP": {
#                   0: {
#                      "ipAddr": [IP address],
#                      "macAddr": [MAC address],
#                      "sourcePort": [port],
#                      "destPort": [port],
#                   },
#                ...31 (repeat for each DIP table entry)
#               },
#               "flowControl": [0, 1],
#            },
#         ...2 (repeat for each Gigabit Ethernet port)
#      },
# }
# \endcode
#
# \section WbddcRates_NDR318 WBDDC Rate Settings
#
# <table>
# <tr><th>Rate Index</th><th>WBDDC Rate (samples per second)</th></tr>
# <tr><td>0</td><td>51200000.0</td></tr>
# <tr><td>1</td><td>25600000.0</td></tr>
# <tr><td>2</td><td>12800000.0</td></tr>
# <tr><td>3</td><td>102400000.0 (real)</td></tr>
# <tr><td>4</td><td>6400000.0</td></tr>
# <tr><td>5</td><td>3200000.0</td></tr>
# </table>
#
# \section NbddcRates_NDR318 NBDDC Rate Settings
#
# <table>
# <tr><th>Rate Index</th><th>NBDDC Rate (samples per second)</th></tr>
# <tr><td>0</td><td>1600000.0</td></tr>
# <tr><td>1</td><td>800000.0</td></tr>
# <tr><td>2</td><td>400000.0</td></tr>
# <tr><td>3</td><td>200000.0</td></tr>
# <tr><td>4</td><td>100000.0</td></tr>
# <tr><td>5</td><td>50000.0</td></tr>
# <tr><td>6</td><td>25000.0</td></tr>
# <tr><td>7</td><td>12500.0</td></tr>
# </table>
#
# \section VitaEnable_NDR318 VITA 49 Enabling Options
#
# <table>
# <tr><th>VITA Enable Option</th><th>Meaning</th></tr>
# <tr><td>0</td><td>VITA-49 header disabled</td></tr>
# <tr><td>1</td><td>VITA-49 header enabled, fractional timestamp in picoseconds</td></tr>
# <tr><td>2</td><td>VITA-49 header disabled</td></tr>
# <tr><td>3</td><td>VITA-49 header enabled, fractional timestamp in sample counts</td></tr>
# </table>
#
# \implements CyberRadioDriver.IRadio
#
class ndr318(ndr308):
    _name = "NDR318"
    numTuner = 8
    numWbddc = 8
    numNbddc = 32
    ifSpec = ndr318_ifSpec
    tunerType = ndr318_tuner
    wbddcType = ndr318_wbddc
    nbddcType = ndr318_nbddc
    wbddcGroupType = ndr318_wbddc_group
    nbddcGroupType = ndr318_nbddc_group


##
# \internal
# \brief WBDDC component class for the NDR318A.
#
class ndr318a_wbddc(ndr318_wbddc):
    _name = "WBDDC(NDR318A)"
    rateSet = { 
            0: 61.44e6,
            1: 30.72e6,
            2: 15.36e6,
            3: 122.88e6,
            4: 7.68e6,
            5: 3.84e6,
        }
    bwSet = { 
            0: 0.8 * 61.44e6,
            1: 0.8 * 30.72e6,
            2: 0.8 * 15.36e6,
            3: 0.8 * 122.88e6,
            4: 0.8 * 7.68e6,
            5: 0.8 * 3.84e6,
        }


##
# \internal
# \brief NBDDC component class for the NDR318A.
#
class ndr318a_nbddc(ndr318_nbddc):
    _name = "NBDDC(NDR318A)"
    frqRange = (-30.72e6, 30.72e6)
    rateSet = { 
            0: 1.92e6,
            1: 960e3,
            2: 480e3,
            3: 240e3,
            4: 120e3,
            5: 60e3,
            6: 30e3,
            7: 15e3,
        }
    bwSet = { 
            0: 0.8 * 1.92e6,
            1: 0.8 * 960e3,
            2: 0.8 * 480e3,
            3: 0.8 * 240e3,
            4: 0.8 * 120e3,
            5: 0.8 * 60e3,
            6: 0.8 * 30e3,
            7: 0.8 * 15e3,
        }


##
# \brief Radio handler class for the NDR318A.
#
# This class implements the CyberRadioDriver.IRadio interface.
#
# \section ConnectionModes_NDR318A Connection Modes
#
# "tcp"
#
# \section RadioConfig_NDR318A Radio Configuration Options
#
# \code
# configDict = {
#      "configMode": [0, 1],
#      "referenceMode": [0, 1, 2, 3, 4],
#      "bypassMode": [0, 1],
#      "freqNormalization": [0, 1],
#      "gpsEnable": [0, 1],
#      "referenceTuningVoltage": [0-65535],
#      "tunerConfiguration": {
#            1: {
#               "frequency": [20000000.0-6000000000.0, step 1000000.0],
#               "attenuation": [0.0-30.0, step 1.0],
#               "enable": [0, 1],
#               "filter": [0, 1],
#               "timingAdjustment": [-200000 - 200000, step 1],
#            },
#         ...8 (repeat for each tuner)
#      },
#      "ddcConfiguration": {
#         "wideband": {
#              1: {
#                 "enable": [0, 1],
#                 "rateIndex": [0, 1, 2],
#                 "udpDest": [DIP table index],
#                 "vitaEnable": [0, 1, 2, 3],
#                 "streamId": [stream ID],
#                 "dataPort": [1, 2],
#              },
#           ...8 (repeat for each WBDDC)
#         },
#         "narrowband": {
#              1: {
#                 "enable": [0, 1],
#                 "frequency": [-30720000.0-30720000.0, step 1],
#                 "rateIndex": [0, 1, 2, 3, 4, 5, 6],
#                 "udpDest": [DIP table index],
#                 "vitaEnable": [0, 1, 2, 3],
#                 "streamId": [stream ID],
#                 "rfIndex": [1, 2, 3, 4, 5, 6, 7, 8],
#                 "dataPort": [1, 2],
#              },
#           ...32 (repeat for each NBDDC)
#         },
#      },
#      "ddcGroupConfiguration": {
#         "wideband": {
#              1: {
#                 "enable": [0, 1],
#                 "members": [None, single DDC, or iterable with multiple DDCs],
#              },
#           ...4 (repeat for each WBDDC group)
#         },
#         "narrowband": {
#              1: {
#                 "enable": [0, 1],
#                 "members": [None, single DDC, or iterable with multiple DDCs],
#              },
#           ...8 (repeat for each NBDDC group)
#         },
#      },
#      "ipConfiguration": {
#            1: {
#               "sourceIP": [IP address],
#               "destIP": {
#                   0: {
#                      "ipAddr": [IP address],
#                      "macAddr": [MAC address],
#                      "sourcePort": [port],
#                      "destPort": [port],
#                   },
#                ...31 (repeat for each DIP table entry)
#               },
#               "flowControl": [0, 1],
#            },
#         ...2 (repeat for each Gigabit Ethernet port)
#      },
# }
# \endcode
#
# \section WbddcRates_NDR318A WBDDC Rate Settings
#
# <table>
# <tr><th>Rate Index</th><th>WBDDC Rate (samples per second)</th></tr>
# <tr><td>0</td><td>61440000.0</td></tr>
# <tr><td>1</td><td>30720000.0</td></tr>
# <tr><td>2</td><td>15360000.0</td></tr>
# <tr><td>3</td><td>122880000.0 (real)</td></tr>
# <tr><td>4</td><td>7680000.0</td></tr>
# <tr><td>5</td><td>3840000.0</td></tr>
# </table>
#
# \section NbddcRates_NDR318A NBDDC Rate Settings
#
# <table>
# <tr><th>Rate Index</th><th>NBDDC Rate (samples per second)</th></tr>
# <tr><td>0</td><td>1920000.0</td></tr>
# <tr><td>1</td><td>960000.0</td></tr>
# <tr><td>2</td><td>480000.0</td></tr>
# <tr><td>3</td><td>240000.0</td></tr>
# <tr><td>4</td><td>120000.0</td></tr>
# <tr><td>5</td><td>60000.0</td></tr>
# <tr><td>6</td><td>30000.0</td></tr>
# <tr><td>7</td><td>15000.0</td></tr>
# </table>
#
# \section VitaEnable_NDR318A VITA 49 Enabling Options
#
# <table>
# <tr><th>VITA Enable Option</th><th>Meaning</th></tr>
# <tr><td>0</td><td>VITA-49 header disabled</td></tr>
# <tr><td>1</td><td>VITA-49 header enabled, fractional timestamp in picoseconds</td></tr>
# <tr><td>2</td><td>VITA-49 header disabled</td></tr>
# <tr><td>3</td><td>VITA-49 header enabled, fractional timestamp in sample counts</td></tr>
# </table>
#
# \implements CyberRadioDriver.IRadio
#
class ndr318a(ndr318):
    _name = "NDR318A"
    adcRate = 122.88e6
    wbddcType = ndr318a_wbddc
    nbddcType = ndr318a_nbddc

class ndr818(ndr318):
    _name = "NDR818"


if __name__ == '__main__':
    pass
