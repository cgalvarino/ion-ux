import os.path
import sys
import cStringIO
import xml.etree.cElementTree as ET
import HTMLParser
import json

from collections import defaultdict
from jinja2 import Template
from jinja2 import FileSystemLoader
from jinja2.environment import Environment

from dummy_data_layout import LAYOUT_SCHEMA
from service_api import service_gateway_get
from config import PORTAL_ROOT, UI_MODE, STATIC_ASSETS

from random import randint

DEFINED_VIEWS = [
    '2163152', # Facepage
    '2163153', # Status
    '2163154', # Related
    '2163156', # Dashboard
    '2163157', # Command
    '2163158', # Direct Command
]

class LayoutApi(object):
    @staticmethod
    def get_new_layout_schema():
        layout_schema = service_gateway_get('directory', 'get_ui_specs', params={'user_id': 'tboteler'})
        return layout_schema

    @staticmethod
    def process_layout(layout_schema=None, interactions=None):
        # Load template and find 'body' for template appendation
        env = Environment()
        env.loader = FileSystemLoader(PORTAL_ROOT+'/templates')
        tmpl_unparsed = env.get_template('ion_ux.html').render(static_assets=STATIC_ASSETS)
        tmpl = ET.fromstring(tmpl_unparsed.encode('utf-8'))
        body_elmt = tmpl.find('body')

        init_script_elmt = ET.Element('script')
        init_script_elmt.set('type', 'text/javascript')
        init_script_elmt.text = "$(function(){initialize_app();});"
        body_elmt.append(init_script_elmt)

        tmpl = ET.tostring(tmpl)
        tmpl = '<!DOCTYPE html>\n' + tmpl

        h = HTMLParser.HTMLParser()
        return h.unescape(tmpl)
    
def _make_element(parent_elmt, elmt_type, **kwargs):
    elmt = ET.SubElement(parent_elmt, elmt_type)
    for (key, value) in kwargs.items():
        if key == 'css':
            elmt.set('class', value)
        elif key.startswith('data'):
            elmt.set(key.replace('_','-'), value)
        elif key == 'content':
            elmt.text = value
        else:
            elmt.set(key, value)

    return elmt

