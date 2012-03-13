#     Copyright 2011 Joachim Basmaison, Cyril Leclerc
#
#     This file is part of xbmc-qobuz.
#
#     xbmc-qobuz is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     xbmc-qobuz is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.   See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with xbmc-qobuz.   If not, see <http://www.gnu.org/licenses/>.

import sys
from time import time
import re
import math
import pprint

import xbmc
import xbmcplugin
import xbmcgui
import json 
import qobuz
from debug import info, warn


from node.track import Node_track

class xbmc_json_rpc():
    def __init__(self):

        pass

    def _call(self, method, params = {}):
        cmd = {
               'jsonrpc': '2.0',
               'method': method,
        }
        if params: cmd['params'] = params
        print "JSONRPC CMD: " + pprint.pformat(cmd)
        response = xbmc.executeJSONRPC(json.dumps( cmd))
        print "JSONRPC Response: " + response
        return response
    
    def Player_SetAudioStream(self, url):
        return self._call('Player.SetAudioStream', { 'id': 0, 'url': url })
    
    def JSONRPC_Version(self):
        return xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "JSONRPC.Version" }')
        return self._call("JSONRPC.Version", None)

class QobuzPlayer(xbmc.Player):

    def __init__(self, type = xbmc.PLAYER_CORE_AUTO):
        super(QobuzPlayer, self).__init__()

    def sendQobuzPlaybackEnded(self, duration):
        qobuz.api.report_streaming_stop(self.id, duration)

    def sendQobuzPlaybackStarted(self,):
        qobuz.api.report_streaming_start(self.id)

    def play(self, id):
        info(self, "Playing track: " + str(id))
        node = Node_track()
        node.set_id(id)
        node._set_cache()
        node.set_data(node.cache.fetch_data())
    
        lang = qobuz.lang
        item = node.make_XbmcListItem()
        item.setProperty('mimetype', node.get_mimetype())
        item.setPath(node.get_streaming_url())
        watchPlayback = False
        '''
            PLaying track
        '''
#        if qobuz.addon.getSetting('notification_playingsong') == 'true':
#            qobuz.gui.showNotificationH(lang(34000), item.getLabel(), item.getProperty('image'))
        rpc = xbmc_json_rpc()
        print "JSON RPC Version: " + rpc.JSONRPC_Version()
        rpc.Player_SetAudioStream(node.get_streaming_url())
        print "INFO: " + xbmc.getInfoLabel('Container.FolderPath')
        return True
        '''
            We are called from playlist...
        '''
        
        if qobuz.boot.handle == -1:
            super(QobuzPlayer, self).play(node.get_streaming_url(), item, False)
        else:
            xbmcplugin.setResolvedUrl(handle = qobuz.boot.handle, succeeded = True, listitem = item)
        '''
            May be a bad idea!!!
        '''
        xbmc.executebuiltin('Dialog.Close(all,true)')
        '''
            Waiting for song to start
        '''
        timeout = 30
        info(self, "Waiting song to start")
        while timeout > 0:
            if self.isPlayingAudio() == False:
                xbmc.sleep(250)
                timeout -= 0.250
            else:
                break
        if timeout <= 0:
            warn(self, "Player can't play track: " + item.getLabel())
            return False
        return True

