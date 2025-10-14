# This file was auto-generated. Do not modify.

from ._bs_c_cffi import ffi
from . import _BS_C #imported from __init__
from .Entity_Entity import *
from .result import Result
from .ffi_utils import data_to_bytearray, bytes_to_string, handle_sign

class I2C(Entity):
    
    """ 
        I2CClass:
        Interface the I2C buses on BrainStem modules.
        The class provides a way to send read and write commands to I2C devices
        on the entities bus.

    """ 

    I2C_DEFAULT_SPEED = 0
    I2C_SPEED_100Khz = 1
    I2C_SPEED_400Khz = 2
    I2C_SPEED_1000Khz = 3

    def __init__(self, module, index):
        super(I2C, self).__init__(module, _BS_C.cmdI2C, index)

    def read(self, address, readLength):

        """ 
        Read from a device on this I2C bus.

        :param address: - The I2C address (7bit <XXXX-XXX0>) of the device to read.
        :type address: const int
        :param readLength: - The length of the data to read in bytes.
        :type readLength: const int

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")

        ffi_buffer = ffi.new("unsigned char[]", 256)
        
        _BS_C.i2c_read(self._module._id_pointer, result, self._index, address, readLength, ffi_buffer)
        return_list = [ffi_buffer[i] for i in range(result.value)]

        return_result = Result(result.error, tuple(return_list) if result.error == Result.NO_ERROR else None)

        return return_result

    def write(self, address, buffer):

        """ 
        Write to a device on this I2C bus.

        :param address: - The I2C address (7bit <XXXX-XXX0>) of the device to write.
        :type address: const int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        byte_array = data_to_bytearray(buffer)

        buffer_length = len(byte_array)
        ffi_buffer = ffi.new("unsigned char[]", buffer_length)
        for x in range(buffer_length):
            ffi_buffer[x] = byte_array[x]

        _BS_C.i2c_write(self._module._id_pointer, result, self._index, address, buffer_length, ffi_buffer)
        return result.error

    def setPullup(self, bEnable):

        """ 
        Set bus pull-up state.
        This call only works with stems that have software controlled pull-ups.
        Check the datasheet for more information. This parameter is saved when
        system.save is called.

        :param bEnable: - true enables pull-ups false disables them.
        :type bEnable: const bool

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.i2c_setPullup(self._module._id_pointer, result, self._index, bEnable)
        return result.error

    def setSpeed(self, speed):

        """ 
        Set I2C bus speed.
        This call sets the communication speed for I2C transactions through
        this API. Speed is an enumeration value which can take the following
        values.
        1 - 100Khz
        2 - 400Khz
        3 - 1MHz

        :param speed: - The speed setting value.
        :type speed: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.i2c_setSpeed(self._module._id_pointer, result, self._index, speed)
        return result.error

    def getSpeed(self):

        """ 
        Get I2C bus speed.
        This call gets the communication speed for I2C transactions through
        this API. Speed is an enumeration value which can take the following
        values.
        1 - 100Khz
        2 - 400Khz
        3 - 1MHz
        - The speed setting value.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.i2c_getSpeed(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

