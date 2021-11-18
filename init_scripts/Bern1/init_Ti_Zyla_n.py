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


@init_hardware('Fake Piezos')
def pz(scope):
    from PYME.Acquire.Hardware.Simulator import fakePiezo
    scope.fakePiezo = fakePiezo.FakePiezo(100)
    scope.register_piezo(scope.fakePiezo, 'z', needCamRestart=True)
    
    scope.fakeXPiezo = fakePiezo.FakePiezo(100)
    scope.register_piezo(scope.fakeXPiezo, 'x')
    
    scope.fakeYPiezo = fakePiezo.FakePiezo(100)
    scope.register_piezo(scope.fakeYPiezo, 'y')

pz.join() #piezo must be there before we start camera

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


# @init_hardware('Nikon Stand')
# def nikon_stand(scope):
#     from PYME.Acquire.Hardware import NikonTi
#     scope.dichroic = NikonTi.FilterChanger()
#     scope.lightpath = NikonTi.LightPath()

    #TiPanel = NikonTiGUI.TiPanel(MainFrame, scope.dichroic, scope.lightpath)
    #MainFrame.toolPanels.append((TiPanel, 'Nikon Ti'))

    #MainFrame.time1.WantNotification.append(scope.dichroic.Poll)
    #MainFrame.time1.WantNotification.append(scope.lightpath.Poll)

    #MetaDataHandler.provideStartMetadata.append(scope.dichroic.ProvideMetadata)
    #MetaDataHandler.provideStartMetadata.append(scope.lightpath.ProvideMetadata)

@init_gui('Filter Wheel')
def filter_wheel(MainFrame,scope):
    from PYME.Acquire.Hardware.FilterWheel import WFilter, FiltFrame, FiltWheel
    filtList = [WFilter(1, 'EMPTY', 'EMPTY', 0),
                WFilter(2, 'ND.5' , 'UVND 0.5', 0.5),
                WFilter(3, 'ND1'  , 'UVND 1'  , 1),
                WFilter(4, 'ND2', 'UVND 2', 2),
                WFilter(5, 'ND3'  , 'UVND 3'  , 3),
                WFilter(6, 'ND4'  , 'UVND 4'  , 4)]
    try:
        scope.filterWheel = FiltWheel(filtList, 'COM4')
        #scope.filterWheel.SetFilterPos("LF488")
        scope.filtPan = FiltFrame(MainFrame, scope.filterWheel)
        MainFrame.toolPanels.append((scope.filtPan, 'Filter Wheel'))
    except:
        print('Error starting filter wheel ...')


@init_hardware('Lasers & Shutters')
def lasers(scope):
    from PYME.Acquire.Hardware import phoxxLaser

    scope.l647 = phoxxLaser.PhoxxLaser('l647', portname='COM3', scopeState=scope.state)
    scope.CleanupFunctions.append(scope.l647.Close)
    scope.lasers = [scope.l647, ]

@init_gui('Laser controls')
def laser_controls(MainFrame, scope):
    from PYME.Acquire.ui import lasersliders
    
    lsf = lasersliders.LaserSliders(MainFrame.toolPanel, scope.state)
    MainFrame.time1.WantNotification.append(lsf.update)
    MainFrame.camPanels.append((lsf, 'Lasers', False, False))


@init_gui('Laser Control 2')
def laser_ctr2(MainFrame, scope):
    from PYME.Acquire.ui import lasersliders
    if 'lasers'in dir(scope):
        lcf = lasersliders.LaserToggles(MainFrame.toolPanel, scope.state)
        MainFrame.time1.WantNotification.append(lcf.update)
        MainFrame.camPanels.append((lcf, 'Laser Control'))

#must be here!!!
joinBGInit() # wait for anything which was being done in a separate thread

scope.initDone = True
