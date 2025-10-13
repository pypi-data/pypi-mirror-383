# (generated with --quick)

import typing
from typing import Any, List, Tuple, Type

Iterable: Type[typing.Iterable]
Iterator: Type[typing.Iterator]

def DiffListsByKey(iterA: typing.Iterator, iterB: typing.Iterator, keyA, keyB) -> Tuple[list, List[Tuple[Any, Any]], list]: ...
def DiffUnsortedLists(listA: typing.Iterable, listB: typing.Iterable, keyA, keyB) -> Any: ...
def _DiffLists(iterA, iterB, compare) -> Tuple[list, List[Tuple[Any, Any]], list]: ...
