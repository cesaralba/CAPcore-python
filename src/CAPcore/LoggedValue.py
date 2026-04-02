from datetime import datetime
from typing import Any, Optional

from .Misc import getUTC

DATEFORMAT = "%Y-%m-%d %H:%M:%S.%f%z"


class LoggedValue:
    def __init__(self, v=None, timestamp: Optional[datetime] = None):
        self.last_updated = timestamp or getUTC()
        self.deleted = False
        self.value = None
        self.history = []

        self.set(v, timestamp, change=True)

    def set(self, v: Any, timestamp: Optional[datetime] = None, change: bool = False):
        result = change
        if self.deleted or (v != self.value):
            changeTime = timestamp or getUTC()
            action = 'U'
            if self.deleted:
                action = 'C'
            result = True
            self._set(v, action, changeTime)
            self.deleted = False
        return result

    def _set(self, v: Any, action: str, changeTime: datetime):
        if changeTime.replace(microsecond=0) < self.last_updated.replace(microsecond=0):
            raise ValueError((
                f"changeTime value '{changeTime.strftime(DATEFORMAT)}' is before the last"
                f" recorded change '{self.last_updated.strftime(DATEFORMAT)}'"))
        newLog = (action, changeTime, v)
        self.last_updated = changeTime
        self.value = v
        self.history.append(newLog)

    def clear(self, timestamp: Optional[datetime] = None):
        if self.deleted:
            return False
        changeTime = timestamp or getUTC()
        self._set(None, 'D', changeTime)
        self.deleted = True

        return True

    def get(self):
        if self.deleted:
            raise ValueError("The variable is deleted")
        return self.value

    def isDeleted(self):
        return self.deleted

    def __repr__(self):
        delTxt = " D" if self.deleted else ""
        dateTxt = self.last_updated.strftime(DATEFORMAT)
        lenTxt = f"l"":"f"{len(self.history)}"

        return f"{self.value.__repr__()} [t:{dateTxt}{delTxt} {lenTxt}]"

    def __len__(self):
        return len(self.history)  # TODO: operaciones relativas a la historia

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.get()
        return self.value == other


def setNewValue(val: LoggedValue | Any, newVal: Any, timestamp: Optional[datetime] = None) -> Any:
    result = newVal
    if isinstance(val, LoggedValue):
        val.set(newVal, timestamp=timestamp)
        result = val
    return result


def extractValue(val) -> Any:
    v = val.get() if isinstance(val, LoggedValue) else val
    return v
