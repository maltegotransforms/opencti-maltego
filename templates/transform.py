#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from maltego_trx.maltego import MaltegoMsg
from maltego_trx.transform import DiscoverableTransform
from opencti.openctitransform import opencti_transform


class {functionName}(DiscoverableTransform):
    @classmethod
    def create_entities(cls, request: MaltegoMsg, response):
        opencti_transform("{transformName}", {output}, request, response)
