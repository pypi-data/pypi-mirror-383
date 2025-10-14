# This file was auto-generated. Do not modify.

from ._bs_c_cffi import ffi
from . import _BS_C #imported from __init__
from .Entity_Entity import *
from .result import Result
from .ffi_utils import data_to_bytearray, bytes_to_string, handle_sign

class PowerDelivery(Entity):
    
    """ 
        PowerDeliveryClass:
        Power Delivery or PD is a power specification which allows more charging options
        and device behaviors within the USB interface.  This Entity will allow you to directly
        access the vast landscape of PD.

    """ 


    def __init__(self, module, index):
        super(PowerDelivery, self).__init__(module, _BS_C.cmdPOWERDELIVERY, index)

    def getConnectionState(self):

        """ 
        Gets the current state of the connection in the form of an enumeration.
        Pointer to be filled with the current connection state.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_getConnectionState(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def getNumberOfPowerDataObjects(self, partner, powerRole):

        """ 
        Gets the number of Power Data Objects (PDOs) for a given partner and power role.
        Variable to be filled with the number of PDOs.

        :param partner: Indicates which side of the PD connection is in question. - Local = 0 = powerdeliveryPartnerLocal - Remote = 1 = powerdeliveryPartnerRemote
        :type partner: const unsigned char
        :param powerRole: Indicates which power role of PD connection is in question. - Source = 1 = powerdeliveryPowerRoleSource - Sink = 2 = powerdeliveryPowerRoleSink
        :type powerRole: const unsigned char

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_getNumberOfPowerDataObjects(self._module._id_pointer, result, self._index, partner, powerRole)
        return handle_sign(result, 8, False)

    def getPowerDataObject(self, partner, powerRole, ruleIndex):

        """ 
        Gets the Power Data Object (PDO) for the requested partner, powerRole and index.
        Variable to be filled with the requested power rule.

        :param partner: Indicates which side of the PD connection is in question. - Local = 0 = powerdeliveryPartnerLocal - Remote = 1 = powerdeliveryPartnerRemote
        :type partner: const unsigned char
        :param powerRole: Indicates which power role of PD connection is in question. - Source = 1 = powerdeliveryPowerRoleSource - Sink = 2 = powerdeliveryPowerRoleSink
        :type powerRole: const unsigned char
        :param ruleIndex: The index of the PDO in question. Valid index are 1-7.
        :type ruleIndex: const unsigned char

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_getPowerDataObject(self._module._id_pointer, result, self._index, partner, powerRole, ruleIndex)
        return handle_sign(result, 32, False)

    def setPowerDataObject(self, powerRole, ruleIndex, pdo):

        """ 
        Sets the Power Data Object (PDO) of the local partner for a given power role and index.

        :param powerRole: Indicates which power role of PD connection is in question. - Source = 1 = powerdeliveryPowerRoleSource - Sink = 2 = powerdeliveryPowerRoleSink
        :type powerRole: const unsigned char
        :param ruleIndex: The index of the PDO in question. Valid index are 1-7.
        :type ruleIndex: const unsigned char
        :param pdo: Power Data Object to be set.
        :type pdo: const unsigned int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_setPowerDataObject(self._module._id_pointer, result, self._index, powerRole, ruleIndex, pdo)
        return result.error

    def resetPowerDataObjectToDefault(self, powerRole, ruleIndex):

        """ 
        Resets the Power Data Object (PDO) of the Local partner for a given power role and index.

        :param powerRole: Indicates which power role of PD connection is in question. - Source = 1 = powerdeliveryPowerRoleSource - Sink = 2 = powerdeliveryPowerRoleSink
        :type powerRole: const unsigned char
        :param ruleIndex: The index of the PDO in question. Valid index are 1-7.
        :type ruleIndex: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_resetPowerDataObjectToDefault(self._module._id_pointer, result, self._index, powerRole, ruleIndex)
        return result.error

    def getPowerDataObjectList(self, buffer_length=65536):

        """ 
        Gets all Power Data Objects (PDOs).
        Equivalent to calling PowerDeliveryClass::getPowerDataObject() on all partners, power roles, and index's.
        Length that was actually received and filled.
        On success this value should be 28 (7 rules * 2 partners * 2 power roles)

        :param buffer_length: Length of the buffer to be filed

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        ffi_buffer = ffi.new("unsigned int[]", buffer_length)
        _BS_C.powerdelivery_getPowerDataObjectList(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return_list = [ffi_buffer[i] for i in range(result.value)]
        return Result(result.error, tuple(return_list) if result.error == Result.NO_ERROR else None)
        
    def getPowerDataObjectEnabled(self, powerRole, ruleIndex):

        """ 
        Gets the enabled state of the Local Power Data Object (PDO) for a given power role and index.
        Enabled refers to whether the PDO will be advertised when a PD connection is made.
        This does not indicate the currently active rule index. This information can be found in Request Data Object (RDO).
        Variable to be filled with enabled state.

        :param powerRole: Indicates which power role of PD connection is in question. - Source = 1 = powerdeliveryPowerRoleSource - Sink = 2 = powerdeliveryPowerRoleSink
        :type powerRole: const unsigned char
        :param ruleIndex: The index of the PDO in question. Valid index are 1-7.
        :type ruleIndex: const unsigned char

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_getPowerDataObjectEnabled(self._module._id_pointer, result, self._index, powerRole, ruleIndex)
        return handle_sign(result, 8, False)

    def setPowerDataObjectEnabled(self, powerRole, ruleIndex, enabled):

        """ 
        Sets the enabled state of the Local Power Data Object (PDO) for a given powerRole and index.
        Enabled refers to whether the PDO will be advertised when a PD connection is made.
        This does not indicate the currently active rule index. This information can be found in Request Data Object (RDO).

        :param powerRole: Indicates which power role of PD connection is in question. - Source = 1 = powerdeliveryPowerRoleSource - Sink = 2 = powerdeliveryPowerRoleSink
        :type powerRole: const unsigned char
        :param ruleIndex: The index of the PDO in question. Valid index are 1-7.
        :type ruleIndex: const unsigned char
        :param enabled: The state to be set.
        :type enabled: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_setPowerDataObjectEnabled(self._module._id_pointer, result, self._index, powerRole, ruleIndex, enabled)
        return result.error

    def getPowerDataObjectEnabledList(self, powerRole):

        """ 
        Gets all Power Data Object enables for a given power role.
        Equivalent of calling PowerDeliveryClass::getPowerDataObjectEnabled() for all indexes.
        Variable to be filled with a mapped representation of the enabled PDOs for a
        given power role. Values align with a given rule index (bits 1-7, bit 0 is invalid)

        :param powerRole: Indicates which power role of PD connection is in question. - Source = 1 = powerdeliveryPowerRoleSource - Sink = 2 = powerdeliveryPowerRoleSink
        :type powerRole: const unsigned char

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_getPowerDataObjectEnabledList(self._module._id_pointer, result, self._index, powerRole)
        return handle_sign(result, 8, False)

    def getRequestDataObject(self, partner):

        """ 
        Gets the current Request Data Object (RDO) for a given partner.
        RDOs:   Are provided by the sinking device.
        Exist only after a successful PD negotiation (Otherwise zero).
        Only one RDO can exist at a time. i.e. Either the Local or Remote partner RDO
        Variable to be filled with the current RDO. Zero indicates the RDO is not active.

        :param partner: Indicates which side of the PD connection is in question. - Local = 0 = powerdeliveryPartnerLocal - Remote = 1 = powerdeliveryPartnerRemote
        :type partner: const unsigned char

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_getRequestDataObject(self._module._id_pointer, result, self._index, partner)
        return handle_sign(result, 32, False)

    def setRequestDataObject(self, rdo):

        """ 
        Sets the current Request Data Object (RDO) for a given partner.
        (Only the local partner can be changed.)
        RDOs:   Are provided by the sinking device.
        Exist only after a successful PD negotiation (Otherwise zero).
        Only one RDO can exist at a time. i.e. Either the Local or Remote partner RDO

        :param rdo: Request Data Object to be set.
        :type rdo: const unsigned int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_setRequestDataObject(self._module._id_pointer, result, self._index, rdo)
        return result.error

    def getPowerRole(self):

        """ 
        Gets the power role that is currently being advertised by the local partner. (CC Strapping).
        Variable to be filed with the power role
        - Disabled = 0 = powerdeliveryPowerRoleDisabled
        - Source = 1= powerdeliveryPowerRoleSource
        - Sink = 2 = powerdeliveryPowerRoleSink
        - Source/Sink = 3 = powerdeliveryPowerRoleSourceSink (Dual Role Port)

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_getPowerRole(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setPowerRole(self, powerRole):

        """ 
        Set the current power role to be advertised by the Local partner. (CC Strapping).

        :param powerRole: Value to be applied. - Disabled = 0 = powerdeliveryPowerRoleDisabled - Source = 1= powerdeliveryPowerRoleSource - Sink = 2 = powerdeliveryPowerRoleSink - Source/Sink = 3 = powerdeliveryPowerRoleSourceSink (Dual Role Port)
        :type powerRole: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_setPowerRole(self._module._id_pointer, result, self._index, powerRole)
        return result.error

    def getPowerRolePreferred(self):

        """ 
        Gets the preferred power role currently being advertised by the Local partner. (CC Strapping).
        Value to be applied.
        - Disabled = 0 = powerdeliveryPowerRoleDisabled
        - Source = 1= powerdeliveryPowerRoleSource
        - Sink = 2 = powerdeliveryPowerRoleSink

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_getPowerRolePreferred(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setPowerRolePreferred(self, powerRole):

        """ 
        Set the preferred power role to be advertised by the Local partner (CC Strapping).

        :param powerRole: Value to be applied. - Disabled = 0 = powerdeliveryPowerRoleDisabled - Source = 1= powerdeliveryPowerRoleSource - Sink = 2 = powerdeliveryPowerRoleSink
        :type powerRole: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_setPowerRolePreferred(self._module._id_pointer, result, self._index, powerRole)
        return result.error

    def getCableVoltageMax(self):

        """ 
        Gets the maximum voltage capability reported by the e-mark of the attached cable.
        Variable to be filled with an enumerated representation of voltage.
        - Unknown/Unattached (0)
        - 20 Volts DC (1)
        - 30 Volts DC (2)
        - 40 Volts DC (3)
        - 50 Volts DC (4)

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_getCableVoltageMax(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def getCableCurrentMax(self):

        """ 
        Gets the maximum current capability report by the e-mark of the attached cable.
        Variable to be filled with an enumerated representation of current.
        - Unknown/Unattached (0)
        - 3 Amps (1)
        - 5 Amps (2)

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_getCableCurrentMax(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def getCableSpeedMax(self):

        """ 
        Gets the maximum data rate capability reported by the e-mark of the attached cable.
        Variable to be filled with an enumerated representation of data speed.
        - Unknown/Unattached (0)
        - USB 2.0 (1)
        - USB 3.2 gen 1 (2)
        - USB 3.2 / USB 4 gen 2 (3)
        - USB 4 gen 3 (4)

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_getCableSpeedMax(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def getCableType(self):

        """ 
        Gets the cable type reported by the e-mark of the attached cable.
        Variable to be filled with an enumerated representation of the cable type.
        - Invalid, no e-mark and not Vconn powered (0)
        - Passive cable with e-mark (1)
        - Active cable (2)

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_getCableType(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def getCableOrientation(self):

        """ 
        Gets the current orientation being used for PD communication
        Variable filled with an enumeration of the orientation.
        - Unconnected (0)
        - CC1 (1)
        - CC2 (2)

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_getCableOrientation(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def request(self, request):

        """ 
        Requests an action of the Remote partner.
        Actions are not guaranteed to occur.
        The returned error represents the success of the request being sent to the partner only.
        The success of the request being serviced by the remote partner can be obtained
        through PowerDeliveryClass::requestStatus()
        Returns \ref EntityReturnValues "common entity" return values

        :param request: Request to be issued to the remote partner - pdRequestHardReset (0) - pdRequestSoftReset (1) - pdRequestDataReset (2) - pdRequestPowerRoleSwap (3) - pdRequestPowerFastRoleSwap (4) - pdRequestDataRoleSwap (5) - pdRequestVconnSwap (6) - pdRequestSinkGoToMinimum (7) - pdRequestRemoteSourcePowerDataObjects (8) - pdRequestRemoteSinkPowerDataObjects (9)
        :type request: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_request(self._module._id_pointer, result, self._index, request)
        return result.error

    def requestStatus(self):

        """ 
        Gets the status of the last request command sent.
        Variable to be filled with the status

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_requestStatus(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def getOverride(self):

        """ 
        Gets the current enabled overrides
        Bit mapped representation of the current override configuration.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_getOverride(self._module._id_pointer, result, self._index)
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
        _BS_C.powerdelivery_setOverride(self._module._id_pointer, result, self._index, overrides)
        return result.error

    def resetEntityToFactoryDefaults(self):

        """ 
        Resets the PowerDeliveryClass Entity to it factory default configuration.

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_resetEntityToFactoryDefaults(self._module._id_pointer, result, self._index)
        return result.error

    def getFlagMode(self, flag):

        """ 
        Gets the current mode of the local partner flag/advertisement.
        These flags are apart of the first Local Power Data Object and must be managed in order to
        accurately represent the system to other PD devices. This API allows overriding of that feature.
        Overriding may lead to unexpected behaviors.
        Variable to be filled with the current mode.
        - Disabled (0)
        - Enabled (1)
        - Auto (2) default

        :param flag: Flag/Advertisement to be modified
        :type flag: const unsigned char

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_getFlagMode(self._module._id_pointer, result, self._index, flag)
        return handle_sign(result, 8, False)

    def setFlagMode(self, flag, mode):

        """ 
        Sets how the local partner flag/advertisement is managed.
        These flags are apart of the first Local Power Data Object and must be managed in order to
        accurately represent the system  to other PD devices. This API allows overriding of that feature.
        Overriding may lead to unexpected behaviors.

        :param flag: Flag/Advertisement to be modified
        :type flag: const unsigned char
        :param mode: Value to be applied. - Disabled (0) - Enabled (1) - Auto (2) default
        :type mode: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_setFlagMode(self._module._id_pointer, result, self._index, flag, mode)
        return result.error

    def getPeakCurrentConfiguration(self):

        """ 
        Gets the Peak Current Configuration for the Local Source.
        The peak current configuration refers to the allowable tolerance/overload capabilities
        in regards to the devices max current.  This tolerance includes a maximum value and a time unit.
        An enumerated value referring to the current configuration.
        - Allowable values are 0 - 4

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_getPeakCurrentConfiguration(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setPeakCurrentConfiguration(self, configuration):

        """ 
        Sets the Peak Current Configuration for the Local Source.
        The peak current configuration refers to the allowable tolerance/overload capabilities
        in regards to the devices max current.  This tolerance includes a maximum value and a time unit.

        :param configuration: An enumerated value referring to the configuration to be set - Allowable values are 0 - 4
        :type configuration: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_setPeakCurrentConfiguration(self._module._id_pointer, result, self._index, configuration)
        return result.error

    def getFastRoleSwapCurrent(self):

        """ 
        Gets the Fast Role Swap Current
        The fast role swap current refers to the amount of current required by the Local Sink
        in order to successfully preform the swap.
        An enumerated value referring to current swap value.
        - 0A (0)
        - 900mA (1)
        - 1.5A (2)
        - 3A (3)

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_getFastRoleSwapCurrent(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setFastRoleSwapCurrent(self, swapCurrent):

        """ 
        Sets the Fast Role Swap Current
        The fast role swap current refers to the amount of current required by the Local Sink
        in order to successfully preform the swap.

        :param swapCurrent: An enumerated value referring to value to be set. - 0A (0) - 900mA (1) - 1.5A (2) - 3A (3)
        :type swapCurrent: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_setFastRoleSwapCurrent(self._module._id_pointer, result, self._index, swapCurrent)
        return result.error

    def packDataObjectAttributes(self, attributes, partner, powerRole, ruleIndex):

        """ 
        Helper function for packing Data Object attributes.
        This value is used as a subindex for all Data Object calls with the BrainStem Protocol.
        aErrNone on success; aErrParam with bad input.

        :param attributes: variable to be filled with packed values.
        :type attributes: unsigned char *
        :param partner: Indicates which side of the PD connection. - Local = 0 = powerdeliveryPartnerLocal - Remote = 1 = powerdeliveryPartnerRemote
        :type partner: const unsigned char
        :param powerRole: Indicates which power role of PD connection. - Source = 1 = powerdeliveryPowerRoleSource - Sink = 2 = powerdeliveryPowerRoleSink
        :type powerRole: const unsigned char
        :param ruleIndex: Data object index.
        :type ruleIndex: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_packDataObjectAttributes(self._module._id_pointer, result, self._index, attributes, partner, powerRole, ruleIndex)
        return result.error

    def unpackDataObjectAttributes(self, attributes, partner, powerRole):

        """ 
        Helper function for unpacking Data Object attributes.
        This value is used as a subindex for all Data Object calls with the BrainStem Protocol.
        Data object index.
        aErrNone on success; aErrParam with bad input.

        :param attributes: variable to be filled with packed values.
        :type attributes: const unsigned char
        :param partner: Indicates which side of the PD connection. - Local = 0 = powerdeliveryPartnerLocal - Remote = 1 = powerdeliveryPartnerRemote
        :type partner: unsigned char *
        :param powerRole: Indicates which power role of PD connection. - Source = 1 = powerdeliveryPowerRoleSource - Sink = 2 = powerdeliveryPowerRoleSink
        :type powerRole: unsigned char *

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.powerdelivery_unpackDataObjectAttributes(self._module._id_pointer, result, self._index, attributes, partner, powerRole)
        return handle_sign(result, 8, False)

