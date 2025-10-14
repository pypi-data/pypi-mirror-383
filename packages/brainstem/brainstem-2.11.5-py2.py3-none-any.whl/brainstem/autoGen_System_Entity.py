# This file was auto-generated. Do not modify.

from ._bs_c_cffi import ffi
from . import _BS_C #imported from __init__
from .Entity_Entity import *
from .result import Result
from .ffi_utils import data_to_bytearray, bytes_to_string, handle_sign

class System(Entity):
    
    """ 
        SystemClass:
        The System class provides access to the core settings,
        configuration and system information of the BrainStem module. The class
        provides access to the model type, serial number and other static
        information as well as the ability to set boot reflexes, toggle the
        user LED, as well as affect module and router addresses etc.

    """ 

    BOOT_SLOT_DISABLE = 255

    def __init__(self, module, index):
        super(System, self).__init__(module, _BS_C.cmdSYSTEM, index)

    def getModule(self):

        """ 
        Get the current address the module uses on the BrainStem network.
        The address the module is using on the BrainStem network.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getModule(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def getModuleBaseAddress(self):

        """ 
        Get the base address of the module. Software offsets and hardware offsets are
        added to this base address to produce the effective module address.
        The address the module is using on the BrainStem network.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getModuleBaseAddress(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setRouter(self, address):

        """ 
        Set the router address the module uses to communicate with the host and heartbeat to
        in order to establish the BrainStem network.
        This setting must be saved and the board reset before the setting
        becomes active.
        Warning: changing the router address may cause the module to "drop off" the
        BrainStem network if the
        new router address is not in use by a BrainStem module.
        Please review the BrainStem network fundamentals before modifying the router
        address.

        :param address: The router address to be used.
        :type address: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_setRouter(self._module._id_pointer, result, self._index, address)
        return result.error

    def getRouter(self):

        """ 
        Get the router address the module uses to communicate with the host and heartbeat to
        in order to establish the BrainStem network.
        The address.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getRouter(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setHBInterval(self, interval):

        """ 
        Set the delay between heartbeat packets which are sent from the module.
        For link modules, these these heartbeat are sent to the host.
        For non-link modules, these heartbeats are sent to the router address.
        Interval values are in 25.6 millisecond increments
        Valid values are 1-255; default is 10 (256 milliseconds).

        :param interval: The desired heartbeat delay.
        :type interval: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_setHBInterval(self._module._id_pointer, result, self._index, interval)
        return result.error

    def getHBInterval(self):

        """ 
        Get the delay between heartbeat packets which are sent from the module.
        For link modules, these these heartbeat are sent to the host.
        For non-link modules, these heartbeats are sent to the router address.
        Interval values are in 25.6 millisecond increments.
        The current heartbeat delay.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getHBInterval(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setLED(self, bOn):

        """ 
        Set the system LED state. Most modules have a blue system LED. Refer to the module
        datasheet for details on the system LED location and color.

        :param bOn: true: turn the LED on, false: turn LED off.
        :type bOn: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_setLED(self._module._id_pointer, result, self._index, bOn)
        return result.error

    def getLED(self):

        """ 
        Get the system LED state. Most modules have a blue system LED. Refer to the module
        datasheet for details on the system LED location and color.
        true: LED on, false: LED off.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getLED(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setLEDMaxBrightness(self, brightness):

        """ 
        Sets the scaling factor for the brightness of all LEDs on the system.
        The brightness is set to the ratio of this value compared to 255 (maximum).
        The colors of each LED may be inconsistent at low brightness levels.
        Note that if the brightness is set to zero and the settings are saved,
        then the LEDs will no longer indicate whether the system is powered on.
        When troubleshooting, the user configuration may need to be manually reset
        in order to view the LEDs again.

        :param brightness: Brightness value relative to 255
        :type brightness: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_setLEDMaxBrightness(self._module._id_pointer, result, self._index, brightness)
        return result.error

    def getLEDMaxBrightness(self):

        """ 
        Gets the scaling factor for the brightness of all LEDs on the system.
        The brightness is set to the ratio of this value compared to 255 (maximum).
        Brightness value relative to 255

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getLEDMaxBrightness(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setBootSlot(self, slot):

        """ 
        Set a store slot to be mapped when the module boots. The boot slot will be
        mapped after the module boots from powers up,
        receives a reset signal on its reset input, or
        is issued a software reset command.
        Set the slot to 255 to disable mapping on boot.

        :param slot: The slot number in aSTORE_INTERNAL to be marked as a boot slot.
        :type slot: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_setBootSlot(self._module._id_pointer, result, self._index, slot)
        return result.error

    def getBootSlot(self):

        """ 
        Get the store slot which is mapped when the module boots.
        The slot number in aSTORE_INTERNAL that is mapped after the module
        boots.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getBootSlot(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def getVersion(self):

        """ 
        Get the modules firmware version number.
        The version number is packed into the return value. Utility functions
        in the aVersion module can unpack the major, minor and patch numbers from
        the version number which looks like M.m.p.
        The build version date code.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getVersion(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def getBuild(self):

        """ 
        Get the modules firmware build number
        The build number is a unique hash assigned to a specific firmware.
        Variable to be filled with build.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getBuild(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def getModel(self):

        """ 
        Get the module's model enumeration. A subset of the possible model enumerations
        is defined in BrainStem.h under "BrainStem model codes". Other codes are be used
        by Acroname for proprietary module types.
        The module's model enumeration.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getModel(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def getHardwareVersion(self):

        """ 
        Get the module's hardware revision information. The content of the hardware version
        is specific to each Acroname product and used to indicate behavioral differences
        between product revisions. The codes are not well defined and may change at any time.
        The module's hardware version information.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getHardwareVersion(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def getSerialNumber(self):

        """ 
        Get the module's serial number. The serial number is a unique 32bit integer
        which is usually communicated in hexadecimal format.
        The module's serial number.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getSerialNumber(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def save(self):

        """ 
        Save the system operating parameters to the persistent module flash memory.
        Operating parameters stored in the system flash will be loaded after the module
        reboots. Operating parameters include: heartbeat interval, module address,
        module router address

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_save(self._module._id_pointer, result, self._index)
        return result.error

    def reset(self):

        """ 
        Reset the system.  aErrTimeout indicates a successful reset, as the system resets immediately, which tears down the USB-link immediately, thus preventing an affirmative response.

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_reset(self._module._id_pointer, result, self._index)
        return result.error

    def logEvents(self):

        """ 
        Saves system log events to a slot defined by the module (usually ram slot 0).

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_logEvents(self._module._id_pointer, result, self._index)
        return result.error

    def getUptime(self):

        """ 
        Get the module's accumulated uptime in minutes
        The module's accumulated uptime in minutes.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getUptime(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def getTemperature(self):

        """ 
        Get the module's current temperature in micro-C
        The module's system temperature in micro-C

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getTemperature(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def getMinimumTemperature(self):

        """ 
        Get the module's minimum temperature ever recorded in micro-C (uC)
        This value will persists through a power cycle.
        The module's minimum system temperature in micro-C

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getMinimumTemperature(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def getMaximumTemperature(self):

        """ 
        Get the module's maximum temperature ever recorded in micro-C (uC)
        This value will persists through a power cycle.
        The module's maximum system temperature in micro-C

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getMaximumTemperature(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def getInputVoltage(self):

        """ 
        Get the module's input voltage.
        The module's input voltage reported in microvolts.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getInputVoltage(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def getInputCurrent(self):

        """ 
        Get the module's input current.
        The module's input current reported in microamps.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getInputCurrent(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def getModuleHardwareOffset(self):

        """ 
        Get the module hardware address offset. This is added to the base address to allow the
        module address to be configured in hardware. Not all modules support the
        hardware module address offset. Refer to the module datasheet.
        The module address offset.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getModuleHardwareOffset(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setModuleSoftwareOffset(self, address):

        """ 
        Set the software address offset.
        This software offset is added to the module base address, and potentially a
        module hardware address to produce the final module address. You
        must save the system settings and restart for this to take effect.
        Please review the BrainStem network fundamentals before modifying the module address.

        :param address: The address for the module. Value must be even from 0-254.
        :type address: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_setModuleSoftwareOffset(self._module._id_pointer, result, self._index, address)
        return result.error

    def getModuleSoftwareOffset(self):

        """ 
        Get the software address offset.
        This software offset is added to the module base address, and potentially a
        module hardware address to produce the final module address. You
        must save the system settings and restart for this to take effect.
        Please review the BrainStem network fundamentals before modifying the module address.
        The address for the module. Value must be even from 0-254.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getModuleSoftwareOffset(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def getRouterAddressSetting(self):

        """ 
        Get the router address system setting.
        This setting may not be the same as the current router address if
        the router setting was set and saved but no reset has occurred.
        Please review the BrainStem network fundamentals before modifying the module address.
        The address for the module. Value must be even from 0-254.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getRouterAddressSetting(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def routeToMe(self, bOn):

        """ 
        Enables/Disables the route to me function.
        This function allows for easy networking of BrainStem modules.
        Enabling (1) this function will send an I2C General Call to all devices
        on the network and request that they change their router address
        to the of the calling device. Disabling (0) will cause all devices
        on the BrainStem network to revert to their default address.

        :param bOn: Enable or disable of the route to me function 1 = enable.
        :type bOn: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_routeToMe(self._module._id_pointer, result, self._index, bOn)
        return result.error

    def getPowerLimit(self):

        """ 
        Reports the amount of power the system has access to and thus how much
        power can be budgeted to sinking devices.
        The available power in milli-Watts (mW, 1 t)

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getPowerLimit(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def getPowerLimitMax(self):

        """ 
        Gets the user defined maximum power limit for the system.
        Provides mechanism for defining an unregulated power supplies capability.
        Variable to be filled with the power limit in milli-Watts (mW)

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getPowerLimitMax(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def setPowerLimitMax(self, power):

        """ 
        Sets a user defined maximum power limit for the system.
        Provides mechanism for defining an unregulated power supplies capability.

        :param power: Limit in milli-Watts (mW) to be set.
        :type power: const unsigned int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_setPowerLimitMax(self._module._id_pointer, result, self._index, power)
        return result.error

    def getPowerLimitState(self):

        """ 
        Gets a bit mapped representation of the factors contributing to the power limit.
        Active limit can be found through PowerDeliverClass::getPowerLimit().
        Variable to be filled with the state.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getPowerLimitState(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def getUnregulatedVoltage(self):

        """ 
        Gets the voltage present at the unregulated port.
        Variable to be filled with the voltage in micro-Volts (uV).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getUnregulatedVoltage(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def getUnregulatedCurrent(self):

        """ 
        Gets the current passing through the unregulated port.
        Variable to be filled with the current in micro-Amps (uA).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getUnregulatedCurrent(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def getInputPowerSource(self):

        """ 
        Provides the source of the current power source in use.
        Variable to be filled with enumerated representation of the source.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getInputPowerSource(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def getInputPowerBehavior(self):

        """ 
        Gets the systems input power behavior.
        This behavior refers to where the device sources its power from and what
        happens if that power source goes away.
        Variable to be filled with an enumerated value representing behavior.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getInputPowerBehavior(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setInputPowerBehavior(self, behavior):

        """ 
        Sets the systems input power behavior.
        This behavior refers to where the device sources its power from and what
        happens if that power source goes away.

        :param behavior: An enumerated representation of behavior to be set.
        :type behavior: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_setInputPowerBehavior(self._module._id_pointer, result, self._index, behavior)
        return result.error

    def getInputPowerBehaviorConfig(self, buffer_length=65536):

        """ 
        Gets the input power behavior configuration
        Certain behaviors use a list of ports to determine priority when budgeting power.
        Length that was actually received and filled.

        :param buffer_length: Length of the buffer to be filed

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        ffi_buffer = ffi.new("unsigned int[]", buffer_length)
        _BS_C.system_getInputPowerBehaviorConfig(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return_list = [ffi_buffer[i] for i in range(result.value)]
        return Result(result.error, tuple(return_list) if result.error == Result.NO_ERROR else None)
        
    def setInputPowerBehaviorConfig(self, buffer):

        """ 
        Sets the input power behavior configuration
        Certain behaviors use a list of ports to determine priority when budgeting power.

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        byte_array = data_to_bytearray(buffer)

        buffer_length = len(byte_array)
        ffi_buffer = ffi.new("unsigned int[]", buffer_length)
        for x in range(buffer_length):
            ffi_buffer[x] = byte_array[x]

        _BS_C.system_setInputPowerBehaviorConfig(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return result.error

    def getName(self, buffer_length=65536):

        """ 
        Gets a user defined name of the device.
        Helpful for identifying ports/devices in a static environment.
        Length that was actually received and filled.

        :param buffer_length: Length of the buffer to be filed

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")

        ffi_buffer = ffi.new("unsigned char[]", buffer_length)
        
        _BS_C.system_getName(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return_list = [ffi_buffer[i] for i in range(result.value)]

        return_result = Result(result.error, tuple(return_list) if result.error == Result.NO_ERROR else None)

        return bytes_to_string(return_result)

    def setName(self, buffer):

        """ 
        Sets a user defined name for the device.
        Helpful for identification when multiple devices of the same type are present in a system.

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        byte_array = data_to_bytearray(buffer)

        buffer_length = len(byte_array)
        ffi_buffer = ffi.new("unsigned char[]", buffer_length)
        for x in range(buffer_length):
            ffi_buffer[x] = byte_array[x]

        _BS_C.system_setName(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return result.error

    def resetEntityToFactoryDefaults(self):

        """ 
        Resets the SystemClass Entity to it factory default configuration.

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_resetEntityToFactoryDefaults(self._module._id_pointer, result, self._index)
        return result.error

    def resetDeviceToFactoryDefaults(self):

        """ 
        Resets the device to it factory default configuration.

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_resetDeviceToFactoryDefaults(self._module._id_pointer, result, self._index)
        return result.error

    def getLinkInterface(self):

        """ 
        Gets the link interface configuration.
        This refers to which interface is being used for control by the device.
        Variable to be filled with an enumerated value representing interface.
        - 0 = Auto= systemLinkAuto
        - 1 = Control Port = systemLinkUSBControl
        - 2 = Hub Upstream Port = systemLinkUSBHub

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getLinkInterface(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setLinkInterface(self, linkInterface):

        """ 
        Sets the link interface configuration.
        This refers to which interface is being used for control by the device.

        :param linkInterface: An enumerated representation of interface to be set. - 0 = Auto= systemLinkAuto - 1 = Control Port = systemLinkUSBControl - 2 = Hub Upstream Port = systemLinkUSBHub
        :type linkInterface: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_setLinkInterface(self._module._id_pointer, result, self._index, linkInterface)
        return result.error

    def getErrors(self):

        """ 
        Gets any system level errors.
        Calling this function will clear the current errors. If the error persists it will be set again.
        Bit mapped field representing the devices errors

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getErrors(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def getProtocolFeatures(self):

        """ 
        Gets the firmware protocol features
        Value representing the firmware protocol features

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.system_getProtocolFeatures(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

