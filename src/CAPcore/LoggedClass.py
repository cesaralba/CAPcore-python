from datetime import datetime
from typing import Optional, Dict, Tuple, Any, List

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
                f"Trying top update in the past. Current: {self.timestamp.strftime()}. "
                f"Parameter: {timestamp.strftime()}")
        if changeInfo:
            if timestamp not in self.changeLog:
                self.changeLog[timestamp] = DataChanges()
            self.changeLog[timestamp].update(timestamp=timestamp, changeInfo=changeInfo)
            self.timestamp = timestamp


class DataChanges:
    def __init__(self):
        self.timestamp: Optional[datetime] = None
        self.changeSet: Dict[str, List[Any]] = {}

    def update(self, timestamp: datetime, changeInfo: Dict[str, Tuple[Any, Any]]) -> bool:
        changes: bool = False

        if self.timestamp and (self.timestamp != timestamp):
            raise ValueError(
                f"Updating a datachange set with a different timestamp. Current: {self.timestamp.strftime()}. "
                f"New: {timestamp.strftime()}")

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
