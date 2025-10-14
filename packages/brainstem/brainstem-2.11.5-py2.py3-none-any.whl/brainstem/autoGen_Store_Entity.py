# This file was auto-generated. Do not modify.

from ._bs_c_cffi import ffi
from . import _BS_C #imported from __init__
from .Entity_Entity import *
from .result import Result
from .ffi_utils import data_to_bytearray, bytes_to_string, handle_sign

class Store(Entity):
    
    """ 
        StoreClass:
        The store provides a flat file system on modules that
        have storage capacity. Files are referred to as slots and they have
        simple zero-based numbers for access.
        Store slots can be used for generalized storage and commonly contain
        compiled reflex code (files ending in .map) or templates used by the
        system. Slots simply contain bytes with no expected organization but
        the code or use of the slot may impose a structure.
        Stores have fixed indices based on type. Not every module contains a
        store of each type. Consult the module datasheet for details on which
        specific stores are implemented, if any, and the capacities of implemented stores.

    """ 

    INTERNAL_STORE = 0
    RAM_STORE = 1
    SD_STORE = 2
    EEPROM_STORE = 3

    def __init__(self, module, index):
        super(Store, self).__init__(module, _BS_C.cmdSTORE, index)

    def getSlotState(self, slot):

        """ 
        Get slot state.
        true: enabled, false: disabled.

        :param slot: The slot number.
        :type slot: const unsigned char

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.store_getSlotState(self._module._id_pointer, result, self._index, slot)
        return handle_sign(result, 8, False)

    def loadSlot(self, slot, buffer):

        """ 
        Load the slot.

        :param slot: The slot number.
        :type slot: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        byte_array = data_to_bytearray(buffer)

        buffer_length = len(byte_array)
        ffi_buffer = ffi.new("unsigned char[]", buffer_length)
        for x in range(buffer_length):
            ffi_buffer[x] = byte_array[x]

        _BS_C.store_loadSlot(self._module._id_pointer, result, self._index, slot, ffi_buffer, buffer_length)
        return result.error

    def unloadSlot(self, slot, buffer_length=65536):

        """ 
        Unload the slot data.
        Length of data that was unloaded. Unloaded length
        will never be larger than dataLength.

        :param slot: The slot number.
        :type slot: const unsigned char
        :param buffer_length: - The length of pData buffer in bytes. This is the maximum number of bytes that should be unloaded.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")

        ffi_buffer = ffi.new("unsigned char[]", buffer_length)
        
        _BS_C.store_unloadSlot(self._module._id_pointer, result, self._index, slot, ffi_buffer, buffer_length)
        return_list = [ffi_buffer[i] for i in range(result.value)]

        return_result = Result(result.error, tuple(return_list) if result.error == Result.NO_ERROR else None)

        return return_result

    def slotEnable(self, slot):

        """ 
        Enable slot.

        :param slot: The slot number.
        :type slot: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.store_slotEnable(self._module._id_pointer, result, self._index, slot)
        return result.error

    def slotDisable(self, slot):

        """ 
        Disable slot.

        :param slot: The slot number.
        :type slot: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.store_slotDisable(self._module._id_pointer, result, self._index, slot)
        return result.error

    def getSlotCapacity(self, slot):

        """ 
        Get the slot capacity.
        Returns the Capacity of the slot, i.e. The number of bytes it can hold.
        The slot capacity.

        :param slot: The slot number.
        :type slot: const unsigned char

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.store_getSlotCapacity(self._module._id_pointer, result, self._index, slot)
        return handle_sign(result, 32, False)

    def getSlotSize(self, slot):

        """ 
        Get the slot size.
        The slot size represents the size of the data currently filling the slot in bytes.
        The slot size.

        :param slot: The slot number.
        :type slot: const unsigned char

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.store_getSlotSize(self._module._id_pointer, result, self._index, slot)
        return handle_sign(result, 32, False)

    def getSlotLocked(self, slot):

        """ 
        Gets the current lock state of the slot
        Allows for write protection on a slot.
        Variable to be filed with the locked state.

        :param slot: The slot number
        :type slot: const unsigned char

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.store_getSlotLocked(self._module._id_pointer, result, self._index, slot)
        return handle_sign(result, 8, False)

    def setSlotLocked(self, slot, lock):

        """ 
        Sets the locked state of the slot
        Allows for write protection on a slot.

        :param slot: The slot number
        :type slot: const unsigned char
        :param lock: state to be set.
        :type lock: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.store_setSlotLocked(self._module._id_pointer, result, self._index, slot, lock)
        return result.error

