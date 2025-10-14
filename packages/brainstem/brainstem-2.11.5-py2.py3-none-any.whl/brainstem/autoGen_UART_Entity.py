# This file was auto-generated. Do not modify.

from ._bs_c_cffi import ffi
from . import _BS_C #imported from __init__
from .Entity_Entity import *
from .result import Result
from .ffi_utils import data_to_bytearray, bytes_to_string, handle_sign

class UART(Entity):
    
    """ 
        UART Class:
        A UART is a "Universal Asynchronous Receiver/Transmitter.  Many times
        referred to as a COM (communication), Serial, or TTY (teletypewriter) port.
        
        The UART Class allows the enabling and disabling of the UART data lines.

    """ 


    def __init__(self, module, index):
        super(UART, self).__init__(module, _BS_C.cmdUART, index)

    def setEnable(self, bEnabled):

        """ 
        Enable the UART channel.

        :param bEnabled: true: enabled, false: disabled.
        :type bEnabled: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.uart_setEnable(self._module._id_pointer, result, self._index, bEnabled)
        return result.error

    def getEnable(self):

        """ 
        Get the enabled state of the uart.
        true: enabled, false: disabled.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.uart_getEnable(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setBaudRate(self, rate):

        """ 
        Set the UART baud rate.

        :param rate: baud rate.
        :type rate: const unsigned int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.uart_setBaudRate(self._module._id_pointer, result, self._index, rate)
        return result.error

    def getBaudRate(self):

        """ 
        Get the UART baud rate.
        Pointer variable to be filled with baud rate.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.uart_getBaudRate(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def setProtocol(self, protocol):

        """ 
        Set the UART protocol.

        :param protocol: An enumeration of serial protocols.
        :type protocol: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.uart_setProtocol(self._module._id_pointer, result, self._index, protocol)
        return result.error

    def getProtocol(self):

        """ 
        Get the UART protocol.
        Pointer to where result is placed.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.uart_getProtocol(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

