# This file was auto-generated. Do not modify.

from ._bs_c_cffi import ffi
from . import _BS_C #imported from __init__
from .Entity_Entity import *
from .result import Result
from .ffi_utils import data_to_bytearray, bytes_to_string, handle_sign

class USBSystem(Entity):
    
    """ 
        USBSystem Class:
        The USBSystem class provides high level control of the lower level Port Class.

    """ 


    def __init__(self, module, index):
        super(USBSystem, self).__init__(module, _BS_C.cmdUSBSYSTEM, index)

    def getUpstream(self):

        """ 
        Gets the upstream port.
        The current upstream port.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.usbsystem_getUpstream(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setUpstream(self, port):

        """ 
        Sets the upstream port.

        :param port: The upstream port to set.
        :type port: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.usbsystem_setUpstream(self._module._id_pointer, result, self._index, port)
        return result.error

    def getEnumerationDelay(self):

        """ 
        Gets the inter-port enumeration delay in milliseconds.
        Delay is applied upon hub enumeration.
        the current inter-port delay in milliseconds.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.usbsystem_getEnumerationDelay(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def setEnumerationDelay(self, msDelay):

        """ 
        Sets the inter-port enumeration delay in milliseconds.
        Delay is applied upon hub enumeration.

        :param msDelay: The delay in milliseconds to be applied between port enables
        :type msDelay: const unsigned int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.usbsystem_setEnumerationDelay(self._module._id_pointer, result, self._index, msDelay)
        return result.error

    def getDataRoleList(self):

        """ 
        Gets the data role of all ports with a single call
        Equivalent to calling PortClass::getDataRole() on each individual port.
        A bit packed representation of the data role for all ports.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.usbsystem_getDataRoleList(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def getEnabledList(self):

        """ 
        Gets the current enabled status of all ports with a single call.
        Equivalent to calling PortClass::setEnabled() on each port.
        Bit packed representation of the enabled status for all ports.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.usbsystem_getEnabledList(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def setEnabledList(self, enabledList):

        """ 
        Sets the enabled status of all ports with a single call.
        Equivalent to calling PortClass::setEnabled() on each port.

        :param enabledList: Bit packed representation of the enabled status for all ports to be applied.
        :type enabledList: const unsigned int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.usbsystem_setEnabledList(self._module._id_pointer, result, self._index, enabledList)
        return result.error

    def getModeList(self, buffer_length=65536):

        """ 
        Gets the current mode of all ports with a single call.
        Equivalent to calling PortClass:getMode() on each port.
        Length that was actually received and filled.

        :param buffer_length: Length of the buffer to be filed

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        ffi_buffer = ffi.new("unsigned int[]", buffer_length)
        _BS_C.usbsystem_getModeList(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return_list = [ffi_buffer[i] for i in range(result.value)]
        return Result(result.error, tuple(return_list) if result.error == Result.NO_ERROR else None)
        
    def setModeList(self, buffer):

        """ 
        Sets the mode of all ports with a single call.
        Equivalent to calling PortClass::setMode() on each port

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        byte_array = data_to_bytearray(buffer)

        buffer_length = len(byte_array)
        ffi_buffer = ffi.new("unsigned int[]", buffer_length)
        for x in range(buffer_length):
            ffi_buffer[x] = byte_array[x]

        _BS_C.usbsystem_setModeList(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return result.error

    def getStateList(self, buffer_length=65536):

        """ 
        Gets the state for all ports with a single call.
        Equivalent to calling PortClass::getState() on each port.
        Length that was actually received and filled.

        :param buffer_length: Length of the buffer to be filed

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        ffi_buffer = ffi.new("unsigned int[]", buffer_length)
        _BS_C.usbsystem_getStateList(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return_list = [ffi_buffer[i] for i in range(result.value)]
        return Result(result.error, tuple(return_list) if result.error == Result.NO_ERROR else None)
        
    def getPowerBehavior(self):

        """ 
        Gets the behavior of the power manager.
        The power manager is responsible for budgeting the power of the system.
        i.e. What happens when requested power greater than available power.
        Variable to be filled with an enumerated representation of behavior.
        Available behaviors are product specific. See the reference documentation.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.usbsystem_getPowerBehavior(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setPowerBehavior(self, behavior):

        """ 
        Sets the behavior of how available power is managed.
        i.e. What happens when requested power is greater than available power.

        :param behavior: An enumerated representation of behavior. Available behaviors are product specific. See the reference documentation.
        :type behavior: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.usbsystem_setPowerBehavior(self._module._id_pointer, result, self._index, behavior)
        return result.error

    def getPowerBehaviorConfig(self, buffer_length=65536):

        """ 
        Gets the current power behavior configuration
        Certain power behaviors use a list of ports to determine priority when budgeting power.
        Length that was actually received and filled.

        :param buffer_length: Length of the buffer to be filed

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        ffi_buffer = ffi.new("unsigned int[]", buffer_length)
        _BS_C.usbsystem_getPowerBehaviorConfig(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return_list = [ffi_buffer[i] for i in range(result.value)]
        return Result(result.error, tuple(return_list) if result.error == Result.NO_ERROR else None)
        
    def setPowerBehaviorConfig(self, buffer):

        """ 
        Sets the current power behavior configuration
        Certain power behaviors use a list of ports to determine priority when budgeting power.

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        byte_array = data_to_bytearray(buffer)

        buffer_length = len(byte_array)
        ffi_buffer = ffi.new("unsigned int[]", buffer_length)
        for x in range(buffer_length):
            ffi_buffer[x] = byte_array[x]

        _BS_C.usbsystem_setPowerBehaviorConfig(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return result.error

    def getDataRoleBehavior(self):

        """ 
        Gets the behavior of how upstream and downstream ports are determined.
        i.e. How do you manage requests for data role swaps and new upstream connections.
        Variable to be filled with an enumerated representation of behavior.
        Available behaviors are product specific. See the reference documentation.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.usbsystem_getDataRoleBehavior(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setDataRoleBehavior(self, behavior):

        """ 
        Sets the behavior of how upstream and downstream ports are determined.
        i.e. How do you manage requests for data role swaps and new upstream connections.

        :param behavior: An enumerated representation of behavior. Available behaviors are product specific. See the reference documentation.
        :type behavior: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.usbsystem_setDataRoleBehavior(self._module._id_pointer, result, self._index, behavior)
        return result.error

    def getDataRoleBehaviorConfig(self, buffer_length=65536):

        """ 
        Gets the current data role behavior configuration
        Certain data role behaviors use a list of ports to determine priority host priority.
        Length that was actually received and filled.

        :param buffer_length: Length of the buffer to be filed

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        ffi_buffer = ffi.new("unsigned int[]", buffer_length)
        _BS_C.usbsystem_getDataRoleBehaviorConfig(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return_list = [ffi_buffer[i] for i in range(result.value)]
        return Result(result.error, tuple(return_list) if result.error == Result.NO_ERROR else None)
        
    def setDataRoleBehaviorConfig(self, buffer):

        """ 
        Sets the current data role behavior configuration
        Certain data role behaviors use a list of ports to determine host priority.

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        byte_array = data_to_bytearray(buffer)

        buffer_length = len(byte_array)
        ffi_buffer = ffi.new("unsigned int[]", buffer_length)
        for x in range(buffer_length):
            ffi_buffer[x] = byte_array[x]

        _BS_C.usbsystem_setDataRoleBehaviorConfig(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return result.error

    def getSelectorMode(self):

        """ 
        Gets the current mode of the selector input.
        This mode determines what happens and in what order when the external
        selector input is used.
        Variable to be filled with the selector mode

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.usbsystem_getSelectorMode(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setSelectorMode(self, mode):

        """ 
        Sets the current mode of the selector input.
        This mode determines what happens and in what order when the external
        selector input is used.

        :param mode: Mode to be set.
        :type mode: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.usbsystem_setSelectorMode(self._module._id_pointer, result, self._index, mode)
        return result.error

    def resetEntityToFactoryDefaults(self):

        """ 
        Resets the USBSystemClass Entity to it factory default configuration.

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.usbsystem_resetEntityToFactoryDefaults(self._module._id_pointer, result, self._index)
        return result.error

    def getUpstreamHS(self):

        """ 
        Gets the USB HighSpeed upstream port.
        The current upstream port.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.usbsystem_getUpstreamHS(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setUpstreamHS(self, port):

        """ 
        Sets the USB HighSpeed upstream port.

        :param port: The upstream port to set.
        :type port: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.usbsystem_setUpstreamHS(self._module._id_pointer, result, self._index, port)
        return result.error

    def getUpstreamSS(self):

        """ 
        Gets the USB SuperSpeed upstream port.
        The current upstream port.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.usbsystem_getUpstreamSS(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setUpstreamSS(self, port):

        """ 
        Sets the USB SuperSpeed upstream port.

        :param port: The upstream port to set.
        :type port: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.usbsystem_setUpstreamSS(self._module._id_pointer, result, self._index, port)
        return result.error

    def getOverride(self):

        """ 
        Gets the current enabled overrides
        Bit mapped representation of the current override configuration.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.usbsystem_getOverride(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def setOverride(self, overrides):

        """ 
        Sets the current enabled overrides

        :param overrides: Overrides to be set in a bit mapped representation.
        :type overrides: const unsigned int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.usbsystem_setOverride(self._module._id_pointer, result, self._index, overrides)
        return result.error

    def setDataHSMaxDatarate(self, datarate):

        """ 
        Sets the USB HighSpeed Max datarate

        :param datarate: Maximum datarate for the USB HighSpeed signals.
        :type datarate: const unsigned int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.usbsystem_setDataHSMaxDatarate(self._module._id_pointer, result, self._index, datarate)
        return result.error

    def getDataHSMaxDatarate(self):

        """ 
        Gets the USB HighSpeed Max datarate
        Current maximum datarate for the USB HighSpeed signals.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.usbsystem_getDataHSMaxDatarate(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def setDataSSMaxDatarate(self, datarate):

        """ 
        Sets the USB SuperSpeed Max datarate

        :param datarate: Maximum datarate for the USB SuperSpeed signals.
        :type datarate: const unsigned int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.usbsystem_setDataSSMaxDatarate(self._module._id_pointer, result, self._index, datarate)
        return result.error

    def getDataSSMaxDatarate(self):

        """ 
        Gets the USB SuperSpeed Max datarate
        Current maximum datarate for the USB SuperSpeed signals.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.usbsystem_getDataSSMaxDatarate(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

