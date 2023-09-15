..
    This file is part of the dionaea honeypot

    SPDX-FileCopyrightText: 2017 PhiBo (DinoTools)

    SPDX-License-Identifier: GPL-2.0-or-later

MongoDB
=======

This module add initial support to emulates a `MongoDB`_ server with the dionaea honeypot.
At the moment it is very limited and the functionality might be improved in one of the next releases.

Requirements
------------

- bson module for Python 3

Example config
--------------

.. literalinclude:: ../../../conf/services/mongo.yaml
    :language: yaml
    :caption: services/mongo.yaml

.. MongoDB: https://www.mongodb.com/
