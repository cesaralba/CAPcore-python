from itertools import chain
from time import gmtime, struct_time
from typing import Tuple, Set, Optional, Dict

from .LoggedValue import LoggedValue


class LoggedDictDiff:
    """
    Contains the differences between a LoggedDict and another Logged Dict or a diff

    It is intended to be created and updated by LoggedDict.diff
    """

    def __init__(self):
        self.changeCount: int = 0
        self.added: dict = {}
        self.changed: dict = {}
        self.removed: dict = {}

    def change(self, k, vOld, vNew):
        if vOld != vNew:
            self.changed[k] = (vOld, vNew)
            self.changeCount += 1

    def addKey(self, k, vNew):
        self.added[k] = vNew
        self.changeCount += 1

    def removeKey(self, k, vOld):
        self.removed[k] = vOld
        self.changeCount += 1

    def __bool__(self):
        """
        :return: True if objects are different, False if they are equal
        """
        return (self.changeCount > 0)

    def show(self, indent: int = 0, compact: bool = False, sepCompact=',') -> str:
        if self.changeCount == 0:
            return ""
        result = []
        result.extend([(k, f"'{k}': A '{v}'") for k, v in self.added.items()])
        result.extend([(k, f"'{k}': D '{v}'") for k, v in self.removed.items()])
        result.extend([(k, f"'{k}': C '{v[0]}' -> '{v[1]}'") for k, v in self.changed.items()])

        auxSep = f"{sepCompact} " if compact else '\n'
        auxIndent = 0 if compact else indent

        resultStr = auxSep.join([f"{' ' * (auxIndent * 2)}{v[1]}" for v in sorted(result, key=lambda x: x[0])])

        return resultStr

    def __len__(self):
        return self.changeCount

    def __repr__(self):
        return self.show(compact=True)

    __str__ = __repr__


class LoggedDict:
    def __init__(self, exclusions: Optional[Set] = None, timestamp=None):

        if exclusions is not None and not isinstance(exclusions, (set, list, tuple)):
            raise TypeError(f"LoggedDict: expected set/list/tuple for exclusions: {exclusions}")

        self.current:Dict[LoggedValue] = {}
        self.exclusions: Set[str] = set(exclusions) if exclusions else set()
        self.timestamp = timestamp or gmtime()

    def __getitem__(self, item):
        return self.current.__getitem__(item).get()

    def __setitem__(self, k, v, timestamp=None):
        if k in self.exclusions:
            raise KeyError(f"Key '{k}' in exclusions: {sorted(self.exclusions)}")
        currVal = self.current.get(k, LoggedValue())  # default=
        changes = currVal.set(v, timestamp=timestamp)

        self.current[k] = currVal
        return changes

    def __len__(self):
        result = len(list(self.keys()))
        return result

    def get(self, key, default=None):
        if key in self.current and not self.current[key].isDeleted():
            return self.__getitem__(key)
        return default

    def getV(self, key, default=None):
        return self.current.get(key, default)

    def update(self, newValues, timestamp=None):
        changeTime = timestamp or gmtime()
        result = False
        newValIter = newValues
        if isinstance(newValues, dict):
            newValIter = newValues.items()

        for k, v in newValIter:
            if k in self.exclusions:
                continue
            v1 = self.current.get(k, LoggedValue(timestamp=changeTime))
            r1 = v1.set(v, changeTime)
            if r1:
                self.current[k] = v1

            result |= r1

        return result

    def purge(self, *kargs, timestamp=None) -> bool:
        changeTime = timestamp or gmtime()
        result = False
        keys2delete = set(chain(*kargs))
        for k in keys2delete:
            if k in self.current:
                result |= self.current[k].clear(timestamp=changeTime)

        return result

    def addExclusion(self, *kargs, timestamp: Optional[struct_time] = None) -> bool:
        keys2add = set(chain(*kargs))
        changed = False
        self.exclusions.update(keys2add)
        changed |= self.purge(keys2add,timestamp=timestamp)

        return changed

    def removeExclusion(self, *kargs):
        keys2remove = set(chain(*kargs))
        self.exclusions.difference_update(keys2remove)

    def keys(self):
        for k, v in self.current.items():
            if not v.isDeleted():
                yield k

    def items(self):
        for k, v in self.current.items():
            if not v.isDeleted():
                yield k, v.get()

    def values(self):
        for v in self.current.values():
            if not v.isDeleted():
                yield v.get()

    def keysV(self):
        return self.current.keys()

    def itemsV(self):
        return self.current.items()

    def valuesV(self):
        return self.current.values()

    def _asdict(self):
        result = dict(self.items())
        return result

    def replace(self, other, timestamp=None) -> bool:
        result = False
        if not isinstance(other, (dict, LoggedDict)):
            raise TypeError(f"Parameter expected to be a dict or LoggedDict. Provided {type(other)}")

        missingKeys, newKeys, sharedKeys = self.compareWithOtherKeys(other)

        result |= self.purge(missingKeys, timestamp=timestamp)
        for k in sorted(newKeys.union(sharedKeys)):
            if k in self.exclusions:
                continue
            result |= self.__setitem__(k, other.get(k), timestamp=timestamp)
        return result

    def diff(self, newValues) -> LoggedDictDiff:
        """
        Returns the differences between a loggedDict and another loggedDict or a dict
        :param newValues: a loggedDict or a dict
        :return: a Difference object
        """
        if not isinstance(newValues, (dict, LoggedDict)):
            raise TypeError(f"Parameter expected to be a dict or LoggedDict. Provided {type(newValues)}")

        result = LoggedDictDiff()

        missingKeys, newKeys, sharedKeys = self.compareWithOtherKeys(newValues)

        for k in sorted(newKeys):
            if k in self.exclusions:
                continue
            result.addKey(k, newValues.get(k))
        for k in sorted(sharedKeys):
            currVal = self.get(k)
            otherVal = newValues.get(k)
            result.change(k, currVal, otherVal)
        for k in sorted(missingKeys):
            result.removeKey(k, self.get(k))

        return result

    def compareWithOtherKeys(self, newValues) -> Tuple[Set, Set, Set]:
        if not isinstance(newValues, (dict, LoggedDict)):
            raise TypeError(f"Parameter expected to be a dict or LoggedDict. Provided {type(newValues)}")

        otherKeys = set(newValues.keys()) if isinstance(newValues, LoggedDict) else set(newValues.keys())
        currentKeys = set(self.keys())
        sharedKeys = set(currentKeys).intersection(otherKeys)
        missingKeys = set(currentKeys).difference(otherKeys)
        newKeys = set(otherKeys).difference(currentKeys)
        return missingKeys, newKeys, sharedKeys

    def show(self, compact=True, indent: int = 0, firstIndent: Optional[int] = None):
        if firstIndent is None:
            firstIndent = indent
        auxResult = {k: repr(self.getV(k)) for k in sorted(self.keysV())}
        if len(auxResult) == 0:
            return "{}"
        if compact or len(auxResult) == 1:
            if compact:
                indent = 0
                firstIndent = 0
            result = (" " * firstIndent) + "{" + ", ".join([f"'{k}': {v}" for k, v in auxResult.items()]) + "}"
            return result

        claves = sorted(auxResult.keys())
        firstLine = (" " * firstIndent) + "{ " + f"'{claves[0]}': {auxResult[claves[0]]},"
        nextLines = ",\n".join([" " * (indent + 2) + f"'{k}': {auxResult[k]}" for k in claves[1:]])
        lastLine = " " * (indent) + "}"
        result = "\n".join([firstLine, nextLines, lastLine])
        return result

    def __ne__(self, other):
        return self.diff(other)

    def __eq__(self, other):
        return not (self.diff(other))

    def __repr__(self):
        return self.show(compact=True)
