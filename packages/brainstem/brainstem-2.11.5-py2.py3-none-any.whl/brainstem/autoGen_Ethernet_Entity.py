# This file was auto-generated. Do not modify.

from ._bs_c_cffi import ffi
from . import _BS_C #imported from __init__
from .Entity_Entity import *
from .result import Result
from .ffi_utils import data_to_bytearray, bytes_to_string, handle_sign

class Ethernet(Entity):
    
    """ 
        EthernetClass:
        IP configuration.  MAC info.  BrainD port.

    """ 


    def __init__(self, module, index):
        super(Ethernet, self).__init__(module, _BS_C.cmdETHERNET, index)

    def setEnabled(self, enabled):

        """ 
        Sets the Ethernet's interface to enabled/disabled.

        :param enabled: 1 = enabled; 0 = disabled
        :type enabled: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.ethernet_setEnabled(self._module._id_pointer, result, self._index, enabled)
        return result.error

    def getEnabled(self):

        """ 
        Gets the current enable value of the Ethernet interface.
        1 = Fully enabled network connectivity; 0 = Ethernet MAC is disabled.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.ethernet_getEnabled(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def getNetworkConfiguration(self):

        """ 
        Get the method in which IP Address is assigned to this device
        Method used.  Current methods
        - NONE = 0
        - STATIC = 1
        - DHCP = 2

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.ethernet_getNetworkConfiguration(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setNetworkConfiguration(self, addressStyle):

        """ 
        Get the method in which IP Address is assigned to this device

        :param addressStyle: Method to use. See getNetworkConfiguration for addressStyle enumerations.
        :type addressStyle: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.ethernet_setNetworkConfiguration(self._module._id_pointer, result, self._index, addressStyle)
        return result.error

    def getStaticIPv4Address(self, buffer_length=65536):

        """ 
        Get the expected IPv4 address of this device, when networkConfiguration == STATIC
        occupied bytes in buffer, Should be 4 post-call.
        The functional IPv4 address of The Module will differ
        if NetworkConfiguration != STATIC.

        :param buffer_length: size of buffer. Should be 4.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")

        ffi_buffer = ffi.new("unsigned char[]", buffer_length)
        
        _BS_C.ethernet_getStaticIPv4Address(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return_list = [ffi_buffer[i] for i in range(result.value)]

        return_result = Result(result.error, tuple(return_list) if result.error == Result.NO_ERROR else None)

        return return_result

    def setStaticIPv4Address(self, buffer):

        """ 
        Set the desired IPv4 address of this device, if NetworkConfiguration == STATIC
        setStaticIPv4Address(192, 168, 10, 2) would equate with address "192.168.10.2"

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        byte_array = data_to_bytearray(buffer)

        buffer_length = len(byte_array)
        ffi_buffer = ffi.new("unsigned char[]", buffer_length)
        for x in range(buffer_length):
            ffi_buffer[x] = byte_array[x]

        _BS_C.ethernet_setStaticIPv4Address(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return result.error

    def getStaticIPv4Netmask(self, buffer_length=65536):

        """ 
        Get the expected IPv4 netmask of this device, when networkConfiguration == STATIC
        occupied bytes in buffer, Should be 4 post-call.
        The functional IPv4 netmask of The Module will differ
        if NetworkConfiguration != STATIC.

        :param buffer_length: size of buffer. Should be 4.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")

        ffi_buffer = ffi.new("unsigned char[]", buffer_length)
        
        _BS_C.ethernet_getStaticIPv4Netmask(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return_list = [ffi_buffer[i] for i in range(result.value)]

        return_result = Result(result.error, tuple(return_list) if result.error == Result.NO_ERROR else None)

        return return_result

    def setStaticIPv4Netmask(self, buffer):

        """ 
        Set the desired IPv4 address of this device, if NetworkConfiguration == STATIC
        setStaticIPv4Netmask([255, 255, 192, 0], 4) would equate
        with address "255.255.192.0", or /18 in CIDR notation.

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        byte_array = data_to_bytearray(buffer)

        buffer_length = len(byte_array)
        ffi_buffer = ffi.new("unsigned char[]", buffer_length)
        for x in range(buffer_length):
            ffi_buffer[x] = byte_array[x]

        _BS_C.ethernet_setStaticIPv4Netmask(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return result.error

    def getStaticIPv4Gateway(self, buffer_length=65536):

        """ 
        Set the desired IPv4 gateway of this device, if NetworkConfiguration == STATIC
        occupied bytes in buffer, Should be 4 post-call.

        :param buffer_length: size of buffer. Should be 4.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")

        ffi_buffer = ffi.new("unsigned char[]", buffer_length)
        
        _BS_C.ethernet_getStaticIPv4Gateway(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return_list = [ffi_buffer[i] for i in range(result.value)]

        return_result = Result(result.error, tuple(return_list) if result.error == Result.NO_ERROR else None)

        return return_result

    def setStaticIPv4Gateway(self, buffer):

        """ 
        Set the desired IPv4 gateway of this device, if NetworkConfiguration == STATIC
        setStaticIPv4Gateway([192, 168, 1, 1], 4) would equate
        with address "192.168.1.1"

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        byte_array = data_to_bytearray(buffer)

        buffer_length = len(byte_array)
        ffi_buffer = ffi.new("unsigned char[]", buffer_length)
        for x in range(buffer_length):
            ffi_buffer[x] = byte_array[x]

        _BS_C.ethernet_setStaticIPv4Gateway(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return result.error

    def getIPv4Address(self, buffer_length=65536):

        """ 
        \brief Get the effective IP address of this device.
        occupied bytes in buffer, Should be 4 post-call.

        :param buffer_length: size of buffer. Should be 4.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")

        ffi_buffer = ffi.new("unsigned char[]", buffer_length)
        
        _BS_C.ethernet_getIPv4Address(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return_list = [ffi_buffer[i] for i in range(result.value)]

        return_result = Result(result.error, tuple(return_list) if result.error == Result.NO_ERROR else None)

        return return_result

    def getIPv4Netmask(self, buffer_length=65536):

        """ 
        \brief Get the effective IP netmask of this device.
        occupied bytes in buffer, Should be 4 post-call.

        :param buffer_length: size of buffer. Should be 4.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")

        ffi_buffer = ffi.new("unsigned char[]", buffer_length)
        
        _BS_C.ethernet_getIPv4Netmask(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return_list = [ffi_buffer[i] for i in range(result.value)]

        return_result = Result(result.error, tuple(return_list) if result.error == Result.NO_ERROR else None)

        return return_result

    def getIPv4Gateway(self, buffer_length=65536):

        """ 
        \brief Get the effective IP gateway of this device.
        occupied bytes in buffer, Should be 4 post-call.

        :param buffer_length: size of buffer. Should be 4.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")

        ffi_buffer = ffi.new("unsigned char[]", buffer_length)
        
        _BS_C.ethernet_getIPv4Gateway(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return_list = [ffi_buffer[i] for i in range(result.value)]

        return_result = Result(result.error, tuple(return_list) if result.error == Result.NO_ERROR else None)

        return return_result

    def setStaticIPv4DNSAddress(self, buffer):

        """ 
        \brief Set IPv4 DNS Addresses (plural), if NetworkConfiguration == STATIC

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        byte_array = data_to_bytearray(buffer)

        buffer_length = len(byte_array)
        ffi_buffer = ffi.new("unsigned char[]", buffer_length)
        for x in range(buffer_length):
            ffi_buffer[x] = byte_array[x]

        _BS_C.ethernet_setStaticIPv4DNSAddress(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return result.error

    def getStaticIPv4DNSAddress(self, buffer_length=65536):

        """ 
        \brief Get IPv4 DNS addresses (plural), when NetworkConfiguration == STATIC
        Length of occupied bytes of buffer, after the call.

        :param buffer_length: Maximum length of array, in bytes.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")

        ffi_buffer = ffi.new("unsigned char[]", buffer_length)
        
        _BS_C.ethernet_getStaticIPv4DNSAddress(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return_list = [ffi_buffer[i] for i in range(result.value)]

        return_result = Result(result.error, tuple(return_list) if result.error == Result.NO_ERROR else None)

        return return_result

    def getIPv4DNSAddress(self, buffer_length=65536):

        """ 
        \brief Get effective IPv4 DNS addresses, for the current NetworkConfiguration
        Length of occupied bytes of buffer, after the call.

        :param buffer_length: Maximum length of array, in bytes.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")

        ffi_buffer = ffi.new("unsigned char[]", buffer_length)
        
        _BS_C.ethernet_getIPv4DNSAddress(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return_list = [ffi_buffer[i] for i in range(result.value)]

        return_result = Result(result.error, tuple(return_list) if result.error == Result.NO_ERROR else None)

        return return_result

    def setHostname(self, buffer):

        """ 
        \brief Set hostname that's requested when this device sends a DHCP request.

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        byte_array = data_to_bytearray(buffer)

        buffer_length = len(byte_array)
        ffi_buffer = ffi.new("unsigned char[]", buffer_length)
        for x in range(buffer_length):
            ffi_buffer[x] = byte_array[x]

        _BS_C.ethernet_setHostname(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return result.error

    def getHostname(self, buffer_length=65536):

        """ 
        \brief Get hostname that's requested when this device sends a DHCP request.
        Length of occupied bytes of buffer, after the call.

        :param buffer_length: N, for N bytes.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")

        ffi_buffer = ffi.new("unsigned char[]", buffer_length)
        
        _BS_C.ethernet_getHostname(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return_list = [ffi_buffer[i] for i in range(result.value)]

        return_result = Result(result.error, tuple(return_list) if result.error == Result.NO_ERROR else None)

        return return_result

    def getMACAddress(self, buffer_length=65536):

        """ 
        \brief Get hostname that's requested when this device sends a DHCP request.
        Length of occupied bytes of buffer, after the call.

        :param buffer_length: length of buffer that's writeable, should be > 6.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")

        ffi_buffer = ffi.new("unsigned char[]", buffer_length)
        
        _BS_C.ethernet_getMACAddress(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return_list = [ffi_buffer[i] for i in range(result.value)]

        return_result = Result(result.error, tuple(return_list) if result.error == Result.NO_ERROR else None)

        return return_result

    def setBraindPort(self, port):

        """ 
        \brief Set the port of the BrainD HTTP server.

        :param port: The port to be used for the BrainD server.
        :type port: const unsigned short

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.ethernet_setBraindPort(self._module._id_pointer, result, self._index, port)
        return result.error

    def getBraindPort(self):

        """ 
        \brief Get the port (desired) of the BrainD HTTP server.
        The port of the BrainD server.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.ethernet_getBraindPort(self._module._id_pointer, result, self._index)
        return handle_sign(result, 16, False)

