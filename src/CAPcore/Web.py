import logging
from argparse import Namespace
from collections import namedtuple
from collections.abc import Callable
from time import time
from typing import Optional
from urllib.parse import (parse_qs, unquote, urlencode, urljoin, urlparse, urlunparse)

import requests
from mechanicalsoup import StatefulBrowser

from .Misc import getUTC

# (connect timeout, read timeout) From https://requests.readthedocs.io/en/latest/api/#requests.request
TIMEOUT = (180, 300)

logger = logging.getLogger()

DownloadedPage = namedtuple('DownloadedPage',
                            field_names=['source', 'data', 'timestamp', 'home', 'browser', 'config', 'extra'],
                            defaults={'home': None, 'browser': None, 'config': None, 'extra': None})


def downloadPage(dest, home=None, browser: Optional[StatefulBrowser] = None, config=Namespace(),
                 sanitizer: Optional[Callable[[bytes], bytes]] = None
                 ) -> DownloadedPage:
    """
    Descarga el contenido de una pagina y lo devuelve con metadatos
    :param dest: Resultado de un link, URL absoluta o relativa.
    :param home: Situación del browser
    :param browser: Stateful Browser Object
    :param config: Namespace de configuración (de argparse) para manipular ciertas características del browser
    :param sanitizer: Function that processes the incoming data (useful for HTML legacy whose format is like it is)
    :return: Diccionario con página bajada y metadatos varios
    """
    timeIn = time()
    if browser is None:
        browser = createBrowser(config)

    if home:
        browser.open(home)
        target = mergeURL(home, dest)
        logger.debug("downloadPage: home %s link  %s", home, target)
        response = browser.open(target)
    else:
        target = dest
        logger.debug("downloadPage: no home %s", target)
        response = browser.open(target)

    response.raise_for_status()

    if sanitizer:
        ammended = sanitizer(response.text)
        browser.open_fake_page(ammended, target)

    source = browser.get_url()
    content = browser.get_current_page()
    timeOut = time()
    timeDL = timeOut - timeIn

    logger.debug("downloadPage: downloaded %s (%f)", target, timeDL)

    return DownloadedPage(source=source, data=content, timestamp=getUTC(), home=home, browser=browser, config=config)


def downloadRawPage(dest, *args, here=None, sanitizer: Optional[Callable[[bytes], bytes]] = None, **kwargs
                    ) -> DownloadedPage:
    """
    Descarga el contenido de una pagina y lo devuelve con metadatos
    :param sanitizer: function to sanitize the result. Takes the downloaded content, returns the sanitized one
    :param dest: Resultado de un link, URL absoluta o relativa.
    :param here: Situación del browser
    :return: Diccionario con página bajada y metadatos varios
    """
    timeIn = time()

    destURL = mergeURL(here, dest)

    response = requests.get(destURL, *args, timeout=TIMEOUT, **kwargs)
    response.raise_for_status()

    timeOut = time()
    timeDL = timeOut - timeIn

    resultData = sanitizer(response.content) if sanitizer else response.content
    logger.debug("downloadPage: downloaded %s (%f)", destURL, timeDL)

    result = DownloadedPage(source=response.url, data=resultData, timestamp=getUTC(), home=here, extra=response)

    return result


def extractGetParams(url):
    """
       Devuelve un diccionario con los parámetros pasados en la URL
    """

    urlcomps = parse_qs(urlparse(unquote(url)).query)
    result = {}
    for i, v in urlcomps.items():
        result[i] = v[0]
    return result


def composeURL(url, argsToAdd=None, argsToRemove=None):
    if not (argsToAdd or argsToRemove):
        return url

    urlGetParams = extractGetParams(url)

    newParams = urlGetParams
    if argsToAdd:
        for k in argsToAdd:
            newParams[k] = argsToAdd[k]

    if argsToRemove:
        for k in argsToRemove:
            newParams.pop(k)

    urlparams = urlencode(newParams)

    urlcomps = list(urlparse(url=url))
    urlcomps[4] = urlparams
    result = urlunparse(urlcomps)

    return result


mergeURL = urljoin


def createBrowser(config=Namespace()):
    browser = StatefulBrowser(soup_config={'features': "html.parser"}, raise_on_404=True, user_agent="Cosecha", )

    if 'verbose' in config:
        browser.set_verbose(config.verbose)

    if 'debug' in config:
        browser.set_debug(config.debug)

    return browser


def findObjectsWithAttributes(webContent, targetTag, targetInfo):
    result = dict()
    for k, fname, fvalue in targetInfo:
        metaF = webContent.find(targetTag, attrs={fname: fvalue})
        if metaF:
            result[k] = metaF
    return result
