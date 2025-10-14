# This file was auto-generated. Do not modify.

from ._bs_c_cffi import ffi
from . import _BS_C #imported from __init__
from .Entity_Entity import *
from .result import Result
from .ffi_utils import data_to_bytearray, bytes_to_string, handle_sign

class Equalizer(Entity):
    
    """ 
        EqualizerClass:
        Provides receiver and transmitter gain/boost/emphasis
        settings for some of Acroname's products.  Please see product
        documentation for further details.

    """ 


    def __init__(self, module, index):
        super(Equalizer, self).__init__(module, _BS_C.cmdEQUALIZER, index)

    def setReceiverConfig(self, channel, config):

        """ 
        Sets the receiver configuration for a given channel.

        :param channel: The equalizer receiver channel.
        :type channel: const unsigned char
        :param config: Configuration to be applied to the receiver.
        :type config: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.equalizer_setReceiverConfig(self._module._id_pointer, result, self._index, channel, config)
        return result.error

    def getReceiverConfig(self, channel):

        """ 
        Gets the receiver configuration for a given channel.
        Configuration of the receiver.

        :param channel: The equalizer receiver channel.
        :type channel: const unsigned char

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.equalizer_getReceiverConfig(self._module._id_pointer, result, self._index, channel)
        return handle_sign(result, 8, False)

    def setTransmitterConfig(self, config):

        """ 
        Sets the transmitter configuration

        :param config: Configuration to be applied to the transmitter.
        :type config: const unsigned char

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.equalizer_setTransmitterConfig(self._module._id_pointer, result, self._index, config)
        return result.error

    def getTransmitterConfig(self):

        """ 
        Gets the transmitter configuration
        Configuration of the Transmitter.

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.equalizer_getTransmitterConfig(self._module._id_pointer, result, self._index)
        return handle_sign(result, 8, False)

