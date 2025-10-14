# This file was auto-generated. Do not modify.

from ._bs_c_cffi import ffi
from . import _BS_C #imported from __init__
from .Entity_Entity import *
from .result import Result
from .ffi_utils import data_to_bytearray, bytes_to_string, handle_sign

class Rail(Entity):
    
    """ 
        RailClass:
        Provides power rail functionality on certain modules.
        This entity is only available on certain modules. The RailClass can
        be used to control power to downstream devices. It has the ability to
        take current and voltage measurements, and depending on hardware, may
        have additional modes and capabilities.

    """ 

    KELVIN_SENSING_OFF = 0
    KELVIN_SENSING_ON = 1
    OPERATIONAL_MODE_AUTO            = 0
    OPERATIONAL_MODE_LINEAR          = 1
    OPERATIONAL_MODE_SWITCHER        = 2
    OPERATIONAL_MODE_SWITCHER_LINEAR = 3
    DEFAULT_OPERATIONAL_MODE         = OPERATIONAL_MODE_AUTO
    OPERATIONAL_STATE_INITIALIZING           = 0
    OPERATIONAL_STATE_ENABLED                = 1
    OPERATIONAL_STATE_FAULT                  = 2
    OPERATIONAL_STATE_HARDWARE_CONFIG        = 8
    OPERATIONAL_STATE_LINEAR                 = 0
    OPERATIONAL_STATE_SWITCHER               = 1
    OPERATIONAL_STATE_LINEAR_SWITCHER        = 2
    OPERATIONAL_STATE_OVER_VOLTAGE_FAULT     = 16
    OPERATIONAL_STATE_UNDER_VOLTAGE_FAULT    = 17
    OPERATIONAL_STATE_OVER_CURRENT_FAULT     = 18
    OPERATIONAL_STATE_OVER_POWER_FAULT       = 19
    OPERATIONAL_STATE_REVERSE_POLARITY_FAULT = 20
    OPERATIONAL_STATE_OVER_TEMPERATURE_FAULT = 21
    OPERATIONAL_STATE_OPERATING_MODE         = 24
    OPERATIONAL_STATE_CONSTANT_CURRENT       = 0
    OPERATIONAL_STATE_CONSTANT_VOLTAGE       = 1
    OPERATIONAL_STATE_CONSTANT_POWER         = 2
    OPERATIONAL_STATE_CONSTANT_RESISTANCE    = 3

    def __init__(self, module, index):
        super(Rail, self).__init__(module, _BS_C.cmdRAIL, index)

    def getCurrent(self):

        """ 
        Get the rail current.
        The current in micro-amps (1 == 1e-6A).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_getCurrent(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def setCurrentSetpoint(self, microamps):

        """ 
        Set the rail supply current. Rail current control capabilities vary between modules.
        Refer to the module datasheet for definition of the rail current capabilities.

        :param microamps: The current in micro-amps (1 == 1e-6A) to be supply by the rail.
        :type microamps: const int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_setCurrentSetpoint(self._module._id_pointer, result, self._index, microamps)
        return result.error

    def getCurrentSetpoint(self):

        """ 
        Get the rail setpoint current. Rail current control capabilities vary between modules.
        Refer to the module datasheet for definition of the rail current capabilities.
        The current in micro-amps (1 == 1e-6A) the rail is trying to
        achieve. On some modules this is a measured value so it may not exactly match what was
        previously set via the setCurrent interface. Refer to the module datasheet to
        to determine if this is a measured or stored value.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_getCurrentSetpoint(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def setCurrentLimit(self, microamps):

        """ 
        Set the rail current limit setting. (Check product datasheet to see if this feature is available)

        :param microamps: The current in micro-amps (1 == 1e-6A).
        :type microamps: const int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_setCurrentLimit(self._module._id_pointer, result, self._index, microamps)
        return result.error

    def getCurrentLimit(self):

        """ 
        Get the rail current limit setting. (Check product datasheet to see if this feature is available)
        The current in micro-amps (1 == 1e-6A).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_getCurrentLimit(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def getTemperature(self):

        """ 
        Get the rail temperature.
        The measured temperature associated with the rail in
        micro-Celsius (1 == 1e-6˚C). The temperature may be associated with the module's
        internal rail circuitry or an externally connected temperature sensors. Refer to
        the module datasheet for definition of the temperature measurement location and
        specific capabilities.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_getTemperature(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def getEnable(self):

        """ 
        Get the state of the external rail switch. Not all rails can be switched
        on and off. Refer to the module datasheet for capability specification of the rails.
        true: enabled: connected to the supply rail voltage;
        false: disabled: disconnected from the supply rail voltage

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_getEnable(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setEnable(self, bEnable):

        """ 
        Set the state of the external rail switch. Not all rails can be switched
        on and off. Refer to the module datasheet for capability specification of the rails.

        :param bEnable: true: enable and connect to the supply rail voltage; false: disable and disconnect from the supply rail voltage
        :type bEnable: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_setEnable(self._module._id_pointer, result, self._index, bEnable)
        return result.error

    def getVoltage(self):

        """ 
        Get the rail supply voltage. Rail voltage control capabilities vary between modules.
        Refer to the module datasheet for definition of the rail voltage capabilities.
        The voltage in micro-volts (1 == 1e-6V) currently supplied by
        the rail. On some modules this is a measured value so it may not exactly match what was
        previously set via the setVoltage interface. Refer to the module datasheet to
        to determine if this is a measured or stored value.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_getVoltage(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def setVoltageSetpoint(self, microvolts):

        """ 
        Set the rail supply voltage. Rail voltage control capabilities vary between modules.
        Refer to the module datasheet for definition of the rail voltage capabilities.

        :param microvolts: The voltage in micro-volts (1 == 1e-6V) to be supplied by the rail.
        :type microvolts: const int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_setVoltageSetpoint(self._module._id_pointer, result, self._index, microvolts)
        return result.error

    def getVoltageSetpoint(self):

        """ 
        Get the rail setpoint voltage. Rail voltage control capabilities vary between modules.
        Refer to the module datasheet for definition of the rail voltage capabilities.
        The voltage in micro-volts (1 == 1e-6V) the rail is trying to
        achieve. On some modules this is a measured value so it may not exactly match what was
        previously set via the setVoltage interface. Refer to the module datasheet to
        to determine if this is a measured or stored value.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_getVoltageSetpoint(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def setVoltageMinLimit(self, microvolts):

        """ 
        Set the rail voltage minimum limit setting. (Check product datasheet to see if this feature is available)

        :param microvolts: The voltage in micro-volts (1 == 1e-6V).
        :type microvolts: const int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_setVoltageMinLimit(self._module._id_pointer, result, self._index, microvolts)
        return result.error

    def getVoltageMinLimit(self):

        """ 
        Get the rail voltage minimum limit setting. (Check product datasheet to see if this feature is available)
        The voltage in micro-volts (1 == 1e-6V).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_getVoltageMinLimit(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def setVoltageMaxLimit(self, microvolts):

        """ 
        Set the rail voltage maximum limit setting. (Check product datasheet to see if this feature is available)

        :param microvolts: The voltage in micro-volts (1 == 1e-6V).
        :type microvolts: const int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_setVoltageMaxLimit(self._module._id_pointer, result, self._index, microvolts)
        return result.error

    def getVoltageMaxLimit(self):

        """ 
        Get the rail voltage maximum limit setting. (Check product datasheet to see if this feature is available)
        The voltage in micro-volts (1 == 1e-6V).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_getVoltageMaxLimit(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def getPower(self):

        """ 
        Get the rail supply power. Rail power control capabilities vary between modules.
        Refer to the module datasheet for definition of the rail power capabilities.
        The power in milli-watts (1 == 1e-3W) currently supplied by
        the rail. On some modules this is a measured value so it may not exactly match what was
        previously set via the setPower interface. Refer to the module datasheet to
        to determine if this is a measured or stored value.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_getPower(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def setPowerSetpoint(self, milliwatts):

        """ 
        Set the rail supply power. Rail power control capabilities vary between modules.
        Refer to the module datasheet for definition of the rail power capabilities.

        :param milliwatts: The power in milli-watts (1 == 1e-3W) to be supplied by the rail.
        :type milliwatts: const int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_setPowerSetpoint(self._module._id_pointer, result, self._index, milliwatts)
        return result.error

    def getPowerSetpoint(self):

        """ 
        Get the rail setpoint power. Rail power control capabilities vary between modules.
        Refer to the module datasheet for definition of the rail power capabilities.
        The power in milli-watts (1 == 1e-3W) the rail is trying to
        achieve. On some modules this is a measured value so it may not exactly match what was
        previously set via the setPower interface. Refer to the module datasheet to
        to determine if this is a measured or stored value.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_getPowerSetpoint(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def setPowerLimit(self, milliwatts):

        """ 
        Set the rail power maximum limit setting. (Check product datasheet to see if this feature is available)

        :param milliwatts: The power in milli-watts (mW).
        :type milliwatts: const int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_setPowerLimit(self._module._id_pointer, result, self._index, milliwatts)
        return result.error

    def getPowerLimit(self):

        """ 
        Get the rail power maximum limit setting. (Check product datasheet to see if this feature is available)
        The power in milli-watts (mW).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_getPowerLimit(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def getResistance(self):

        """ 
        Get the rail load resistance. Rail resistance control capabilities vary between modules.
        Refer to the module datasheet for definition of the rail resistance capabilities.
        The resistance in milli-ohms (1 == 1e-3Ohms) currently drawn by
        the rail. On some modules this is a measured value so it may not exactly match what was
        previously set via the setResistance interface. Refer to the module datasheet to
        to determine if this is a measured or stored value.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_getResistance(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def setResistanceSetpoint(self, milliohms):

        """ 
        Set the rail load resistance. Rail resistance control capabilities vary between modules.
        Refer to the module datasheet for definition of the rail resistance capabilities.

        :param milliohms: The resistance in milli-ohms (1 == 1e-3Ohms) to be drawn by the rail.
        :type milliohms: const int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_setResistanceSetpoint(self._module._id_pointer, result, self._index, milliohms)
        return result.error

    def getResistanceSetpoint(self):

        """ 
        Get the rail setpoint resistance. Rail resistance control capabilities vary between modules.
        Refer to the module datasheet for definition of the rail resistance capabilities.
        The resistance in milli-ohms (1 == 1e-3Ohms) the rail is trying to
        achieve. On some modules this is a measured value so it may not exactly match what was
        previously set via the setResistance interface. Refer to the module datasheet to
        to determine if this is a measured or stored value.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_getResistanceSetpoint(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def setKelvinSensingEnable(self, bEnable):

        """ 
        Enable or Disable kelvin sensing on the module.
        Refer to the module datasheet for definition of the rail kelvin sensing capabilities.

        :param bEnable: enable or disable kelvin sensing.
        :type bEnable: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_setKelvinSensingEnable(self._module._id_pointer, result, self._index, bEnable)
        return result.error

    def getKelvinSensingEnable(self):

        """ 
        Determine whether kelvin sensing is enabled or disabled.
        Refer to the module datasheet for definition of the rail kelvin sensing capabilities.
        Kelvin sensing is enabled or disabled.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_getKelvinSensingEnable(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def getKelvinSensingState(self):

        """ 
        Determine whether kelvin sensing has been disabled by the system.
        Refer to the module datasheet for definition of the rail kelvin sensing capabilities.
        Kelvin sensing is enabled or disabled.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_getKelvinSensingState(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setOperationalMode(self, mode):

        """ 
        Set the operational mode of the rail.
        Refer to the module datasheet for definition of the rail operational capabilities.

        :param mode: The operational mode to employ.
        :type mode: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_setOperationalMode(self._module._id_pointer, result, self._index, mode)
        return result.error

    def getOperationalMode(self):

        """ 
        Determine the current operational mode of the system.
        Refer to the module datasheet for definition of the rail operational mode capabilities.
        The current operational mode setting.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_getOperationalMode(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def getOperationalState(self):

        """ 
        Determine the current operational state of the system.
        Refer to the module datasheet for definition of the rail operational states.
        The current operational state, hardware configuration, faults, and operating mode.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_getOperationalState(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def clearFaults(self):

        """ 
        Clears the current fault state of the rail.
        Refer to the module datasheet for definition of the rail faults.

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.rail_clearFaults(self._module._id_pointer, result, self._index)
        return result.error

