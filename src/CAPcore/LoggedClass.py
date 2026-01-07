from datetime import datetime
from typing import Optional, Dict, Tuple, Any, List, Callable

from .DataChangeLogger import DATEFORMAT, DataChangesTuples
from .DictLoggedDict import DictOfLoggedDict
from .LoggedDict import LoggedDict
from .LoggedValue import extractValue, setNewValue
from .Misc import getUTC
from .Web import sentinel


class LoggedClass:
    changesClass = DataChangesTuples

    def __init__(self, **kwargs):
        timestamp = kwargs.get('timestamp', getUTC())

        self.timestamp: Optional[datetime] = timestamp
        self.changeLog: Dict[datetime, Any] = {}

    def updateDataLog(self, changeInfo, timestamp=sentinel):
        if timestamp is sentinel:
            timestamp = getUTC()

        if self.timestamp > timestamp:
            raise ValueError(
                f"Trying top update in the past. Current: {self.timestamp.strftime(format=DATEFORMAT)}. "
                f"Parameter: {timestamp.strftime(format=DATEFORMAT)}")
        if changeInfo:
            if timestamp not in self.changeLog:
                self.changeLog[timestamp] = self.changesClass()
            self.changeLog[timestamp].update(timestamp=timestamp, changeInfo=changeInfo)
            self.timestamp = timestamp

    def class2dict(self, keyList: List[str], mapFunc: Optional[Callable] = None) -> Dict[str, Any]:
        result: Dict = {}
        for k in keyList:
            if not hasattr(self, k):
                continue
            val = getattr(self, k)
            result[k] = val if mapFunc is None else mapFunc(val)

        return result

    def updateDataFields(self, excludes: Optional[List[str]] = sentinel, **kwargs) -> bool:
        timestamp = kwargs['timestamp'] = kwargs.get('timestamp', getUTC())
        if excludes is sentinel:
            excludes = set()
        changes = False

        for k, newVal in kwargs.items():
            if k in excludes or k == 'timestamp':
                continue
            if hasattr(self, k):
                currVal = extractValue(getattr(self, k))
                if isinstance(currVal, (DictOfLoggedDict, LoggedDict)):
                    changes |= currVal.update(newVal, timestamp=timestamp)
                elif currVal != newVal:
                    setattr(self, k, setNewValue(currVal, newVal=newVal, timestamp=timestamp))
                    changes |= True

        if changes:
            self.timestamp = timestamp

        return changes


def diffDicts(oldDict: Dict[str, Any], newDict: Dict[str, Any]) -> Dict[str, Tuple[Any, Any]]:
    result = {}

    for k, oldV in oldDict.items():
        newV = newDict.get(k, None)
        if newV == oldV:
            continue
        result[k] = (oldV, newV)

    for k, newV in newDict.items():
        if k in oldDict:
            continue
        result[k] = (None, newV)

    return result


def LoggedClassGenerator(dataChangeLogger=DataChangesTuples):
    result = LoggedClass
    result.changesClass = dataChangeLogger
    return result
