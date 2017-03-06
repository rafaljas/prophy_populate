# -*- coding: utf-8 -*-
"""
:author: Rafal Jasicki
:contact: rafal.jasicki@gmail.com
"""
import prophy

TInt = prophy.u32


class PStruct2(prophy.struct):
    __metaclass__ = prophy.struct_generator
    _descriptor = [('int', TInt)]


class PStruct1(prophy.struct):
    __metaclass__ = prophy.struct_generator
    _descriptor = [('pstruct2', PStruct2),
                   ('int1', TInt),
                   ('int2', TInt),
                   ('array_fixed', prophy.array(TInt, size=17))]


class pmessage(prophy.struct):
    __metaclass__ = prophy.struct_generator
    _descriptor = [('int1', TInt),
                   ('pstruct1a', PStruct1),
                   ('pstruct1b', PStruct1),
                   ('int2', TInt),
                   ('pstruct_opt', prophy.optional(PStruct1)),
                   ('array_variable_len', prophy.u32),
                   ('array_variable', prophy.array(PStruct1, bound='array_variable_len', size=3)),
                   ('pstruct1c', PStruct1)]
