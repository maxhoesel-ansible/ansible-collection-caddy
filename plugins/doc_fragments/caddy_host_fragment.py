# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Max Hösel <ansible@maxhoesel.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r'''
    requirements:
      - C(requests) must be installed on the host executing the query
    options:
      caddy_host:
        description: Address of the caddy API endpoint
        default: "http://localhost:2019"
        type: str
    '''
