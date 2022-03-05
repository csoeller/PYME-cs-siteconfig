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

@init_hardware('Andor Zyla')
def init_zyla(scope):
    from PYME.Acquire.Hardware.AndorNeo import AndorZyla
    cam =  AndorZyla.AndorZyla(0)
    cam.Init()
    cam.port = 'R100'
    cam.orientation = dict(rotate=False, flipx=False, flipy=False)
    cam.DefaultEMGain = 0 #hack to make camera work with standard protocols
    cam.SetROI(512,512,1024,1024)
    #cam.SetSimpleGainMode('16-bit (low noise & high well capacity)')
    
    scope.register_camera(cam, 'Zyla')
    scope.StatusCallbacks.append(cam.TemperatureStatusText)
    
@init_gui('Zyla Controls')
def zyla_controls(MainFrame,scope):
    from PYME.Acquire.Hardware.AndorNeo import ZylaControlPanel
    scope.camControls['Zyla'] = ZylaControlPanel.ZylaControl(MainFrame, scope.cameras['Zyla'], scope)
    MainFrame.camPanels.append((scope.camControls['Zyla'], 'sCMOS Properties'))

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
                                                   axes=['X', 'Y'], steppers=['M-229.25S', 'M-229.25S'])
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
