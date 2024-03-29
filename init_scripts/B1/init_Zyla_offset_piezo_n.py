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
def pz(scope):
    from PYME.Acquire.Hardware.Piezos import piezo_e709, offsetPiezoREST

    scope._piFoc = piezo_e709.piezo_e709T('COM8', 400, 0, True)
    #scope.hardwareChecks.append(scope.piFoc.OnTarget)
    scope.CleanupFunctions.append(scope._piFoc.close)

    scope.piFoc = offsetPiezoREST.server_class()(scope._piFoc)
    scope.register_piezo(scope.piFoc, 'z', needCamRestart=True)

@init_gui('Focus Keys z')
def focus_keys_z(MainFrame,scope):
    from PYME.Acquire.Hardware import focusKeys
    fk = focusKeys.FocusKeys(MainFrame, scope.piezos[0], scope=scope)
    MainFrame.time1.WantNotification.append(fk.refresh)

@init_gui('Filter Wheel 1')
def filter_wheel(MainFrame,scope):
    from PYME.Acquire.Hardware.FilterWheel import WFilter, FiltFrame, FiltWheel
    filtList = [WFilter(1, 'EMPTY', 'EMPTY', 0),
                WFilter(2, 'ND.5' , 'UVND 0.5', 0.5),
                WFilter(3, 'ND1'  , 'UVND 1'  , 1),
                WFilter(4, 'ND2', 'UVND 2', 2),
                WFilter(5, 'ND3'  , 'UVND 3'  , 3),
                WFilter(6, 'ND4'  , 'UVND 4'  , 4)]
    try:
        scope.filterWheel = FiltWheel(filtList, 'COM10')
        #scope.filterWheel.SetFilterPos("LF488")
        scope.filtPan = FiltFrame(MainFrame, scope.filterWheel)
        MainFrame.toolPanels.append((scope.filtPan, 'Filter Wheel'))
    except:
        print('Error starting filter wheel ...')

@init_gui('Filter Wheel 2')
def filter_wheel(MainFrame,scope):
    from PYME.Acquire.Hardware.FilterWheel import WFilter, FiltFrame, FiltWheel
    filtList = [WFilter(1, 'GFP', 'GFP exciter', 0),
                WFilter(2, 'TxRed' , 'TxRed exciter', 0),
                WFilter(3, 'Cy5'  , 'Cy5 exciter'  , 0),
                WFilter(4, 'Cy5.5', 'Cy5.5 exciter', 0),
                WFilter(5, 'Cy7'  , 'Cy7 exciter'  , 0),
                WFilter(6, 'ND4'  , 'UVND 4'  , 0)]
    try:
        scope.filterWheel = FiltWheel(filtList, 'COM11')
        #scope.filterWheel.SetFilterPos("LF488")
        scope.filtPan = FiltFrame(MainFrame, scope.filterWheel)
        MainFrame.toolPanels.append((scope.filtPan, 'Filter Wheel'))
    except:
        print('Error starting filter wheel ...')

@init_hardware('Lasers & Shutters')
def lasers(scope):
    from PYME.Acquire.Hardware import phoxxLaser

    scope.l647 = phoxxLaser.PhoxxLaser('l647', portname='COM4', scopeState=scope.state)
    scope.CleanupFunctions.append(scope.l647.Close)
    from PYME.Acquire.Hardware import cobaltLaser
    scope.l561 = cobaltLaser.CobaltLaserE('l561',portname='COM5',minpower=0.1,maxpower=0.2,scopeState = scope.state)
    scope.l488 = cobaltLaser.CobaltLaserE('l488',portname='COM6',minpower=0.005,maxpower=0.2,scopeState = scope.state)  
    scope.lasers = [scope.l647,scope.l561,scope.l488]

@init_gui('Laser Sliders')
def laser_sliders(MainFrame, scope):
    from PYME.Acquire.ui import lasersliders
    
    lsf = lasersliders.LaserSliders(MainFrame.toolPanel, scope.state)
    MainFrame.time1.WantNotification.append(lsf.update)
    MainFrame.camPanels.append((lsf, 'Lasers', False, False))


# the laser toggle buttons are now part of the improved laser sliders
# @init_gui('Laser Toggles')
# def laser_toggles(MainFrame, scope):
#     from PYME.Acquire.ui import lasersliders
#     if 'lasers'in dir(scope):
#         lcf = lasersliders.LaserToggles(MainFrame.toolPanel, scope.state)
#         MainFrame.time1.WantNotification.append(lcf.update)
#         MainFrame.camPanels.append((lcf, 'Laser Control'))

#must be here!!!
joinBGInit() # wait for anything which was being done in a separate thread

scope.initDone = True
