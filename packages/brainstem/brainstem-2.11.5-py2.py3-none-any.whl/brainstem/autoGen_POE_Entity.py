# This file was auto-generated. Do not modify.

from ._bs_c_cffi import ffi
from . import _BS_C #imported from __init__
from .Entity_Entity import *
from .result import Result
from .ffi_utils import data_to_bytearray, bytes_to_string, handle_sign

class POE(Entity):
    
    """ 
        /
        Congratulations! You found an Easter egg!
        Unfortunately, this code is still under construction and should not be used.
        /
        POEClass:
        This entity is only available on certain modules, and provides a
        Power Over Ethernet control ability.

    """ 


    def __init__(self, module, index):
        super(POE, self).__init__(module, _BS_C.cmdPOE, index)

    def getPowerMode(self):

        """ 
        Gets the power mode of the device
        The power mode (PD, PSE, Auto, Off).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.poe_getPowerMode(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setPowerMode(self, value):

        """ 
        Sets the power mode of the device

        :param value: The power mode (PD, PSE, Auto, Off).
        :type value: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.poe_setPowerMode(self._module._id_pointer, result, self._index, value)
        return result.error

    def getPowerState(self):

        """ 
        Gets the power state of the device
        The power state (PD, PSE, Off).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.poe_getPowerState(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def getPair12SourcingClass(self):

        """ 
        Gets the sourcing class on Pair 1/2 of the device
        The POE class being offered by the device (PSE).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.poe_getPair12SourcingClass(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setPair12SourcingClass(self, value):

        """ 
        Sets the sourcing class on Pair 1/2 of the device

        :param value: The POE class being offered by the device (PSE).
        :type value: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.poe_setPair12SourcingClass(self._module._id_pointer, result, self._index, value)
        return result.error

    def getPair34SourcingClass(self):

        """ 
        Gets the sourcing class on Pair 3/4 of the device
        The POE class being offered by the device (PSE).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.poe_getPair34SourcingClass(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setPair34SourcingClass(self, value):

        """ 
        Sets the sourcing class on Pair 3/4 of the device

        :param value: The POE class being offered by the device (PSE).
        :type value: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.poe_setPair34SourcingClass(self._module._id_pointer, result, self._index, value)
        return result.error

    def getPair12RequestedClass(self):

        """ 
        Gets the requested class on Pair 1/2 of the device
        The requested POE class by the device (PD).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.poe_getPair12RequestedClass(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def getPair34RequestedClass(self):

        """ 
        Gets the requested class on Pair 3/4 of the device
        The requested POE class by the device (PD).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.poe_getPair34RequestedClass(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def getPair12DiscoveredClass(self):

        """ 
        Gets the discovered class on Pair 1/2 of the device
        The negotiated POE class by the device (PSE/PD).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.poe_getPair12DiscoveredClass(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def getPair34DiscoveredClass(self):

        """ 
        Gets the discovered class on Pair 3/4 of the device
        The negotiated POE class by the device (PSE/PD).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.poe_getPair34DiscoveredClass(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def getPair12DetectionStatus(self):

        """ 
        Gets detected status of the POE connection on Pair 1/2
        The current detected status of the pairs.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.poe_getPair12DetectionStatus(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def getPair34DetectionStatus(self):

        """ 
        Gets detected status of the POE connection on Pair 3/4
        The current detected status of the pairs.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.poe_getPair34DetectionStatus(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def getPair12Voltage(self):

        """ 
        Gets the Voltage on Pair 1/2
        The voltage in microvolts (1 == 1e-6V).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.poe_getPair12Voltage(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def getPair34Voltage(self):

        """ 
        Gets the Voltage on Pair 3/4
        The voltage in microvolts (1 == 1e-6V).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.poe_getPair34Voltage(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def getPair12Current(self):

        """ 
        Gets the Voltage on Pair 1/2
        The current in microamps (1 == 1e-6V).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.poe_getPair12Current(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def getPair34Current(self):

        """ 
        Gets the Voltage on Pair 3/4
        The current in microamps (1 == 1e-6V).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.poe_getPair34Current(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def getPair12Resistance(self):

        """ 
        Gets the Voltage on Pair 1/2
        The resistance in milliohms (1 == 1e-3V).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.poe_getPair12Resistance(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def getPair34Resistance(self):

        """ 
        Gets the Voltage on Pair 3/4
        The resistance in milliohms (1 == 1e-3V).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.poe_getPair34Resistance(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def getPair12Capacitance(self):

        """ 
        Gets the Voltage on Pair 1/2
        The capacitance in nanocoulombs (1 == 1e-9V).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.poe_getPair12Capacitance(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def getPair34Capacitance(self):

        """ 
        Gets the Voltage on Pair 3/4
        The capacitance in nanocoulombs (1 == 1e-9V).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.poe_getPair34Capacitance(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def resetEntityToFactoryDefaults(self):

        """ 
        Resets the POEClass Entity to it factory default configuration.

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.poe_resetEntityToFactoryDefaults(self._module._id_pointer, result, self._index)
        return result.error

