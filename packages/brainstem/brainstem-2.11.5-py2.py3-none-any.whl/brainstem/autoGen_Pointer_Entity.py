# This file was auto-generated. Do not modify.

from ._bs_c_cffi import ffi
from . import _BS_C #imported from __init__
from .Entity_Entity import *
from .result import Result
from .ffi_utils import data_to_bytearray, bytes_to_string, handle_sign

class Pointer(Entity):
    
    """ 
        PointerClass:
        Allows access to the reflex scratchpad from a host computer.
        
        The Pointers access the pad which is a shared memory area on a
        BrainStem module. The interface allows the use of the BrainStem
        scratchpad from the host, and provides a mechanism for allowing the
        host application and BrainStem relexes to communicate.
        
        The Pointer allows access to the pad in a similar manner as a file
        pointer accesses the underlying file. The cursor position can be
        set via setOffset. A read of a character short or int can be made
        from that cursor position. In addition the mode of the pointer can
        be set so that the cursor position automatically increments or set
        so that it does not this allows for multiple reads of the same pad
        value, or reads of multi-record values, via an incrementing pointer.

    """ 

    POINTER_MODE_STATIC = 0
    POINTER_MODE_INCREMENT = 1

    def __init__(self, module, index):
        super(Pointer, self).__init__(module, _BS_C.cmdPOINTER, index)

    def getOffset(self):

        """ 
        Get the offset of the pointer
        The value of the offset.
        All possible standard UEI return values.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.pointer_getOffset(self._module._id_pointer, result, self._index)
        return handle_sign(result, 16, False)

    def setOffset(self, offset):

        """ 
        Set the offset of the pointer
        All possible standard UEI return values.

        :param offset: The value of the offset.
        :type offset: unsigned short

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.pointer_setOffset(self._module._id_pointer, result, self._index, offset)
        return result.error

    def getMode(self):

        """ 
        Get the mode of the pointer
        The mode: aPOINTER_MODE_STATIC or aPOINTER_MODE_AUTO_INCREMENT.
        All possible standard UEI return values.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.pointer_getMode(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setMode(self, mode):

        """ 
        Set the mode of the pointer
        All possible standard UEI return values.

        :param mode: The mode: aPOINTER_MODE_STATIC or aPOINTER_MODE_AUTO_INCREMENT.
        :type mode: unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.pointer_setMode(self._module._id_pointer, result, self._index, mode)
        return result.error

    def getTransferStore(self):

        """ 
        Get the handle to the store.
        The handle of the store.
        All possible standard UEI return handles.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.pointer_getTransferStore(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setTransferStore(self, handle):

        """ 
        Set the handle to the store.
        All possible standard UEI return handles.

        :param handle: The handle of the store.
        :type handle: unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.pointer_setTransferStore(self._module._id_pointer, result, self._index, handle)
        return result.error

    def initiateTransferToStore(self, transferLength):

        """ 
        Transfer data to the store.
        All possible standard UEI return values.

        :param transferLength: The length of the data transfer.
        :type transferLength: unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.pointer_initiateTransferToStore(self._module._id_pointer, result, self._index, transferLength)
        return result.error

    def initiateTransferFromStore(self, transferLength):

        """ 
        Transfer data from the store.
        All possible standard UEI return values.

        :param transferLength: The length of the data transfer.
        :type transferLength: unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.pointer_initiateTransferFromStore(self._module._id_pointer, result, self._index, transferLength)
        return result.error

    def getChar(self):

        """ 
        Get a char (1 byte) value from the pointer at this object's index,
        where elements are 1 byte long.
        The value of a single character (1 byte) stored in the pointer.
        All possible standard UEI return values.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.pointer_getChar(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setChar(self, value):

        """ 
        Set a char (1 byte) value to the pointer at this object's element index,
        where elements are 1 byte long.
        All possible standard UEI return values.

        :param value: The single char (1 byte) value to be stored in the pointer.
        :type value: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.pointer_setChar(self._module._id_pointer, result, self._index, value)
        return result.error

    def getShort(self):

        """ 
        Get a short (2 byte) value from the pointer at this objects index,
        where elements are 2 bytes long
        The value of a single short (2 byte) stored in the pointer.
        All possible standard UEI return values.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.pointer_getShort(self._module._id_pointer, result, self._index)
        return handle_sign(result, 16, False)

    def setShort(self, value):

        """ 
        Set a short (2 bytes) value to the pointer at this object's element index,
        where elements are 2 bytes long.
        All possible standard UEI return values.

        :param value: The single short (2 byte) value to be set in the pointer.
        :type value: const unsigned short

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.pointer_setShort(self._module._id_pointer, result, self._index, value)
        return result.error

    def getInt(self):

        """ 
        Get an int (4 bytes) value from the pointer at this objects index,
        where elements are 4 bytes long
        The value of a single int (4 byte) stored in the pointer.
        All possible standard UEI return values.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.pointer_getInt(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def setInt(self, value):

        """ 
        Set an int (4 bytes) value from the pointer at this objects index,
        where elements are 4 bytes long
        All possible standard UEI return values.

        :param value: The single int (4 byte) value to be stored in the pointer.
        :type value: const unsigned int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.pointer_setInt(self._module._id_pointer, result, self._index, value)
        return result.error

