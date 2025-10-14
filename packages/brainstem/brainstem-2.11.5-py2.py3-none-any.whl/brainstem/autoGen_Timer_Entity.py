# This file was auto-generated. Do not modify.

from ._bs_c_cffi import ffi
from . import _BS_C #imported from __init__
from .Entity_Entity import *
from .result import Result
from .ffi_utils import data_to_bytearray, bytes_to_string, handle_sign

class Timer(Entity):
    
    """ 
        TimerClass:
        The Timer Class provides access to a simple scheduler.
        The timer can set to fire only once, or to repeat at a certain
        interval. Additionally, a timer entity can execute custom Reflex
        routines upon firing.

    """ 

    SINGLE_SHOT_MODE = 0
    REPEAT_MODE = 1
    DEFAULT_MODE = SINGLE_SHOT_MODE

    def __init__(self, module, index):
        super(Timer, self).__init__(module, _BS_C.cmdTIMER, index)

    def getExpiration(self):

        """ 
        Get the currently set expiration time in microseconds. This is not a "live" timer.
        That is, it shows the expiration time originally set with setExpiration; it does
        not "tick down" to show the time remaining before expiration.
        The timer expiration duration in microseconds.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.timer_getExpiration(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def setExpiration(self, usecDuration):

        """ 
        Set the expiration time for the timer entity. When the timer expires, it will
        fire the associated timer[index]() reflex.

        :param usecDuration: The duration before timer expiration in microseconds.
        :type usecDuration: const unsigned int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.timer_setExpiration(self._module._id_pointer, result, self._index, usecDuration)
        return result.error

    def getMode(self):

        """ 
        Get the mode of the timer which is either single or repeat mode.
        The mode of the time. aTIMER_MODE_REPEAT or aTIMER_MODE_SINGLE.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.timer_getMode(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setMode(self, mode):

        """ 
        Set the mode of the timer which is either single or repeat mode.
        aErrNone Action completed successfully.

        :param mode: The mode of the timer. aTIMER_MODE_REPEAT or aTIMER_MODE_SINGLE.
        :type mode: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.timer_setMode(self._module._id_pointer, result, self._index, mode)
        return result.error

