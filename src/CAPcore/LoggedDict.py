from time import gmtime
from itertools import chain
from .LoggedValue import LoggedValue

INDENTSEPR = 2
SEPRPR = ",\n" + " " * INDENTSEPR


class LoggedDict:
    def __init__(self, exclusions: set = None):

        if exclusions is not None and not isinstance(exclusions, (set, list, tuple)):
            raise TypeError(f"LoggedDict: expected set/list/tuple for exclusions: {exclusions}")

        self.current = dict()
        self.exclusions = exclusions or set()
        self.timestamp = gmtime()

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

    def getValue(self, key, default=None):
        return self.current.get(key, default)

    def update(self, newValues, timestamp=None):
        changeTime = timestamp or gmtime()
        result = []
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
            result.append(r1)

        return any(result)

    def purge(self, *kargs, timestamp=None):
        changeTime = timestamp or gmtime()
        result = []
        keys2delete = set(chain(*kargs))
        for k in keys2delete:
            if k in self.exclusions:
                continue
            if k in self.current:
                r1 = self.current[k].clear(timestamp=changeTime)
                result.append(r1)

        return any(result)

    def addExclusion(self, *kargs):
        keys2add = set(chain(*kargs))
        changed = False
        self.exclusions.update(keys2add)
        currKeys = self.exclusions.intersection(self.current.keys())
        for k in currKeys:
            if k in self.exclusions:
                self.current.pop(k)
                changed = True

        return changed

    def removeExclusion(self, *kargs):
        keys2remove = set(chain(*kargs))
        self.exclusions.difference_update(keys2remove)

    def keys(self):
        for k,v in self.current.items():
            if not v.isDeleted():
                yield k

    def items(self):
        for k,v in self.current.items():
            if not v.isDeleted():
                yield k,v.get()

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

    def diff(self, other):
        if not isinstance(other, (dict, LoggedDict)):
            raise TypeError(f"Parameter expected to be a dict or LoggedDict. Provided {type(other)}")

        result = LoggedDictDiff()

        currentKeys = {k for k, v in self.current.items() if not v.isDeleted()}
        sharedKeys = set(currentKeys).intersection(other.keysV())
        missingKeys = set(currentKeys).difference(other.keysV())
        newKeys = set(other.keysV()).difference(currentKeys)

        for k in sorted(newKeys):
            if k in self.exclusions:
                continue
            result.addKey(k, other.get(k))
        for k in sorted(sharedKeys):
            currVal = self.get(k)
            otherVal = other.get(k)
            result.change(k, currVal, otherVal)
        for k in sorted(missingKeys):
            result.removeKey(k, self.get(k))

        return result

    def replace(self, other, timestamp=None):
        if not isinstance(other, (dict, LoggedDict)):
            raise TypeError(f"Parameter expected to be a dict or LoggedDict. Provided {type(other)}")

        currentKeys = {k for k, v in self.current.items() if not v.isDeleted()}
        sharedKeys = set(currentKeys).intersection(other.keysV())
        missingKeys = set(currentKeys).difference(other.keysV())
        newKeys = set(other.keysV()).difference(currentKeys)

        self.purge(missingKeys, timestamp=timestamp)

        for k in sorted(newKeys.union(sharedKeys)):
            if k in self.exclusions:
                continue
            self.__setitem__(k, other.get(k), timestamp=timestamp)

    def __repr__(self):
        auxResult = {k: self.current[k].__repr__() for k in sorted(self.current)}

        if len(auxResult) == 1:
            result = "{  " + "".join([f"{k.__repr__()}: {v}" for k, v in auxResult.items()]) + "}"
        else:
            claves = sorted(auxResult.keys())
            result = ("{ " + SEPRPR.join([f"{k.__repr__()}: {auxResult[k]}" for k in claves[
                                                                                     :-1]]) + SEPRPR + f"{claves[-1].__repr__()}: {auxResult[claves[-1]]}" + "\n}")
        return result

    def __ne__(self, other):
        return self.diff(other)


class LoggedDictDiff:
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
        return (self.changeCount > 0)

    def show(self, indent: int = 0, compact: bool = False, sepCompact=',') -> str:
        if self.changeCount == 0:
            return ""
        result = []
        result.extend([(k, f"{k}: A '{v}'") for k, v in self.added.items()])
        result.extend([(k, f"{k}: D '{v}'") for k, v in self.removed.items()])
        result.extend([(k, f"{k}: C '{v[0]}' -> '{v[1]}'") for k, v in self.changed.items()])

        auxSep = f"{sepCompact} " if compact else '\n'
        auxIndent = 0 if compact else indent

        resultStr = auxSep.join([f"{' ' * ((auxIndent * 2) + 1)}{v[1]}" for v in sorted(result, key=lambda x: x[0])])

        return resultStr

    def __repr__(self):
        return self.show(compact=True)


def dumpLoggedDict(k, v, indent=2):
    AUXSEP = "\n" + " " * (indent + 1)
    vSplit = v.split('\n')

    if len(vSplit) == 1:
        result = (" " * indent) + f"{repr(k)}: {v}"
    else:
        result = (" " * (indent - 2)) + f"{repr(k)}: {vSplit[0]}" + AUXSEP
        result = result + AUXSEP.join(vSplit[1:])
        result = result + " " * (indent + 1)

    return result
