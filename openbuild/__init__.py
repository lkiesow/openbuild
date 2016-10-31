#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    opemnuild
    ~~~~~~~~~

    :copyright: 2016, Lars Kiesow <lkiesow@uos.de>
    :license: AGPL – see license.lgpl for more details.
'''

import logging


# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s ' +
                    '[%(filename)s:%(lineno)s:%(funcName)s()] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

