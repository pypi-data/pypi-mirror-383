# This file was auto-generated. Do not modify.

from ._bs_c_cffi import ffi
from . import _BS_C #imported from __init__
from .Entity_Entity import *
from .result import Result
from .ffi_utils import data_to_bytearray, bytes_to_string, handle_sign

class Clock(Entity):
    
    """ 
        ClockClass:
        Provides an interface to a real-time clock entity on a BrainStem module.
        The clock entity may be used to get and set the real time of the system.
        The clock entity has a one second resolution.
        @note Clock time must be reset if power to the BrainStem module is lost.

    """ 


    def __init__(self, module, index):
        super(Clock, self).__init__(module, _BS_C.cmdCLOCK, index)

    def getYear(self):

        """ 
        Get the four digit year value (0-4095).
        Get the year portion of the real-time clock value.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.clock_getYear(self._module._id_pointer, result, self._index)
        return handle_sign(result, 16, False)

    def setYear(self, year):

        """ 
        Set the four digit year value (0-4095).

        :param year: Set the year portion of the real-time clock value.
        :type year: const unsigned short

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.clock_setYear(self._module._id_pointer, result, self._index, year)
        return result.error

    def getMonth(self):

        """ 
        Get the two digit month value (1-12).
        The two digit month portion of the real-time clock value.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.clock_getMonth(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setMonth(self, month):

        """ 
        Set the two digit month value (1-12).

        :param month: The two digit month portion of the real-time clock value.
        :type month: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.clock_setMonth(self._module._id_pointer, result, self._index, month)
        return result.error

    def getDay(self):

        """ 
        Get the two digit day of month value (1-28, 29, 30 or 31 depending
        on the month).
        The two digit day portion of the real-time clock value.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.clock_getDay(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setDay(self, day):

        """ 
        Set the two digit day of month value (1-28, 29, 30 or 31 depending
        on the month).

        :param day: The two digit day portion of the real-time clock value.
        :type day: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.clock_setDay(self._module._id_pointer, result, self._index, day)
        return result.error

    def getHour(self):

        """ 
        Get the two digit hour value (0-23).
        The two digit hour portion of the real-time clock value.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.clock_getHour(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setHour(self, hour):

        """ 
        Set the two digit hour value (0-23).

        :param hour: The two digit hour portion of the real-time clock value.
        :type hour: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.clock_setHour(self._module._id_pointer, result, self._index, hour)
        return result.error

    def getMinute(self):

        """ 
        Get the two digit minute value (0-59).
        The two digit minute portion of the real-time clock value.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.clock_getMinute(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setMinute(self, min):

        """ 
        Set the two digit minute value (0-59).

        :param min: The two digit minute portion of the real-time clock value.
        :type min: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.clock_setMinute(self._module._id_pointer, result, self._index, min)
        return result.error

    def getSecond(self):

        """ 
        Get the two digit second value (0-59).
        The two digit second portion of the real-time clock value.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.clock_getSecond(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setSecond(self, sec):

        """ 
        Set the two digit second value (0-59).

        :param sec: The two digit second portion of the real-time clock value.
        :type sec: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.clock_setSecond(self._module._id_pointer, result, self._index, sec)
        return result.error

