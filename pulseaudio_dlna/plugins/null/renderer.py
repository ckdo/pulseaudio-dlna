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

import re
import random
import urlparse
import urllib
import functools
import logging
import base64

import pulseaudio_dlna.pulseaudio
import pulseaudio_dlna.rules

logger = logging.getLogger('pulseaudio_dlna.plugins.null.renderer')


class NoEncoderFoundException():
    pass


@functools.total_ordering
class NullMediaRenderer(pulseaudio_dlna.plugins.renderer.BaseRenderer, pulseaudio_dlna.plugins.renderer.CoinedBaseRendererMixin):

    def __init__(self, udn, flavour):
        pulseaudio_dlna.plugins.renderer.BaseRenderer.__init__(
            self, udn)
        self.flavour = flavour
        self.state = self.IDLE

    def register(self, stream_url, codec=None, artist=None, title=None, thumb=None):
        return 200, None
            
    def activate(self, config):
        if config:
            self.set_rules_from_config(config)

    def validate(self):
        return True

    def play(self):
        self.state = self.PLAYING
        return 200, None
        
    def play(self, url=None, codec=None, artist=None, title=None, thumb=None):
        self.state = self.PLAYING
        return 200, None

    def pause(self):
        self.state = self.PAUSE
        return 200, None

    def stop(self):
        self.state = self.IDLE
        return 200, None

    def add_mime_type(self, mime_type):
        pass

    def prioritize_codecs(self):
        pass

    def check_for_device_rules(self):
        pass

    def check_for_codec_rules(self):
        pass

    def __str__(self, detailed=False):
        return (
            '<{} name="{}" short="{}" state="{}" udn="{}" model_name="{}" ').format(
                self.__class__.__name__,
                self.name,
                self.short_name,
                self.state,
                self.udn,
                self.model_name
        )

    def to_json(self):
        return {
            'name': self.name,
            'flavour': self.flavour
        }
        
class NullMediaRendererFactory(object):

    @classmethod
    def from_udn(cls, udn, flavour):
        return NullMediaRenderer(udn, flavour)