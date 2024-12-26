from functools import wraps
from itertools import chain
from time import gmtime, struct_time, strftime
from typing import Optional, Set, List, Dict, Tuple

from .LoggedDict import LoggedDict
from .LoggedValue import DATEFORMAT

def _checkDeletedUpdate(func, canDiff=False):
    @wraps(func)
    def wrapper(self, *kargs, **kwargs):
        if self.deleted:
            raise ValueError("Attempting to update a deleted record")
        result = False

        changes = f"{func.__name__} kargs={kargs} kwargs={kwargs}"
        if canDiff:
            purgedKWParams = {k: v for k, v in kwargs.items() if k not in {'timestamp'}}
            auxChanges = self.diff(*kargs, **purgedKWParams)
            changes = f"{auxChanges}"

        result = func(self, *kargs, **kwargs)

        if result:
            dateField = kwargs.get('timestamp', gmtime())
            self.addHistory(dateField, f"Updated data {changes}")
        return result

    return wrapper


def _checkDeletedRead(func):
    @wraps(func)
    def wrapper(self, *kargs, **kwargs):
        if self.deleted:
            raise ValueError("Attempting to read a deleted record")
        result = func(self, *kargs, **kwargs)
        return result

    return wrapper


class DictData(LoggedDict):
    def __init__(self, timestamp: Optional[struct_time] = None, exclusions: Optional[Set] = None):
        super(DictData, self).__init__(exclusions=exclusions)
        self.last_updated = timestamp or gmtime()
        self.deleted = False
        self.history: List = []

        self.addHistory(data="Creation without data", timestamp=self.last_updated)

    def isDeleted(self):
        return self.deleted

    def addHistory(self, data, timestamp: Optional[struct_time] = None):
        dateField = timestamp or gmtime()
        self.history.append((dateField, data))

    def delete(self, timestamp: Optional[struct_time] = None) -> bool:
        if self.isDeleted():
            return False
        dateField = timestamp or gmtime()
        self.last_updated = dateField
        self.deleted = True
        self.addHistory(data="Deleted", timestamp=dateField)

        return True

    def restore(self, timestamp: Optional[struct_time] = None) -> bool:
        if not self.isDeleted():
            return False

        dateField = timestamp or gmtime()
        self.last_updated = dateField
        self.deleted = False
        self.addHistory(data="Restored", timestamp=dateField)

        return True

    def showV(self, compact=True, indent: int = 0, firstIndent: Optional[int] = None):
        delTxt = " D" if self.deleted else ""
        dateTxt = strftime(DATEFORMAT, self.last_updated)
        lenTxt = f"l"":"f"{len(self.history)}"

        result = (f"{super(DictData, self).show(compact=compact, indent=indent, firstIndent=firstIndent)}" + f" (t:{dateTxt}{delTxt} {lenTxt})")

        return result

    def __repr__(self):
        return self.showV(compact=True)

    __str__ = __repr__

    __setitem__ = _checkDeletedUpdate(LoggedDict.__setitem__, canDiff=False)
    update = _checkDeletedUpdate(LoggedDict.update, canDiff=True)
    purge = _checkDeletedUpdate(LoggedDict.purge)
    addExclusion = _checkDeletedUpdate(LoggedDict.addExclusion)
    replace = _checkDeletedUpdate(LoggedDict.replace, canDiff=True)

    __getitem__ = _checkDeletedRead(LoggedDict.__getitem__)
    __len__ = _checkDeletedRead(LoggedDict.__len__)
    get = _checkDeletedRead(LoggedDict.get)
    # getV=_checkDeletedRead(LoggedDict.getV)
    keys = _checkDeletedRead(LoggedDict.keys)
    items = _checkDeletedRead(LoggedDict.items)
    values = _checkDeletedRead(LoggedDict.values)
    # keysV=_checkDeletedRead(LoggedDict.keysV)
    # itemsV=_checkDeletedRead(LoggedDict.itemsV)
    # valuesV=_checkDeletedRead(LoggedDict.valuesV)

    _asdict = _checkDeletedRead(LoggedDict._asdict)
    diff = _checkDeletedRead(LoggedDict.diff)
    compareWithOtherKeys = _checkDeletedRead(LoggedDict.compareWithOtherKeys)
    # show=_checkDeletedRead(LoggedDict.show)
    # __repr__=_checkDeletedRead(LoggedDict.__repr__)
    __ne__ = _checkDeletedRead(LoggedDict.__ne__)
    __eq__ = _checkDeletedRead(LoggedDict.__eq__)


class DictOfLoggedDict:
    def __init__(self, exclusions: Optional[Set[str]] = None, timestamp: Optional[struct_time] = None):
        changeTime = timestamp or gmtime()
        if exclusions is not None and not isinstance(exclusions, (set, list, tuple)):
            raise TypeError(
                f"DictOfLoggedDict: expected set/list/tuple for exclusions: '{exclusions}' ({type(exclusions)}")

        self.current: Dict[str, DictData] = dict()

        self.exclusions: Set[str] = set(exclusions) if exclusions else set()
        self.timestamp: struct_time = changeTime
        self.numChanges:int = 0
        self.history:List[Tuple[struct_time,str]] = []

        self.addHistory("Created",changeTime)

    def __getitem__(self, k):
        if k not in self.current:
            raise KeyError(f"Requested key '{k}' does not exists")
        auxResult = self.current[k]
        if auxResult.isDeleted():
            raise KeyError(f"Attempting to get a deleted item '{k}'.You must undelete first")
        return auxResult._asdict()

    def __setitem__(self, k, v, timestamp: Optional[struct_time] = None):
        changeTime = timestamp or gmtime()
        currVal = self.current.get(k, DictData(exclusions=self.exclusions, timestamp=changeTime))
        changes = currVal.replace(v, timestamp=changeTime)

        self.current[k] = currVal
        if changes:
            self.timestamp = changeTime
            self.numChanges += 1
            self.addHistory(f"Set '{k}':{currVal}")
        return changes

    def addHistory(self, data:str, timestamp: Optional[struct_time] = None):
        dateField = timestamp or gmtime()
        self.history.append((dateField, data))

    def get(self, key):
        if key not in self.current:
            raise KeyError(f"Unknown key '{key}'")
        if self.current[key].isDeleted():
            raise KeyError(f"Requested item is deleted '{key}'")
        return self.current.get(key)._asdict()

    def getV(self, key):
        if key not in self.current:
            raise KeyError(f"Unknown key '{key}'")
        return self.current.get(key)

    def pop(self, key, *kargs, timestamp: Optional[struct_time] = None):
        changeTime = timestamp or gmtime()
        if (key not in self.current) or (self.current[key].isDeleted()):
            if kargs:
                return kargs[0]  # default
            elif (key not in self.current):
                raise KeyError(f"Unknown key '{key}'")
            else:
                raise KeyError(f"Requested item is deleted '{key}'")
        result = self.get(key)

        changes = self.getV(key).delete(timestamp=changeTime)
        if changes:
            self.timestamp = changeTime

        return result

    def update(self, newValues, timestamp: Optional[struct_time] = None, replaceInner: bool = False):
        changeTime = timestamp or gmtime()
        result = False

        if not isinstance(newValues, (dict, DictOfLoggedDict)):
            raise TypeError(f"update: expected dict or DictOfLoggedDict, got '{type(newValues)}'")

        for k, v in newValues.items():
            currVal = self.current.get(k, DictData(exclusions=self.exclusions, timestamp=timestamp))

            if currVal.isDeleted():
                result |= currVal.restore()

            r1 = currVal.replace(v, timestamp=changeTime) if replaceInner else currVal.update(v, timestamp=changeTime)

            if r1:
                self.current[k] = currVal

            result |= r1
        if result:
            self.timestamp=changeTime
            self.numChanges += 1
            self.addHistory(f"Update {newValues}",timestamp=timestamp)
        return result

    def purge(self, *kargs, timestamp: Optional[struct_time] = None):
        changeTime = timestamp or gmtime()
        result = False
        keys2delete = set(chain(*kargs))

        for k in keys2delete:
            if k in self.current:
                result |= self.current[k].delete(timestamp=changeTime)

        if result:
            keysStr = ",".join(map(lambda x:f"'{x}'",keys2delete))
            self.timestamp=changeTime
            self.numChanges += 1
            self.addHistory(f"Purged {keysStr}",timestamp=timestamp)

        return result

    def addExclusion(self, *kargs, timestamp: Optional[struct_time] = None) -> bool:
        keys2add = set(chain(*kargs))
        changed = False
        self.exclusions.update(keys2add)

        for v in self.valuesV():
            if v.isDeleted():
                continue
            changed |=  v.addExclusion(keys2add, timestamp=timestamp)

        return changed

    def removeExclusion(self, *kargs):
        keys2remove = set(chain(*kargs))

        self.exclusions.difference_update(keys2remove)

        for v in self.valuesV():
            if v.isDeleted():
                continue
            v.removeExclusion(keys2remove)

    def keys(self):
        for k, v in self.current.items():
            if not v.isDeleted():
                yield k

    def items(self):
        for k, v in self.current.items():
            if not v.isDeleted():
                yield k, v._asdict()

    def values(self):
        for v in self.current.values():
            if not v.isDeleted():
                yield v._asdict()

    def keysV(self):
        return self.current.keys()

    def itemsV(self):
        return self.current.items()

    def valuesV(self):
        return self.current.values()

    def _asdict(self):
        result = {k: v for k, v in self.items()}
        return result

    def subkeys(self):
        result = set()

        for v in self.values():
            result.update(v.keys())

        return result

    def diff(self, other):  #:(Dict[Any,(LoggedDict,dict)],LoggedDict)
        if not isinstance(other, (dict, DictOfLoggedDict)):
            raise TypeError(f"Parameter expected to be a dict or DictOfLoggedDict. Provided {type(other)}")

        result = DictOfLoggedDictDiff()

        currentKeys = set(self.current.keys())
        sharedKeys = set(currentKeys).intersection(other.keys())
        missingKeys = set(currentKeys).difference(other.keys())
        newKeys = set(other.keys()).difference(currentKeys)

        for k in sorted(newKeys):
            result.addKey(k, other.get(k))
        for k in sorted(sharedKeys):
            currVal = self.getV(k)
            otherVal = other.get(k) if isinstance(other,dict) else other.getV(k)
            result.change(k, currVal, otherVal)
        for k in sorted(missingKeys):
            result.removeKey(k, self.getV(k))

        return result

    def __len__(self):
        return sum(1 for _ in self.keys())

    def lenV(self):
        return len(self.current)


    def show(self,compact:bool=False, indent: int = 0, firstIndent: Optional[int] = None):
        if firstIndent is None:
            firstIndent = indent

        metadataStr = self.buildMetadataStr()
        claves = sorted(self.keysV())

        if compact:
            indent = 0
            firstIndent = 0


        if self.lenV() == 0:
            return f"{self.current} {metadataStr}"
        if compact:
            result="{" + ", ".join(map(lambda k: f"'{k}':{self.current[k].showV(compact,indent,firstIndent)}",claves)) +"}"+ f" {metadataStr}"
        else:
            longestK = 0 if compact else max([len(k) for k in claves])
            linesList = []
            flag=False
            for k in claves:
                extraIndent = " " *(2 if flag else 0)
                auxFirst = (longestK - len(k))
                auxIndent = longestK +2 + 4
                newLine =extraIndent + f"'{k}': " + self.current[k].showV(compact=compact,indent=auxIndent,firstIndent=auxFirst)
                linesList.append(newLine             )
                flag=True
            result = "{ " + ",\n".join(linesList) + "\n} " + metadataStr
        return result

    def buildMetadataStr(self):
        dateTxt = strftime(DATEFORMAT, self.timestamp)
        lenTxt = f"l"":"f"{self.numChanges}"
        metadataStr = f"[t:{dateTxt} {lenTxt}]"
        return metadataStr

    def __repr__(self):
        return self.show(compact=True)


    def __ne__(self, other):
        return self.diff(other)


class DictOfLoggedDictDiff:
    def __init__(self):
        self.changeCount: int = 0
        self.added: dict = {}
        self.changed: dict = {}
        self.removed: dict = {}

    def change(self, k, vOld: LoggedDict, vNew):
        diff = vOld.diff(vNew)
        if diff:
            self.changed[k] = diff
            self.changeCount += 1

    def addKey(self, k, vNew):
        self.added[k] = vNew
        self.changeCount += 1

    def removeKey(self, k, vOld):
        self.removed[k] = vOld
        self.changeCount += 1

    def __bool__(self):
        return (self.changeCount > 0)

    def show(self, indent: int = 0, compact: bool = False, sepCompact=','):
        if self.changeCount == 0:
            return ""
        result = []
        result.extend([(k, f"'{k}': A {v}") for k, v in self.added.items()])
        result.extend([(k, f"'{k}': D {v}") for k, v in self.removed.items()])
        result.extend([(k, f"'{k}': C {v}") for k, v in self.changed.items()])

        auxSep = f"{sepCompact} " if compact else '\n'
        auxIndent = 0 if compact else indent

        resultStr = auxSep.join([f"{' ' * ((auxIndent * 2) + 1)}{v[1]}" for v in sorted(result, key=lambda x: x[0])])

        return resultStr

    def __repr__(self):
        return self.show(compact=True)
