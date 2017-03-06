# -*- coding: utf-8 -*-
"""
:author: Rafal Jasicki
:contact: rafal.jasicki@nsn.com
"""

from populate import populate, PopulateError
from binascii import hexlify
from prophy_test_structs import *


def test_populate():
    data = {'int2': 12,
            'int1': 11,
            'pstruct1a': {'int1': 8},            # recursive impl.
            'pstruct1b.int1': 11,                # dot-syntax
            'pstruct1a.pstruct2.int': 2,        # nested
            'pstruct_opt.int1': 3,               # optional item
            'array_variable': [{'int1': 2}],    # array of var. length
            'pstruct1c.array_fixed':
            [i*3 for i in xrange(17)]}  # array of fixed length

    msg = populate(pmessage(), data)

    try:
        msg = populate(msg, {'xxx': 0})
    except PopulateError as e:
        print "{}; problem for field/message '{}'".format(e, msg.__class__.__name__)
    try:
        msg = populate(msg, {'container.array': [0, 1]})
    except PopulateError as e:
        print "{}; problem for field/message '{}'".format(e, msg.__class__.__name__)

    print (hexlify(msg.encode('>')))

    # Check that optional arguments can be removed with populate
    msg1 = populate(pmessage(), {})
    msg2 = populate(pmessage(), {'pstruct_opt.int1': 7})

    msg1s = hexlify(msg1.encode('>'))
    msg2s = hexlify(msg2.encode('>'))
    assert msg1s != msg2s
    msg2 = populate(msg2, {'pstruct_opt': None})
    msg2s = hexlify(msg2.encode('>'))
    assert msg1s == msg2s


def test_order_of_population():
    data = {'pstruct1a': {'int1': 8, 'int2': 1},
            'pstruct1a.int2': 11}
    msg = populate(pmessage(), data)
    assert msg.pstruct1a.int2 == 11
    assert msg.pstruct1a.int1 == 8


def test_populate_with_prophy_struct():
    s = PStruct1()
    s.int1 = 4
    data = {'pstruct1a': s}
    msg = populate(pmessage(), data)
    assert msg.pstruct1a.int1 == 4
    # only values are copied
    assert id(msg.pstruct1a) != id(s)
