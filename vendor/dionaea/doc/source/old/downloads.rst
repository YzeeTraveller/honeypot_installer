..
    This file is part of the dionaea honeypot

    SPDX-FileCopyrightText: 2011-2012 Markus Koetter
    SPDX-FileCopyrightText: 2015-2017 PhiBo (DinoTools)

    SPDX-License-Identifier: GPL-2.0-or-later

Downloads
=========

Once dionaea gained the location of the file the attacker wants it to
downloads from the shellcode, dionaea will try to download the file. The
protocol to downloads files via tftp and ftp is implemented in python
(ftp.py and tftp.py) as part of dionaea, downloading files via http is
done in the curl module - which makes use of libcurl's awsome http
capabilities. Of course libcurl can run downloads for ftp too, but the
ftp services embedded in malware a designed to work with windows ftp.exe
client, and fail for others.
