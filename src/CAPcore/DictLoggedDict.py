from time import gmtime

from src.CAPcore.LoggedDict import LoggedDict, dumpLoggedDict, INDENTSEPR, SEPRPR


class DictOfLoggedDict:
    def __init__(self, exclusions: set = None):

        if exclusions is not None and not isinstance(exclusions, (set, list, tuple)):
            raise TypeError(f"DictOfLoggedDict: expected set/list/tuple for exclusions: {exclusions}")

        self.current = dict()
        self.exclusions = exclusions or set()
        self.timestamp = gmtime()

    def __getitem__(self, item):
        return self.current.__getitem__(item)

    def __setitem__(self, k, v):
        currVal = self.current.get(k, LoggedDict(exclusions=self.exclusions))
        changes = currVal.update(v)

        self.current[k] = currVal
        return changes

    def get(self, key, default=None):
        return self.current.get(key, default)

    def update(self, newValues, timestamp=None):
        changeTime = timestamp or gmtime()
        result = []

        if not isinstance(newValues, dict):
            raise TypeError("LoggedDict.DictOfLoggedDict.update: expected dict")

        for k, v in newValues.items():
            currVal = self.current.get(k, LoggedDict(exclusions=self.exclusions))

            r1 = currVal.update(v, timestamp=changeTime)

            if r1:
                self.current[k] = currVal

            result.append(r1)

        return any(result)

    def purge(self, keys2delete, timestamp=None):
        changeTime = timestamp or gmtime()
        result = []

        for k in keys2delete:
            if k in self.exclusions:
                continue
            if k in self.current:
                r1 = self.current[k].clear(timestamp=changeTime)
                result.append(r1)

        return any(result)

    def addExclusion(self, *kargs):
        self.exclusions.update(set(kargs))

        for v in self.current.values():
            v.addExclusion(set(kargs))
        # TOTHINK: Qué hacer con los valores almacenados y que han quedado excluidos?

    def removeExclusion(self, *kargs):
        self.exclusions.remove(set(kargs).intersection(self.exclusions))

        for v in self.current.values():
            v.removeExclusion(set(kargs))

    def extractKey(self, key, default=None):
        result = {k: v.get(key, default=default) for k, v in self.current.items()}

        return result

    def subkeys(self):
        auxList = []

        for v in self.current.values():
            auxList = auxList + list(v.keys())

        return set(auxList)

    def diff(self,other):  #:(Dict[Any,(LoggedDict,dict)],LoggedDict)
        if not isinstance(other,(dict,DictOfLoggedDict)):
            raise TypeError(f"Parameter expected to be a dict or DictOfLoggedDict. Provided {type(other)}")

        result = DictOfLoggedDictDiff()

        currentKeys = set(self.current.keys())
        sharedKeys = set(currentKeys).intersection(other.keys())
        missingKeys = set(currentKeys).difference(other.keys())
        newKeys = set(other.keys()).difference(currentKeys)

        for k in sorted(newKeys):
            result.addKey(k,other.get(k))
        for k in sorted(sharedKeys):
            currVal = self.get(k)
            otherVal= other.get(k)
            result.change(k,currVal,otherVal)
        for k in sorted(missingKeys):
            result.removeKey(k,self.get(k))

        return result

    def __len__(self):
        return len(self.current)

    def __repr__(self):
        auxResult = {k: self.current[k].__repr__() for k in sorted(self.current)}

        if len(auxResult) == 1:
            k, v = auxResult.pop()
            result = dumpLoggedDict(k, v)
        else:
            claves = sorted(auxResult.keys())
            result = "{" + " " * (INDENTSEPR - 1) + dumpLoggedDict(claves[0], auxResult[claves[0]]) + SEPRPR + " "
            result = result + (SEPRPR + " ").join([dumpLoggedDict(k, auxResult[k]) for k in claves[1:]])
            result = result + "\n}"
            # TODO: WTF los espacios adicionales tras la coma
        return result

    def __ne__(self, other):
        return self.diff(other)


class DictOfLoggedDictDiff:
    def __init__(self):
        self.changeCount:int = 0
        self.added:dict = {}
        self.changed:dict = {}
        self.removed:dict = {}

    def change(self,k,vOld:LoggedDict,vNew):
        diff = vOld.diff(vNew)
        if diff:
            self.changed[k]=diff
            self.changeCount +=1

    def addKey(self,k,vNew):
        self.added[k]=vNew
        self.changeCount +=1

    def removeKey(self,k,vOld):
        self.removed[k]=vOld
        self.changeCount +=1

    def __bool__(self):
        return (self.changeCount>0)

    def show(self,indent:int=0, compact:bool=False,sepCompact=','):
        if self.changeCount == 0:
            return ""
        result= []
        result.extend([(k,f"{k}: A '{v}'") for k,v in self.added.items()])
        result.extend([(k,f"{k}: D '{v}'") for k,v in self.removed.items()])
        result.extend([(k,f"{k}: C '{v}'") for k,v in self.changed.items()])

        auxSep = f"{sepCompact} " if compact else '\n'
        auxIndent = 0 if compact else indent

        resultStr = auxSep.join([f"{' '*((auxIndent*2)+1)}{v[1]}" for v in sorted(result,key=lambda x:x[0])])

        return resultStr

    def __repr__(self):
        return self.show(compact=True)
