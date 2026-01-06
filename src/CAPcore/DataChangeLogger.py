from datetime import datetime
from typing import Optional, Dict, List, Any, Tuple

from src.CAPcore.Misc import getUTC

DATEFORMAT = "%Y-%m-%d %H:%M:%S.%f%z"


class DataChangesRaw:
    def __init__(self):
        self.timestamp: Optional[datetime] = None
        self.changeSet: Dict[str, List[Any]] = {}

    def update(self, timestamp: datetime, changeInfo: Dict[str, Any]) -> bool:
        changes: bool = False

        if self.timestamp and (self.timestamp != timestamp):
            raise ValueError(
                f"Updating a datachange set with a different timestamp. Current: {self.timestamp.strftime(DATEFORMAT)}. "
                f"New: {timestamp.strftime(DATEFORMAT)}")

        for k, vNew in changeInfo.items():
            if k not in self.changeSet:
                self.changeSet[k] = vNew
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


class DataChangesTuples(DataChangesRaw):
    def __init__(self):
        super().__init__()

    def update(self, timestamp: datetime, changeInfo: Dict[str, Tuple[Any, Any]]) -> bool:
        changes: bool = False

        if self.timestamp and (self.timestamp != timestamp):
            raise ValueError(
                f"Updating a datachange set with a different timestamp. Current: {self.timestamp.strftime(DATEFORMAT)}. "
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
