# This file is part of the dionaea honeypot
#
# SPDX-FileCopyrightText: 2009  Paul Baecher & Markus Koetter
#
# SPDX-License-Identifier: GPL-2.0-or-later

from dionaea import IHandlerLoader
from dionaea.core import ihandler, incident, connection
from struct import pack, unpack, calcsize
from socket import inet_aton

import logging

logger = logging.getLogger('p0f')
logger.setLevel(logging.DEBUG)


class P0FHandlerLoader(IHandlerLoader):
    name = "p0f"

    @classmethod
    def start(cls, config=None):
        return p0fhandler(config=config)


class p0fconnection(connection):
    def __init__(self, p0fpath, con):
        connection.__init__(self, 'tcp')
        self.con = con
        self.con.ref()
        self.connect(p0fpath, 0)

    def handle_established(self):
        if True:
            # p0f >= 2.0.8
            data = pack("III4s4sHH",
                        0x0defaced,                     # p0f magic
                        1,                              # type
                        0xffffffff,                     # id
                        inet_aton(self.con.remote.host),# remote host
                        inet_aton(self.con.local.host), # local host
                        self.con.remote.port,           # remote port
                        self.con.local.port)            # local port
        else:
            # p0f < 2.0.8
            data = pack("=II4s4sHH",
                        0x0defaced,                     # p0f magic
                        0xffffffff,                     # type
                        inet_aton(self.con.remote.host),# remote host
                        inet_aton(self.con.local.host), # local host
                        self.con.remote.port,           # remote port
                        self.con.local.port)            # local port

        self.send(data)

    def handle_io_in(self, data):
        fmt = "IIB20s40sB30s30sBBBhHi"
        if len(data) != calcsize(fmt):
            return 0
        values = unpack(fmt, data)
        names=["magic","id","type","genre","detail","dist","link",
               "tos","fw","nat","real","score","mflags","uptime"]
        icd = incident(origin='dionaea.modules.python.p0f')
        for i in range(len(values)):
            s = values[i]
            if type(s) == bytes:
                if s.find(b'\x00'):
                    s = s[:s.find(b'\x00')]
                try:
                    s = s.decode("ascii")
                except UnicodeDecodeError:
                    logger.warning("Unable to decode p0f information %s=%r", i, s, exc_info=True)
                icd.set(names[i], s)
            elif type(s) == int:
                icd.set(names[i], str(s))
        icd.set('con',self.con)
        icd.report()
        self.close()
        return len(data)

    def handle_disconnect(self):
        self.con.unref()
        return 0

    def handle_error(self, err):
        self.con.unref()

class p0fhandler(ihandler):
    def __init__(self, config=None):
        logger.debug("p0fHandler")
        ihandler.__init__(self, 'dionaea.connection.*')
        self.p0fpath = config.get("path")

    def handle_incident(self, icd):
        if icd.origin == 'dionaea.connection.tcp.accept' or icd.origin == 'dionaea.connection.tls.accept' or icd.origin == 'dionaea.connection.tcp.reject':
            logger.debug("p0f action")
#           icd.dump()
            con = icd.get('con')
            p = p0fconnection(self.p0fpath, con)




# p0f = p0fHandler('un:///tmp/p0f.sock')
