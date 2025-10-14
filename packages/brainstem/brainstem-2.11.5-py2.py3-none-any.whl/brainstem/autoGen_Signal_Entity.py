# This file was auto-generated. Do not modify.

from ._bs_c_cffi import ffi
from . import _BS_C #imported from __init__
from .Entity_Entity import *
from .result import Result
from .ffi_utils import data_to_bytearray, bytes_to_string, handle_sign

class Signal(Entity):
    
    """ 
        SignalClass:
        Interface to digital pins configured to produce square wave signals.
        This class is designed to allow for square waves at various frequencies and duty cycles. Control
        is defined by specifying the wave period as (T3Time) and the active portion of the cycle as (T2Time).
        See the entity overview section of the reference for more detail regarding the timing.

    """ 


    def __init__(self, module, index):
        super(Signal, self).__init__(module, _BS_C.cmdSIGNAL, index)

    def setEnable(self, enable):

        """ 
        Enable/Disable the signal output.

        :param enable: True to enable, false to disable
        :type enable: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.signal_setEnable(self._module._id_pointer, result, self._index, enable)
        return result.error

    def getEnable(self):

        """ 
        Get the Enable/Disable of the signal.
        True to enable, false to disable

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.signal_getEnable(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setInvert(self, invert):

        """ 
        Invert the signal output.
        Normal mode is High on t0 then low at t2.
        Inverted mode is Low at t0 on period start and high at t2.

        :param invert: to invert, false for normal mode.
        :type invert: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.signal_setInvert(self._module._id_pointer, result, self._index, invert)
        return result.error

    def getInvert(self):

        """ 
        Get the invert status the signal output.
        Normal mode is High on t0 then low at t2.
        Inverted mode is Low at t0 on period start and high at t2.
        to invert, false for normal mode.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.signal_getInvert(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setT3Time(self, t3_nsec):

        """ 
        Set the signal period or T3 in nanoseconds.

        :param t3_nsec: Integer not larger than unsigned 32 bit max value representing the wave period in nanoseconds.
        :type t3_nsec: const unsigned int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.signal_setT3Time(self._module._id_pointer, result, self._index, t3_nsec)
        return result.error

    def getT3Time(self):

        """ 
        Get the signal period or T3 in nanoseconds.
        Integer not larger than unsigned 32 bit max value representing
        the wave period in nanoseconds.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.signal_getT3Time(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def setT2Time(self, t2_nsec):

        """ 
        Set the signal active period or T2 in nanoseconds.

        :param t2_nsec: Integer not larger than unsigned 32 bit max value representing the wave active period in nanoseconds.
        :type t2_nsec: const unsigned int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.signal_setT2Time(self._module._id_pointer, result, self._index, t2_nsec)
        return result.error

    def getT2Time(self):

        """ 
        Get the signal active period or T2 in nanoseconds.
        Integer not larger than unsigned 32 bit max value representing
        the wave active period in nanoseconds.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.signal_getT2Time(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

