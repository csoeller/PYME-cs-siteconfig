#!/usr/bin/python

##################
# init_TIRF.py
#
# Copyright David Baddeley, 2009
# d.baddeley@auckland.ac.nz
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##################
from PYME.Acquire.ExecTools import joinBGInit, HWNotPresent, init_gui, init_hardware
import time

@init_hardware('Andor sCMOS')
def init_zyla(scope):
    from PYME.Acquire.Hardware.AndorNeo import AndorZyla
    cam =  AndorZyla.AndorZyla(0)
    cam.Init()
    cam.orientation = dict(rotate=False, flipx=False, flipy=False) # we may want to tweak this
    cam.DefaultEMGain = 0 #hack to make camera work with standard protocols
    cam.SetROI(512,512,1024,1024)
    #cam.SetSimpleGainMode('16-bit (low noise & high well capacity)')
    hdmodes = [ match for match in cam.PixelEncodingForGain.keys() if match.startswith('16-bit')]
    if len(hdmodes) > 0:
        cam.SetSimpleGainMode(hdmodes[0])
  
    scope.register_camera(cam, 'sCMOS')
    scope.StatusCallbacks.append(cam.TemperatureStatusText)
    
@init_gui('sCMOS Controls')
def zyla_controls(MainFrame,scope):
    from PYME.Acquire.Hardware.AndorNeo import ZylaControlPanel
    scope.camControls['sCMOS'] = ZylaControlPanel.ZylaControl(MainFrame, scope.cameras['sCMOS'], scope)
    MainFrame.camPanels.append((scope.camControls['sCMOS'], 'sCMOS Properties'))

#PIFoc
@init_hardware('PIFoc')
def pifoc(scope):
    from PYMEcs.Acquire.Hardware import offsetPiezoRESTCorrelLog
    scope.piFoc = offsetPiezoRESTCorrelLog.getClient()
    scope.register_piezo(scope.piFoc, 'z')

@init_hardware('Z Piezo')
def zpiezo(scope):
    from PYME.Acquire.Hardware.Piezos import piezo_e709
    from PYMEcs.Acquire.Hardware import offsetPiezoRESTCorrelLog

    scope._piFoc = piezo_e709.piezo_e709T('COM11')
    scope.CleanupFunctions.append(scope._piFoc.close)

    scope.piFoc = offsetPiezoRESTCorrelLog.getServer()(scope._piFoc)
    scope.register_piezo(scope.piFoc, 'z', needCamRestart=True) # David's code has an extra ...,needCamRestart=True)
    
@init_gui('Drift tracking')
def init_driftTracking(MainFrame,scope):
    # we changed this to PYMEcs, i.e. our extra code
    from PYMEcs.Acquire.Hardware import driftTracking, driftTrackGUI
    # we limit stacksize to 2*7+1, possibly less in future?
    scope.dt = driftTracking.Correlator(scope, scope.piFoc, stackHalfSize = 4)
    dtp = driftTrackGUI.DriftTrackingControl(MainFrame, scope.dt)
    MainFrame.camPanels.append((dtp, 'Focus Lock'))
    MainFrame.time1.WantNotification.append(dtp.refresh)

@init_gui('Focus Keys')
def focus_keys(MainFrame, scope):
    from PYME.Acquire.Hardware import focusKeys
    fk = focusKeys.FocusKeys(MainFrame, scope.piezos[0])
    MainFrame.time1.WantNotification.append(fk.refresh)

#must be here!!!
joinBGInit() #wait for anyhting which was being done in a separate thread

#scope.SetCamera('A')

time.sleep(.5)
scope.initDone = True
