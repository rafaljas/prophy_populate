# -*- coding: utf-8 -*-
"""
:author: Rafal Jasicki
:contact: rafal.jasicki@gmail.com
"""
import logging
import traceback
import prophy
from binascii import hexlify

logger = logging.getLogger('dev')


class PopulateError(Exception):
    pass


def handle_optional_struct(field, attr):
    """
    handle optional struct
    """
    if issubclass(type(field), prophy.union):
        for e in field._descriptor:
            name = e[0]
            inx = e[2]
            if name == attr:
                field.discriminator = inx
                return
    if field.__getattribute__(attr) is None:
        field.__setattr__(attr, True)


def handle_struct_list(field, value, state):
    """Handle lists of structures."""
    if not field._BOUND:
        for inx in xrange(len(value)):
            populate_recursion(field[inx], value[inx], state)
        return

    inx = 0
    for item_value in value:
        if len(field) > inx:
            item = field[inx]
        else:
            item = field.add()
        inx += 1
        populate_recursion(item, item_value, state)


def set_list_value(field, attrs, value, state):
    """Set value to specific element of mesage."""
    field = field.__getattribute__(attrs[-1])

    # case of [] -- remove old values
    if field._BOUND and len(value) == 0:
        del field[:]
        return
    # case of list with fixed legth
    if not field._BOUND and len(field) != len(value):
        raise ValueError("Expected list of {} items, got '{}' instead".format(len(field), value))

    # case of [{},...]
    if type(value[0]) is dict:
        handle_struct_list(field, value, state)
    # case of [1,...]
    else:
        field[:len(value)] = value[:]


def populate(msg, data, state=None):
    """Initiation of recursion."""
    if state is None:
        state = []
    try:
        return populate_recursion(msg, data, state)
    except Exception as e:
        state = state.pop()
        if len(state) == 2:
            txt = ("There was problem while populating message:\n"
                   "Last attempt was for field '{}' with data:\n"
                   "'{}'\nException: {}\nTraceback:{}\n").format(state[0], state[1], e, traceback.format_exc())
        else:
            txt = ("There was problem while populating message:\n"
                   "Last attempt was for field '{}'\nException: {}\nTraceback:{}\n").format(state[0], e, traceback.format_exc())
        logger.error(txt)
        logger.error("Full operation context: {}".format(state))
        raise PopulateError(txt)


def populate_recursion(msg, data, state):
    """Pupulate message msg with data from dictionary.
    Internal structures are represented either by dictionaries or
    can be assigned by '.' reference.
    """
    keys = data.keys()
    keys.sort()
    for key in keys:
        state.append([key])
        value = data[key]
        state[-1].append(value)
        # logger.debug("Setting field '{}' of message/field '{}'."
        #              "Data:\n{}".format(key, msg.__class__.__name__,
        #                                 str(value)[:70]))
        attrs = key.split('.')
        field = msg
        # handling od paths constructed with '.'
        for attr in attrs[:-1]:
            handle_optional_struct(field, attr)
            field = field.__getattribute__(attr)

        # hanlindg of '{...}'
        if type(value) is dict:
            handle_optional_struct(field, attrs[-1])
            populate_recursion(field.__getattribute__(attrs[-1]), value, state)
            continue

        # handling of '[...]'
        if type(value) is list:
            set_list_value(field, attrs, value, state)
            continue
        # case of simple type
        assignment(field, attrs[-1], value)
        state.pop()

    return msg


def assignment(field, attr, value):
    """
    Assign simple value.
    It is possible that simple value is actually a prophy structure.
    """
    # case of struct
    if issubclass(type(value), prophy.struct):
        new_field = field.__getattribute__(attr)
        new_field.copy_from(value)
        return
    # simple value
    field.__setattr__(attr, value)
