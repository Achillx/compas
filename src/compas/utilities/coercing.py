from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

try:
    basestring
except NameError:
    basestring = str


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = [
    'is_sequence_of_str',
    'is_sequence_of_int',
    'is_sequence_of_float',
    'is_sequence_of_long',
    'is_sequence_of_tuple',
    'is_sequence_of_list',
    'is_sequence_of_dict',

    'is_item_iterable',
    'is_sequence_of_iterable',

    'coerce_sequence_of_tuple',
    'coerce_sequence_of_list',
]


# ==============================================================================
# check
# ==============================================================================


def is_sequence_of_str(sequence):
    return is_sequence_of_type(sequence, basestring)


def is_sequence_of_int(sequence):
    return is_sequence_of_type(sequence, int)


def is_sequence_of_float(sequence):
    return is_sequence_of_type(sequence, float)


def is_sequence_of_long(sequence):
    return is_sequence_of_type(sequence, long)


def is_sequence_of_list(sequence):
    return is_sequence_of_type(sequence, list)


def is_sequence_of_tuple(sequence):
    return is_sequence_of_type(sequence, tuple)


def is_sequence_of_dict(sequence):
    return is_sequence_of_type(sequence, dict)


def is_sequence_of_type(sequence, t):
    if any(not isinstance(item, t) for item in sequence):
        return False
    return True


def is_item_iterable(item):
    try:
        _ = [for i in item]
    except TypeError:
        return False
    return True


def is_sequence_of_iterable(sequence):
    if any(not is_item_iterable(item) for item in sequence):
        return False
    return True


# ==============================================================================
# coerce
# ==============================================================================


def coerce_sequence_of_tuple(sequence):
    items = []
    for item in sequence:
        if not isinstance(item, tuple):
            if not is_item_iterable(item):
                item = (item, )
            else:
                item = tuple(item)
        items.append(item)
    return items


def coerce_sequence_of_list(sequence):
    items = []
    for item in sequence:
        if not isinstance(item, list):
            if not is_item_iterable(item):
                item = [item, ]
            else:
                item = list(item)
        items.append(item)
    return items


def coerce_sequence_of_dict(sequence):
    raise NotImplementedError


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    items = range(10)
    items = map(int, items)

    print(is_sequence_of_int(items))