# This file was auto-generated. Do not modify.

from ._bs_c_cffi import ffi
from . import _BS_C #imported from __init__
from .Entity_Entity import *
from .result import Result
from .ffi_utils import data_to_bytearray, bytes_to_string, handle_sign

class Temperature(Entity):
    
    """ 
        TemperatureClass:
        This entity is only available on certain modules, and provides a
        temperature reading in microcelsius.

    """ 


    def __init__(self, module, index):
        super(Temperature, self).__init__(module, _BS_C.cmdTEMPERATURE, index)

    def getValue(self):

        """ 
        Get the modules temperature in micro-C
        The temperature in micro-Celsius (1 == 1e-6C).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.temperature_getValue(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def getValueMin(self):

        """ 
        Get the module's minimum temperature in micro-C since the last power cycle.
        The module's minimum temperature in micro-C

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.temperature_getValueMin(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def getValueMax(self):

        """ 
        Get the module's maximum temperature in micro-C since the last power cycle.
        The module's maximum temperature in micro-C

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.temperature_getValueMax(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def resetEntityToFactoryDefaults(self):

        """ 
        Resets the TemperatureClass Entity to it factory default configuration.

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.temperature_resetEntityToFactoryDefaults(self._module._id_pointer, result, self._index)
        return result.error

