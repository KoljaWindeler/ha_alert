import asyncio
import re
import json
import feedparser
import logging
from datetime import timedelta
from dateutil import parser
from homeassistant.helpers.entity import Entity
from homeassistant.helpers import config_validation as cv, entity_platform, service
from homeassistant.components.recorder.models import States
from homeassistant.components.recorder.util import execute, session_scope

from homeassistant.const import (
	CONF_NAME,
	STATE_OFF,
	STATE_ON,
    EVENT_HOMEASSISTANT_START
)

REQUIREMENTS = ['feedparser']
PLATFORM = "sensor"
DOMAIN = 'ha_alert'
VERSION = "0.1"
SCAN_INTERVAL = timedelta(hours=3)
ISSUE_URL = 'https://github.com/KoljaWindeler/ha_alert/issues'
ICON = 'mdi:rss'
__version__ = VERSION

