# This file was auto-generated. Do not modify.

from ._bs_c_cffi import ffi
from . import _BS_C #imported from __init__
from .Entity_Entity import *
from .result import Result
from .ffi_utils import data_to_bytearray, bytes_to_string, handle_sign

class Digital(Entity):
    
    """ 
        DigitalClass:
        Interface to digital entities on BrainStem modules.
        Digital entities have the following 5 possibilities: Digital Input,
        Digital Output, RCServo Input, RCServo Output, and HighZ.
        Other capabilities may be available and not all pins support all
        configurations. Please see the product datasheet.

    """ 

    VALUE_LOW = 0
    VALUE_HIGH = 1
    CONFIGURATION_INPUT = 0
    CONFIGURATION_OUTPUT = 1
    CONFIGURATION_RCSERVO_INPUT = 2
    CONFIGURATION_RCSERVO_OUTPUT = 3
    CONFIGURATION_HIGHZ = 4
    CONFIGURATION_INPUT_PULL_UP = 0
    CONFIGURATION_INPUT_NO_PULL = 4
    CONFIGURATION_INPUT_PULL_DOWN = 5
    CONFIGURATION_SIGNAL_OUTPUT = 6
    CONFIGURATION_SIGNAL_INPUT = 7
    CONFIGURATION_SIGNAL_COUNTER_INPUT = 8

    def __init__(self, module, index):
        super(Digital, self).__init__(module, _BS_C.cmdDIGITAL, index)

    def setConfiguration(self, configuration):

        """ 
        Set the digital configuration to one of the available 5 states.
        Note: Some configurations are only supported on specific pins.
        aErrConfiguration Entity does not support this configuration.

        :param configuration: The configuration to be applied - Digital Input: digitalConfigurationInput = 0 - Digital Output: digitalConfigurationOutput = 1 - RCServo Input: digitalConfigurationRCServoInput = 2 - RCServo Output: digitalConfigurationRCServoOutput = 3 - High Z State: digitalConfigurationHiZ = 4 - Digital Input: digitalConfigurationInputPullUp = 0 - Digital Input: digitalConfigurationInputNoPull = 4 - Digital Input: digitalConfigurationInputPullDown = 5
        :type configuration: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.digital_setConfiguration(self._module._id_pointer, result, self._index, configuration)
        return result.error

    def getConfiguration(self):

        """ 
        Get the digital configuration.
        - Current configuration of the digital entity.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.digital_getConfiguration(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setState(self, state):

        """ 
        Set the logical state.

        :param state: The state to be set. 0 is logic low, 1 is logic high.
        :type state: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.digital_setState(self._module._id_pointer, result, self._index, state)
        return result.error

    def getState(self):

        """ 
        Get the state.
        The current state of the digital entity. 0 is logic low,
        1 is logic high. Note: If in high Z state an error will be returned.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.digital_getState(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setStateAll(self, state):

        """ 
        Sets the logical state of all available digitals based on the bit mapping.
        Number of digitals varies across BrainStem modules.  Refer
        to the datasheet for the capabilities  of your module.

        :param state: The state to be set for all digitals in a bit mapped representation. 0 is logic low, 1 is logic high. Where bit 0 = digital 0, bit 1 = digital 1 etc.
        :type state: const unsigned int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.digital_setStateAll(self._module._id_pointer, result, self._index, state)
        return result.error

    def getStateAll(self):

        """ 
        Gets the logical state of all available digitals in a bit mapped representation.
        Number of digitals varies across BrainStem modules.  Refer
        to the datasheet for the capabilities  of your module.
        The state of all digitals where bit 0 = digital 0,
        bit 1 = digital 1 etc. 0 is logic low, 1 is logic high.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.digital_getStateAll(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

