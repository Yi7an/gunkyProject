#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyvirtualdisplay import Display

class LinksProvider ():

    def __init__ (self):
        self.display = Display(visible=0, size=(800, 600))
        self.display.start()
