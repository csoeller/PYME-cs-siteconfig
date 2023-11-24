#!/usr/bin/python

##################
# init_cubicle_PHY_AMG.py
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
    #cam.SetSimpleGainMode('16-bit (low noise & high well capacity)')
    
    scope.register_camera(cam, 'Zyla', 'R100')
    scope.cam = cam # make the camera connected to the splitter as the startup cam. 


@init_gui('Zyla Controls')
def zyla_controls(MainFrame,scope):
    from PYME.Acquire.Hardware.AndorNeo import ZylaControlPanel
    scope.camControls['Zyla'] = ZylaControlPanel.ZylaControl(MainFrame, scope.cameras['Zyla'], scope)
    MainFrame.camPanels.append((scope.camControls['Zyla'], 'sCMOS Properties'))


@init_hardware('Andor Ixon')
def init_ixon(scope):
    from PYME.Acquire.Hardware.AndorIXon import AndorIXon
    cam = AndorIXon.iXonCamera(0)
    cam.SetShutter(False)
    cam.SetActive(False)
    cam.port = 'L100'
    scope.register_camera(cam, 'Ixon', 'L100')


@init_gui('Ixon Controls')
def ixon_controls(MainFrame,scope):
    from PYME.Acquire.Hardware.AndorIXon import AndorControlFrame
    scope.camControls['Ixon'] = AndorControlFrame.AndorPanel(MainFrame, scope.cameras['Ixon'], scope)
    MainFrame.camPanels.append((scope.camControls['Ixon'], 'EMCCD Properties'))


@init_gui('Sample database')
def samp_db(MainFrame, scope):
    from PYME.Acquire import sampleInformation
    from PYME.IO import MetaDataHandler
    
    MetaDataHandler.provideStartMetadata.append(lambda mdh: sampleInformation.getSampleDataFailsafe(MainFrame, mdh))
    
    sampPan = sampleInformation.slidePanel(MainFrame)
    MainFrame.camPanels.append((sampPan, 'Current Slide'))


@init_hardware('Z Piezo')
def init_zpiezo(scope):
    from PYME.Acquire.Hardware.Piezos import piezo_e816, offsetPiezo

    scope._piFoc = piezo_e816.piezo_e816T('COM22', 400, 0, False)
    scope.piFoc = offsetPiezo.piezoOffsetProxy(scope._piFoc)
    scope.register_piezo(scope.piFoc, 'z') # David's code has an extra ...,needCamRestart=True)

    #server so drift correction can connect to the piezo
    pst = offsetPiezo.ServerThread(scope.piFoc)
    pst.start()
    scope.CleanupFunctions.append(pst.cleanup)


@init_hardware('XY Stage')
def init_xy(scope):
    from PYME.Acquire.Hardware.Mercury import mercuryStepper
    scope.stage = mercuryStepper.mercuryStepper(comPort=21, baud=38400, axes=['A', 'B'], steppers=['M-229.25S', 'M-229.25S'])
    scope.stage.SetSoftLimits(0, [1.06, 20.7])
    scope.stage.SetSoftLimits(1, [.8, 17.6])
    scope.joystick = scope.stage.joystick
    scope.joystick.Enable(True)
    scope.CleanupFunctions.append(scope.stage.Cleanup)

    scope.register_piezo(scope.stage, 'x', channel=0, multiplier=1)
    scope.register_piezo(scope.stage, 'y', channel=1, multiplier=1)


# @init_gui('tracker')
# def postracker(MainFrame,scope):
#     from PYME.Acquire import positionTracker
#     pt = positionTracker.PositionTracker(scope, MainFrame.time1)
#     pv = positionTracker.TrackerPanel(MainFrame, pt)
#     MainFrame.AddPage(page=pv, select=False, caption='Track')
#     MainFrame.time1.WantNotification.append(pv.draw)


@init_gui('splitter')
def init_splitter(MainFrame,scope):
    from PYME.Acquire.Hardware import splitter
    splt = splitter.Splitter(MainFrame, scope, scope.cameras['Ixon'], flipChan = 0,
                             transLocOnCamera = 'bottom', flip=False, dir='up_down', constrain=False, dichroic='T710LPXXR-785R')


@init_gui('Nikon Stand')
def nikon_stand(MainFrame,scope):
    from PYME.IO import MetaDataHandler
    from PYME.Acquire.Hardware import NikonTi, NikonTiGUI
    scope.dichroic = NikonTi.FilterChanger()
    scope.lightpath = NikonTi.LightPath()

    TiPanel = NikonTiGUI.TiPanel(MainFrame, scope.dichroic, scope.lightpath)
    MainFrame.toolPanels.append((TiPanel, 'Nikon Ti'))

    MainFrame.time1.WantNotification.append(scope.dichroic.Poll)
    MainFrame.time1.WantNotification.append(scope.lightpath.Poll)

    MetaDataHandler.provideStartMetadata.append(scope.dichroic.ProvideMetadata)
    MetaDataHandler.provideStartMetadata.append(scope.lightpath.ProvideMetadata)


@init_gui('Focus Keys z')
def focus_keys_z(MainFrame,scope):
    from PYME.Acquire.Hardware import focusKeys
    fk = focusKeys.FocusKeys(MainFrame, scope.piezos[0], scope=scope)
    MainFrame.time1.WantNotification.append(fk.refresh)


# @init_gui('Focus Keys xy')
# def focus_keys_xy(MainFrame,scope):
#     from PYME.Acquire.Hardware import focusKeys
#     Posk = focusKeys.PositionKeys(MainFrame, scope.piezos[1], scope.piezos[2], scope=scope)
#     MainFrame.time1.WantNotification.append(Posk.refresh)


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
        scope.filterWheel = FiltWheel(filtList, 'COM7')
        #scope.filterWheel.SetFilterPos("LF488")
        scope.filtPan = FiltFrame(MainFrame, scope.filterWheel)
        MainFrame.toolPanels.append((scope.filtPan, 'Filter Wheel'))
    except:
        print 'Error starting filter wheel ...'


@init_gui('Exciter Wheel')
def exciter_wheel(MainFrame,scope):
    from PYME.Acquire.Hardware import ExciterWheel
    exciterList = [ExciterWheel.WFilter(1, 'FITC', 'FITC exciter', 0),
                   ExciterWheel.WFilter(2, '560' , '560 exciter', 0),
                   ExciterWheel.WFilter(3, 'TxRed'  , 'TxRed exciter'  , 0),
                   ExciterWheel.WFilter(4, 'Cy5', 'Cy5 exciter', 0),
                   ExciterWheel.WFilter(5, 'Cy5.5'  , 'Cy5.5 exciter'  , 0),
                   ExciterWheel.WFilter(6, 'EMPTY'  , 'EMPTY/no exciter'  , 0)]

    filterpair = [ExciterWheel.FilterPair('FITC', 'FITC'),
    ExciterWheel.FilterPair('560', '560'),
    ExciterWheel.FilterPair('TxRed', 'TxRed'),
    ExciterWheel.FilterPair('Cy5', 'Cy5'),
    ExciterWheel.FilterPair('Cy5', 'ChCy5'),
    ExciterWheel.FilterPair('Cy5.5', 'Cy5.5')]

    try:
        scope.exciterWheel = ExciterWheel.FiltWheel(exciterList, filterpair, 'COM19', dichroic=scope.dichroic)
        #scope.filterWheel.SetFilterPos("LF488")
        scope.exciterPan = ExciterWheel.FiltFrame(MainFrame, scope.exciterWheel)
        MainFrame.toolPanels.append((scope.exciterPan, 'Exciter Wheel'))
    except:
        print 'Error starting exciter wheel ...'


@init_hardware('Lasers')
def lasers(scope):
    from PYME.Acquire.Hardware import lasers
    sb = lasers.SBox(com_port='COM20')
    scope.l671 = lasers.SerialSwitchedLaser('l671',sb,0,scopeState = scope.state)
    scope.l671.register(scope)
    
    from PYME.Acquire.Hardware import phoxxLaser
    scope.l642 = phoxxLaser.PhoxxLaser('l642',portname='COM24',scopeState = scope.state)
    scope.CleanupFunctions.append(scope.l642.Close)
    scope.l642.register(scope)
    
    from PYME.Acquire.Hardware import cobaltLaser
    scope.l561 = cobaltLaser.CobaltLaserE('l561',portname='COM23',minpower=0.1, maxpower=0.2,scopeState = scope.state)
    scope.l561.register(scope)
    scope.l405 = cobaltLaser.CobaltLaserE('l405',portname='COM25',minpower=0.001, maxpower=0.1,scopeState = scope.state)
    scope.l405.register(scope)


@init_gui('Laser Control 1')
def laser_ctr1(MainFrame, scope):
    from PYME.Acquire.ui import lasersliders
    lsf = lasersliders.LaserSliders_(MainFrame.toolPanel, scope.lasers)
    MainFrame.time1.WantNotification.append(lsf.update)
    #lsf.update()
    MainFrame.camPanels.append((lsf, 'Laser Powers'))


@init_gui('Laser Control 2')
def laser_ctr2(MainFrame, scope):
    from PYME.Acquire.ui import lasersliders
    if 'lasers'in dir(scope):
        lcf = lasersliders.LaserToggles(MainFrame.toolPanel, scope.state)
        MainFrame.time1.WantNotification.append(lcf.update)
        MainFrame.camPanels.append((lcf, 'Laser Control'))


@init_gui('Action Panel')
def action_panel(MainFrame, scope):
    from PYME.Acquire.ui import actionUI

    ap = actionUI.ActionPanel(MainFrame, scope.actions, scope)
    MainFrame.AddPage(ap, caption='Queued Actions')


@init_gui('Analysis Settings')
def analysis_settings(MainFrame, scope):
    from PYME.Acquire.ui import AnalysisSettingsUI
    AnalysisSettingsUI.Plug(scope, MainFrame)


#must be here!!!
joinBGInit() #wait for anyhting which was being done in a separate thread


# time.sleep(.5) # this should not be necessary anymore
scope.initDone = True
