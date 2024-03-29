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

@init_hardware('Cameras')
def cam(scope):
    if True:
        from PYME.Acquire.Hardware.uc480 import uCam480
        uCam480.init(cameratype='ueye')
        cam = uCam480.uc480Camera(0,nbits=12)
    else: # use the pyueye interface
        from PYME.Acquire.Hardware.ueye import UEyeCamera
        cam = UEyeCamera(0, 12)
    cam.SetIntegTime(1.0) # by default we use 1s integration time
    # possibly set preamp gain as well - check!
    scope.register_camera(cam, 'Drift')

@init_gui('Camera controls')
def cam_control(MainFrame, scope):
    from PYME.Acquire.Hardware.uc480 import ucCamControlFrame
    scope.camControls['Drift'] = ucCamControlFrame.ucCamPanel(MainFrame, scope.cameras['Drift'], scope)
    MainFrame.camPanels.append((scope.camControls['Drift'], 'Drift Cam Properties'))

#PIFoc
@init_hardware('PIFoc')
def pifoc(scope):
    from PYME.Acquire.Hardware.Piezos import piezo_e709, offsetPiezoREST

    # check COM Port number
    scope._piFoc = piezo_e709.piezo_e709T('COM11', 400, 0, True)
    #scope.hardwareChecks.append(scope.piFoc.OnTarget)
    scope.CleanupFunctions.append(scope._piFoc.close)

    scope.piFoc = offsetPiezoREST.server_class()(scope._piFoc)
    scope.register_piezo(scope.piFoc, 'z', needCamRestart=True)

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
