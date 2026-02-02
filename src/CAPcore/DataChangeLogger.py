from datetime import datetime
from pprint import pp, pformat
from typing import Optional, Dict, List, Any, Tuple

from .DictLoggedDict import DictOfLoggedDictDiff
from .LoggedDict import LoggedDictDiff
from .Misc import getUTC

DATEFORMAT = "%Y-%m-%d %H:%M:%S.%f%z"


class DataChanges:
    def __init__(self):
        self.timestamp: Optional[datetime] = None
        self.changeSet: Dict[str, List[Any]] = {}

    def update(self, timestamp: datetime, changeInfo: Dict[str, Any]):
        raise NotImplementedError("update: You must use a derived class")

    def __lt__(self, other):
        return self.timestamp < other.timestamp

    @classmethod
    def merge(cls, *kargs):
        raise NotImplementedError("merge: You must use derived classes")


class DataChangesRaw(DataChanges):
    def update(self, timestamp: datetime, changeInfo: Dict[str, Any]) -> bool:
        changes: bool = False

        if self.timestamp and (self.timestamp != timestamp):
            raise ValueError(
                f"Updating a datachange set with a different timestamp. "
                f"Current: {self.timestamp.strftime(DATEFORMAT)}. "
                f"New: {timestamp.strftime(DATEFORMAT)}")

        for k, vNew in changeInfo.items():
            if k not in self.changeSet:
                self.changeSet[k] = [vNew]
                changes |= True
            else:
                currLast = self.changeSet[k][-1]
                if currLast == vNew:
                    continue
                self.changeSet[k].append(vNew)
                changes |= True

        if changes:
            self.timestamp = getUTC() if timestamp is None else timestamp

        return changes

    @classmethod
    def merge(cls, *kargs):
        if not all(isinstance(k, cls) for k in kargs):
            paramList = [type(v).__name__ for v in kargs]
            statusList = [isinstance(v, cls) for v in kargs]
            message = (f"{cls.__name__}.merge requires all parameters to be class {cls.__name__}. "
                       f"Provided: [{','.join(str(p) for p in zip(paramList, statusList))}]")
            raise ValueError(message)

        result = genStoreDict()

        c: DataChangesRaw
        for c in sorted(kargs):
            if 'dicts' not in c.changeSet:
                continue
            result['timestamps'].append(c.timestamp)
            for chgItem in c.changeSet.get('dicts', []):
                key: str
                val: Tuple[Any, DictOfLoggedDictDiff | LoggedDictDiff]
                for key, val in chgItem.items():
                    if isinstance(val, LoggedDictDiff):
                        result['values'][key] = MergeLoggedDictDiff(result['values'].get(key, genStoreDict()), val,
                                                                    c.timestamp)
                    elif isinstance(val, DictOfLoggedDictDiff):
                        pp(result)
                        result['values'][key] = MergeDictLoggedDictDiff(result['values'].get(key, genStoreDict()), val,
                                                                        c.timestamp)
                    else:
                        raise TypeError(
                            f"Don't know hot to handle {type(val).__name__}. "
                            f"Accepted types:DictOfLoggedDictDiff,LoggedDictDiff ")

        return result


class DataChangesTuples(DataChanges):

    def update(self, timestamp: datetime, changeInfo: Dict[str, Tuple[Any, Any]]) -> bool:
        changes: bool = False

        if self.timestamp and (self.timestamp != timestamp):
            raise ValueError(
                f"Updating a datachange set with a different timestamp. "
                f"Current: {self.timestamp.strftime(DATEFORMAT)}. "
                f"New: {timestamp.strftime(DATEFORMAT)}")

        for k, (vOld, vNew) in changeInfo.items():
            if k not in self.changeSet:
                self.changeSet[k] = [vOld, vNew]
                changes |= True
            else:
                currLast = self.changeSet[k][-1]
                if currLast != vOld:
                    raise ValueError(
                        f"Updating a datachange set. Breaking a transition. Key: '{k}'. Old: '{currLast}'. "
                        f"New: '{vOld}'")
                if currLast == vNew:
                    continue
                self.changeSet[k].append(vNew)
                changes |= True

        if changes:
            self.timestamp = getUTC() if timestamp is None else timestamp

        return changes

    @classmethod
    def merge(cls, *kargs):
        if not all(isinstance(k, cls) for k in kargs):
            paramList = [type(v).__name__ for v in kargs]
            statusList = [isinstance(v, cls) for v in kargs]
            message = (f"{cls.__name__}.merge requires all parameters to be class {cls.__name__}. "
                       f"Provided: [{','.join(str(p) for p in zip(paramList, statusList))}]")
            raise ValueError(message)

        result = genStoreDict()

        c: DataChangesTuples
        for c in sorted(kargs):
            result['timestamps'].append(c.timestamp)
            k: str
            v: Tuple[Any, Any]
            for k, v in c.changeSet.items():
                result['values'][k] = updateDataSeq(currData=result['values'].get(k, genStoreValue()), newValues=v,
                                                    timestamp=c.timestamp)

        return result


def genStoreValue():
    return {'changeCounter': 0, 'values': [], 'timestamps': []}


def genStoreDict():
    return {'timestamps': [], 'values': {}}


def MergeLoggedDictDiff(mergedData: Dict, change2add: LoggedDictDiff, timestamp: datetime):
    for k, v in change2add.added.items():
        mergedData['values'][k] = updateDataSeq(currData=mergedData['values'].get(k, genStoreValue()),
                                                newValues=(None, v),
                                                timestamp=timestamp)
        mergedData['values'][k]['addedKey'] = True

    for k, vals in change2add.changed.items():
        mergedData['values'][k] = updateDataSeq(currData=mergedData['values'].get(k, genStoreValue()), newValues=vals,
                                                timestamp=timestamp)

    for k, v in change2add.removed.items():
        mergedData['values'][k]['removedKey'] = True
        print(f"TODO MergeLoggedDictDiff removed: {k} -> {pformat(v)}")

    return mergedData


def MergeDictLoggedDictDiff(mergedData: Dict, change2add: DictOfLoggedDictDiff, timestamp: datetime):
    mergedData['timestamps'].append(timestamp)

    for k, v in change2add.added.items():
        mergedData['values'][k] = genStoreDict()
        mergedData['values'][k]['timestamps'].append(timestamp)
        for subk, subv in v.items():
            mergedData['values'][k]['values'][subk] = updateDataSeq(
                currData=mergedData['values'][k]['values'].get(subk, genStoreValue()), newValues=(None, subv),
                timestamp=timestamp)
        mergedData['values'][k]['addedValue'] = True
    for k, vals in change2add.changed.items():
        mergedData['values'][k]['timestamps'].append(timestamp)
        mergedData['values'][k] = MergeLoggedDictDiff(mergedData=mergedData['values'][k],
                                                      change2add=vals,
                                                      timestamp=timestamp)

    for k, v in change2add.removed.items():
        print(f"TODO MergeDictLoggedDictDiff removed: {k} -> {pformat(v)}")
        mergedData['values'][k]['removedValue'] = True

    return mergedData


def updateDataSeq(currData: Dict, newValues: Tuple[Any, Any], timestamp: datetime):
    if currData['changeCounter'] == 0:
        currData['values'].extend(list(newValues))
    else:
        if currData['values'][-1] != newValues[0]:
            raise ValueError(
                f"DataChanges.merge: broken sequence for key: registering {newValues}. Sequence {currData['values']}")
        currData['values'].append(newValues[1])
    currData['timestamps'].append(timestamp)
    currData['changeCounter'] += 1

    return currData
