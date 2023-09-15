# This file is part of the dionaea honeypot
#
# SPDX-FileCopyrightText: 2016 PhiBo (DinoTools)
#
# SPDX-License-Identifier: GPL-2.0-or-later

import logging

from dionaea import IHandlerLoader
from dionaea.core import ihandler, incident
from dionaea.exception import LoaderError


logger = logging.getLogger("emu_scripts")
logger.setLevel(logging.DEBUG)


class EmulateScriptsLoader(IHandlerLoader):
    name = "emu_scripts"

    @classmethod
    def start(cls, config=None):
        try:
            return EmulateScriptsHandler("*", config=config)
        except LoaderError as e:
            logger.error(e.msg, *e.args)


class EmulateScriptsHandler(ihandler):
    def __init__(self, path, config=None):
        logger.debug("%s ready!", self.__class__.__name__)
        ihandler.__init__(self, path)
        self.path = path
        self._config = config
        self.handlers = []
        self.connection_url_levels = {}
        self.max_subdownloads = 20

        from .handler import PowerShell, RawURL, VBScript

        tmp_handlers = {}
        for h in (PowerShell, RawURL,VBScript):
            tmp_handlers[h.name] = h

        tmp = config.get("max_subdownloads")
        if isinstance(tmp, int):
            self.max_subdownloads = tmp

        enabled_handlers = config.get("enabled_handlers")
        if not isinstance(enabled_handlers, list) or len(enabled_handlers) == 0:
            logger.warning("No handlers specified")
            # Set empty list on error
            enabled_handlers = []

        handler_configs = config.get("handler_configs")
        if not isinstance(handler_configs, dict):
            handler_configs = {}

        for handler_name in enabled_handlers:
            h = tmp_handlers.get(handler_name)
            if h is None:
                logger.warning("Unable to load handler '%s'", handler_name)
                continue

            handler_config = handler_configs.get(handler_name)
            if not isinstance(handler_config, dict):
                handler_config = {}

            self.handlers.append(h(config=handler_config))

    def handle_incident_dionaea_connection_free(self, icd):
        # Delete levels for this connection
        if icd.con not in self.connection_url_levels:
            return
        try:
            del self.connection_url_levels[icd.con]
        except KeyError:
            pass

    def handle_incident_dionaea_download_complete(self, icd):
        url_levels = self.connection_url_levels.get(icd.con)
        if not isinstance(url_levels, dict):
            url_levels = {}
            # Store dict pointer in list, so others can use it
            self.connection_url_levels[icd.con] = url_levels

        next_level = url_levels.get(icd.url, 0) + 1
        if next_level > 1:
            # ToDo: use config value
            return

        fp = open(icd.path, "rb")
        # ToDo: check size
        data = fp.read()
        fp.close()
        urls = None
        # use the url list of the first handler that matches
        for handler in self.handlers:
            urls = handler.run(data)
            if urls is not None:
                break

        if urls is None:
            return

        for url in set(urls):
            if url in url_levels:
                # don't download a file multiple times
                continue

            if len(url_levels) > self.max_subdownloads:
                logger.warning("Max number of subdownloads reached")
                break
            url_levels[url] = next_level
            i = incident("dionaea.download.offer")
            i.con = icd.con
            i.url = url
            i.report()
