#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyvirtualdisplay import Display

class LinksProvider ():

    def __init__ (self, name):
        self._name = name

    def getName (self):
        return self._name
