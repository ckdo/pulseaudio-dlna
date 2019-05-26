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
import requests
import traceback

logger = logging.getLogger('pulseaudio_dlna.holder')


class Holder(object):
    def __init__(
            self, plugins,
            stream_ip=None, stream_port=None, message_queue=None,
            device_filter=None, device_config=None):
        self.plugins = plugins
        self.stream_ip = stream_ip
        self.stream_port = stream_port
        self.device_filter = device_filter or None
        self.device_config = device_config or {}
        self.message_queue = message_queue
        self.devices = {}
        self.nulldevices = {}
        self.lock = threading.Lock()

    def search(self, ttl=None):
        self._init()
        threads = []
        for plugin in self.plugins:
            thread = threading.Thread(
                target=plugin.discover, args=[self, ttl])
            thread.daemon = True
            threads.append(thread)
        try:
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
        except:
            traceback.print_exc()

        logger.debug('Holder.search() quit')

    def _init(self):
        for udn, config in self.device_config.items():
            if config.get("alwayson", None):
                for plugin in self.plugins:
                    nulldevice=plugin.get_fromudn(udn, config["flavour"])
                    if nulldevice:
                        self.nulldevices[udn]={}
                        self.nulldevices[udn]["device"]=nulldevice
                        self.nulldevices[udn]["inuse"]=0
                        self.add_device(nulldevice)
            
      
    def lookup(self, locations):
        xmls = {}
        for url in locations:
            try:
                response = requests.get(url, timeout=5)
                logger.debug('Response from device ({url})\n{response}'.format(
                    url=url, response=response.text))
                xmls[url] = response.content
            except requests.exceptions.Timeout:
                logger.warning(
                    'Could no connect to {url}. '
                    'Connection timeout.'.format(url=url))
            except requests.exceptions.ConnectionError:
                logger.warning(
                    'Could no connect to {url}. '
                    'Connection refused.'.format(url=url))

        for plugin in self.plugins:
            for url, xml in xmls.items():
                device = plugin.lookup(url, xml)
                self.add_device(device)

    def add_device(self, device):
        if not device:
            return
        try:
            self.lock.acquire()
            if device.udn not in self.devices or \
               (device.udn in self.devices and device.udn in self.nulldevices and self.nulldevices[device.udn]["inuse"] == 1):
            
                if device.validate():
                    config = self.device_config.get(device.udn, None)
                    logger.debug("config is {}".format(config))
                    device.activate(config)
                    if self.stream_ip and self.stream_port:
                        device.set_server_location(
                            self.stream_ip, self.stream_port)
                    if not self.device_filter or \
                       device.name in self.device_filter:
                        if config:
                            logger.info(
                                'Using device configuration:\n{}'.format(
                                    device.__str__(True)))
                        
                        if device.udn not in self.devices:
                            self._send_message('add_device', device)
                        else:
                            logger.debug(
                                'Updating device:\n{} with device\n{}'.format(
                                    self.devices[device.udn], device.__str__(True)))
                            self._send_message('replace_device', device)
                        self.devices[device.udn] = device
                        if device.udn in self.nulldevices:
                            if device is self.nulldevices[device.udn]["device"]:
                                self.nulldevices[device.udn]["inuse"]=1
                            else:
                                self.nulldevices[device.udn]["inuse"]=0
                    else:
                        logger.info('Skipped the device "{name}" ...'.format(
                            name=device.label))
            else:
                if device.validate():
                    self._send_message('update_device', device)
        finally:
            self.lock.release()

    def remove_device(self, device_id):
        if not device_id or device_id not in self.devices:
            return
        try:
            self.lock.acquire()
            device = self.devices[device_id]
            if not device.alwayson:
              self._send_message('remove_device', device)
              del self.devices[device_id]
            else:
              logger.info('Do not remove always on device {}'.format(device.name)) 
              self.devices[device_id]=self.nulldevices[device_id]["device"]
              self.nulldevices[device_id]["inuse"]=1
              self._send_message('replace_device', device)
        finally:
            self.lock.release()

    def _send_message(self, _type, device):
        if self.message_queue:
            self.message_queue.put({
                'type': _type,
                'device': device
            })
