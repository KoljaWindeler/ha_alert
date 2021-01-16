"""Provide the config flow."""
from homeassistant.core import callback
from homeassistant import config_entries
import voluptuous as vol
import logging
from .const import *

_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class haAlertFlowHandler(config_entries.ConfigFlow):
	"""Provide the initial setup."""

	CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL
	VERSION = 1

	def __init__(self):
		"""Provide the init function of the config flow."""
		# Called once the flow is started by the user
		self._errors = {}

	# will be called by sending the form, until configuration is done
	async def async_step_user(self, user_input=None):   # pylint: disable=unused-argument
		"""Call this as first page."""
		return self.async_create_entry(title="HA Alert!", data={})