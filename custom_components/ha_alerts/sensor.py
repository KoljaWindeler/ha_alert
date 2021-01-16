""" A component which allows you to parse an RSS feed into a sensor """
from .const import *
_LOGGER = logging.getLogger(__name__)






class ha_alert(Entity):
    def __init__(self, hass):
        self._feed = "https://alerts.home-assistant.io/feed.xml"
        self._name = DOMAIN
        self.hass = hass
        self._state = None
        self._newest_read = ''
        self._entries = []
        self._database_done = False
        self._database_update_needed = False
        self._date_format = '%a, %b %d %I:%M %p'

        platform = entity_platform.current_platform.get()
        platform.async_register_entity_service("mark_read", {}, "async_mark_read",)

        if hass.is_running:
            if "recorder" in self.hass.config.components:
                self._database_update_needed = True
            else:
                self._database_done = True
        else:
            if "recorder" in self.hass.config.components:
                self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, self._async_initialize_from_database)
            else:
                self._database_done = True
        

    def get_feed(self):
        return feedparser.parse(self._feed)

    async def async_update(self):
        if(self._database_update_needed):
            self._async_initialize_from_database()
        if(self._database_done == False):
            return
        
        parsedFeed = await self.hass.async_add_executor_job(self.get_feed)
        
        if not parsedFeed:
            return False
        else:
            self._state = STATE_OFF
            self._entries = []

            for entry in parsedFeed.entries:
                entryValue = {}
                entryValue['date'] = None

                for key, value in entry.items():
                    if('parsed' in key):
                        continue
                    if key in ['published', 'updated', 'created']:
                        if(entryValue['date']==None):
                            entryValue['date'] = parser.parse(value)
                        elif(parser.parse(value) < entryValue['date']):
                            entryValue['date'] = parser.parse(value)
                        value = parser.parse(value).strftime(self._date_format)
                    entryValue[key] = value

                if 'image' not in entryValue.keys():
                    images = []
                    if 'summary' in entry.keys():
                        images = re.findall(r"<img.+?src=\"(.+?)\".+?>", entry['summary'])
                    if images:
                        entryValue['image'] = images[0]
                    else:
                        entryValue['image'] = "https://www.home-assistant.io/images/favicon-192x192-full.png"

                self._entries.append(entryValue)
            
            self._entries.sort(key=lambda x: x['date'], reverse=True)
            if(len(self._entries)>0):
                if(self._newest_read != self._entries[0]['id']):
                    self._state = STATE_ON
            self.schedule_update_ha_state()

    def async_mark_read(self):
        self._state = STATE_OFF
        if(len(self._entries)>0):
            if('id' in self._entries[0]):
                self._newest_read = self._entries[0]['id']
                self.schedule_update_ha_state()

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def icon(self):
        return ICON

    @property
    def device_state_attributes(self):
        return {
            'newest_read': self._newest_read,
            'entries': self._entries
        }

    async def _async_initialize_from_database(self,hass):
        """Initialize the list of states from the database."""
        with session_scope(hass=self.hass) as session:
            query = session.query(States).filter(States.entity_id == 'sensor.'+self._name)
            states = execute(query)
            states.sort(key=lambda x: x.last_updated)
            s = states[len(states)-1]
            session.expunge_all()

        j = json.loads(s.attributes)
        if('newest_read' in j):
            self._newest_read = j['newest_read']
        self._database_done = True
        await self.async_update()
    
