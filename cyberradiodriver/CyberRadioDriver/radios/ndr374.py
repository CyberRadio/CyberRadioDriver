#!/usr/bin/env python
##################################################################
# \package CyberRadioDriver.radios.ndr374 
# \brief NDR374 Support
# \author BS
# \copyright Copyright (c) 2014-2021 CyberRadio Solutions, Inc.  
#     All rights reserved.
##################################################################

# Imports from other modules in this package
from CyberRadioDriver.radios.ndr551 import ndr551, \
                                           ndr551_tuner, \
                                           ndr551_wbddc, \
                                           ndr551_nbddc, \
                                           ndr551_ddc_group, \
                                           ndr551_ddc_ifSpec, \
                                           ndr551_adc_ifSpec, \
                                           ndr551_demod_ifSpec
from CyberRadioDriver.command import _jsonCommandBase, jsonConfig
from CyberRadioDriver import configKeys
from CyberRadioDriver.radio import _ifSpec, _radio, funJSON

# Imports from external modules
# Python standard library imports

##
# \brief Tuner component class for the NDR374.
#
class ndr374_tuner(ndr551_tuner):
    _name = "Tuner(NDR374)"
    frqRange = (20e6,8e9)

##
# \brief WBDDC component class for the NDR374.
class ndr374_wbddc(ndr551_wbddc):
    _name = "WBDDC(NDR374)"
    frqRange = (-62.5e6,62.5e6)
    rateSet = {
        0   :1.2288e6,
        1   :1.92e6,
        2   :3.84e6,
        3   :7.68e6,
        4   :8e6,
        5   :9.2e6,
        6   :15.36e6,
        7   :23.04e6,
        8   :18.4e6,
        9   :20e6,
        10  :30.72e6,
        11  :22e6,
        12  :46.08e6,
        13  :36.8e6,
        14  :61.44e6,
        15  :73.6e6,
        16  :92.16e6,
        17  :100e6,
        18  :122.88e6,
        19  :147.2e6,

    }
    bwSet = {
        0   :1.25e6,
        1   :1.4e6,
        2   :2.8e6,
        3   :5e6,
        4   :6.64e6,
        5   :7.8125e6,
        6   :10e6,
        7   :15e6,
        8   :15.625e6,
        9   :16.6e6,
        10  :20e6,
        11  :22e6,
        12  :30e6,
        13  :31.25e6,
        14  :40e6,
        15  :62.5e6,
        16  :73.728e6,
        17  :80e6,
        18  :98.304e6,
        19  :125e6,

    }
    sampleSizeSet = {
       0   : 1152,
       1   : 1152,
       2   : 1152,
       3   : 1152,
       4   : 1000,
       5   : 1000,
       6   : 1152,
       7   : 1152,
       8   : 1000,
       9   : 1000,
       10  : 1152,
       11  : 1100,
       12  : 1152,
       13  : 1000,
       14  : 1152,
       15  : 1000,
       16  : 1152,
       17  : 1250,
       18  : 1152,
       19  : 1000,
    }

    def getRateAndBwSet(self, ):
        ret = {}
        for i in range(0,20):
            ret[i] = (ndr374_wbddc.rateSet.get(i),ndr374_wbddc.bwSet.get(i),ndr374_wbddc.sampleSizeSet.get(i))
        return ret

    def getRateAndBw(self, index):
        return {"rate": ndr374_wbddc.rateSet.get(index),
                "bw": ndr374_wbddc.bwSet.get(index),
                "samples": ndr374_wbddc.sampleSizeSet.get(index)}



##
# \brief NBDDC component class for the NDR374.
class ndr374_nbddc(ndr551_nbddc):
    _name = "NBDDC(NDR374)"
    frqRange = (-62.5e6, 62.5e6)
    rateSet = {
        0   :16e3,
        1   :32e3,
        2   :64e3,
        3   :128e3,
        4   :200e3,
        5   :250e3,
        6   :320e3,
        7   :400e3,
        8   :1000e3,
        9   :1600e3,
        10  :2000e3,
        11  :3200e3,
        12  :4000e3,
    }

    bwSet = {
        0   :12.8e3,
        1   :25.6e3,
        2   :51.2e3,
        3   :102.4e3,
        4   :160e3,
        5   :200e3,
        6   :256e3,
        7   :320e3,
        8   :800e3,
        9   :1280e3,
        10  :1600e3,
        11  :2560e3,
        12  :3200e3,
    }
    sampleSizeSet = {
       0   : 100,
       1   : 100,
       2   : 100,
       3   : 1000,
       4   : 1000,
       5   : 1000,
       6   : 1000,
       7   : 1000,
       8   : 1000,
       9   : 1000,
       10  : 1000,
       11  : 1000,
       12  : 1000,
    }

##
# \brief NBDDC component class for the NDR374.
class ndr374_ddc_group(ndr551_ddc_group):
    _name = "DDCGroup(NDR374)"

##
# \internal
# \brief VITA 49 interface specification class for the NDR374's DDC format.
# \note Some explanation for these values is probably in order.
# * The "header" includes not only the 7 words of the standard VITA
#   packet header, but also the 5 words of the metadata included in
#   each DDC payload.
# * The "tail" includes not only the standard VITA packet trailer, 
#   but also the trailer word within the DDC payload.
# * The definition of "payload" deviates from the ICD here, as we
#   want the "payload" to be only the part of the packet that 
#   contains data samples.  
# ** For DDC format, each 32-bit word contains one 16-bit I/16-bit Q 
#    sample, so the number of samples is getVitaPayloadSize("ddc") / 4.
class ndr374_ddc_ifSpec(_ifSpec):
    vita49_1 = False
    vita49_0 = True
    headerSizeWords = 5
    payloadSizeWords = 1024
    tailSizeWords = 1
    byteOrder = "big"
    pass

##
# \brief Radio handler class for the NDR374.
#
# This class implements the CyberRadioDriver.IRadio interface.
#
# \section ConnectionModes_NDR374 Connection Modes
#
# "udp"
#
# \section RadioConfig_NDR374 Radio Configuration Options
#
# \code
# configDict = {
#      "referenceMode": [0, 1],
#      "function": [integer (meaning is radio-dependent],
#      "tunerConfiguration": {
#            0: {
#               "preselectorBypass": [True, False], 
#               "frequency": [20000000.0-6000000000.0, step 1000000.0],
#               "attenuation": [0.0-40.0, step 1.0],
#               "enable": [True, False],
#               "ifFilter": [3, 10, 40, 80],
#               "delay": [0.0-1.0, step 8e-6],
#               "fnr": [True, False],
#               "gainMode": ["auto", "manual", "freeze"],
#               "asp": [-40.0-0.0, step 1.0],
#               "aul": [-40.0-0.0, step 1.0],
#               "all": [-40.0-0.0, step 1.0],
#               "aat": [1.0-128.0, step 1.0],
#               "adt": [1.0-128.0, step 1.0],
#               "aas": [0.0-40.0, step 1.0],
#               "ads": [0.0-40.0, step 1.0],
#               "aal": [1.0-30.0, step 1.0],
#               "adl": [1.0-30.0, step 1.0],
#            },
#         ...7 (repeat for each tuner)
#      },
#      "ddcConfiguration": {
#         "wideband": {
#              0: {
#                 "enable": [True, False],
#                 "rfIndex": ["0", "1", "2", "3"],
#                 "outputType": ["iq", "raw"],
#                 "frequency": [-40e6-40e6, step 1e3],
#                 "decimation": [1, 2, 4, 8, 16],
#                 "filterIndex": [32-63, step 1],
#                 "oversampling": [1, 2, 4],
#                 "startTime": [start time],
#                 "samples": [samples],
#                 "udpDest": [UDP destination table index],
#                 "groupId": [0-15, step 1],
#                 "streamId": [stream ID],
#                 "link": [0, 1, 2, 3],
#                 "gainMode": ["auto", "manual", "freeze"],
#                 "dgv": [0.0-96.0, step 1.0],
#                 "dul": [0.0-96.0, step 1.0],
#                 "dll": [0.0-96.0, step 1.0],
#                 "dtl": [-96.0-0.0, step 0.5],
#                 "dal": [0.0-30.0, step 0.5],
#                 "ddl": [0.0-30.0, step 0.5],
#                 "dao": [0.0-24.0, step 0.5],
#                 "ddo": [0.0-24.0, step 0.5],
#                 "datc": [10-3000, step 10],
#                 "ddtc": [10-3000, step 10],
#                 "dat": [1-100, step 1],
#                 "ddt": [1-100, step 1],
#              },
#           ...7 (repeat for each WBDDC)
#         },
#         "narrowband": {
#              0: {
#                 "enable": [True, False],
#                 "frequency": [-40e6-40e6, step 1e3],
#                 "rfIndex": ["0", "1", "2", "3"],
#                 "filterIndex": [0-31 step 1, 64-4095 step 1],
#                 "cic0": [4-500, step 1],
#                 "cic1": [1, 4-500, step 1],
#                 "oversampling": [1, 2, 4, 8, 16],
#                 "demod": ["none", "cw", "fm", "am", "usb", "lsb"],
#                 "demodGain": [gain],
#                 "audioDecimation": [True, False],
#                 "bfo": [-12e3-12e3, step 1],
#                 "startTime": [ISO 8601 time string],
#                 "samples": [number of samples],
#                 "udpDest": [UDP destination table index],
#                 "groupId": [0-15, step 1],
#                 "streamId": [stream ID],
#                 "gainMode": ["auto", "manual", "freeze"],
#                 "dgv": [0.0-96.0, step 1.0],
#                 "dul": [0.0-96.0, step 1.0],
#                 "dll": [0.0-96.0, step 1.0],
#                 "dtl": [-96.0-0.0, step 0.5],
#                 "dal": [0.0-30.0, step 0.5],
#                 "ddl": [0.0-30.0, step 0.5],
#                 "dao": [0.0-24.0, step 0.5],
#                 "ddo": [0.0-24.0, step 0.5],
#                 "datc": [10-3000, step 10],
#                 "ddtc": [10-3000, step 10],
#                 "dat": [1-100, step 1],
#                 "ddt": [1-100, step 1],
#              },
#           ...63 (repeat for each NBDDC)
#         },
#      },
#      "ipConfiguration": {
#            0: {
#               "destIP": {
#                   0: {
#                      "ipAddr": [IP address],
#                      "macAddr": [MAC address],
#                      "destPort": [port],
#                      "arp": [True, False],
#                   },
#                ...63 (repeat for each UDP destination index)
#               },
#               "sourceIP": {
#                   "ipAddr": [IP address],
#                   "macAddr": [MAC address],
#                   "netmask": [netmask],
#                   "sourcePort": [port],
#               },
#            },
#         ...3 (repeat for each 10-Gigabit Ethernet port)
#      },
# }
# \endcode
#
# \section VITA_Notes_NDR374 VITA 49 Notes
#
# When dealing with VITA 49 payloads, we have historically relied on the 
# following convention:
# * getVitaHeaderSize() provides how many bytes contain metadata information 
#   at the beginning of the packet
# * getVitaPayloadSize() provides how many bytes contain data samples
# * getVitaTailSize() provides how many bytes contain metadata information 
#   at the end of the packet
#
# For NDR551-class radios, this convention requires us to deviate, not only
# from the VITA 49 standard, but also from the NDR551 ICD itself.
# * The getVitaHeaderSize(), getVitaPayloadSize(), and getVitaTailSize() 
#   methods use the payloadType argument to differentiate between the 
#   three supported payload formats.
#   * DDC format: "ddc"
#   * ADC format: "adc"
#   * Demod format: "demod"
# * The "header" includes not only the 7 words of the standard VITA
#   packet header, but also the 5 words of the metadata included in
#   each payload.
# * The "tail" includes not only the standard VITA packet trailer, 
#   but also the trailer word within the payload.
# * The definition of "payload" deviates from the ICD here, as we
#   want the "payload" to be only the part of the packet that 
#   contains data samples.  
# ** For ADC format, each 32-bit word contains two 16-bit ADC samples,
#    so the number of samples is getVitaPayloadSize("adc") / 2.
# ** For DDC format, each 32-bit word contains one 16-bit I/16-bit Q 
#    sample, so the number of samples is getVitaPayloadSize("ddc") / 4.
# ** For demod format, each 32-bit word contains two 16-bit demod samples,
#    so the number of samples is getVitaPayloadSize("demod") / 2.
#
# \implements CyberRadioDriver.IRadio    
class ndr374(ndr551):
    _name = "NDR374"
    ifSpec = ndr374_ddc_ifSpec
    ifSpecMap = {
            "ddc":   ndr374_ddc_ifSpec
        }
    tunerType = ndr374_tuner
    numTuner = 4
    wbddcType = ndr374_wbddc
    numWbddc = 4
    nbddcType = ndr374_nbddc
    numNbddc = 32
    numGigE = 2
    cddcGroupType = None


    # def getWbddcRateSet(self, index=None):
    #     ret = {}
    #     try:
    #         firstIndex = self.getWbddcIndexRange()[0]
    #         ret = self.wbddcDict[firstIndex if index is None else index].getRateAndBwSet()
    #     except:
    #         pass
    #     return ret
