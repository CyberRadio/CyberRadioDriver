#!/usr/bin/env python
###############################################################
# \package CyberRadioDriver.components
# 
# \brief Provides classes that define basic functionality for 
#     hardware components (tuners, wideband DDCs, narrowband 
#     DDCs, etc.).
#
# \note This module defines basic behavior only.  To customize
#     a component class for a particular radio, derive a new
#     class from the appropriate base class.  It is recommended
#     that behavior specific to a given radio be placed in the
#     module that supports that radio.
#
# \author NH
# \author DA
# \author MN
# \copyright Copyright (c) 2014-2021 CyberRadio Solutions, Inc.  
#    All rights reserved.
#
###############################################################

# Imports from other modules in this package
from . import command
from . import configKeys
from . import log
# Imports from external modules
import numpy
# Python standard library imports
# import time
# import traceback

##
# \internal
# Helper method that adjusts an input frequency to a given
# range, resolution, and unit specifier.
def adjustFrequency(frqIn, frange, res, units):
    frqOut = frange[0] if frqIn<frange[0] else frqIn
    frqOut = frange[1] if frqIn>frange[1] else frqOut
    frqOut = numpy.around( frqOut, int(numpy.log10(1.0/res)), )
    frqOut /= units
    return frqOut

##
# \internal
# Helper method that adjusts an input attenuation to a given
# range, resolution, and unit specifier.
def adjustAttenuation(attIn, attRange, attRes, attUnits=1):
    attOut = max(attIn, attRange[0])
    attOut = min(attOut, attRange[1])
    attOut = numpy.around( attOut, int(numpy.log10(1.0/attRes)), )
    attOut /= attUnits
    return attOut

class DDC_DATA_FORMAT():
    IQ = "iq"
    REAL = "real"
    FFT = "fft"

#----------------------------------------------------------------------------#
#--  Base Radio Component Object  -------------------------------------------# 

##
# Base hardware component class.
#
# A radio handler object maintains a series of component objects, one
# per component of each type (tuner, WBDDC, NBDDC, etc.).  Each component 
# object is responsible for managing the hardware object that it represents.
# Each component object is also responsible for querying the component's 
# current configuration and for maintaining the object's configuration
# as it changes during radio operation.
#
class _base(log._logger, configKeys.Configurable):
    _name = "_baseObject"
    ## Communication transport
    transport = None
    ## Callback function that executes commands on the transport
    callback = None
    ## Index
    index = None
    ##
    # Constructs a hardware component object.
    #
    # The constructor uses keyword arguments to configure the class.  It 
    # consumes the following keyword arguments:
    # <ul>
    # <li> "verbose": Verbose mode (Boolean)
    # <li> "logFile": An open file or file-like object to be used for log output.  
    #    If not provided, this defaults to standard output. 
    # <li> "parent": The radio handler object that manages this component object. 
    # <li> "callback": A method that the component uses to send data over a
    #   connected transport.
    # <li> "index": The index number for this component. 
    # </ul>
    #
    # \param args Variable-length list of positional arguments.  Positional
    #     arguments are ignored.
    # \param kwargs Dictionary of keyword arguments for the component
    #     object.  Which keyword arguments are valid depends on the 
    #     specific component.  Unsupported keyword arguments will be ignored.
    def __init__(self, *args, **kwargs):
        # Set up configuration capabilities
        configKeys.Configurable.__init__(self)
        # Consume keyword arguments "verbose" and "logFile" for logging support
        log._logger.__init__(self, *args, **kwargs)
        # Consume our own keyword arguments
        self.parent = kwargs.get("parent",None)
        self.callback = kwargs.get("callback",None)
        self.index = int( kwargs.get(configKeys.INDEX) )
        self.logIfVerbose("Hello!")
        
    ##
    # Adds a communication transport to this component.
    #
    # The component will query the hardware for its configuration after the
    # transport is added.
    #
    # \param transport The communication transport (an object of type 
    #    CyberRadioDriver.transport.radio_transport). 
    # \param callback A method that the component uses to send data over the
    #   connected transport.
    # \param queryConfig Whether or not to query the configuration
    #   through hardware commands
    def addTransport(self,transport,callback,queryConfig=True):
        self.transport = transport
        self.callback = callback
        if queryConfig:
            self.queryConfiguration()
        
    ##
    # Deletes the communication transport from this component.
    #
    def delTransport(self):
        self.transport = None
        self.callback = None
    
    ##
    # \internal
    # Perform actions on object being deleted.
    def __del__(self,):
        self.logIfVerbose("Goodbye!")
            
    ##
    # \internal
    # Define this object's string representation.
    def __str__(self,):
        return "%s.%s.%d" % (str(self.parent), self._name, self.index)
    
    ##
    # Disables this component.
    #
    def disable(self):
        return self._setConfiguration({configKeys.ENABLE: 0})
    
    ##
    # Enables this component.
    #
    def enable(self):
        return self._setConfiguration({configKeys.ENABLE: 1})
    
    

#----------------------------------------------------------------------------#
#--  Tuner Objects  ---------------------------------------------------------#

##
# Base tuner component class.
#
# A radio handler object maintains one tuner component object per tuner
# on the radio.  
#
class _tuner(_base):
    _name = "Tuner"
    ## Tunable frequency range.  This is a 2-tuple: (minimum, maximum).
    frqRange = (20e6,3e9)
    ## Frequency resolution.
    frqRes = 1e6
    ## Frequency units.
    frqUnits = 1e6
    ## Tunable attenuation range.  This is a 2-tuple: (minimum, maximum).
    attRange = (0.0,30.0)
    ## Attenuation resolution.
    attRes = 1.0
    ## ifFilters
    ifFilters = [0, 1]
    ## Automatic gain control (AGC) supported.
    agc = False
    # Supported commands
    ## Frequency set/query command.
    frqCmd = command.frq
    ## Attenuation set/query command.
    attCmd = command.att
    ## AGP set/query command.
    agpCmd = None    
    ## Tuner power set/query command.
    tpwrCmd = command.tpwr
    ## Tuner filter set/query command.
    fifCmd = None
    ## Timing adjustment set/query command.
    tadjCmd = None
    # OVERRIDE
    ##
    # The list of valid configuration keywords supported by this
    # object.  Override in derived classes as needed.
    validConfigurationKeywords = [
                                  configKeys.TUNER_FREQUENCY, 
                                  configKeys.TUNER_ATTENUATION, 
                                  configKeys.TUNER_RF_ATTENUATION,
                                  configKeys.ENABLE, 
                                  ]
    
    ##
    # Constructs a tuner component object.
    #
    # The constructor uses keyword arguments to configure the class.  It 
    # consumes the following keyword arguments:
    # <ul>
    # <li> "verbose": Verbose mode (Boolean)
    # <li> "logFile": An open file or file-like object to be used for log output.  
    #    If not provided, this defaults to standard output. 
    # <li> "parent": The radio handler object that manages this component object. 
    # <li> "callback": A method that the component uses to send data over a
    #   connected transport.
    # <li> "index": The index number for this component. 
    # </ul>
    #
    # \param args Variable-length list of positional arguments.  Positional
    #     arguments are ignored.
    # \param kwargs Dictionary of keyword arguments for the component
    #     object.  Which keyword arguments are valid depends on the 
    #     specific component.  Unsupported keyword arguments will be ignored.
    def __init__(self,*args,**kwargs):
        _base.__init__(self,*args,**kwargs)
        
    # OVERRIDE
    ##
    # \protected
    # Queries hardware to determine the object's current configuration.  
    def _queryConfiguration(self):
        # Call the base-class implementation
        configKeys.Configurable._queryConfiguration(self)
        # Override
        if self.tpwrCmd is not None:
            cmd = self.tpwrCmd(**{ "parent": self, 
                                   configKeys.INDEX: self.index,
                                   "query": True,
                                    "verbose": self.verbose, 
                                    "logFile": self.logFile })
            cmd.send( self.callback, )
            self._addLastCommandErrorInfo(cmd)
            rspInfo = cmd.getResponseInfo()
            if rspInfo is not None:
                self.configuration[configKeys.ENABLE] = rspInfo.get(configKeys.ENABLE, 0)
        if self.frqCmd is not None:
            cmd = self.frqCmd(**{ "parent": self, 
                                   configKeys.INDEX: self.index,
                                   "query": True,
                                    "verbose": self.verbose, 
                                    "logFile": self.logFile })
            cmd.send( self.callback, )
            self._addLastCommandErrorInfo(cmd)
            rspInfo = cmd.getResponseInfo()
            if rspInfo is not None:
                freq = rspInfo.get(configKeys.TUNER_FREQUENCY, None)
                self.configuration[configKeys.TUNER_FREQUENCY] = None if freq is None else \
                                                  freq * self.frqUnits
        if self.attCmd is not None:
            cmd = self.attCmd(**{ "parent": self, 
                                   configKeys.INDEX: self.index,
                                   "query": True,
                                    "verbose": self.verbose, 
                                    "logFile": self.logFile })
            cmd.send( self.callback, )
            self._addLastCommandErrorInfo(cmd)
            rspInfo = cmd.getResponseInfo()
            if rspInfo is not None:
                self.configuration[configKeys.TUNER_ATTENUATION] = rspInfo.get(configKeys.TUNER_ATTENUATION, None)
                self.configuration[configKeys.TUNER_RF_ATTENUATION] = rspInfo.get(configKeys.TUNER_ATTENUATION, None)
        if self.agpCmd is not None:
            cmd = self.agpCmd(**{ "parent": self, 
                                   configKeys.INDEX: self.index,
                                   "query": True,
                                    "verbose": self.verbose, 
                                    "logFile": self.logFile })
            cmd.send( self.callback, )
            self._addLastCommandErrorInfo(cmd)
            rspInfo = cmd.getResponseInfo()
            if rspInfo is not None:
                self.configuration[configKeys.TUNER_AGP] = rspInfo.get(configKeys.TUNER_AGP, None)
        if self.fifCmd is not None:
            cmd = self.fifCmd(**{ "parent": self, 
                                   configKeys.INDEX: self.index,
                                   "query": True,
                                    "verbose": self.verbose, 
                                    "logFile": self.logFile })
            cmd.send( self.callback, )
            self._addLastCommandErrorInfo(cmd)
            rspInfo = cmd.getResponseInfo()
            if rspInfo is not None:
                self.configuration[configKeys.TUNER_FILTER] = rspInfo.get(configKeys.TUNER_FILTER, None)
        if self.tadjCmd is not None:
            cmd = self.tadjCmd(**{ "parent": self, 
                                   configKeys.INDEX: self.index,
                                   "query": True,
                                    "verbose": self.verbose, 
                                    "logFile": self.logFile })
            cmd.send( self.callback, )
            self._addLastCommandErrorInfo(cmd)
            rspInfo = cmd.getResponseInfo()
            if rspInfo is not None:
                self.configuration[configKeys.TUNER_TIMING_ADJ] = rspInfo.get(configKeys.TUNER_TIMING_ADJ, None)
        pass

    # OVERRIDE
    ##
    # \protected
    # Issues hardware commands to set the object's current configuration.  
    def _setConfiguration(self, confDict):
        ret = True
        if configKeys.ENABLE in confDict:
            if self.tpwrCmd is not None:
                cmd = self.tpwrCmd(**{ "parent": self, 
                                       configKeys.INDEX: self.index,
                                       configKeys.ENABLE: confDict.get(configKeys.ENABLE, 0),
                                        "verbose": self.verbose, 
                                        "logFile": self.logFile })
                ret &= cmd.send( self.callback, )
                ret &= cmd.success
                self._addLastCommandErrorInfo(cmd)
                if ret:
                    self.configuration[configKeys.ENABLE] = getattr(cmd, configKeys.ENABLE)
                pass
        if configKeys.TUNER_FREQUENCY in confDict:
            if self.frqCmd is not None:
                freqIn = float(confDict.get(configKeys.TUNER_FREQUENCY, 0)) 
                freqAdj = adjustFrequency(freqIn, self.frqRange, 
                                          self.frqRes, self.frqUnits)
                cmd = self.frqCmd(**{ "parent": self, 
                                       configKeys.INDEX: self.index,
                                       configKeys.TUNER_FREQUENCY: freqAdj,
                                        "verbose": self.verbose, 
                                        "logFile": self.logFile })
                ret &= cmd.send( self.callback, )
                ret &= cmd.success
                self._addLastCommandErrorInfo(cmd)
                if ret:
                    self.configuration[configKeys.TUNER_FREQUENCY] = freqAdj * self.frqUnits
                pass
        if configKeys.TUNER_ATTENUATION in confDict or configKeys.TUNER_RF_ATTENUATION in confDict:
            if self.attCmd is not None:
                rfAttIn = float(confDict.get(configKeys.TUNER_RF_ATTENUATION, 
                                confDict.get(configKeys.TUNER_ATTENUATION, 0))) 
                rfAttAdj = adjustAttenuation(rfAttIn, self.attRange, 
                                            self.attRes, 1)
                cmd = self.attCmd(**{ "parent": self, 
                                       configKeys.INDEX: self.index,
                                       configKeys.TUNER_ATTENUATION: rfAttAdj,
                                        "verbose": self.verbose, 
                                        "logFile": self.logFile })
                ret &= cmd.send( self.callback, )
                ret &= cmd.success
                self._addLastCommandErrorInfo(cmd)
                if ret:
                    self.configuration[configKeys.TUNER_ATTENUATION] = rfAttAdj
                    self.configuration[configKeys.TUNER_RF_ATTENUATION] = rfAttAdj
                pass
        if configKeys.TUNER_AGP in confDict:
            if self.agpCmd is not None:
                cmd = self.agpCmd(**{ "parent": self, 
                                       configKeys.INDEX: self.index,
                                       configKeys.TUNER_AGP: confDict.get(configKeys.TUNER_AGP, 0),
                                        "verbose": self.verbose, 
                                        "logFile": self.logFile })
                ret &= cmd.send( self.callback, )
                ret &= cmd.success
                self._addLastCommandErrorInfo(cmd)
                if ret:
                    self.configuration[configKeys.TUNER_AGP] = getattr(cmd, configKeys.TUNER_AGP)
                pass                
        if configKeys.TUNER_FILTER in confDict:
            if self.fifCmd is not None:
                cmd = self.fifCmd(**{ "parent": self, 
                                       configKeys.INDEX: self.index,
                                       configKeys.TUNER_FILTER: confDict.get(configKeys.TUNER_FILTER, 0),
                                        "verbose": self.verbose, 
                                        "logFile": self.logFile })
                ret &= cmd.send( self.callback, )
                ret &= cmd.success
                self._addLastCommandErrorInfo(cmd)
                if ret:
                    self.configuration[configKeys.TUNER_FILTER] = getattr(cmd, configKeys.TUNER_FILTER)
                pass
        if configKeys.TUNER_TIMING_ADJ in confDict:
            if self.tadjCmd is not None:
                cmd = self.tadjCmd(**{ "parent": self, 
                                       configKeys.INDEX: self.index,
                                       configKeys.TUNER_TIMING_ADJ: confDict.get(configKeys.TUNER_TIMING_ADJ, 0),
                                        "verbose": self.verbose, 
                                        "logFile": self.logFile })
                ret &= cmd.send( self.callback, )
                ret &= cmd.success
                self._addLastCommandErrorInfo(cmd)
                if ret:
                    self.configuration[configKeys.TUNER_TIMING_ADJ] = getattr(cmd, configKeys.TUNER_TIMING_ADJ)
                pass
        return ret


#----------------------------------------------------------------------------#
#--  DDC Objects  -----------------------------------------------------------#

##
# Base DDC component class.
#
# A radio handler object maintains one DDC component object per DDC
# on the radio.  
#
class _ddc(_base):
    _name = "DDC"
    ## Whether this is a wideband DDC.
    wideband = True
    ## Whether this DDC is tunable.
    tunable = False
    ## Whether this DDC can be set to a specific source tuner.
    selectableSource = False
    ## Whether this DDC supports automatic gain control (AGC).
    agc = False
    ## Tunable frequency offset range.  This is a 2-tuple: (minimum, maximum).
    frqRange = (-0.0,0.0)
    ## Tunable frequency offset resolution.
    frqRes = 1.0
    ## Tunable frequency offset units.
    frqUnits = 1.0
    ## DDC rate set.  This is a dictionary whose keys are rate index numbers and 
    # whose values are DDC rates. 
    rateSet = {}
    bwSet = {}
    dataFormat = {}
    ## DDC configuration query/set command.
    cfgCmd = None
    ## DDC tuning query/set command.    ## Whether this DDC is tunable.
    tunable = False
    ## Whether this DDC can be set to a specific source tuner.
    selectableSource = False
    ## Whether this DDC supports automatic gain control (AGC).
    agc = False
    ## Tunable frequency offset range.  This is a 2-tuple: (minimum, maximum).
    frqRange = (-0.0,0.0)
    ## Tunable frequency offset resolution.
    frqRes = 1.0
    ## Tunable frequency offset units.
    frqUnits = 1.0
    ## DDC rate set.  This is a dictionary whose keys are rate index numbers and 
    # whose values are DDC rates. 
    rateSet = {}

    frqCmd = None
    ## DDC source select query/set command.
    nbssCmd = None
    ## DDC data port (10GigE interface) query/set command.
    dportCmd = None
    ## DDC demod query/set command.
    demodCmd = None
    otherCmdList = []
    # OVERRIDE
    ##
    # The list of valid configuration keywords supported by this
    # object.  Override in derived classes as needed.
    validConfigurationKeywords = [
                                  configKeys.ENABLE, 
                                  configKeys.DDC_RATE_INDEX, 
                                  configKeys.DDC_UDP_DESTINATION, 
                                  configKeys.DDC_VITA_ENABLE, 
                                  configKeys.DDC_STREAM_ID, 
                                  ]
    
    ##
    # Constructs a DDC component object.
    #
    # The constructor uses keyword arguments to configure the class.  It 
    # consumes the following keyword arguments:
    # <ul>
    # <li> "verbose": Verbose mode (Boolean)
    # <li> "logFile": An open file or file-like object to be used for log output.  
    #    If not provided, this defaults to standard output. 
    # <li> "parent": The radio handler object that manages this component object. 
    # <li> "callback": A method that the component uses to send data over a
    #   connected transport.
    # <li> "index": The index number for this component. 
    # </ul>
    #
    # \param args Variable-length list of positional arguments.  Positional
    #     arguments are ignored.
    # \param kwargs Dictionary of keyword arguments for the component
    #     object.  Which keyword arguments are valid depends on the 
    #     specific component.  Unsupported keyword arguments will be ignored.
    def __init__(self,*args,**kwargs):
        _base.__init__(self,*args,**kwargs)
    
    # EXTENSION
    ##
    # Gets the list of available DDC rates.
    #
    # \param index If not None, get the list for the DDC with the given index. 
    # \return A list of DDC rates.
    @classmethod
    def getDdcRates(cls,index=None):
        rateKeys = list(cls.getDdcRateSet(index).keys())
        rateKeys.sort()
        return [cls.rateSet[k] for k in rateKeys]
    
    # EXTENSION
    ##
    # Gets the list of available DDC rates.
    #
    # \param index If not None, get the list for the DDC with the given index. 
    # \return A list of DDC rates.
    @classmethod
    def getDdcRateList(cls,index=None):
        rateDict = cls.getDdcRateSet(index)
        rateKeys = list(rateDict.keys())
        rateKeys.sort()
        return [rateDict[k] for k in rateKeys]
    
    # EXTENSION
    ##
    # Gets the set of available DDC rates.
    #
    # \param index If not None, get the set for the DDC with the given index. 
    # \return A set of DDC rates.  This is a dictionary where the keys are 
    #    rate indices and the values are the corresponding DDC rates.
    @classmethod
    def getDdcRateSet(cls, index=None):
        return cls.rateSet
    
    # EXTENSION
    ##
    # Gets the set of available DDC data formats.
    #
    # \return A dictionary where the keys are rate indices and the values are 
    #    the corresponding DDC data formats ("iq" or "real").
    @classmethod
    def getDdcDataFormat(cls,):
        return dict( (i,cls.dataFormat.get(i,DDC_DATA_FORMAT.IQ)) for i in list(cls.getDdcRateSet().keys()) )
    
    # EXTENSION
    ##
    # Gets the list of available DDC bandwidths.
    #
    # \param index If not None, get the list for the DDC with the given index. 
    # \return A list of DDC bandwidths.
    @classmethod
    def getDdcBwList(cls,index=None):
        bwDict = cls.getDdcBwSet(index)
        rateKeys = list(bwDict.keys())
        rateKeys.sort()
        return [bwDict[k] for k in rateKeys]
    
    # EXTENSION
    ##
    # Gets the set of available DDC bandwidths.
    #
    # \param index If not None, get the set for the DDC with the given index. 
    # \return A set of DDC rates.  This is a dictionary where the keys are 
    #    rate indices and the values are the corresponding DDC bandwidths.
    @classmethod
    def getDdcBwSet(cls,index=None):
        return cls.bwSet
    
    # OVERRIDE
    ##
    # \protected
    # Queries hardware to determine the object's current configuration.  
    def _queryConfiguration(self):
        # Call the base-class implementation
        configKeys.Configurable._queryConfiguration(self)
        # Override
        if self.frqCmd is not None:
            cmd = self.frqCmd(**{ "parent": self, 
                                   configKeys.INDEX: self.index,
                                   "query": True,
                                    "verbose": self.verbose, 
                                    "logFile": self.logFile })
            cmd.send( self.callback, )
            self._addLastCommandErrorInfo(cmd)
            rspInfo = cmd.getResponseInfo()
            if rspInfo is not None:
                freq = rspInfo.get(configKeys.DDC_FREQUENCY_OFFSET, None)
                self.configuration[configKeys.DDC_FREQUENCY_OFFSET] = None if freq is None else \
                                                                      freq * self.frqUnits
        if self.cfgCmd is not None:
            cmd = self.cfgCmd(**{ "parent": self, 
                                   configKeys.INDEX: self.index,
                                   "query": True,
                                    "verbose": self.verbose, 
                                    "logFile": self.logFile })
            cmd.send( self.callback, )
            self._addLastCommandErrorInfo(cmd)
            rspInfo = cmd.getResponseInfo()
            #self.logIfVerbose("rspInfo =", rspInfo)
            if rspInfo is not None:
                for key in [configKeys.DDC_RATE_INDEX, 
                            configKeys.DDC_UDP_DESTINATION,
                            configKeys.ENABLE,
                            configKeys.DDC_VITA_ENABLE,
                            configKeys.DDC_STREAM_ID]:
                    self.configuration[key] = rspInfo.get(key, None)
        if self.dportCmd is not None:
            cmd = self.dportCmd(**{ "parent": self, 
                                   configKeys.INDEX: self.index,
                                   "query": True,
                                    "verbose": self.verbose, 
                                    "logFile": self.logFile })
            cmd.send( self.callback, )
            self._addLastCommandErrorInfo(cmd)
            rspInfo = cmd.getResponseInfo()
            #self.logIfVerbose("rspInfo =", rspInfo)
            if rspInfo is not None:
                for key in [configKeys.DDC_DATA_PORT, 
                            ]:
                    self.configuration[key] = rspInfo.get(key, None)
        pass

    # OVERRIDE
    ##
    # \protected
    # Issues hardware commands to set the object's current configuration.  
    def _setConfiguration(self, confDict):
        ret = True
        if self.dportCmd is not None and \
           configKeys.DDC_DATA_PORT in confDict:
            cDict = {}
            self._dictUpdate(cDict, confDict, self.configuration, 
                             [configKeys.DDC_DATA_PORT])
            cDict.update({ "parent": self, 
                            configKeys.INDEX: self.index,
                             "verbose": self.verbose, 
                             "logFile": self.logFile })
            cmd = self.dportCmd(**cDict)
            ret &= cmd.send( self.callback, )
            ret &= cmd.success
            self._addLastCommandErrorInfo(cmd)
            if ret:
                self.configuration[configKeys.DDC_DATA_PORT] = getattr(cmd, configKeys.DDC_DATA_PORT)
            pass
        if configKeys.DDC_FREQUENCY_OFFSET in confDict:
            if self.frqCmd is not None:
                freqIn = float(confDict.get(configKeys.DDC_FREQUENCY_OFFSET, 0)) 
                freqAdj = adjustFrequency(freqIn, self.frqRange, 
                                          self.frqRes, self.frqUnits)
                cmd = self.frqCmd(**{ "parent": self, 
                                       configKeys.INDEX: self.index,
                                       configKeys.DDC_FREQUENCY_OFFSET: freqAdj,
                                        "verbose": self.verbose, 
                                        "logFile": self.logFile })
                ret &= cmd.send( self.callback, )
                ret &= cmd.success
                self._addLastCommandErrorInfo(cmd)
                if ret:
                    self.configuration[configKeys.DDC_FREQUENCY_OFFSET] = freqAdj * self.frqUnits
                pass
        keys = [configKeys.ENABLE,
                configKeys.DDC_RATE_INDEX, 
                configKeys.DDC_UDP_DESTINATION, 
                configKeys.DDC_VITA_ENABLE, 
                configKeys.DDC_STREAM_ID]
        if any([q in confDict for q in keys]):
            if self.cfgCmd is not None:
                cDict = {}
                self._dictUpdate(cDict, confDict, self.configuration, keys)
                cDict.update({ "parent": self, 
                                configKeys.INDEX: self.index,
                                 "verbose": self.verbose, 
                                 "logFile": self.logFile })
                cmd = self.cfgCmd(**cDict)
                ret &= cmd.send( self.callback, )
                ret &= cmd.success
                self._addLastCommandErrorInfo(cmd)
                if ret:
                    for key in keys:
                        self.configuration[key] = getattr(cmd, key)
                pass
        return ret
    

#--  WBDDC Objects  ---------------------------------------------------------#

##
# Base WBDDC component class.
#
# A radio handler object maintains one WBDDC component object per WBDDC
# on the radio.  
#
class _wbddc(_ddc):
    _name = "WBDDC"
    wideband = True
    cfgCmd = command.wbddc
    frqCmd = command.wbfrq


#--  NBDDC Objects  ---------------------------------------------------------#

##
# Base NBDDC component class.
#
# A radio handler object maintains one NBDDC component object per NBDDC
# on the radio.  
#
class _nbddc(_ddc):
    _name = "NBDDC"
    wideband = False
    tunable = True
    cfgCmd = command.nbddc
    frqCmd = command.nbfrq
    # OVERRIDE
    validConfigurationKeywords = [
                                  configKeys.ENABLE, 
                                  configKeys.DDC_FREQUENCY_OFFSET,
                                  configKeys.DDC_RATE_INDEX, 
                                  configKeys.DDC_UDP_DESTINATION, 
                                  configKeys.DDC_VITA_ENABLE, 
                                  configKeys.DDC_STREAM_ID, 
                                  configKeys.NBDDC_RF_INDEX, 
                                  ]
    
    # OVERRIDE
    ##
    # \protected
    # Queries hardware to determine the object's current configuration.  
    def _queryConfiguration(self):
        # Call the base-class implementation
        configKeys.Configurable._queryConfiguration(self)
        # Override
        if self.frqCmd is not None and self.tunable:
            cmd = self.frqCmd(**{ "parent": self, 
                                   configKeys.INDEX: self.index,
                                   "query": True,
                                    "verbose": self.verbose, 
                                    "logFile": self.logFile })
            cmd.send( self.callback, )
            self._addLastCommandErrorInfo(cmd)
            rspInfo = cmd.getResponseInfo()
            if rspInfo is not None:
                freq = rspInfo.get(configKeys.DDC_FREQUENCY_OFFSET, None)
                self.configuration[configKeys.DDC_FREQUENCY_OFFSET] = None if freq is None else \
                                                                      freq * self.frqUnits
        if self.cfgCmd is not None:
            cmd = self.cfgCmd(**{ "parent": self, 
                                   configKeys.INDEX: self.index,
                                   "query": True,
                                    "verbose": self.verbose, 
                                    "logFile": self.logFile })
            cmd.send( self.callback, )
            self._addLastCommandErrorInfo(cmd)
            rspInfo = cmd.getResponseInfo()
            #self.logIfVerbose("rspInfo =", rspInfo)
            if rspInfo is not None:
                for key in [configKeys.ENABLE, 
                            configKeys.DDC_RATE_INDEX, 
                            configKeys.DDC_UDP_DESTINATION, 
                            configKeys.DDC_VITA_ENABLE, 
                            configKeys.DDC_STREAM_ID, 
                            configKeys.NBDDC_RF_INDEX]:
                    self.configuration[key] = rspInfo.get(key, None)
        pass

    # OVERRIDE
    ##
    # \protected
    # Sets the component's current configuration.  
    def _setConfiguration(self, confDict):
        ret = True
        if configKeys.DDC_FREQUENCY_OFFSET in confDict:
            if self.frqCmd is not None:
                freqIn = float(confDict.get(configKeys.DDC_FREQUENCY_OFFSET, 0)) 
                freqAdj = adjustFrequency(freqIn, self.frqRange, 
                                          self.frqRes, self.frqUnits)
                cmd = self.frqCmd(**{ "parent": self, 
                                       configKeys.INDEX: self.index,
                                       configKeys.DDC_FREQUENCY_OFFSET: freqAdj,
                                        "verbose": self.verbose, 
                                        "logFile": self.logFile })
                ret &= cmd.send( self.callback, )
                ret &= cmd.success
                self._addLastCommandErrorInfo(cmd)
                if ret:
                    self.configuration[configKeys.DDC_FREQUENCY_OFFSET] = freqAdj * self.frqUnits
                pass
        keys = [configKeys.ENABLE, 
                configKeys.DDC_RATE_INDEX, 
                configKeys.DDC_UDP_DESTINATION, 
                configKeys.DDC_VITA_ENABLE, 
                configKeys.DDC_STREAM_ID, 
                configKeys.NBDDC_RF_INDEX]
        if any([q in confDict for q in keys]):
            if self.cfgCmd is not None:
                cDict = {}
                self._dictUpdate(cDict, confDict, self.configuration, keys)
                cDict.update({ "parent": self, 
                                configKeys.INDEX: self.index,
                                 "verbose": self.verbose, 
                                 "logFile": self.logFile })
                cmd = self.cfgCmd(**cDict)
                ret &= cmd.send( self.callback, )
                ret &= cmd.success
                self._addLastCommandErrorInfo(cmd)
                if ret:
                    for key in keys:
                        self.configuration[key] = getattr(cmd, key)
                pass
        return ret


#----------------------------------------------------------------------------#
#--  Tone Generator Objects  ------------------------------------------------#

##
# Base continuous-wave (CW) tone generator component class.
#
# Depending on the radio, the tone generator component can be maintained
# at the radio level or at the transmitter level (as a sub-component).
#
class _cwToneGen(_base):
    _name = "CWToneGen"
    ## Tone frequency range.  This is a 2-tuple: (minimum, maximum).
    frqRange = (-512e5,512e5)
    ## Tone frequency resolution.
    frqRes = 1
    ## Tone amplitude range.  This is a 2-tuple: (minimum, maximum).
    ampRange = (0, 65535)
    ## Tone amplitude resolution.
    ampRes = 1
    ## Tone phase range.  This is a 2-tuple: (minimum, maximum).
    phaseRange = (-180, 180)
    ## Tone phase resolution.
    phaseRes = 1
    ## Tone sweep start frequency range.  This is a 2-tuple: (minimum, maximum).
    startRange = (-512e5,512e5)
    ## Tone sweep start frequency resolution.
    startRes = 1
    ## Tone sweep stop frequency range.  This is a 2-tuple: (minimum, maximum).
    stopRange = (-512e5,512e5)
    ## Tone sweep stop frequency resolution.
    stopRes = 1
    ## Tone sweep step frequency range.  This is a 2-tuple: (minimum, maximum).
    stepRange = (-512e5,512e5)
    ## Tone sweep step frequency resolution.
    stepRes = 1
    ## Tone sweep dwell time range.  This is a 2-tuple: (minimum, maximum).
    dwellRange = (0, 0xFFFFFFFF)
    ## Tone sweep dwell time resolution.
    dwellRes = 1
    ## Command: CW tone characteristics set/query
    toneCmd = command.cwt
    ## Command: CW tone sweep set/query
    sweepCmd = command.cws
    
    # OVERRIDE
    ##
    # The list of valid configuration keywords supported by this
    # object.  Override in derived classes as needed.
    validConfigurationKeywords = [
                                configKeys.CW_FREQUENCY,
                                configKeys.CW_AMPLITUDE,
                                configKeys.CW_PHASE,
                                configKeys.CW_SWEEP_START,
                                configKeys.CW_SWEEP_STOP,
                                configKeys.CW_SWEEP_STEP,
                                configKeys.CW_SWEEP_DWELL,
                                  ]
    
    ##
    # Constructs a tone generator component object.
    #
    # The constructor uses keyword arguments to configure the class.  It 
    # consumes the following keyword arguments:
    # <ul>
    # <li> "verbose": Verbose mode (Boolean)
    # <li> "logFile": An open file or file-like object to be used for log output.  
    #    If not provided, this defaults to standard output. 
    # <li> "parent": The object that manages this component object. 
    # <li> "callback": A method that the component uses to send data over a
    #   connected transport.
    # <li> "index": The index number for this component. 
    # </ul>
    #
    # \param args Variable-length list of positional arguments.  Positional
    #     arguments are ignored.
    # \param kwargs Dictionary of keyword arguments for the component
    #     object.  Which keyword arguments are valid depends on the 
    #     specific component.  Unsupported keyword arguments will be ignored.
    def __init__(self,*args,**kwargs):
        _base.__init__(self,*args,**kwargs)
        
    # OVERRIDE
    ##
    # \protected
    # Queries hardware to determine the object's current configuration.  
    def _queryConfiguration(self):
        # Call the base-class implementation
        configKeys.Configurable._queryConfiguration(self)
        # Override
        if self.toneCmd is not None:
            cmd = self.toneCmd(**{ "parent": self, 
                                   configKeys.CW_INDEX: self.index, \
                                   configKeys.TX_INDEX: self.parent.index, \
                                   "query": True,
                                    "verbose": self.verbose, 
                                    "logFile": self.logFile })
            cmd.send( self.callback, )
            self._addLastCommandErrorInfo(cmd)
            rspInfo = cmd.getResponseInfo()
            if rspInfo is not None:
                self.configuration[configKeys.CW_FREQUENCY] = rspInfo.get(configKeys.CW_FREQUENCY, None)
                self.configuration[configKeys.CW_AMPLITUDE] = rspInfo.get(configKeys.CW_AMPLITUDE, None)
                self.configuration[configKeys.CW_PHASE] = rspInfo.get(configKeys.CW_PHASE, None)
        if self.sweepCmd is not None:
            cmd = self.sweepCmd(**{ "parent": self, 
                                   configKeys.CW_INDEX: self.index, \
                                   configKeys.TX_INDEX: self.parent.index, \
                                   "query": True,
                                    "verbose": self.verbose, 
                                    "logFile": self.logFile })
            cmd.send( self.callback, )
            self._addLastCommandErrorInfo(cmd)
            rspInfo = cmd.getResponseInfo()
            if rspInfo is not None:
                self.configuration[configKeys.CW_SWEEP_START] = rspInfo.get(configKeys.CW_SWEEP_START, None)
                self.configuration[configKeys.CW_SWEEP_STOP] = rspInfo.get(configKeys.CW_SWEEP_STOP, None)
                self.configuration[configKeys.CW_SWEEP_STEP] = rspInfo.get(configKeys.CW_SWEEP_STEP, None)
                self.configuration[configKeys.CW_SWEEP_DWELL] = rspInfo.get(configKeys.CW_SWEEP_DWELL, None)
        pass

    # OVERRIDE
    ##
    # \protected
    # Issues hardware commands to set the object's current configuration.  
    def _setConfiguration(self, confDict):
        ret = True
        keys = [configKeys.CW_FREQUENCY,
                configKeys.CW_AMPLITUDE,
                configKeys.CW_PHASE,
                ]
        if any([q in confDict for q in keys]):
            if self.toneCmd is not None:
                cDict = {}
                self._dictUpdate(cDict, confDict, self.configuration, keys)
                cDict.update({ "parent": self, 
                                configKeys.CW_INDEX: self.index,
                                configKeys.TX_INDEX: self.parent.index,
                                 "verbose": self.verbose, 
                                 "logFile": self.logFile })
                cmd = self.toneCmd(**cDict)
                ret &= cmd.send( self.callback, )
                ret &= cmd.success
                self._addLastCommandErrorInfo(cmd)
                if ret:
                    for key in keys:
                        self.configuration[key] = getattr(cmd, key)
                pass
        keys = [configKeys.CW_SWEEP_START,
                configKeys.CW_SWEEP_STOP,
                configKeys.CW_SWEEP_STEP,
                configKeys.CW_SWEEP_DWELL,
                ]
        if any([q in confDict for q in keys]):
            if self.sweepCmd is not None:
                cDict = {}
                self._dictUpdate(cDict, confDict, self.configuration, keys)
                cDict.update({ "parent": self, 
                                configKeys.CW_INDEX: self.index,
                                configKeys.TX_INDEX: self.parent.index,
                                 "verbose": self.verbose, 
                                 "logFile": self.logFile })
                cmd = self.sweepCmd(**cDict)
                ret &= cmd.send( self.callback, )
                ret &= cmd.success
                self._addLastCommandErrorInfo(cmd)
                if ret:
                    for key in keys:
                        self.configuration[key] = getattr(cmd, key)
                pass
        return ret

#----------------------------------------------------------------------------#
#--  Transmitter Objects  ---------------------------------------------------#

##
# Base transmitter component class.
#
# A radio handler object maintains one transmitter component object per 
# transmitter on the radio.  
#
class _tx(_base):
    _name = "TX"
    ## Tunable frequency range.  This is a 2-tuple: (minimum, maximum).
    frqRange = (20e6,6e9)
    ## Frequency resolution.
    frqRes = 1e6
    ## Frequency units.
    frqUnits = 1e6
    ## Tunable attenuation range.  This is a 2-tuple: (minimum, maximum).
    attRange = (0.0,10.0)
    ## Attenuation resolution.
    attRes = 1.0
    ## Number of tone generators.
    numToneGen = 0
    ## Tone generator component type.
    toneGenType = None
    ## Tone generator index base (where index numbers start from).
    toneGenIndexBase = 1
    # Supported commands
    ## Frequency set/query command.
    frqCmd = command.txf
    ## Attenuation set/query command.
    attCmd = command.txa
    ## TX power set/query command.
    tpwrCmd = command.txp
    # OVERRIDE
    ##
    # The list of valid configuration keywords supported by this
    # object.  Override in derived classes as needed.
    validConfigurationKeywords = [
                                   configKeys.TX_FREQUENCY, 
                                   configKeys.TX_ATTENUATION, 
                                   configKeys.ENABLE, 
                                   configKeys.CONFIG_CW,
                                  ]
    
    ##
    # Constructs a transmitter component object.
    #
    # The constructor uses keyword arguments to configure the class.  It 
    # consumes the following keyword arguments:
    # <ul>
    # <li> "verbose": Verbose mode (Boolean)
    # <li> "logFile": An open file or file-like object to be used for log output.  
    #    If not provided, this defaults to standard output. 
    # <li> "parent": The radio handler object that manages this component object. 
    # <li> "callback": A method that the component uses to send data over a
    #   connected transport.
    # <li> "index": The index number for this component. 
    # </ul>
    #
    # \param args Variable-length list of positional arguments.  Positional
    #     arguments are ignored.
    # \param kwargs Dictionary of keyword arguments for the component
    #     object.  Which keyword arguments are valid depends on the 
    #     specific component.  Unsupported keyword arguments will be ignored.
    def __init__(self,*args,**kwargs):
        _base.__init__(self,*args,**kwargs)
        self.toneGenDict = {}
        for i in range(self.toneGenIndexBase, 
                        self.toneGenIndexBase + self.numToneGen, 1):
            self.toneGenDict[i] = self.toneGenType(parent=self, 
                                                   callback=self.callback, 
                                                   index=i, 
                                                   verbose=self.verbose, 
                                                   logFile=self.logFile)
        
    # OVERRIDE
    ##
    # Adds a communication transport to this component.
    #
    # The component will query the hardware for its configuration after the
    # transport is added.
    #
    # \param transport The communication transport (an object of type 
    #    CyberRadioDriver.transport.radio_transport). 
    # \param callback A method that the component uses to send data over the
    #   connected transport.
    # \param queryConfig Whether or not to query the configuration
    #   through hardware commands
    def addTransport(self,transport,callback,queryConfig=True):
        for i in self.toneGenDict:
            self.toneGenDict[i].addTransport(transport, callback, queryConfig)
        _base.addTransport(self, transport, callback, queryConfig)
        
    # OVERRIDE
    ##
    # \protected
    # Queries hardware to determine the object's current configuration.  
    def _queryConfiguration(self):
        # Call the base-class implementation
        configKeys.Configurable._queryConfiguration(self)
        # Override
        if self.tpwrCmd is not None:
            cmd = self.tpwrCmd(**{ "parent": self, 
                                   configKeys.TX_INDEX: self.index,
                                   "query": True,
                                    "verbose": self.verbose, 
                                    "logFile": self.logFile })
            cmd.send( self.callback, )
            self._addLastCommandErrorInfo(cmd)
            rspInfo = cmd.getResponseInfo()
            if rspInfo is not None:
                self.configuration[configKeys.ENABLE] = rspInfo.get(configKeys.ENABLE, 0)
        if self.frqCmd is not None:
            cmd = self.frqCmd(**{ "parent": self, 
                                   configKeys.TX_INDEX: self.index,
                                   "query": True,
                                    "verbose": self.verbose, 
                                    "logFile": self.logFile })
            cmd.send( self.callback, )
            self._addLastCommandErrorInfo(cmd)
            rspInfo = cmd.getResponseInfo()
            if rspInfo is not None:
                freq = rspInfo.get(configKeys.TX_FREQUENCY, None)
                self.configuration[configKeys.TX_FREQUENCY] = None if freq is None else \
                                                  freq * self.frqUnits
        if self.attCmd is not None:
            cmd = self.attCmd(**{ "parent": self, 
                                   configKeys.TX_INDEX: self.index,
                                   "query": True,
                                    "verbose": self.verbose, 
                                    "logFile": self.logFile })
            self._addLastCommandErrorInfo(cmd)
            cmd.send( self.callback, )
            rspInfo = cmd.getResponseInfo()
            if rspInfo is not None:
                self.configuration[configKeys.TX_ATTENUATION] = rspInfo.get(configKeys.TX_ATTENUATION, None)
        if self.toneGenType is not None:
            self.configuration[configKeys.CONFIG_CW] = {}
            for i in self.toneGenDict:
                self.configuration[configKeys.CONFIG_CW][i] = self.toneGenDict[i].queryConfiguration()
                self.cmdErrorInfo.extend(self.toneGenDict[i].getLastCommandErrorInfo())
        pass

    # OVERRIDE
    ##
    # \protected
    # Issues hardware commands to set the object's current configuration.  
    def _setConfiguration(self, confDict):
        ret = True
        if configKeys.ENABLE in confDict:
            if self.tpwrCmd is not None:
                cmd = self.tpwrCmd(**{ "parent": self, 
                                       configKeys.TX_INDEX: self.index,
                                       configKeys.ENABLE: confDict.get(configKeys.ENABLE, 0),
                                        "verbose": self.verbose, 
                                        "logFile": self.logFile })
                ret &= cmd.send( self.callback, )
                ret &= cmd.success
                self._addLastCommandErrorInfo(cmd)
                if ret:
                    self.configuration[configKeys.ENABLE] = getattr(cmd, configKeys.ENABLE)
                pass
        if configKeys.TX_FREQUENCY in confDict:
            if self.frqCmd is not None:
                freqIn = float(confDict.get(configKeys.TX_FREQUENCY, 0)) 
                freqAdj = adjustFrequency(freqIn, self.frqRange, 
                                          self.frqRes, self.frqUnits)
                cmd = self.frqCmd(**{ "parent": self, 
                                       configKeys.TX_INDEX: self.index,
                                       configKeys.TX_FREQUENCY: freqAdj,
                                        "verbose": self.verbose, 
                                        "logFile": self.logFile })
                ret &= cmd.send( self.callback, )
                ret &= cmd.success
                self._addLastCommandErrorInfo(cmd)
                if ret:
                    self.configuration[configKeys.TX_FREQUENCY] = freqAdj * self.frqUnits
                pass
        if configKeys.TX_ATTENUATION in confDict:
            if self.attCmd is not None:
                rfAttIn = float(confDict.get(configKeys.TX_ATTENUATION, 0))
                rfAttAdj = adjustAttenuation(rfAttIn, self.attRange, 
                                            self.attRes, 1)
                cmd = self.attCmd(**{ "parent": self, 
                                       configKeys.TX_INDEX: self.index,
                                       configKeys.TX_ATTENUATION: rfAttAdj,
                                        "verbose": self.verbose, 
                                        "logFile": self.logFile })
                ret &= cmd.send( self.callback, )
                ret &= cmd.success
                self._addLastCommandErrorInfo(cmd)
                if ret:
                    self.configuration[configKeys.TX_ATTENUATION] = rfAttAdj
                pass
        if self.numToneGen > 0 and configKeys.CONFIG_CW in confDict:
            for tgNum in range(self.toneGenIndexBase, self.toneGenIndexBase + self.numToneGen):
                if tgNum in confDict[configKeys.CONFIG_CW]:
                    self.toneGenDict[tgNum].setConfiguration(**confDict[configKeys.CONFIG_CW][tgNum])
                    self.cmdErrorInfo.extend(self.toneGenDict[tgNum].getLastCommandErrorInfo())
                pass
        return ret

#----------------------------------------------------------------------------#
#--  DUC Objects  ---------------------------------------------------#

class _duc(_base):
    _name = "_baseDuc"
    ## Whether this is a wideband DUC.
    wideband = True
    ## Tunable frequency offset range.  This is a 2-tuple: (minimum, maximum).
    frqRange = (-51.2e6, 51.2e6)
    ## Frequency offset resolution.
    frqRes = 1
    ## Frequency offset units.
    frqUnits = 1
    ## Tunable attenuation range.  This is a 2-tuple: (minimum, maximum).
    attRange = (-60.0,60.0)
    ## Attenuation resolution.
    attRes = 0.1
    ## DUC rate set.  This is a dictionary whose keys are rate index numbers and 
    # whose values are DUC rates. 
    rateSet = { \
                0: 102.4e6, 
                1:  51.2e6, 
                2:  25.6e6, 
                3:  12.8e6, 
                4:   6.4e6, 
                6:   1.6e6, 
                7: 800.0e3, 
                8: 400.0e3, 
                9: 200.0e3, 
               10: 100.0e3, 
               11:  50.0e3, 
               12:  25.0e3, 
               13:  12.5e3, 
                16: 13e6/48, 
               20:   5.6e6, 
                 }
    ## DUC configuration query/set command.
    cfgCmd = command.duc
    ## DUC load snapshot command [set only].
    snapshotLoadCmd = None
    ## DUC transmit snapshot query/set command.
    snapshotTxCmd = None
    # OVERRIDE
    ##
    # The list of valid configuration keywords supported by this
    # object.  Override in derived classes as needed.
    validConfigurationKeywords = [
                                  configKeys.DUC_DATA_PORT,
                                  configKeys.DUC_FREQUENCY,
                                  configKeys.DUC_ATTENUATION,
                                  configKeys.DUC_RATE_INDEX, 
                                  configKeys.DUC_TX_CHANNELS, 
                                  configKeys.DUC_MODE,
                                  configKeys.DUC_STREAM_ID, 
                                  #configKeys.DUC_START_BLOCK,
                                  #configKeys.DUC_END_BLOCK,
                                  configKeys.DUC_FILENAME,
                                  configKeys.DUC_START_SAMPLE,
                                  configKeys.DUC_SAMPLES,
                                  configKeys.DUC_SINGLE_PLAYBACK,
                                  ]

    # OVERRIDE
    ##
    # \protected
    # Queries hardware to determine the object's current configuration.  
    def _queryConfiguration(self):
        # Call the base-class implementation
        configKeys.Configurable._queryConfiguration(self)
        # Override
        if self.cfgCmd is not None:
            cmd = self.cfgCmd(**{ "parent": self, 
                                  configKeys.DUC_INDEX: self.index,
                                  "query": True,
                                   "verbose": self.verbose, 
                                   "logFile": self.logFile })
            cmd.send( self.callback, )
            self._addLastCommandErrorInfo(cmd)
            rspInfo = cmd.getResponseInfo()
            if rspInfo is not None:
                self.configuration[configKeys.DUC_DATA_PORT] = rspInfo.get(configKeys.DUC_DATA_PORT, 0)
                self.configuration[configKeys.DUC_FREQUENCY] = rspInfo.get(configKeys.DUC_FREQUENCY, 0)
                self.configuration[configKeys.DUC_ATTENUATION] = rspInfo.get(configKeys.DUC_ATTENUATION, 0)
                self.configuration[configKeys.DUC_RATE_INDEX] = rspInfo.get(configKeys.DUC_RATE_INDEX, 0)
                self.configuration[configKeys.DUC_TX_CHANNELS] = rspInfo.get(configKeys.DUC_TX_CHANNELS, 0)
                self.configuration[configKeys.DUC_MODE] = rspInfo.get(configKeys.DUC_MODE, 0)
                self.configuration[configKeys.DUC_STREAM_ID] = rspInfo.get(configKeys.DUC_STREAM_ID, 0)
        pass

    # OVERRIDE
    ##
    # \protected
    # Issues hardware commands to set the object's current configuration.  
    def _setConfiguration(self, confDict):
        ret = True
        keys = [ 
            configKeys.DUC_DATA_PORT,
            configKeys.DUC_FREQUENCY,
            configKeys.DUC_ATTENUATION,
            configKeys.DUC_RATE_INDEX,
            configKeys.DUC_TX_CHANNELS,
            configKeys.DUC_MODE,
            configKeys.DUC_STREAM_ID,
            ]
        if any([q in confDict for q in keys]):
            if self.cfgCmd is not None:
                cDict = {}
                self._dictUpdate(cDict, confDict, self.configuration, keys)
                cDict.update({ "parent": self, 
                                configKeys.DUC_INDEX: self.index,
                                 "verbose": self.verbose, 
                                 "logFile": self.logFile })
                cmd = self.cfgCmd(**cDict)
                ret &= cmd.send( self.callback, )
                ret &= cmd.success
                self._addLastCommandErrorInfo(cmd)
                if ret:
                    self.configuration[configKeys.DUC_DATA_PORT] = getattr(cmd, configKeys.DUC_DATA_PORT)
                    self.configuration[configKeys.DUC_FREQUENCY] = getattr(cmd, configKeys.DUC_FREQUENCY)
                    self.configuration[configKeys.DUC_ATTENUATION] = getattr(cmd, configKeys.DUC_ATTENUATION)
                    self.configuration[configKeys.DUC_RATE_INDEX] = getattr(cmd, configKeys.DUC_RATE_INDEX)
                    self.configuration[configKeys.DUC_TX_CHANNELS] = getattr(cmd, configKeys.DUC_TX_CHANNELS)
                    self.configuration[configKeys.DUC_MODE] = getattr(cmd, configKeys.DUC_MODE)
                    self.configuration[configKeys.DUC_STREAM_ID] = getattr(cmd, configKeys.DUC_STREAM_ID)
                pass
        # DUC snapshot load command comes first, so that the user can provide snapshot
        # load information and snapshot transmission information in one setConfiguration() 
        # command.
        keys = [ 
            configKeys.DUC_FILENAME,
            configKeys.DUC_START_SAMPLE,
            configKeys.DUC_SAMPLES,
            ]
        if all([q in confDict for q in keys]):
            if self.snapshotLoadCmd is not None:
                cmd = self.snapshotLoadCmd(**{ "parent": self, 
                                      configKeys.DUC_FILENAME: confDict[configKeys.DUC_FILENAME],
                                      configKeys.DUC_INDEX: self.index,
                                      configKeys.DUC_START_SAMPLE: confDict[configKeys.DUC_START_SAMPLE],
                                      configKeys.DUC_SAMPLES: confDict[configKeys.DUC_SAMPLES],
                                       "verbose": self.verbose, 
                                       "logFile": self.logFile })
                ret &= cmd.send( self.callback, )
                ret &= cmd.success
                self._addLastCommandErrorInfo(cmd)
                pass
        keys = [ 
            configKeys.DUC_START_SAMPLE,
            configKeys.DUC_SAMPLES,
            configKeys.DUC_SINGLE_PLAYBACK,
            ]
        if any([q in confDict for q in keys]):
            if self.snapshotTxCmd is not None:
                cDict = {}
                self._dictUpdate(cDict, confDict, self.configuration, keys)
                cDict.update({ "parent": self, 
                                configKeys.DUC_INDEX: self.index,
                                configKeys.DUC_START_SAMPLE: confDict[configKeys.DUC_START_SAMPLE],
                                configKeys.DUC_SAMPLES: confDict[configKeys.DUC_SAMPLES],
                                configKeys.DUC_SINGLE_PLAYBACK: confDict[configKeys.DUC_SINGLE_PLAYBACK],
                                 "verbose": self.verbose, 
                                 "logFile": self.logFile })
                cmd = self.snapshotTxCmd(**cDict)
                ret &= cmd.send( self.callback, )
                ret &= cmd.success
                self._addLastCommandErrorInfo(cmd)
                pass
        return ret



class _wbduc(_duc):
    _name = "WBDUC"
    wideband = True



#----------------------------------------------------------------------------#
#--  DDC Group Objects  ---------------------------------------------------#

##
# Base DDC group component class.
#
# A DDC group component object maintains one DDC group on the radio.  
#
class ddc_group(_base):
    _name = "DDCGroup"
    ## Whether this is a wideband DDC group.
    wideband = True
    ## \brief Group member index base (what number indices start at) 
    groupMemberIndexBase = 1
    ## \brief Number of potential group members 
    numGroupMembers = 0
    ## DDC group member assignment command
    groupMemberCmd = None
    ## DDC group enable command
    groupEnableCmd = None

    # OVERRIDE
    ##
    # The list of valid configuration keywords supported by this
    # object.  Override in derived classes as needed.
    validConfigurationKeywords = [
                                  configKeys.ENABLE, 
                                  configKeys.DDC_GROUP_MEMBERS,
                                  ]
    
    ##
    # Constructs a DDC group component object.
    #
    # The constructor uses keyword arguments to configure the class.  It 
    # consumes the following keyword arguments:
    # <ul>
    # <li> "verbose": Verbose mode (Boolean)
    # <li> "logFile": An open file or file-like object to be used for log output.  
    #    If not provided, this defaults to standard output. 
    # <li> "parent": The radio handler object that manages this component object. 
    # <li> "callback": A method that the component uses to send data over a
    #   connected transport.
    # <li> "index": The index number for this component. 
    # </ul>
    #
    # \param args Variable-length list of positional arguments.  Positional
    #     arguments are ignored.
    # \param kwargs Dictionary of keyword arguments for the component
    #     object.  Which keyword arguments are valid depends on the 
    #     specific component.  Unsupported keyword arguments will be ignored.
    def __init__(self,*args,**kwargs):
        _base.__init__(self, *args, **kwargs)
    
    # OVERRIDE
    ##
    # \protected
    # Queries hardware to determine the object's current configuration.  
    def _queryConfiguration(self):
        # Call the base-class implementation
        configKeys.Configurable._queryConfiguration(self)
        # Override
        if self.groupMemberCmd is not None:
            members = []
            for memberIndex in range(self.groupMemberIndexBase,
                                      self.groupMemberIndexBase + self.numGroupMembers, 1):
                cmd = self.groupMemberCmd(**{ "parent": self, 
                                       configKeys.INDEX: self.index,
                                       configKeys.DDC_GROUP_MEMBER: memberIndex,
                                       "query": True,
                                        "verbose": self.verbose, 
                                        "logFile": self.logFile })
                cmd.send( self.callback, )
                self._addLastCommandErrorInfo(cmd)
                rspInfo = cmd.getResponseInfo()
                if rspInfo is not None:
                    enabled = rspInfo.get(configKeys.ENABLE, False)
                    if enabled:
                        members.append(memberIndex)
            self.configuration[configKeys.DDC_GROUP_MEMBERS] = members
        if self.groupEnableCmd is not None:
            cmd = self.groupEnableCmd(**{ "parent": self, 
                                   configKeys.INDEX: self.index,
                                   "query": True,
                                    "verbose": self.verbose, 
                                    "logFile": self.logFile })
            cmd.send( self.callback, )
            self._addLastCommandErrorInfo(cmd)
            rspInfo = cmd.getResponseInfo()
            if rspInfo is not None:
                self.configuration[configKeys.ENABLE] = rspInfo.get(configKeys.ENABLE, 0)
        pass

    # OVERRIDE
    ##
    # \protected
    # Issues hardware commands to set the object's current configuration.  
    def _setConfiguration(self, confDict):
        ret = True
        if self.groupMemberCmd is not None and \
           configKeys.DDC_GROUP_MEMBERS in confDict:
            if confDict[configKeys.DDC_GROUP_MEMBERS] is None:
                members = []
            elif isinstance(confDict[configKeys.DDC_GROUP_MEMBERS], int):
                members = [confDict[configKeys.DDC_GROUP_MEMBERS]]
            else:
                members = confDict[configKeys.DDC_GROUP_MEMBERS]
            for member in range(self.groupMemberIndexBase, 
                                 self.groupMemberIndexBase + self.numGroupMembers):
                enabled = 1 if member in members else 0
                cDict = { "parent": self, 
                          configKeys.INDEX: self.index,
                          configKeys.DDC_GROUP_MEMBER: member,
                          configKeys.ENABLE: enabled,
                           "verbose": self.verbose, 
                           "logFile": self.logFile }
                cmd = self.groupMemberCmd(**cDict)
                ret &= cmd.send( self.callback, )
                ret &= cmd.success
                self._addLastCommandErrorInfo(cmd)
            if ret:
                self.configuration[configKeys.DDC_GROUP_MEMBERS] = members
            pass
        if configKeys.ENABLE in confDict:
            if self.groupEnableCmd is not None:
                cmd = self.groupEnableCmd(**{ "parent": self, 
                                       configKeys.INDEX: self.index,
                                       configKeys.ENABLE: confDict.get(configKeys.ENABLE, 0),
                                        "verbose": self.verbose, 
                                        "logFile": self.logFile })
                ret &= cmd.send( self.callback, )
                ret &= cmd.success
                self._addLastCommandErrorInfo(cmd)
                if ret:
                    self.configuration[configKeys.ENABLE] = getattr(cmd, configKeys.ENABLE)
                pass
        return ret


##
# WBDDC group component class.
#
# A WBDDC group component object maintains one WBDDC group on the radio.  
#
class wbddc_group(ddc_group):
    _name = "WBDDCGroup"
    ## Whether this is a wideband DDC group.
    wideband = True
    ## DDC group member assignment command
    groupMemberCmd = command.wbg
    ## DDC group enable command
    groupEnableCmd = command.wbge


##
# NBDDC group component class.
#
# A NBDDC group component object maintains one NBDDC group on the radio.  
#
class nbddc_group(ddc_group):
    _name = "NBDDCGroup"
    ## Whether this is a wideband DDC group.
    wideband = False
    ## DDC group member assignment command
    groupMemberCmd = command.nbg
    ## DDC group enable command
    groupEnableCmd = command.nbge
    

##
# Base DUC group component class.
#
# A DUC group component object maintains one DUC group on the radio.  
#
class duc_group(_base):
    _name = "DUCGroup"
    ## Whether this is a wideband DUC group.
    wideband = True
    ## \brief Group member index base (what number indices start at) 
    groupMemberIndexBase = 1
    ## \brief Number of potential group members 
    numGroupMembers = 0
    ## DUC group member assignment command
    groupMemberCmd = None
    ## DUC group enable command
    groupEnableCmd = None

    # OVERRIDE
    ##
    # The list of valid configuration keywords supported by this
    # object.  Override in derived classes as needed.
    validConfigurationKeywords = [
                                  configKeys.ENABLE, 
                                  configKeys.DUC_GROUP_MEMBERS,
                                  ]
    
    ##
    # Constructs a DUC group component object.
    #
    # The constructor uses keyword arguments to configure the class.  It 
    # consumes the following keyword arguments:
    # <ul>
    # <li> "verbose": Verbose mode (Boolean)
    # <li> "logFile": An open file or file-like object to be used for log output.  
    #    If not provided, this defaults to standard output. 
    # <li> "parent": The radio handler object that manages this component object. 
    # <li> "callback": A method that the component uses to send data over a
    #   connected transport.
    # <li> "index": The index number for this component. 
    # </ul>
    #
    # \param args Variable-length list of positional arguments.  Positional
    #     arguments are ignored.
    # \param kwargs Dictionary of keyword arguments for the component
    #     object.  Which keyword arguments are valid depends on the 
    #     specific component.  Unsupported keyword arguments will be ignored.
    def __init__(self,*args,**kwargs):
        _base.__init__(self, *args, **kwargs)
    
    # OVERRIDE
    ##
    # \protected
    # Queries hardware to determine the object's current configuration.  
    def _queryConfiguration(self):
        # Call the base-class implementation
        configKeys.Configurable._queryConfiguration(self)
        # Override
        if self.groupMemberCmd is not None:
            members = []
            for memberIndex in range(self.groupMemberIndexBase,
                                      self.groupMemberIndexBase + self.numGroupMembers, 1):
                cmd = self.groupMemberCmd(**{ "parent": self, 
                                       configKeys.INDEX: self.index,
                                       configKeys.DUC_GROUP_MEMBER: memberIndex,
                                       "query": True,
                                        "verbose": self.verbose, 
                                        "logFile": self.logFile })
                cmd.send( self.callback, )
                self._addLastCommandErrorInfo(cmd)
                rspInfo = cmd.getResponseInfo()
                if rspInfo is not None:
                    enabled = rspInfo.get(configKeys.ENABLE, False)
                    if enabled:
                        members.append(memberIndex)
            self.configuration[configKeys.DUC_GROUP_MEMBERS] = members
        if self.groupEnableCmd is not None:
            cmd = self.groupEnableCmd(**{ "parent": self, 
                                   configKeys.INDEX: self.index,
                                   "query": True,
                                    "verbose": self.verbose, 
                                    "logFile": self.logFile })
            cmd.send( self.callback, )
            self._addLastCommandErrorInfo(cmd)
            rspInfo = cmd.getResponseInfo()
            if rspInfo is not None:
                self.configuration[configKeys.ENABLE] = rspInfo.get(configKeys.ENABLE, 0)
        pass

    # OVERRIDE
    ##
    # \protected
    # Issues hardware commands to set the object's current configuration.  
    def _setConfiguration(self, confDict):
        ret = True
        if self.groupMemberCmd is not None and \
           configKeys.DUC_GROUP_MEMBERS in confDict:
            if confDict[configKeys.DUC_GROUP_MEMBERS] is None:
                members = []
            elif isinstance(confDict[configKeys.DUC_GROUP_MEMBERS], int):
                members = [confDict[configKeys.DUC_GROUP_MEMBERS]]
            else:
                members = confDict[configKeys.DUC_GROUP_MEMBERS]
            for member in range(self.groupMemberIndexBase, 
                                 self.groupMemberIndexBase + self.numGroupMembers):
                enabled = 1 if member in members else 0
                cDict = { "parent": self, 
                          configKeys.INDEX: self.index,
                          configKeys.DUC_GROUP_MEMBERS: member,
                          configKeys.ENABLE: enabled,
                           "verbose": self.verbose, 
                           "logFile": self.logFile }
                cmd = self.groupMemberCmd(**cDict)
                ret &= cmd.send( self.callback, )
                ret &= cmd.success
                self._addLastCommandErrorInfo(cmd)
            if ret:
                self.configuration[configKeys.DUC_GROUP_MEMBERS] = members
            pass
        if configKeys.ENABLE in confDict:
            if self.groupEnableCmd is not None:
                cmd = self.groupEnableCmd(**{ "parent": self, 
                                       configKeys.INDEX: self.index,
                                       configKeys.ENABLE: confDict.get(configKeys.ENABLE, 0),
                                        "verbose": self.verbose, 
                                        "logFile": self.logFile })
                ret &= cmd.send( self.callback, )
                ret &= cmd.success
                self._addLastCommandErrorInfo(cmd)
                if ret:
                    self.configuration[configKeys.ENABLE] = getattr(cmd, configKeys.ENABLE)
                pass
        return ret


##
# WBDUC group component class.
#
# A WBDUC group component object maintains one WBDUC group on the radio.  
#
class wbduc_group(ddc_group):
    _name = "WBDUCGroup"
    ## Whether this is a wideband DUC group.
    wideband = True
    ## DUC group member assignment command
    groupMemberCmd = command.ducg
    ## DUC group enable command
    groupEnableCmd = command.ducge


##
# Base tuner group component class.
#
# A tuner group component object maintains one tuner group on the radio.
#
# \note Tuner groups are normally used for coherent tuning support.  
#
class tuner_group(_base):
    _name = "TunerGroup"
    ## \brief Group member index base (what number indices start at) 
    groupMemberIndexBase = 1
    ## \brief Number of potential group members 
    numGroupMembers = 0
    ## Group member assignment command
    groupMemberCmd = None
    ## Group enable command
    groupEnableCmd = None

    # OVERRIDE
    ##
    # The list of valid configuration keywords supported by this
    # object.  Override in derived classes as needed.
    validConfigurationKeywords = [
                                  configKeys.ENABLE, 
                                  configKeys.TUNER_GROUP_MEMBERS,
                                  ]
    
    ##
    # Constructs a tuner group component object.
    #
    # The constructor uses keyword arguments to configure the class.  It 
    # consumes the following keyword arguments:
    # <ul>
    # <li> "verbose": Verbose mode (Boolean)
    # <li> "logFile": An open file or file-like object to be used for log output.  
    #    If not provided, this defaults to standard output. 
    # <li> "parent": The radio handler object that manages this component object. 
    # <li> "callback": A method that the component uses to send data over a
    #   connected transport.
    # <li> "index": The index number for this component. 
    # </ul>
    #
    # \param args Variable-length list of positional arguments.  Positional
    #     arguments are ignored.
    # \param kwargs Dictionary of keyword arguments for the component
    #     object.  Which keyword arguments are valid depends on the 
    #     specific component.  Unsupported keyword arguments will be ignored.
    def __init__(self,*args,**kwargs):
        _base.__init__(self, *args, **kwargs)
    
    # OVERRIDE
    ##
    # \protected
    # Queries hardware to determine the object's current configuration.  
    def _queryConfiguration(self):
        # Call the base-class implementation
        configKeys.Configurable._queryConfiguration(self)
        # Override
        if self.groupMemberCmd is not None:
            members = []
            for memberIndex in range(self.groupMemberIndexBase,
                                      self.groupMemberIndexBase + self.numGroupMembers, 1):
                cmd = self.groupMemberCmd(**{ "parent": self, 
                                       configKeys.INDEX: self.index,
                                       configKeys.TUNER_GROUP_MEMBER: memberIndex,
                                       "query": True,
                                        "verbose": self.verbose, 
                                        "logFile": self.logFile })
                cmd.send( self.callback, )
                self._addLastCommandErrorInfo(cmd)
                rspInfo = cmd.getResponseInfo()
                if rspInfo is not None:
                    enabled = rspInfo.get(configKeys.ENABLE, False)
                    if enabled:
                        members.append(memberIndex)
            self.configuration[configKeys.TUNER_GROUP_MEMBERS] = members
        if self.groupEnableCmd is not None:
            cmd = self.groupEnableCmd(**{ "parent": self, 
                                   configKeys.INDEX: self.index,
                                   "query": True,
                                    "verbose": self.verbose, 
                                    "logFile": self.logFile })
            cmd.send( self.callback, )
            self._addLastCommandErrorInfo(cmd)
            rspInfo = cmd.getResponseInfo()
            if rspInfo is not None:
                self.configuration[configKeys.ENABLE] = rspInfo.get(configKeys.ENABLE, 0)
        pass

    # OVERRIDE
    ##
    # \protected
    # Issues hardware commands to set the object's current configuration.  
    def _setConfiguration(self, confDict):
        ret = True
        if self.groupMemberCmd is not None and \
           configKeys.TUNER_GROUP_MEMBERS in confDict:
            if confDict[configKeys.TUNER_GROUP_MEMBERS] is None:
                members = []
            elif isinstance(confDict[configKeys.TUNER_GROUP_MEMBERS], int):
                members = [confDict[configKeys.TUNER_GROUP_MEMBERS]]
            else:
                members = confDict[configKeys.TUNER_GROUP_MEMBERS]
            for member in range(self.groupMemberIndexBase, 
                                 self.groupMemberIndexBase + self.numGroupMembers):
                enabled = 1 if member in members else 0
                cDict = { "parent": self, 
                          configKeys.INDEX: self.index,
                          configKeys.TUNER_GROUP_MEMBERS: member,
                          configKeys.ENABLE: enabled,
                           "verbose": self.verbose, 
                           "logFile": self.logFile }
                cmd = self.groupMemberCmd(**cDict)
                ret &= cmd.send( self.callback, )
                ret &= cmd.success
                self._addLastCommandErrorInfo(cmd)
            if ret:
                self.configuration[configKeys.TUNER_GROUP_MEMBERS] = members
            pass
        if configKeys.ENABLE in confDict:
            if self.groupEnableCmd is not None:
                cmd = self.groupEnableCmd(**{ "parent": self, 
                                       configKeys.INDEX: self.index,
                                       configKeys.ENABLE: confDict.get(configKeys.ENABLE, 0),
                                        "verbose": self.verbose, 
                                        "logFile": self.logFile })
                ret &= cmd.send( self.callback, )
                ret &= cmd.success
                self._addLastCommandErrorInfo(cmd)
                if ret:
                    self.configuration[configKeys.ENABLE] = getattr(cmd, configKeys.ENABLE)
                pass
        return ret


