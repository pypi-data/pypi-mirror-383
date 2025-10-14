# This file was auto-generated. Do not modify.

from ._bs_c_cffi import ffi
from . import _BS_C #imported from __init__
from .Entity_Entity import *
from .result import Result
from .ffi_utils import data_to_bytearray, bytes_to_string, handle_sign

class Relay(Entity):
    
    """ 
        RelayClass:
        Interface to relay entities on BrainStem modules.
        Relay entities can be set, and the voltage read.  Other capabilities
        may be available, please see the product datasheet.

    """ 

    VALUE_LOW = 0
    VALUE_HIGH = 1

    def __init__(self, module, index):
        super(Relay, self).__init__(module, _BS_C.cmdRELAY, index)

    def setEnable(self, bEnable):

        """ 
        Set the enable/disable state.

        :param bEnable: False or 0 = Disabled, True or 1 = Enabled
        :type bEnable: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.relay_setEnable(self._module._id_pointer, result, self._index, bEnable)
        return result.error

    def getEnable(self):

        """ 
        Get the state.
        False or 0 = Disabled, True or 1 = Enabled

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.relay_getEnable(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def getVoltage(self):

        """ 
        Get the scaled micro volt value with reference to ground.
        32 bit signed integer (in micro Volts) based on the boards
        ground and reference voltages.
        Note: Not all modules provide 32 bits of accuracy; Refer to the module's
        datasheet to determine the analog bit depth and reference voltage.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.relay_getVoltage(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

