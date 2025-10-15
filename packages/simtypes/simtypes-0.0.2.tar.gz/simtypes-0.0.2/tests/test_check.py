import sys

try:
    from types import NoneType  # type: ignore[attr-defined]
except ImportError:
    NoneType = type(None)  # type: ignore[misc]

from typing import List, Dict, Tuple, Set, Optional, Any, Union
from collections.abc import Sequence

import pytest
from full_match import match

from simtypes import check


def test_none():
    assert check(None, None) is True
    assert check(NoneType, None) is True

    assert check(None, 1) is False
    assert check(None, 'None') is False
    assert check(None, 0) is False
    assert check(None, False) is False
    assert check(NoneType, False) is False
    assert check(NoneType, 0) is False
    assert check(NoneType, 'some string') is False

    assert check(NoneType, NoneType) is False
    assert check(None, NoneType) is False


def test_built_in_types():
    assert check(bool, True) is True
    assert check(int, 1) is True
    assert check(float, 1.0) is True
    assert check(str, 'hello') is True

    assert check(bool, 1) is False
    assert check(bool, 'True') is False
    assert check(bool, 1.0) is False
    assert check(bool, None) is False
    assert check(int, '1') is False
    assert check(int, 1.0) is False
    assert check(int, None) is False
    assert check(str, 1) is False
    assert check(str, None) is False
    assert check(float, '1.0') is False
    assert check(float, 1) is False
    assert check(float, None) is False


def test_any():
    assert check(Any, True) is True
    assert check(Any, False) is True
    assert check(Any, 0) is True
    assert check(Any, 'kek') is True
    assert check(Any, 1.0) is True
    assert check(Any, [1, 2, 3]) is True
    assert check(Any, (1, 2, 3)) is True
    assert check(Any, [True]) is True
    assert check(Any, 'True') is True
    assert check(Any, None) is True
    assert check(Any, str) is True
    assert check(Any, -1000) is True


@pytest.mark.skipif(sys.version_info > (3, 13), reason="Before Python 3.14, you couldn't just use Union as an annotation.")
def test_empty_union_old_pythons():
    with pytest.raises(ValueError, match=match('Type must be a valid type object.')):
        check(Union, None)


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Before Python 3.14, you couldn't just use Union as an annotation.")
def test_empty_union():
    assert check(Union, None) == False
    assert check(Union, 1) == False
    assert check(Union, 'kek') == False


def test_empty_optional():
    with pytest.raises(ValueError, match=match('Type must be a valid type object.')):
        check(Optional, None)


def test_union():
    assert check(Union[int, str], 1) is True
    assert check(Union[int, str], 'hello') is True
    assert check(Union[int, float], 1.0) is True

    assert check(Union[int, str], 1.0) is False
    assert check(Union[int, str], None) is False


@pytest.mark.skipif(sys.version_info < (3, 10), reason='Union type expressions appeared in Python 3.10')
def test_union_new_style():
    assert check(int | str, 1) is True
    assert check(int | str, 'hello') is True
    assert check(int | float, 1.0) is True

    assert check(int | str, 1.0) is False
    assert check(int | str, None) is False


def test_union_recursive():
    assert check(Union[int, Union[float, str]], 1) is True
    assert check(Union[int, Union[float, str]], 1.0) is True
    assert check(Union[int, Union[float, str]], 'kek') is True

    assert check(Union[Union[float, str], int], 1) is True
    assert check(Union[Union[float, str], int], 1.0) is True
    assert check(Union[Union[float, str], int], 'kek') is True

    assert check(Union[int, Union[float, str]], None) is False
    assert check(Union[int, Union[float, str]], [1, 2, 3]) is False
    assert check(Union[int, Union[float, str]], ['kek']) is False
    assert check(Union[int, Union[float, str]], ('kek',)) is False
    assert check(Union[int, Union[float, str]], set()) is False

    assert check(Union[Union[float, str], int], None) is False
    assert check(Union[Union[float, str], int], [1, 2, 3]) is False
    assert check(Union[Union[float, str], int], ['kek']) is False
    assert check(Union[Union[float, str], int], ('kek',)) is False
    assert check(Union[Union[float, str], int], set()) is False


@pytest.mark.skipif(sys.version_info < (3, 10), reason='Union type expressions appeared in Python 3.10')
def test_new_style_union_is_recursive():
    assert check(int | float | str, 1) is True
    assert check(int | float | str, 1.0) is True
    assert check(int | float | str, 'kek') is True

    assert check(int | float | str, 1) is True
    assert check(int | float | str, 1.0) is True
    assert check(int | float | str, 'kek') is True

    assert check(int | float | str, None) is False
    assert check(int | float | str, [1, 2, 3]) is False
    assert check(int | float | str, ['kek']) is False
    assert check(int | float | str, ('kek',)) is False
    assert check(int | float | str, set()) is False

    assert check(int | float | str, None) is False
    assert check(int | float | str, [1, 2, 3]) is False
    assert check(int | float | str, ['kek']) is False
    assert check(int | float | str, ('kek',)) is False
    assert check(int | float | str, set()) is False


def test_bool_is_int():
    assert check(int, True) is True
    assert check(int, False) is True

    assert check(Union[int, str], True) is True
    assert check(Union[str, int], True) is True
    assert check(Union[int, str], False) is True
    assert check(Union[str, int], False) is True

    assert check(Optional[int], False) is True
    assert check(Optional[int], True) is True

    assert check(Optional[Union[int, str]], True) is True
    assert check(Optional[Union[int, str]], False) is True


def test_optional():
    assert check(Optional[int], None) is True
    assert check(Optional[int], 1) is True
    assert check(Optional[int], 0) is True
    assert check(Optional[int], -1000) is True

    assert check(Optional[int], 1.0) is False
    assert check(Optional[int], '1.0') is False
    assert check(Optional[int], 'kek') is False
    assert check(Optional[int], 'None') is False
    assert check(Optional[int], [1, 2, 3]) is False
    assert check(Optional[int], ('kek',)) is False
    assert check(Optional[int], (1, 2, 3)) is False
    assert check(Optional[int], set()) is False

    assert check(Optional[str], None) is True
    assert check(Optional[str], '1') is True
    assert check(Optional[str], 'kek') is True
    assert check(Optional[str], '') is True

    assert check(Optional[str], 1.0) is False
    assert check(Optional[str], 1) is False
    assert check(Optional[str], ['kek']) is False

    assert check(Optional[List], []) is True
    assert check(Optional[list], []) is True


@pytest.mark.skipif(sys.version_info < (3, 10), reason='Union type expressions appeared in Python 3.10')
def test_new_style_optional():
    assert check(int | None, None) is True
    assert check(int | None, 1) is True
    assert check(int | None, 0) is True
    assert check(int | None, -1000) is True

    assert check(int | None, 1.0) is False
    assert check(int | None, '1.0') is False
    assert check(int | None, 'kek') is False
    assert check(int | None, 'None') is False
    assert check(int | None, [1, 2, 3]) is False
    assert check(int | None, ('kek',)) is False
    assert check(int | None, (1, 2, 3)) is False
    assert check(int | None, set()) is False

    assert check(str | None, None) is True
    assert check(str | None, '1') is True
    assert check(str | None, 'kek') is True
    assert check(str | None, '') is True

    assert check(str | None, 1.0) is False
    assert check(str | None, 1) is False
    assert check(str | None, ['kek']) is False

    assert check(List | None, []) is True
    assert check(list | None, []) is True


def test_optional_union():
    assert check(Optional[Union[int, str]], None) is True
    assert check(Optional[Union[int, str]], 1) is True
    assert check(Optional[Union[int, str]], 'kek') is True
    assert check(Optional[Union[int, str]], '') is True
    assert check(Optional[Union[int, str]], -1000) is True
    assert check(Optional[Union[int, str]], 0) is True

    assert check(Optional[Union[int, str]], 1.0) is False
    assert check(Optional[Union[int, str]], [1.0]) is False
    assert check(Optional[Union[int, str]], [1]) is False
    assert check(Optional[Union[int, str]], ['kek']) is False
    assert check(Optional[Union[int, str]], [None]) is False
    assert check(Optional[Union[int, str]], [[]]) is False


def test_list_without_arguments():
    assert check(list, [])
    assert check(list, [1, 2, 3])
    assert check(list, ['kek', 'lol'])
    assert check(list, [1, 'kek', 2.0])

    assert check(List, [])
    assert check(List, [1, 2, 3])
    assert check(List, ['kek', 'lol'])
    assert check(List, [1, 'kek', 2.0])

    assert check(list, ()) == False
    assert check(list, (1, 2, 3)) == False
    assert check(list, ('kek', 'lol')) == False
    assert check(list, (1, 'kek', 2.0)) == False

    assert check(List, ()) == False
    assert check(List, (1, 2, 3)) == False
    assert check(List, ('kek', 'lol')) == False
    assert check(List, (1, 'kek', 2.0)) == False

    assert check(list, 1) == False
    assert check(list, 1.0) == False
    assert check(list, 'kek') == False
    assert check(list, None) == False


def test_tuple_without_arguments():
    assert check(tuple, ())
    assert check(tuple, (1,))
    assert check(tuple, (None,))
    assert check(tuple, ('kek',))
    assert check(tuple, (1, 2, 3))
    assert check(tuple, ('lol', 'kek'))

    assert check(Tuple, ())
    assert check(Tuple, (1,))
    assert check(Tuple, (None,))
    assert check(Tuple, ('kek',))
    assert check(Tuple, (1, 2, 3))
    assert check(Tuple, ('lol', 'kek'))

    assert check(tuple, []) == False
    assert check(tuple, [(1, 2, 3)]) == False
    assert check(tuple, '(1, 2, 3)') == False
    assert check(tuple, 'kek') == False
    assert check(tuple, 1) == False
    assert check(tuple, 1.0) == False
    assert check(tuple, None) == False

    assert check(Tuple, []) == False
    assert check(Tuple, [(1, 2, 3)]) == False
    assert check(Tuple, '(1, 2, 3)') == False
    assert check(Tuple, 'kek') == False
    assert check(Tuple, 1) == False
    assert check(Tuple, 1.0) == False
    assert check(Tuple, None) == False



def test_set_without_arguments():
    assert check(set, set())
    assert check(set, {1})
    assert check(set, {None})
    assert check(set, {'kek'})
    assert check(set, {1, 2, 3})
    assert check(set, {'lol', 'kek'})

    assert check(Set, set())
    assert check(Set, {1})
    assert check(Set, {None})
    assert check(Set, {'kek'})
    assert check(Set, {1, 2, 3})
    assert check(Set, {'lol', 'kek'})

    assert check(set, []) == False
    assert check(set, [(1, 2, 3)]) == False
    assert check(set, '(1, 2, 3)') == False
    assert check(set, 'kek') == False
    assert check(set, 1) == False
    assert check(set, 1.0) == False
    assert check(set, None) == False

    assert check(Set, []) == False
    assert check(Set, [(1, 2, 3)]) == False
    assert check(Set, '(1, 2, 3)') == False
    assert check(Set, 'kek') == False
    assert check(Set, 1) == False
    assert check(Set, 1.0) == False
    assert check(Set, None) == False

def test_dict_without_arguments():
    assert check(dict, {})
    assert check(dict, {'lol': 'kek'})
    assert check(dict, {1: 'kek'})
    assert check(dict, {'lol': 1})
    assert check(dict, {'lol': None})
    assert check(dict, {1: None})

    assert check(Dict, {})
    assert check(Dict, {'lol': 'kek'})
    assert check(Dict, {1: 'kek'})
    assert check(Dict, {'lol': 1})
    assert check(Dict, {'lol': None})
    assert check(Dict, {1: None})

    assert check(dict, []) == False
    assert check(dict, set([1, 2, 3])) == False
    assert check(dict, None) == False
    assert check(dict, 1) == False
    assert check(dict, 1.0) == False
    assert check(dict, '{1: None}') == False
    assert check(dict, 'kek') == False
    assert check(dict, dict) == False
    assert check(dict, Dict) == False

    assert check(Dict, []) == False
    assert check(Dict, set([1, 2, 3])) == False
    assert check(Dict, None) == False
    assert check(Dict, 1) == False
    assert check(Dict, 1.0) == False
    assert check(Dict, '{1: None}') == False
    assert check(Dict, 'kek') == False
    assert check(Dict, dict) == False
    assert check(Dict, Dict) == False


@pytest.mark.skipif(sys.version_info < (3, 9), reason='Subscribing to objects became available in Python 3.9')
def test_content_of_list_is_not_checking():
    assert check(list[int], [])
    assert check(list[int], ['lol', 'kek'])
    assert check(list[int], [1.0, 2.0])
    assert check(list[int], [None, None])
    assert check(list[int], [None, 'kek', 1, 1.0])

    assert check(List[int], [])
    assert check(List[int], ['lol', 'kek'])
    assert check(List[int], [1.0, 2.0])
    assert check(List[int], [None, None])
    assert check(List[int], [None, 'kek', 1, 1.0])


@pytest.mark.skipif(sys.version_info < (3, 9), reason='Subscribing to objects became available in Python 3.9')
def test_content_of_tuple_is_not_checking():
    assert check(tuple[int], ())
    assert check(tuple[int], ('lol', 'kek'))
    assert check(tuple[int], (1.0, 2.0))
    assert check(tuple[int], (None, None))
    assert check(tuple[int], (None, 'kek', 1, 1.0))

    assert check(Tuple[int], ())
    assert check(Tuple[int], ('lol', 'kek'))
    assert check(Tuple[int], (1.0, 2.0))
    assert check(Tuple[int], (None, None))
    assert check(Tuple[int], (None, 'kek', 1, 1.0))


@pytest.mark.skipif(sys.version_info < (3, 9), reason='Subscribing to objects became available in Python 3.9')
def test_content_of_dict_is_not_checking():
    assert check(dict[int, int], {})
    assert check(dict[int, int], {1: 'kek'})
    assert check(dict[int, int], {'lol': 'kek'})
    assert check(dict[int, int], {'lol': 1})
    assert check(dict[int, int], {1.0: 1})

    assert check(Dict[int, int], {})
    assert check(Dict[int, int], {1: 'kek'})
    assert check(Dict[int, int], {'lol': 'kek'})
    assert check(Dict[int, int], {'lol': 1})
    assert check(Dict[int, int], {1.0: 1})


@pytest.mark.skipif(sys.version_info < (3, 9), reason='Subscribing to objects became available in Python 3.9')
def test_content_of_set_is_not_checking():
    assert check(set[int], set())
    assert check(set[int], set(['lol', 'kek']))
    assert check(set[int], set([1, 'kek']))
    assert check(set[int], set([1, None]))
    assert check(set[int], set([None, None]))
    assert check(set[int], set(['1', '2']))


def test_try_to_pass_not_type_object_as_type():
    with pytest.raises(ValueError, match=match('Type must be a valid type object.')):
        check(1, 1)

    with pytest.raises(ValueError, match=match('Type must be a valid type object.')):
        check('1', 1)

    with pytest.raises(ValueError, match=match('Type must be a valid type object.')):
        check('SomeClass', 1)


def test_simle_isinstance():
    class SomeType:
        pass

    assert check(SomeType, SomeType())

    assert check(SomeType, None) == False
    assert check(SomeType, 1) == False
    assert check(SomeType, 'SomeType') == False
    assert check(SomeType, 1.5) == False


def test_sequence():
    assert check(Sequence, [1, 2, 3])
    assert check(Sequence, (1, 2, 3))
    assert check(Sequence, 'kek')

    assert check(Sequence, 1) == False


@pytest.mark.skipif(sys.version_info < (3, 9), reason='Subscribing to objects became available in Python 3.9')
def test_sequence_is_not_checking_content():
    assert check(Sequence[str], (1, 2, 3))
    assert check(Sequence[str], [1, 2, 3])
