# This file was auto-generated. Do not modify.

from ._bs_c_cffi import ffi
from . import _BS_C #imported from __init__
from .Entity_Entity import *
from .result import Result
from .ffi_utils import data_to_bytearray, bytes_to_string, handle_sign

class Port(Entity):
    
    """ 
        Port Class:
        The Port Entity provides software control over the most basic items related to a
        USB Port. This includes everything from the complete enable and disable of the
        entire port to the individual control of specific pins. Voltage and Current
        measurements are also included for devices which support the Port Entity.

    """ 


    def __init__(self, module, index):
        super(Port, self).__init__(module, _BS_C.cmdPORT, index)

    def getVbusVoltage(self):

        """ 
        Gets the Vbus Voltage
        The voltage in microvolts (1 == 1e-6V) currently present on Vbus.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getVbusVoltage(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def getVbusCurrent(self):

        """ 
        Gets the Vbus Current
        The current in microamps (1 == 1e-6A) currently present on Vbus.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getVbusCurrent(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def getVconnVoltage(self):

        """ 
        Gets the Vconn Voltage
        The voltage in microvolts (1 == 1e-6V) currently present on Vconn.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getVconnVoltage(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def getVconnCurrent(self):

        """ 
        Gets the Vconn Current
        The current in microamps (1 == 1e-6A) currently present on Vconn.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getVconnCurrent(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def getPowerMode(self):

        """ 
        Gets the Port Power Mode: Convenience Function of get/setPortMode
        The current power mode.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getPowerMode(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setPowerMode(self, powerMode):

        """ 
        Sets the Port Power Mode: Convenience Function of get/setPortMode

        :param powerMode: The power mode to be set.
        :type powerMode: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_setPowerMode(self._module._id_pointer, result, self._index, powerMode)
        return result.error

    def getEnabled(self):

        """ 
        Gets the current enable value of the port.
        1 = Fully enabled port; 0 = One or more disabled components.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getEnabled(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setEnabled(self, enable):

        """ 
        Enables or disables the entire port.

        :param enable: 1 = Fully enable port; 0 = Fully disable port.
        :type enable: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_setEnabled(self._module._id_pointer, result, self._index, enable)
        return result.error

    def getDataEnabled(self):

        """ 
        Gets the current enable value of the data lines.: Sub-component (Data) of getEnabled.
        1 = Data enabled; 0 = Data disabled.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getDataEnabled(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setDataEnabled(self, enable):

        """ 
        Enables or disables the data lines. Sub-component (Data) of setEnabled.

        :param enable: 1 = Enable data; 0 = Disable data.
        :type enable: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_setDataEnabled(self._module._id_pointer, result, self._index, enable)
        return result.error

    def getDataHSEnabled(self):

        """ 
        Gets the current enable value of the High Speed (HS) data lines.
        Sub-component of getDataEnabled.
        1 = Data enabled; 0 = Data disabled.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getDataHSEnabled(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setDataHSEnabled(self, enable):

        """ 
        Enables or disables the High Speed (HS) data lines.
        Sub-component of setDataEnabled.

        :param enable: 1 = Enable data; 0 = Disable data.
        :type enable: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_setDataHSEnabled(self._module._id_pointer, result, self._index, enable)
        return result.error

    def getDataHS1Enabled(self):

        """ 
        Gets the current enable value of the High Speed A side (HSA) data lines.:
        Sub-component of getDataHSEnabled.
        1 = Data enabled; 0 = Data disabled.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getDataHS1Enabled(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setDataHS1Enabled(self, enable):

        """ 
        Enables or disables the Hight Speed A side (HSA) data lines.
        Sub-component of setDataHSEnabled.

        :param enable: 1 = Enable data; 0 = Disable data.
        :type enable: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_setDataHS1Enabled(self._module._id_pointer, result, self._index, enable)
        return result.error

    def getDataHS2Enabled(self):

        """ 
        Gets the current enable value of the High Speed B side (HSB) data lines.:
        Sub-component of getDataHSEnabled.
        1 = Data enabled; 0 = Data disabled.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getDataHS2Enabled(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setDataHS2Enabled(self, enable):

        """ 
        Enables or disables the Hight Speed B side (HSB) data lines.
        Sub-component of setDataHSEnabled.

        :param enable: 1 = Enable data; 0 = Disable data.
        :type enable: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_setDataHS2Enabled(self._module._id_pointer, result, self._index, enable)
        return result.error

    def getDataSSEnabled(self):

        """ 
        Gets the current enable value of the Super Speed (SS) data lines.
        Sub-component of getDataEnabled.
        1 = Data enabled; 0 = Data disabled.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getDataSSEnabled(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setDataSSEnabled(self, enable):

        """ 
        Enables or disables the Super Speed (SS) data lines.
        Sub-component of setDataEnabled.

        :param enable: 1 = Enable data; 0 = Disable data.
        :type enable: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_setDataSSEnabled(self._module._id_pointer, result, self._index, enable)
        return result.error

    def getDataSS1Enabled(self):

        """ 
        Gets the current enable value of the Super Speed A side (SSA) data lines.:
        Sub-component of getDataSSEnabled.
        1 = Data enabled; 0 = Data disabled.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getDataSS1Enabled(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setDataSS1Enabled(self, enable):

        """ 
        Enables or disables the Super Speed (SS) data lines.
        Sub-component of setDataEnabled.

        :param enable: 1 = Enable data; 0 = Disable data.
        :type enable: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_setDataSS1Enabled(self._module._id_pointer, result, self._index, enable)
        return result.error

    def getDataSS2Enabled(self):

        """ 
        Gets the current enable value of the Super Speed B side (SSB) data lines.:
        Sub-component of getDataSSEnabled.
        1 = Data enabled; 0 = Data disabled.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getDataSS2Enabled(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setDataSS2Enabled(self, enable):

        """ 
        Enables or disables the Super Speed B side (SSB) data lines.
        Sub-component of setDataSSEnabled.

        :param enable: 1 = Enable data; 0 = Disable data.
        :type enable: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_setDataSS2Enabled(self._module._id_pointer, result, self._index, enable)
        return result.error

    def getPowerEnabled(self):

        """ 
        Gets the current enable value of the power lines.: Sub-component (Power) of getEnabled.
        1 = Power enabled; 0 = Power disabled.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getPowerEnabled(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setPowerEnabled(self, enable):

        """ 
        Enables or Disables the power lines. Sub-component (Power) of setEnable.

        :param enable: 1 = Enable power; 0 = Disable disable.
        :type enable: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_setPowerEnabled(self._module._id_pointer, result, self._index, enable)
        return result.error

    def getDataRole(self):

        """ 
        Gets the Port Data Role.
        The data role to be set. See datasheet for details.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getDataRole(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def getVconnEnabled(self):

        """ 
        Gets the current enable value of the Vconn lines.: Sub-component (Vconn) of getEnabled.
        1 = Vconn enabled; 0 = Vconn disabled.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getVconnEnabled(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setVconnEnabled(self, enable):

        """ 
        Enables or disables the Vconn lines. Sub-component (Vconn) of setEnabled.

        :param enable: 1 = Enable Vconn lines; 0 = Disable Vconn lines.
        :type enable: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_setVconnEnabled(self._module._id_pointer, result, self._index, enable)
        return result.error

    def getVconn1Enabled(self):

        """ 
        Gets the current enable value of the Vconn1 lines. Sub-component of getVconnEnabled.
        1 = Vconn1 enabled; 0 = Vconn1 disabled.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getVconn1Enabled(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setVconn1Enabled(self, enable):

        """ 
        Enables or disables the Vconn1 lines. Sub-component of setVconnEnabled.

        :param enable: 1 = Enable Vconn1 lines; 0 = Disable Vconn1 lines.
        :type enable: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_setVconn1Enabled(self._module._id_pointer, result, self._index, enable)
        return result.error

    def getVconn2Enabled(self):

        """ 
        Gets the current enable value of the Vconn2 lines. Sub-component of getVconnEnabled.
        1 = Vconn2 enabled; 0 = Vconn2 disabled.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getVconn2Enabled(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setVconn2Enabled(self, enable):

        """ 
        Enables or disables the Vconn2 lines. Sub-component of setVconnEnabled.

        :param enable: 1 = Enable Vconn2 lines; 0 = Disable Vconn2 lines.
        :type enable: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_setVconn2Enabled(self._module._id_pointer, result, self._index, enable)
        return result.error

    def getCCEnabled(self):

        """ 
        Gets the current enable value of the CC lines.: Sub-component (CC) of getEnabled.
        1 = CC enabled; 0 = CC disabled.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getCCEnabled(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setCCEnabled(self, enable):

        """ 
        Enables or disables the CC lines. Sub-component (CC) of setEnabled.

        :param enable: 1 = Enable CC lines; 0 = Disable CC lines.
        :type enable: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_setCCEnabled(self._module._id_pointer, result, self._index, enable)
        return result.error

    def getCC1Enabled(self):

        """ 
        Gets the current enable value of the CC1 lines. Sub-component of getCCEnabled.
        1 = CC1 enabled; 0 = CC1 disabled.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getCC1Enabled(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setCC1Enabled(self, enable):

        """ 
        Enables or disables the CC1 lines. Sub-component of setCCEnabled.

        :param enable: 1 = Enable CC1 lines; 0 = Disable CC1 lines.
        :type enable: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_setCC1Enabled(self._module._id_pointer, result, self._index, enable)
        return result.error

    def getCC2Enabled(self):

        """ 
        Gets the current enable value of the CC2 lines. Sub-component of getCCEnabled.
        1 = CC2 enabled; 0 = CC2 disabled.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getCC2Enabled(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setCC2Enabled(self, enable):

        """ 
        Enables or disables the CC2 lines. Sub-component of setCCEnabled.

        :param enable: 1 = Enable CC2 lines; 0 = Disable CC2 lines.
        :type enable: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_setCC2Enabled(self._module._id_pointer, result, self._index, enable)
        return result.error

    def getVoltageSetpoint(self):

        """ 
        Gets the current voltage setpoint value for the port.
        the voltage setpoint of the port in uV.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getVoltageSetpoint(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def setVoltageSetpoint(self, value):

        """ 
        Sets the current voltage setpoint value for the port.

        :param value: the voltage setpoint of the port in uV.
        :type value: const unsigned int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_setVoltageSetpoint(self._module._id_pointer, result, self._index, value)
        return result.error

    def getState(self):

        """ 
        A bit mapped representation of the current state of the port.
        Reflects what he port IS which may differ from what was requested.
        Variable to be filled with the current state.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getState(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def getDataSpeed(self):

        """ 
        Gets the speed of the enumerated device.
        Bit mapped value representing the devices speed.
        See "Devices" reference for details.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getDataSpeed(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def getMode(self):

        """ 
        Gets current mode of the port
        Bit mapped value representing the ports mode.
        See "Devices" reference for details.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getMode(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def setMode(self, mode):

        """ 
        Sets the mode of the port

        :param mode: Port mode to be set. See "Devices" documentation for details.
        :type mode: const unsigned int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_setMode(self._module._id_pointer, result, self._index, mode)
        return result.error

    def getErrors(self):

        """ 
        Returns any errors that are present on the port.
        Calling this function will clear the current errors. If the error persists it will be set again.
        Bit mapped field representing the current errors of the ports

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getErrors(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def getCurrentLimit(self):

        """ 
        Gets the current limit of the port.
        Variable to be filled with the limit in microAmps (uA).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getCurrentLimit(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def setCurrentLimit(self, limit):

        """ 
        Sets the current limit of the port.

        :param limit: Current limit to be applied in microAmps (uA).
        :type limit: const unsigned int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_setCurrentLimit(self._module._id_pointer, result, self._index, limit)
        return result.error

    def getCurrentLimitMode(self):

        """ 
        Gets the current limit mode.
        The mode determines how the port will react to an over current condition.
        Variable to be filled with an enumerated representation of the current limit mode.
        Available modes are product specific. See the reference documentation.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getCurrentLimitMode(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setCurrentLimitMode(self, mode):

        """ 
        Sets the current limit mode.
        The mode determines how the port will react to an over current condition.

        :param mode: An enumerated representation of the current limit mode. Available modes are product specific. See the reference documentation.
        :type mode: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_setCurrentLimitMode(self._module._id_pointer, result, self._index, mode)
        return result.error

    def getAvailablePower(self):

        """ 
        Gets the current available power.
        This value is determined by the power manager which is responsible for budgeting the
        systems available power envelope.
        Variable to be filled with the available power in milli-watts (mW).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getAvailablePower(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def getAllocatedPower(self):

        """ 
        Gets the currently allocated power
        This value is determined by the power manager which is responsible for budgeting the
        systems available power envelope.
        Variable to be filled with the allocated power in milli-watts (mW).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getAllocatedPower(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def getPowerLimit(self):

        """ 
        Gets the user defined power limit for the port.
        Variable to be filled with the power limit in milli-watts (mW).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getPowerLimit(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def setPowerLimit(self, limit):

        """ 
        Sets a user defined power limit for the port.

        :param limit: Power limit to be applied in milli-watts (mW).
        :type limit: const unsigned int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_setPowerLimit(self._module._id_pointer, result, self._index, limit)
        return result.error

    def getPowerLimitMode(self):

        """ 
        Gets the power limit mode.
        The mode determines how the port will react to an over power condition.
        Variable to be filled with an enumerated representation of the power limit mode.
        Available modes are product specific. See the reference documentation.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getPowerLimitMode(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setPowerLimitMode(self, mode):

        """ 
        Sets the power limit mode.
        The mode determines how the port will react to an over power condition.

        :param mode: An enumerated representation of the power limit mode to be applied Available modes are product specific. See the reference documentation.
        :type mode: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_setPowerLimitMode(self._module._id_pointer, result, self._index, mode)
        return result.error

    def getName(self, buffer_length=65536):

        """ 
        Gets a user defined name of the port.
        Helpful for identifying ports/devices in a static environment.
        Length that was actually received and filled.

        :param buffer_length: Length of the buffer to be filed

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")

        ffi_buffer = ffi.new("unsigned char[]", buffer_length)
        
        _BS_C.port_getName(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return_list = [ffi_buffer[i] for i in range(result.value)]

        return_result = Result(result.error, tuple(return_list) if result.error == Result.NO_ERROR else None)

        return bytes_to_string(return_result)

    def setName(self, buffer):

        """ 
        Sets a user defined name of the port.
        Helpful for identifying ports/devices in a static environment.

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        byte_array = data_to_bytearray(buffer)

        buffer_length = len(byte_array)
        ffi_buffer = ffi.new("unsigned char[]", buffer_length)
        for x in range(buffer_length):
            ffi_buffer[x] = byte_array[x]

        _BS_C.port_setName(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return result.error

    def getCCCurrentLimit(self):

        """ 
        Gets the CC Current Limit Resistance
        The CC Current limit is the value that's set for the pull up resistance
        on the CC lines for basic USB-C negotations.
        Variable to be filled with an enumerated representation of the CC Current limit.
        0 = None, 1 = Default (500/900mA), 2 = 1.5A, and 3 = 3.0A

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getCCCurrentLimit(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setCCCurrentLimit(self, value):

        """ 
        Sets the CC Current Limit Resistance
        The CC Current limit is the value that's set for the pull up resistance
        on the CC lines for basic USB-C negotations.

        :param value: Variable to be filled with an enumerated representation of the CC Current limit. 0 = None, 1 = Default (500/900mA), 2 = 1.5A, and 3 = 3.0A
        :type value: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_setCCCurrentLimit(self._module._id_pointer, result, self._index, value)
        return result.error

    def getDataHSRoutingBehavior(self):

        """ 
        Gets the HighSpeed Data Routing Behavior.
        The mode determines how the port will route the data lines.
        Variable to be filled with an enumerated representation of the routing behavior.
        Available modes are product specific. See the reference documentation.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getDataHSRoutingBehavior(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setDataHSRoutingBehavior(self, mode):

        """ 
        Sets the HighSpeed Data Routing Behavior.
        The mode determines how the port will route the data lines.

        :param mode: An enumerated representation of the routing behavior. Available modes are product specific. See the reference documentation.
        :type mode: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_setDataHSRoutingBehavior(self._module._id_pointer, result, self._index, mode)
        return result.error

    def getDataSSRoutingBehavior(self):

        """ 
        Gets the SuperSpeed Data Routing Behavior.
        The mode determines how the port will route the data lines.
        Variable to be filled with an enumerated representation of the routing behavior.
        Available modes are product specific. See the reference documentation.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getDataSSRoutingBehavior(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setDataSSRoutingBehavior(self, mode):

        """ 
        Sets the SuperSpeed Data Routing Behavior.
        The mode determines how the port will route the data lines.

        :param mode: An enumerated representation of the routing behavior. Available modes are product specific. See the reference documentation.
        :type mode: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_setDataSSRoutingBehavior(self._module._id_pointer, result, self._index, mode)
        return result.error

    def getVbusAccumulatedPower(self):

        """ 
        Gets the Vbus Accumulated Power
        The accumuled power on Vbus in milliwatt-hours.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getVbusAccumulatedPower(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def resetVbusAccumulatedPower(self):

        """ 
        Resets the Vbus Accumulated Power to zero.

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_resetVbusAccumulatedPower(self._module._id_pointer, result, self._index)
        return result.error

    def getVconnAccumulatedPower(self):

        """ 
        Gets the Vconn Accumulated Power
        The accumuled power on Vconn in milliwatt-hours.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getVconnAccumulatedPower(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def resetVconnAccumulatedPower(self):

        """ 
        Resets the Vconn Accumulated Power to zero.

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_resetVconnAccumulatedPower(self._module._id_pointer, result, self._index)
        return result.error

    def setHSBoost(self, boost):

        """ 
        Sets the ports USB 2.0 High Speed Boost Settings
        The setting determines how much additional drive the USB 2.0 signal
        will have in High Speed mode.

        :param boost: An enumerated representation of the boost range. Available value are product specific. See the reference documentation.
        :type boost: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_setHSBoost(self._module._id_pointer, result, self._index, boost)
        return result.error

    def getHSBoost(self):

        """ 
        Gets the ports USB 2.0 High Speed Boost Settings
        The setting determines how much additional drive the USB 2.0 signal
        will have in High Speed mode.
        An enumerated representation of the boost range.
        Available modes are product specific. See the reference documentation.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getHSBoost(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def resetEntityToFactoryDefaults(self):

        """ 
        Resets the PortClass Entity to it factory default configuration.

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_resetEntityToFactoryDefaults(self._module._id_pointer, result, self._index)
        return result.error

    def getCC1State(self):

        """ 
        Gets the current CC1 Strapping on local and remote
        The state is a bit packed value where the upper byte is used to represent
        the remote or partner device attached to the ports resistance and the
        lower byte is used to represent the local or hubs resistance.
        Variable to be filled with an packed enumerated representation of the CC state.
        Enumeration values for each byte are as follows:
        - None = 0 = portCC1State_None
        - Invalid = 1 = portCC1State_Invalid
        - Rp (default) = 2 = portCC1State_RpDefault
        - Rp (1.5A) = 3 = portCC1State_Rp1p5
        - Rp (3A) = 4 = portCC1State_Rp3p0
        - Rd = 5 = portCC1State_Rd
        - Ra = 6 = portCC1State_Ra
        - Managed by controller = 7 = portCC1State_Managed
        - Unknown = 8 = portCC1State_Unknown

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getCC1State(self._module._id_pointer, result, self._index)
        return handle_sign(result, 16, False)

    def getCC2State(self):

        """ 
        Gets the current CC2 Strapping on local and remote
        The state is a bit packed value where the upper byte is used to represent
        the remote or partner device attached to the ports resistance and the
        lower byte is used to represent the local or hubs resistance.
        Variable to be filled with an packed enumerated representation of the CC state.
        Enumeration values for each byte are as follows:
        - None = 0 = portCC2State_None
        - Invalid = 1 = portCC2State_Invalid
        - Rp (default) = 2 = portCC2State_RpDefault
        - Rp (1.5A) = 3 = portCC2State_Rp1p5
        - Rp (3A) = 4 = portCC2State_Rp3p0
        - Rd = 5 = portCC2State_Rd
        - Ra = 6 = portCC2State_Ra
        - Managed by controller = 7 = portCC2State_Managed
        - Unknown = 8 = portCC2State_Unknown

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.port_getCC2State(self._module._id_pointer, result, self._index)
        return handle_sign(result, 16, False)

