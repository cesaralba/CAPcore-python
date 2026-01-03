from datetime import datetime
from typing import Optional, Dict, Tuple, Any

from .Misc import getUTC
from .Web import sentinel


class LoggedClass:
    def __init__(self, **kwargs):
        timestamp = kwargs.get('timestamp', getUTC())

        self.timestamp: Optional[datetime] = timestamp
        self.changeLog: Dict[datetime, DataChanges] = {}

    def updateDataLog(self, changeInfo, timestamp=sentinel):
        if timestamp is sentinel:
            timestamp = getUTC()

        if self.timestamp > timestamp:
            raise ValueError(
                f"Trying top update in the past. Current: {self.timestamp.strftime()}. Parameter: {timestamp.strftime()}")
        if changeInfo:
            if timestamp not in self.changeLog:
                self.changeLog[timestamp] = DataChanges()
            self.changeLog[timestamp].update(timestamp=timestamp, changeInfo=changeInfo)
            self.timestamp = timestamp


class DataChanges:
    def __init__(self):
        self.timestamp: Optional[datetime] = None
        self.changeSet: Dict[str, Tuple[Any, Any]] = {}

    def update(self, timestamp: datetime, changeInfo: Dict[str, Tuple[Any, Any]]) -> bool:
        changes: bool = False

        if self.timestamp and (self.timestamp != timestamp):
            raise ValueError(
                f"Updating a datachange set with a different timestamp. Current: {self.timestamp.strftime()}. New: {timestamp.strftime()}")

        for k, (vOld, vNew) in changeInfo.items():
            if k not in self.changeSet:
                self.changeSet[k] = (vOld, vNew)
                changes |= True
            else:
                (currOld, currNew) = self.changeSet[k]
                if (currOld, currNew) == (vOld, vNew):
                    continue
                if currNew != vOld:
                    raise ValueError(
                        f"Updating a datachange set. Breaking a transition. Key: '{k}'. Old: '{currNew}'. New: '{vOld}'")
                self.changeSet[k] = (currOld, vNew)
                changes |= True

        if changes:
            self.timestamp = getUTC() if timestamp is None else timestamp

        return changes
