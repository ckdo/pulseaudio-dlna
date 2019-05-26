#!/usr/bin/python

# This file is part of pulseaudio-dlna.

# pulseaudio-dlna is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pulseaudio-dlna is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with pulseaudio-dlna.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import logging
import threading
import traceback

import pulseaudio_dlna.plugins
import pulseaudio_dlna.plugins.upnp.ssdp
import pulseaudio_dlna.plugins.upnp.ssdp.listener
import pulseaudio_dlna.plugins.upnp.ssdp.discover
from pulseaudio_dlna.plugins.upnp.renderer import (
    CoinedUpnpMediaRenderer, UpnpMediaRendererFactory)

logger = logging.getLogger('pulseaudio_dlna.plugins.upnp')


class NullPlugin(pulseaudio_dlna.plugins.BasePlugin):

    NOTIFICATION_TYPES = [
        'urn:schemas-upnp-org:device:MediaRenderer:1',
        'urn:schemas-upnp-org:device:MediaRenderer:2',
    ]

    def __init__(self, *args):
        pulseaudio_dlna.plugins.BasePlugin.__init__(self, *args)

    def lookup(self, url, xml):
        raise NotImplementedError()

    def discover(self, holder, ttl=None):
        raise NotImplementedError()

    @pulseaudio_dlna.plugins.BasePlugin.add_device_after
    def _on_device_added(self, header):
        return NullMediaRendererFactory.from_
        nt_header = header.get('nt', None)
        if nt_header and nt_header in self.NOTIFICATION_TYPES:
            return UpnpMediaRendererFactory.from_header(
                header, CoinedUpnpMediaRenderer)

    @pulseaudio_dlna.plugins.BasePlugin.remove_device_after
    def _on_device_removed(self, header):
        raise NotImplementedError()
