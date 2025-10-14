# This file was auto-generated. Do not modify.

from ._bs_c_cffi import ffi
from . import _BS_C #imported from __init__
from .Entity_Entity import *
from .result import Result
from .ffi_utils import data_to_bytearray, bytes_to_string, handle_sign

class App(Entity):
    
    """ 
        AppClass:
        Used to send a cmdAPP packet to the BrainStem network.
        These commands are used for either host-to-stem or stem-to-stem interactions.
        BrainStem modules can implement a reflex origin to complete an action when
        a cmdAPP packet is addressed to the module.

    """ 


    def __init__(self, module, index):
        super(App, self).__init__(module, _BS_C.cmdAPP, index)

    def execute(self, appParam):

        """ 
        Execute the app reflex on the module. Don't wait for a return
        value from the execute call; this call returns immediately upon execution
        of the module's reflex.
        aErrNone success.
        aErrTimeout The request timed out waiting to start execution.
        aErrConnection No active link connection.
        aErrNotFound the app reflex was not found or not enabled on
        the module.

        :param appParam: The app parameter handed to the reflex.
        :type appParam: const unsigned int

        :return: An error result from the list of defined error codes in brainstem.result
        :rtype: unsigned byte
        
        """

        result = ffi.new("struct Result*")
        _BS_C.app_execute(self._module._id_pointer, result, self._index, appParam)
        return result.error

    def executeAndReturn(self, appParam, msTimeout):

        """ 
        Execute the app reflex on the module. Wait for a return from the
        reflex execution for msTimoue milliseconds. This method will block for
        up to msTimeout.
        The return value filled in from the result of
        executing the reflex routine.
        aErrNone success.
        aErrTimeout The request timed out waiting for a response.
        aErrConnection No active link connection.
        aErrNotFound the app reflex was not found or not enabled on
        the module.

        :param appParam: The app parameter handed to the reflex.
        :type appParam: const unsigned int
        :param msTimeout: The amount of time to wait for the return value from the reflex routine. The default value is 1000 milliseconds if not specified.
        :type msTimeout: const unsigned int

        :return: Result object containing the requested value when the results error is set to NO_ERROR(0)
        :rtype: Result
        
        """

        result = ffi.new("struct Result*")
        _BS_C.app_executeAndReturn(self._module._id_pointer, result, self._index, appParam, msTimeout)
        return handle_sign(result, 0, False)

