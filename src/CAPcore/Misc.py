import re
from collections import defaultdict
from collections import namedtuple
from datetime import datetime, timezone
from pathlib import Path
from types import NoneType
from typing import Callable, Dict, Iterable, Optional, Tuple, Set, Any, List

from dateutil import tz

####################################################################################################################

FORMATOtimestamp = "%Y-%m-%d %H:%M"
FORMATOfecha = "%Y-%m-%d"
PARSERfechaC = "%d/%m/%Y"


class BadString(Exception):
    def __init__(self, cadena=None):
        if cadena:
            Exception.__init__(self, cadena)
        else:
            Exception.__init__(self, "Data doesn't fit expected format")


class BadParameters(Exception):
    def __init__(self, cadena=None):
        if cadena:
            Exception.__init__(self, cadena)
        else:
            Exception.__init__(self, "Wrong (or missing) parameters")


def removeSuffix(source: str, suffix: str) -> str:
    """
    Removes a suffix from the source parameter if source ends with it
    :param source:
    :param suffix:
    :return:
    """
    if not isinstance(source, str) or not isinstance(suffix, str):
        raise TypeError(f"removeSuffix: one or both parameters are not a str: source: '{source}' suffix: '{suffix}'")

    result = source
    if source.endswith(suffix):
        result = source[0: (len(source) - len(suffix))]
    return result


def extractREGroups(cadena, regex="."):
    datos = re.match(pattern=regex, string=cadena)

    if datos:
        return datos.groups()

    return None


def countKeys(x):
    if not isinstance(x, (dict, defaultdict)):
        raise ValueError("countKeys: necesita un diccionario")

    resultado = defaultdict(int)

    for clave, valor in x.items():
        if not isinstance(valor, (dict, defaultdict)):
            print(f"countKeys: objeto de clave '{clave}' no es un diccionario")
            continue

        for subclave in valor:
            resultado[subclave] += 1

    return resultado


def values2Keys(x):
    if not isinstance(x, (dict, defaultdict)):
        raise ValueError("countKeys: necesita un diccionario")

    resultado = defaultdict(set)

    for clave, valor in x.items():
        (resultado[valor]).add(clave)

    return resultado


def dumpDict(x, claves=None):
    if not isinstance(x, (dict, defaultdict)):
        raise ValueError("countKeys: necesita un diccionario")

    if claves:
        clavesOk = [clave for clave in claves if clave in x]
    else:
        clavesOk = x.keys()

    result = [f"{clave} -> {x[clave]}" for clave in clavesOk]

    return "\n".join(result)


def subSet(lista, idx):
    if not idx:
        return []

    return [lista[x] for x in idx if x < len(lista) and lista[x] is not None]


def deepDictSet(dic, keys, value):
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value


def deepDict(dic, keys, tipoFinal):
    if len(keys) == 0:
        return dic
    if keys[0] not in dic and len(keys) == 1:
        dic[keys[0]] = (tipoFinal)()

    return deepDict(dic.setdefault(keys[0], {}), keys[1:], tipoFinal)


def generaDefaultDict(listaClaves, tipoFinal):
    """
    Genera un diccionario (defauldict) de 4 niveles de profundidad y cuyo tipo final es el que se indica en el parámetro
    :param listaClaves: lista con los niveles de claves (en realidad se usa la longitud)
    :param tipoFinal: tipo que va almacenar el diccionario más profundo
    :return: defaultdict(defaultdict(...(defaultdict(tipoFinal)))
    """

    def actGenera(objLen, tipo):
        if objLen == 1:
            return defaultdict((tipo))

        return defaultdict(lambda: actGenera(objLen - 1, tipo))

    return actGenera(len(listaClaves), tipoFinal)


def createPath(*kargs):
    pathList = [Path(p) for p in kargs]

    return Path.joinpath(*pathList)


def normalize_data_structs(data, **kwargs):
    """
    Returns a 'normalized' version of data (lists ordered, strings lowercased,...)
    :param data: thing to normalize
    :param kwargs: manipulation of data
      * sort_lists: (default python sorted order)
      * lowercase_strings:
    :return:
    """

    if isinstance(data, str):
        return data.lower() if kwargs.get("lowercase_strings", False) else data

    if isinstance(data, list):
        result = [normalize_data_structs(x, **kwargs) for x in data]
        return sorted(result) if kwargs.get("sort_lists", False) else result

    if isinstance(data, dict):
        return {k: normalize_data_structs(data[k], **kwargs) for k in sorted(data.keys())}

    return data


def listize(param):
    """
    Convierte un parámetro en un iterable (list, set, tuple) si no lo es ya
    :param param:
    :return:
    """
    return param if isinstance(param, (list, set, tuple)) else [param]


def onlySetElement(myset):
    """
    Returns only element of set or full set
    :param myset: a set
    :return:
    """
    return (list(myset.copy())[0] if isinstance(myset, (set, list)) and len(myset) == 1 else myset)


def cosaCorta(c1, c2):
    return c1 if len(c2) > len(c1) else c2


def cosaLarga(c1, c2):
    return c2 if len(c2) > len(c1) else c1


def datePub2structTime(datePublished, dateformat):
    result = datetime.strptime(datePublished, dateformat)
    return result


def datePub2Id(datePublished: str, formatDatePub: str, formatId: str) -> str:
    datePub = datePub2structTime(datePublished, formatDatePub)
    result = datePub.strftime(formatId)

    return result


def stripPubDate(datePublished: str, formatDatePub: str) -> Tuple[str, str, str, str, str, str]:
    datePub = datePub2structTime(datePublished, formatDatePub)
    result = (datePub.strftime("%Y"), datePub.strftime("%m"), datePub.strftime("%d"), datePub.strftime("%H"),
              datePub.strftime("%M"), datePub.strftime("%S"),)

    return result


def getUTC() -> datetime:
    result = datetime.now(timezone.utc)

    return result


def UTC2local(t: datetime):
    return t.astimezone(tz.tzlocal())


def trueF(x: Any) -> bool:
    return True or x


def falseF(x: Any) -> bool:
    return False and x


def prepareBuilderPayloadDict(source: Dict, dest: object, fieldList: Optional[Iterable] = None,
                              condition: Optional[Callable] = None, ):
    auxList = fieldList

    auxCond = condition
    if auxCond is None:
        auxCond = trueF
    if fieldList is None:
        auxList = {k for k in dir(dest) if ((not callable(getattr(dest, k))) and auxCond(k))}
    result = {k: source[k] for k in auxList if k in source and source[k] is not None}

    return result


def prepareBuilderPayloadObj(source: object, dest: object, fieldList: Optional[Iterable] = None,
                             condition: Optional[Callable] = None, ):
    auxList = fieldList

    auxCond = condition
    if auxCond is None:
        auxCond = trueF
    if fieldList is None:
        auxList = {k for k in dir(dest) if ((not callable(getattr(dest, k))) and auxCond(k) and not k.startswith("_"))}

    result = {k: getattr(source, k) for k in auxList if hasattr(source, k) and getattr(source, k) is not None}

    return result


SetDiff = namedtuple('SetDiff', field_names=['missing', 'new', 'shared'], defaults=[set(), set(), set()])


def compareSets(oldSet: Set, newSet: Set) -> SetDiff:
    sharedKeys = set(oldSet).intersection(newSet)
    missingKeys = set(oldSet).difference(newSet)
    newKeys = set(newSet).difference(oldSet)
    result = SetDiff(missing=missingKeys, shared=sharedKeys, new=newKeys)
    return result


def chainKargs(*kargs) -> List[Any]:
    result = []

    for k in kargs:
        if isinstance(k, (str, int, float, bool, NoneType)):
            result.append(k)
            continue
        if isinstance(k, (set, list, tuple)):
            result.extend(chainKargs(*k))
            continue
        raise TypeError(f"chainKargs: can't handle type '{type(k)}': {k}")

    return result
