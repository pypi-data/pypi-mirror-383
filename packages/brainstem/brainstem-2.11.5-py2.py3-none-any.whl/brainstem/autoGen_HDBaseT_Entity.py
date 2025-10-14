# This file was auto-generated. Do not modify.

from ._bs_c_cffi import ffi
from . import _BS_C #imported from __init__
from .Entity_Entity import *
from .result import Result
from .ffi_utils import data_to_bytearray, bytes_to_string, handle_sign

class HDBaseT(Entity):
    
    """ 
        /
        Congratulations! You found an Easter egg!
        Unfortunately, this code is still under construction and should not be used.
        /
        HDBaseTClass:
        This entity is only available on certain modules, and provides a
        Power Over Ethernet control ability.

    """ 


    def __init__(self, module, index):
        super(HDBaseT, self).__init__(module, _BS_C.cmdHDBASET, index)

    def getSerialNumber(self, buffer_length=65536):

        """ 
        Gets the serial number of the HDBaseT device (6 bytes)
        Length that was actually received and filled.

        :param buffer_length: Length of the buffer to be filed

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")

        ffi_buffer = ffi.new("unsigned char[]", buffer_length)
        
        _BS_C.hdbaset_getSerialNumber(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return_list = [ffi_buffer[i] for i in range(result.value)]

        return_result = Result(result.error, tuple(return_list) if result.error == Result.NO_ERROR else None)

        return return_result

    def getFirmwareVersion(self):

        """ 
        Gets the firmware version of the HDBaseT device
        A bit packet representation of the firmware version
        Major: Bits 24-31; Minor: Bits 16-23; Patch: Bits 8-15; Build: Bits 0-7

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.hdbaset_getFirmwareVersion(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def getState(self):

        """ 
        Gets the current state of the HDBaseT link
        Bit packeted representation of the state.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.hdbaset_getState(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def getCableLength(self):

        """ 
        Gets the perceived cable length
        Cable length in meters

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.hdbaset_getCableLength(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def getMSE(self):

        """ 
        Gets the Mean Squared Error (MSE)
        A bit packed representation for A and B channels
        Channel A: Bits 0-15; Channel B: Bits 16-31;
        Each channel has a unit of milli-dB, represented as a signed int16_t.
        Effective range of [-32.768dB, 32.767dB]

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.hdbaset_getMSE(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def getRetransmissionRate(self):

        """ 
        Gets the number of retransmissions that have occurred
        retransmissions since link creation.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.hdbaset_getRetransmissionRate(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def getLinkUtilization(self):

        """ 
        Gets the current link utilization
        Utilization in milli-percent

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.hdbaset_getLinkUtilization(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def getEncodingState(self):

        """ 
        Gets the current encoding state.
        Signal modulation encoding type.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.hdbaset_getEncodingState(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def getUSB2DeviceTree(self, buffer_length=65536):

        """ 
        Gets the USB2 tree at the HDBaseT device.
        Length that was actually received and filled.

        :param buffer_length: Length of the buffer to be filed

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")

        ffi_buffer = ffi.new("unsigned char[]", buffer_length)
        
        _BS_C.hdbaset_getUSB2DeviceTree(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return_list = [ffi_buffer[i] for i in range(result.value)]

        return_result = Result(result.error, tuple(return_list) if result.error == Result.NO_ERROR else None)

        return return_result

    def getUSB3DeviceTree(self, buffer_length=65536):

        """ 
        Gets the USB3 tree at the HDBaseT device.
        Length that was actually received and filled.

        :param buffer_length: Length of the buffer to be filed

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")

        ffi_buffer = ffi.new("unsigned char[]", buffer_length)
        
        _BS_C.hdbaset_getUSB3DeviceTree(self._module._id_pointer, result, self._index, ffi_buffer, buffer_length)
        return_list = [ffi_buffer[i] for i in range(result.value)]

        return_result = Result(result.error, tuple(return_list) if result.error == Result.NO_ERROR else None)

        return return_result

