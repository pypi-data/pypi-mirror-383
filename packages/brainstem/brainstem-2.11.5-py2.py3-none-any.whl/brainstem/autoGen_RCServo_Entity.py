# This file was auto-generated. Do not modify.

from ._bs_c_cffi import ffi
from . import _BS_C #imported from __init__
from .Entity_Entity import *
from .result import Result
from .ffi_utils import data_to_bytearray, bytes_to_string, handle_sign

class RCServo(Entity):
    
    """ 
        RCServoClass:
        Interface to servo entities on BrainStem modules.
        Servo entities are built upon the digital input/output pins and therefore
        can also be inputs or outputs. Please see the product datasheet on the
        configuration limitations.

    """ 

    SERVO_DEFAULT_POSITION = 128
    SERVO_DEFAULT_MIN = 64
    SERVO_DEFAULT_MAX = 192

    def __init__(self, module, index):
        super(RCServo, self).__init__(module, _BS_C.cmdSERVO, index)

    def setEnable(self, enable):

        """ 
        Enable the servo channel

        :param enable: The state to be set. 0 is disabled, 1 is enabled.
        :type enable: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rcservo_setEnable(self._module._id_pointer, result, self._index, enable)
        return result.error

    def getEnable(self):

        """ 
        Get the enable status of the servo channel.
        The current enable status of the servo entity. 0 is disabled,
        1 is enabled.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rcservo_getEnable(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setPosition(self, position):

        """ 
        Set the position of the servo channel

        :param position: The position to be set. Default 64 = a 1ms pulse and 192 = a 2ms pulse.
        :type position: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rcservo_setPosition(self._module._id_pointer, result, self._index, position)
        return result.error

    def getPosition(self):

        """ 
        Get the position of the servo channel
        The current position of the servo channel. Default
        64 = a 1ms pulse and 192 = a 2ms pulse.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rcservo_getPosition(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setReverse(self, reverse):

        """ 
        Set the output to be reversed on the servo channel

        :param reverse: Reverses the value set by "setPosition". ie. if the position is set to 64 (1ms pulse) the output will now be 192 (2ms pulse); however, "getPostion" will return the set value of 64. 0 = not reversed, 1 = reversed.
        :type reverse: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rcservo_setReverse(self._module._id_pointer, result, self._index, reverse)
        return result.error

    def getReverse(self):

        """ 
        Get the reverse status of the servo channel
        The current reverse status of the servo entity. 0 = not
        reversed, 1 = reversed.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rcservo_getReverse(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

