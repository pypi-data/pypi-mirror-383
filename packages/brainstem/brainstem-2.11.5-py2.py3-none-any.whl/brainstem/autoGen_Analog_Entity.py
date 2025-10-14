# This file was auto-generated. Do not modify.

from ._bs_c_cffi import ffi
from . import _BS_C #imported from __init__
from .Entity_Entity import *
from .result import Result
from .ffi_utils import data_to_bytearray, bytes_to_string, handle_sign

class Analog(Entity):
    
    """ 
        AnalogClass:
        Interface to analog entities on BrainStem modules.
        Analog entities may be configured as a input or output depending
        on hardware capabilities. Some modules are capable of providing actual
        voltage readings, while other simply return the raw analog-to-digital converter (ADC)
        output value. The resolution of the voltage or number of useful bits is also
        hardware dependent.

    """ 

    CONFIGURATION_INPUT = 0
    CONFIGURATION_OUTPUT = 1
    HERTZ_MINIMUM = 7000
    HERTZ_MAXIMUM = 200000
    BULK_CAPTURE_IDLE = 0
    BULK_CAPTURE_PENDING = 1
    BULK_CAPTURE_FINISHED = 2
    BULK_CAPTURE_ERROR = 3

    def __init__(self, module, index):
        super(Analog, self).__init__(module, _BS_C.cmdANALOG, index)

    def getValue(self):

        """ 
        Get the raw ADC output value in bits.
        16 bit analog reading with 0 corresponding to the negative
        analog voltage reference and
        0xFFFF corresponding to the positive analog voltage reference.
        Note: Not all modules are provide 16 useful bits; this value's least
        significant bits are zero-padded to 16 bits. Refer to the module's
        datasheet to determine analog bit depth and reference voltage.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.analog_getValue(self._module._id_pointer, result, self._index)
        return handle_sign(result, 16, False)

    def getVoltage(self):

        """ 
        Get the scaled micro volt value with reference to ground.
        32 bit signed integer (in microvolts) based on the board's
        ground and reference voltages.
        Note: Not all modules provide 32 bits of accuracy; Refer to the module's
        datasheet to determine the analog bit depth and reference voltage.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.analog_getVoltage(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def getRange(self):

        """ 
        Get the analog input range.
        8 bit value corresponding to a discrete range option

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.analog_getRange(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def getEnable(self):

        """ 
        Get the analog output enable status.
        0 if disabled 1 if enabled.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.analog_getEnable(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setValue(self, value):

        """ 
        Set the value of an analog output (DAC) in bits.

        :param value: 16 bit analog set point with 0 corresponding to the negative analog voltage reference and 0xFFFF corresponding to the positive analog voltage reference. Note: Not all modules are provide 16 useful bits; the least significant bits are discarded. E.g. for a 10 bit DAC, 0xFFC0 to 0x0040 is the useful range. Refer to the module's datasheet to determine analog bit depth and reference voltage.
        :type value: const unsigned short

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.analog_setValue(self._module._id_pointer, result, self._index, value)
        return result.error

    def setVoltage(self, microvolts):

        """ 
        Set the voltage level of an analog output (DAC) in microvolts.

        :param microvolts: 32 bit signed integer (in microvolts) based on the board's ground and reference voltages. Note: Voltage range is dependent on the specific DAC channel range.
        :type microvolts: const int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.analog_setVoltage(self._module._id_pointer, result, self._index, microvolts)
        return result.error

    def setRange(self, range):

        """ 
        Set the analog input range.

        :param range: 8 bit value corresponding to a discrete range option
        :type range: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.analog_setRange(self._module._id_pointer, result, self._index, range)
        return result.error

    def setEnable(self, enable):

        """ 
        Set the analog output enable state.

        :param enable: set 1 to enable or 0 to disable.
        :type enable: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.analog_setEnable(self._module._id_pointer, result, self._index, enable)
        return result.error

    def setConfiguration(self, configuration):

        """ 
        Set the analog configuration.
        aErrConfiguration - Entity does not support this configuration.

        :param configuration: - bitAnalogConfigurationOutput configures the analog entity as an output.
        :type configuration: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.analog_setConfiguration(self._module._id_pointer, result, self._index, configuration)
        return result.error

    def getConfiguration(self):

        """ 
        Get the analog configuration.
        - Current configuration of the analog entity.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.analog_getConfiguration(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setBulkCaptureSampleRate(self, value):

        """ 
        Set the sample rate for this analog when bulk capturing.

        :param value: sample rate in samples per second (Hertz). Minimum rate: 7,000 Hz Maximum rate: 200,000 Hz
        :type value: const unsigned int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.analog_setBulkCaptureSampleRate(self._module._id_pointer, result, self._index, value)
        return result.error

    def getBulkCaptureSampleRate(self):

        """ 
        Get the current sample rate setting for this analog when bulk capturing.
        upon success filled with current sample rate in samples per second (Hertz).

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.analog_getBulkCaptureSampleRate(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def setBulkCaptureNumberOfSamples(self, value):

        """ 
        Set the number of samples to capture for this analog when bulk capturing.

        :param value: number of samples. Minimum # of Samples: 0 Maximum # of Samples: (BRAINSTEM_RAM_SLOT_SIZE / 2) = (3FFF / 2) = 1FFF = 8191
        :type value: const unsigned int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.analog_setBulkCaptureNumberOfSamples(self._module._id_pointer, result, self._index, value)
        return result.error

    def getBulkCaptureNumberOfSamples(self):

        """ 
        Get the current number of samples setting for this analog when bulk capturing.
        number of samples.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.analog_getBulkCaptureNumberOfSamples(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, False)

    def initiateBulkCapture(self):

        """ 
        Initiate a BulkCapture on this analog. Captured measurements are stored in the
        module's RAM store (RAM_STORE) slot 0. Data is stored in a contiguous byte array
        with each sample stored in two consecutive bytes, LSB first.

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.analog_initiateBulkCapture(self._module._id_pointer, result, self._index)
        return result.error

    def getBulkCaptureState(self):

        """ 
        Get the current bulk capture state for this analog.
        the state of bulk capture.
        - Idle: bulkCaptureIdle = 0
        - Pending: bulkCapturePending = 1
        - Finished: bulkCaptureFinished = 2
        - Error: bulkCaptureError = 3

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.analog_getBulkCaptureState(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

