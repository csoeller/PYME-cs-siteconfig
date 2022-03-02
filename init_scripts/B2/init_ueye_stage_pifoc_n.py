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
    scope.register_camera(cam, 'Ueye')

@init_gui('Camera controls')
def cam_control(MainFrame, scope):
    from PYME.Acquire.Hardware.uc480 import ucCamControlFrame
    scope.camControls['Ueye'] = ucCamControlFrame.ucCamPanel(MainFrame, scope.cameras['Ueye'], scope)
    MainFrame.camPanels.append((scope.camControls['Ueye'], 'Ueye Cam Properties'))

# #PIFoc
# @init_hardware('PIFoc')
# def pifoc(scope):
#     from PYME.Acquire.Hardware.Piezos import piezo_e709, offsetPiezoREST

#     # check COM Port number
#     scope._piFoc = piezo_e709.piezo_e709T('COM11', 400, 0, True)
#     #scope.hardwareChecks.append(scope.piFoc.OnTarget)
#     scope.CleanupFunctions.append(scope._piFoc.close)

#     scope.piFoc = offsetPiezoREST.server_class()(scope._piFoc)
#     scope.register_piezo(scope.piFoc, 'z', needCamRestart=True)

@init_hardware('Z Piezo')
def zpiezo(scope):
    from PYME.Acquire.Hardware.Piezos import piezo_e816, offsetPiezoREST

    scope._piFoc = piezo_e816.piezo_e816T('COM14', 400, 0, False)
    scope.CleanupFunctions.append(scope._piFoc.close)

    scope.piFoc = offsetPiezoREST.server_class()(scope._piFoc)
    scope.register_piezo(scope.piFoc, 'z') # David's code has an extra ...,needCamRestart=True)


@init_hardware('XY Stage')
def init_xy(scope):
    from PYME.Acquire.Hardware.Mercury import mercuryStepperGCS
    scope.stage = mercuryStepperGCS.mercuryStepper(comPort='COM12', baud=115200,
                                                axes=['A', 'B'], steppers=['M-229.25S', 'M-229.25S'])
    scope.stage.SetSoftLimits(0, [1.06, 20.7])
    scope.stage.SetSoftLimits(1, [.8, 17.6])

    scope.register_piezo(scope.stage, 'x', needCamRestart=True, channel=0, multiplier=1)
    scope.register_piezo(scope.stage, 'y', needCamRestart=True, channel=1, multiplier=-1)

    scope.joystick = scope.stage.joystick
    scope.joystick.Enable(True)

    scope.CleanupFunctions.append(scope.stage.Cleanup)


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
