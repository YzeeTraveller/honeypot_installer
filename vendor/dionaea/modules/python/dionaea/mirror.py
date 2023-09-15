# This file is part of the dionaea honeypot
#
# SPDX-FileCopyrightText: 2006-2009 Michael P. Soulier
# SPDX-FileCopyrightText: 2009  Paul Baecher & Markus Koetter
#
# SPDX-License-Identifier: GPL-2.0-or-later

from dionaea import ServiceLoader
from dionaea.core import connection
import logging

logger = logging.getLogger('mirror')
logger.setLevel(logging.DEBUG)


class MirrorService(ServiceLoader):
    name = "mirror"

    @classmethod
    def start(cls, addr, iface=None, config=None):
        daemon = mirrord('tcp', addr, 42, iface)
        return daemon


class mirrorc(connection):
    def __init__(self, peer=None):
        logger.debug("mirror connection %s %s" %
                     ( peer.remote.host, peer.local.host))
        connection.__init__(self,peer.transport)
        self.bind(peer.local.host,0)
        self.connect(peer.remote.host,peer.local.port)
#		self.connect('',peer.local.port)
        self.peer = peer

    def handle_established(self):
        self.peer.peer = self

    def handle_io_in(self, data):
        if self.peer:
            self.peer.send(data)
        return len(data)

    def handle_error(self, err):
        if self.peer:
            self.peer.peer = None
            self.peer.close()

    def handle_disconnect(self):
        if self.peer:
            self.peer.close()
        if self.peer:
            self.peer.peer = None
        return 0

class mirrord(connection):
    def __init__(self, proto=None, host=None, port=None, iface=None):
        connection.__init__(self,proto)
        if host:
            self.bind(host, port, iface)
            self.listen()
        self.peer=None

    def handle_established(self):
        self.peer=mirrorc(self)
        self.timeouts.sustain = 60
        self._in.accounting.limit  = 100*1024
        self._out.accounting.limit = 100*1024

    def handle_io_in(self, data):
        if self.peer:
            self.peer.send(data)
        return len(data)

    def handle_error(self, err):
        logger.debug("mirrord connection error?, should not happen")
        if self.peer:
            self.peer.peer = None

    def handle_disconnect(self):
        if self.peer:
            self.peer.close()
        if self.peer:
            self.peer.peer = None
        return 0
