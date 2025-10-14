# -*- coding: utf-8 -*-
from plone.restapi.services import Service

class WidgetGet(Service):
    def reply(self):      
        value = {"url": "https://www.skynettechnologies.com/accessibility/js/all-in-one-accessibility-js-widget-minify.js?colorcode={}&token={}&t={}&position={}"}
        
        return value
