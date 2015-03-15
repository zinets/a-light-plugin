# -*- coding: utf-8 -*- 
import xbmc
import xbmcaddon
import xbmcgui
import os

__addon__      = xbmcaddon.Addon()
__scriptname__ = __addon__.getAddonInfo('name')
__icon__       = __addon__.getAddonInfo('icon')
__cwd__        = __addon__.getAddonInfo('path')
__resource__   = xbmc.translatePath(os.path.join(__cwd__, 'lib'))

# serial
sys.path.append (__resource__)
import serial
ser = serial.Serial()

# settings
__resource__   = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) )
sys.path.append (__resource__)
from settings import *
settings = settings()

START_CHAR = chr(0x55)

# logger
def log(msg):
  xbmc.log("### [%s] - %s" % (__scriptname__, msg,), level=xbmc.LOGNOTICE)

# ----------------------- classes ---------------------------------------------
class MyPlayer( xbmc.Player ):
  def __init__(self, *args, **kwargs):
    xbmc.Player.__init__(self)
        
  def onPlayBackStopped(self):
    log("playback stopped")
    stateChanged(stateStopped)

  def onPlayBackPaused(self):
    log("playback paused")
    stateChanged(statePaused)

  def onPlayBackResumed( self ):
    log("playback resumed")
    stateChanged(statePlaying)
  
  def onPlayBackEnded(self):
    log("playback ended")
    stateChanged(stateStopped)
  
  def onPlayBackStarted(self):
    log("playback started")
    stateChanged(statePlaying)
  
# -----------------------------------------------------------------------------
class MyMonitor(xbmc.Monitor):
  def __init__(self, *args, **kwargs):
    xbmc.Monitor.__init__(self)
            
  def onSettingsChanged(self):
    settings.update()
    if ser.port != settings.com_port:
      settings.connected = initHardware(settings.com_port)
    else:
      stateChanged(settings.state)
      
  def onScreensaverDeactivated( self ):
    # settings.setScreensaver(False)
    pass
      
  def onScreensaverActivated( self ):    
    # settings.setScreensaver(True)
    pass
# ----------------------- classes ---------------------------------------------

def turnLightsOff():
  ser.write(START_CHAR)
  ser.write(START_CHAR)
  w = settings.screen_width;
  h = settings.screen_height;

  for x in range(0, (w + h) * 2):
    ser.write(chr(0))
    ser.write(chr(0))
    ser.write(chr(0))

# -----------------------------------------------------------------------------
def turnStaticLigths():
  w = settings.screen_width;
  h = settings.screen_height;

  ser.write(START_CHAR)
  ser.write(START_CHAR)
  
  for x in range(0, (w + h) * 2):
    ser.write(chr(settings.static_r))
    ser.write(chr(settings.static_g))
    ser.write(chr(settings.static_b))

# -----------------------------------------------------------------------------
def stateChanged(state):
  if settings.connected:
    log("state changed to %d, connected" % state)
    settings.state = state
    if state == stateStopped:
      if settings.static_light:
        turnStaticLigths()
      else:
        turnLightsOff()
  else:
    log("state changed, not connected")
    settings.state = stateStopped  

# -----------------------------------------------------------------------------
def initHardware(port_num):
  # print "Found ports:"
  # for n,s in scan():
  #   print "(%d) %s" % (n,s)

  connected = False  

  if ser.isOpen():
    ser.close()
  
  try:      
    ser.port = port_num
    ser.baudrate = 115200
    ser.open()
    connected = ser.isOpen()    
    log("connected! %d" % connected)
  except serial.SerialException:
    log("serial port opening error")
    
  if (connected):
    xbmc.executebuiltin("XBMC.Notification(%s,%s,%s,%s)" % (__scriptname__,
                        "Connected",
                        750,
                        __icon__))
    log("connected to lights")
  else:
    log("no hardware connection")
  return connected

# -----------------------------------------------------------------------------
def runloop():
  xbmc_monitor = MyMonitor()
  player_monitor = MyPlayer()
  port_num = settings.com_port
  settings.connected = initHardware(settings.com_port) 
  turnStaticLigths()
  
  w = settings.screen_width
  h = settings.screen_height
  offset = settings.screen_offset;
  
  capture = xbmc.RenderCapture()
  capture.capture(w, h, xbmc.CAPTURE_FLAG_CONTINUOUS)
  
  while not xbmc.abortRequested:
    xbmc.sleep(20)

    capture.waitForCaptureStateChangeEvent(1000)
    if settings.state == statePlaying and capture.getCaptureState() == xbmc.CAPTURE_STATE_DONE: # and player_monitor.isPlaying():
      # width = capture.getWidth();
      # height = capture.getHeight();
      pixels = capture.getImage();

      ser.write(START_CHAR)
      ser.write(START_CHAR)

      # (1)
      y = h - 1;
      for x in range(offset - 1, -1, -1):
        addr = 4 * (x + y * w)

        ser.write(chr(pixels[addr + 2]))
        ser.write(chr(pixels[addr + 1]))
        ser.write(chr(pixels[addr]))

      # (2)
      x = 0;
      for y in range(h - 1, -1, -1):
        addr = 4 * (x + y * w)

        ser.write(chr(pixels[addr + 2]))
        ser.write(chr(pixels[addr + 1]))
        ser.write(chr(pixels[addr]))

      # (3)
      y = 0;
      for x in range(w): 
        addr = 4 * (x + y * w)

        ser.write(chr(pixels[addr + 2]))
        ser.write(chr(pixels[addr + 1]))
        ser.write(chr(pixels[addr]))

      # (4)
      x = w - 1;
      for y in range(h):
        addr = 4 * (x + y * w)

        ser.write(chr(pixels[addr + 2]))
        ser.write(chr(pixels[addr + 1]))
        ser.write(chr(pixels[addr]))

      # (5)
      y = h - 1
      for x in range(offset, w):
        addr = 4 * (x + y * w)

        ser.write(chr(pixels[addr + 2]))
        ser.write(chr(pixels[addr + 1]))
        ser.write(chr(pixels[addr]))

  turnLightsOff()
  ser.close()
  del xbmc_monitor
  del player_monitor

if ( __name__ == "__main__" ):
  runloop()
