# Copyright (c) 2018 Acroname Inc. - All Rights Reserved
#
# This file is part of the BrainStem (tm) package which is released under MIT.
# See file LICENSE or go to https://acroname.com for full license details.

""" Provides version access utilities. """

from .result import Result


def data_to_bytearray(data):
    if isinstance(data, str):
        return bytearray(data.encode('utf-8'))

    elif hasattr(data, '__iter__'):
        if len(data) == 0: #This provides index safety of the below elif's
            return bytearray()
        elif isinstance(data[0], str):
            return bytearray([ord(char) for char in data])
        else:
            return bytearray(data)

    elif isinstance(data, int):
        return bytearray([data])
        
    #This covers:
    # - isinstance(data, tuple):
    # - isinstance(data, bytearray):
    # - isinstance(data, bytes):
    # - and everything else. 
    else:
        return bytearray(data)


def bytes_to_string(result):
    """ Helper function for UEIBytes to convert byte array value to a string

        args:
            result (Result): The Result object from a get_UEIBytes

        returns:
            Result: Returns a result object, whose value is set,
                    or with the requested value when the results error is
                    set to NO_ERROR
    """
    if result.error != Result.NO_ERROR:
        return result

    temp_value = bytes(result.value).decode('utf-8')
    return Result(Result.NO_ERROR, temp_value)


def handle_sign(result, num_bits=0, signed=True):
    """ Helper function for managing the sign of the returned value.
        The CCA Result object is of type int; however, sometimes the
        values returned are unsigned. 

        args:
            result (Result (CCA)): The CCA Result object
            num_bits (uint): The number of bits the value represents
            signed (bool): Indicates if the value is signed or not.

        returns:
            Result: Returns a python result object, whose value is set,
                    or with the requested value when the results error is
                    set to NO_ERROR
    """
    value = result.value # Move value out of c type object.
    if result.error == Result.NO_ERROR and num_bits and not signed:
        value = value & ((1 << num_bits)-1) if value < 0 else value

    return Result(result.error, value)
