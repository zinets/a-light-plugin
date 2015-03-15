# -*- coding: utf-8 -*- 
import sys
import xbmc, xbmcgui

__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__addon__      = sys.modules[ "__main__" ].__addon__
__cwd__        = sys.modules[ "__main__" ].__cwd__
__icon__       = sys.modules[ "__main__" ].__icon__

stateStopped = 0
statePlaying = 1
statePaused = 2

def log(msg):
  xbmc.log("### [%s] - %s" % (__scriptname__, msg,), level=xbmc.LOGNOTICE)

class settings():
  def __init__( self, *args, **kwargs ):
    self.connected = False
    self.state = stateStopped
    self.update()
     
  def update(self):
    log('settings() - start')
    self.static_light = __addon__.getSetting("static_light") == "true";
    self.com_port = int(__addon__.getSetting("com_port"))
    # todo - защита от дурака при вводе данных
    self.screen_width = int(__addon__.getSetting("screen_width"))
    self.screen_height = int(__addon__.getSetting("screen_height"))
    self.screen_offset = int(__addon__.getSetting("screen_offset"))
    self.static_r = int(__addon__.getSetting("static_r"))
    self.static_g = int(__addon__.getSetting("static_g"))
    self.static_b = int(__addon__.getSetting("static_b"))


  def handleStaticBgSettings(self):
    log('settings() - handleStaticBgSettings')


  def handleStereoscopic(self, isStereoscopic):
    log('settings() - handleStereoscopic')

# def scan():
#   """scan for available ports. return a list of tuples (num, name)"""
#   available = []
#   for i in range(256):
#     try:
#       s = serial.Serial(i)
#       available.append((i, s.portstr))
#       s.close()   # explicit close 'cause of delayed GC in java
#     except serial.SerialException:
#       pass
#   return available
