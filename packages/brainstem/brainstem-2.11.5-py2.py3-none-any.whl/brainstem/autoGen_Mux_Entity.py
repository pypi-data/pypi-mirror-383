# This file was auto-generated. Do not modify.

from ._bs_c_cffi import ffi
from . import _BS_C #imported from __init__
from .Entity_Entity import *
from .result import Result
from .ffi_utils import data_to_bytearray, bytes_to_string, handle_sign

class Mux(Entity):
    
    """ 
        MuxClass:
        A MUX is a multiplexer that takes one or more similar inputs
        (bus, connection, or signal) and allows switching to one or more outputs.
        An analogy would be the switchboard of a telephone operator.  Calls (inputs)
        come in and by re-connecting the input to an output, the operator
        (multiplexer) can direct that input to on or more outputs.
        
        One possible output is to not connect the input to anything which
        essentially disables that input's connection to anything.
        
        Not every MUX has multiple inputs.  Some may simply be a single input that
        can be enabled (connected to a single output) or disabled
        (not connected to anything).

    """ 

    UPSTREAM_STATE_ONBOARD = 0
    UPSTREAM_STATE_EDGE = 1
    UPSTREAM_MODE_AUTO = 0
    UPSTREAM_MODE_ONBOARD = 1
    UPSTREAM_MODE_EDGE = 2
    DEFAULT_MODE = UPSTREAM_MODE_AUTO

    def __init__(self, module, index):
        super(Mux, self).__init__(module, _BS_C.cmdMUX, index)

    def getEnable(self):

        """ 
        Get the mux enable/disable status
        true: mux is enabled, false: the mux is disabled.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.mux_getEnable(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setEnable(self, bEnable):

        """ 
        Enable the mux.

        :param bEnable: true: enables the mux for the selected channel.
        :type bEnable: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.mux_setEnable(self._module._id_pointer, result, self._index, bEnable)
        return result.error

    def getChannel(self):

        """ 
        Get the current selected mux channel.
        Indicates which chanel is selected.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.mux_getChannel(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

    def setChannel(self, channel):

        """ 
        Set the current mux channel.

        :param channel: mux channel to select.
        :type channel: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.mux_setChannel(self._module._id_pointer, result, self._index, channel)
        return result.error

    def getChannelVoltage(self, channel):

        """ 
        Get the voltage of the indicated mux channel.
        32 bit signed integer (in microvolts) based on the board's
        ground and reference voltages.
        Note: Not all modules provide 32 bits of accuracy; Refer to the module's
        datasheet to determine the analog bit depth and reference voltage.

        :param channel: The channel in which voltage was requested.
        :type channel: const unsigned char

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.mux_getChannelVoltage(self._module._id_pointer, result, self._index, channel)
        return handle_sign(result, 32, True)

    def getConfiguration(self):

        """ 
        Get the configuration of the mux.
        integer representing the mux configuration either default, or split-mode.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.mux_getConfiguration(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def setConfiguration(self, config):

        """ 
        Set the configuration of the mux.

        :param config: integer representing the mux configuration either muxConfig_default, or muxConfig_splitMode.
        :type config: const int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.mux_setConfiguration(self._module._id_pointer, result, self._index, config)
        return result.error

    def getSplitMode(self):

        """ 
        Get the current split mode mux configuration.
        integer representing the channel selection for
        each sub-channel within the mux. See the data-sheet for the device
        for specific information.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.mux_getSplitMode(self._module._id_pointer, result, self._index)
        return handle_sign(result, 32, True)

    def setSplitMode(self, splitMode):

        """ 
        Sets the mux's split mode configuration.

        :param splitMode: integer representing the channel selection for each sub-channel within the mux. See the data-sheet for the device for specific information.
        :type splitMode: const int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.mux_setSplitMode(self._module._id_pointer, result, self._index, splitMode)
        return result.error

