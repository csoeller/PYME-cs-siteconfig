#!/usr/bin/python

##################
# init_offsetpiezo_N2.py
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


@init_hardware('UEye Camera')
def ueye_cam(scope):
    import logging
    import pprint
    from PYME.Acquire.Hardware.uc480 import uCam480

    def findcamID_startswith(modelname):
        if cl['count'] <= 0:
            raise RuntimeError('no suitable camera found')

        for cam in range(cl['count']):
            if cl['cameras'][cam]['model'].startswith(modelname):
                id = cl['cameras'][cam]['DeviceID']
                logging.info('found model %s with ID %d' % (cl['cameras'][cam]['model'],id))
                return id

        return None

    uCam480.init(cameratype='ueye')
    cl = uCam480.GetCameraList()
    pprint.pprint(cl)

    cam = uCam480.uc480Camera(findcamID_startswith('UI306x'),nbits=12, isDeviceID=True)
    cam.SetGain(50)
    cam.port = 'L100'
    scope.register_camera(cam, 'UEye', 'L100')


@init_gui('Camera controls')
def cam_control(MainFrame, scope):
    from PYME.Acquire.Hardware.uc480 import ucCamControlFrame
    scope.camControls['UEye'] = ucCamControlFrame.ucCamPanel(MainFrame, scope.cameras['UEye'], scope)
    MainFrame.camPanels.append((scope.camControls['UEye'], 'UEye Properties'))


@init_gui('sample database')
def sample_db(MainFrame,scope):
    from PYME.IO import MetaDataHandler
    from PYME.Acquire import sampleInformationDjangoDirect as sampleInformation
    sampPan = sampleInformation.slidePanel(MainFrame)
    MetaDataHandler.provideStartMetadata.append(lambda mdh: sampleInformation.getSampleDataFailesafe(MainFrame,mdh))
    MainFrame.camPanels.append((sampPan, 'Current Slide'))


@init_hardware('Z Piezo')
def init_zpiezo(scope):
    from PYME.Acquire.Hardware.Piezos import piezo_e709, offsetPiezo

    scope._piFoc = piezo_e709.piezo_e709T('COM20', 400, 0, True)
    scope.hardwareChecks.append(scope._piFoc.OnTarget)
    scope.CleanupFunctions.append(scope._piFoc.close)
    scope.piFoc = offsetPiezo.piezoOffsetProxy(scope._piFoc)
    scope.register_piezo(scope.piFoc, 'z') # David's code has an extra ...,needCamRestart=True)

    #server so drift correction can connect to the piezo
    pst = offsetPiezo.ServerThread(scope.piFoc)
    pst.start()
    scope.CleanupFunctions.append(pst.cleanup)


@init_hardware('XY Stage')
def init_xy(scope):
    from PYME.Acquire.Hardware.Piezos import piezo_c867
    scope.xystage = piezo_c867.piezo_c867T('COM16')
    scope.joystick = piezo_c867.c867Joystick(scope.xystage)
    #scope.joystick.Enable(True)
    scope.hardwareChecks.append(scope.xystage.OnTarget)
    scope.CleanupFunctions.append(scope.xystage.close)

    scope.register_piezo(scope.xystage, 'x', channel=1) # David's code has an extra ...,needCamRestart=True)
    scope.register_piezo(scope.xystage, 'y', channel=2, multiplier=1) # David's code has an extra ...,needCamRestart=True)


@init_gui('tracker')
def postracker(MainFrame,scope):
    from PYME.Acquire import positionTracker
    pt = positionTracker.PositionTracker(scope, MainFrame.time1)
    pv = positionTracker.TrackerPanel(MainFrame, pt)
    MainFrame.AddPage(page=pv, select=False, caption='Track')
    MainFrame.time1.WantNotification.append(pv.draw)


@init_gui('splitter')
def ini_splitter(MainFrame,scope):
    from PYME.Acquire.Hardware import splitter
    splt = splitter.Splitter(MainFrame, scope, scope.cameras['Zyla'], flipChan = 0,
                             transLocOnCamera = 'Left', flip=False, dir='left_right', constrain=False)


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


@init_gui('spacenav')
def ini_spacenav(MainFrame,scope):
    from PYME.Acquire.Hardware import spacenav
    scope.spacenav = spacenav.SpaceNavigator()
    scope.CleanupFunctions.append(scope.spacenav.close)
    scope.ctrl3d = spacenav.SpaceNavPiezoCtrl(scope.spacenav, scope.piFoc, scope.xystage)


@init_gui('Focus Keys z')
def focus_keys_z(MainFrame,scope):
    from PYME.Acquire.Hardware import focusKeys
    fk = focusKeys.FocusKeys(MainFrame, scope.piezos[0], scope=scope)
    MainFrame.time1.WantNotification.append(fk.refresh)


@init_gui('Focus Keys xy')
def focus_keys_xy(MainFrame,scope):
    from PYME.Acquire.Hardware import focusKeys
    Posk = focusKeys.PositionKeys(MainFrame, scope.piezos[1], scope.piezos[2], scope=scope)


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
        scope.filterWheel = FiltWheel(filtList, 'COM21')
        #scope.filterWheel.SetFilterPos("LF488")
        scope.filtPan = FiltFrame(MainFrame, scope.filterWheel)
        MainFrame.toolPanels.append((scope.filtPan, 'Filter Wheel'))
    except:
        print 'Error starting filter wheel ...'


@init_gui('Exciter Wheel')
def exciter_wheel(MainFrame,scope):
    from PYME.Acquire.Hardware import ExciterWheel
    exciterList = [ExciterWheel.WFilter(1, 'GFP', 'GFP exciter', 0),
                   ExciterWheel.WFilter(2, 'TxRed' , 'TxRed exciter', 0),
                   ExciterWheel.WFilter(3, 'Cy5'  , 'Cy5 exciter'  , 0),
                   ExciterWheel.WFilter(4, 'Cy5.5', 'Cy5.5 exciter', 0),
                   ExciterWheel.WFilter(5, 'Cy7'  , 'Cy7 exciter'  , 0),
                   ExciterWheel.WFilter(6, 'ND4'  , 'ND4'  , 0)]

    filterpair = [ExciterWheel.FilterPair('GFP', 'GFP'),
                  ExciterWheel.FilterPair('TxRed', 'TxRed'),
                  ExciterWheel.FilterPair('Cy5', 'Cy5'),
                  ExciterWheel.FilterPair('Cy5.5', 'Cy5.5'),
                  ExciterWheel.FilterPair('Cy7', 'Cy7'),
                  ExciterWheel.FilterPair('To be added', 'To be added')]
    try:
        scope.exciterWheel = ExciterWheel.FiltWheel(exciterList, filterpair, 'COM22', dichroic=scope.dichroic)
        #scope.filterWheel.SetFilterPos("LF488")
        scope.exciterPan = ExciterWheel.FiltFrame(MainFrame, scope.exciterWheel)
        MainFrame.toolPanels.append((scope.exciterPan, 'Exciter Wheel'))
    except:
        print 'Error starting exciter wheel ...'


@init_hardware('Lasers')
def lasers(scope):
    from PYME.Acquire.Hardware import lasers
    sb = lasers.SBox(com_port='COM6')
    scope.l671 = lasers.SerialSwitchedLaser('l671',sb,0,scopeState = scope.state)
    scope.l671.register(scope)
    #scope.l532 = lasers.SerialSwitchedLaser('l532',sb,2,scopeState = scope.state)
    #scope.l532.register(scope)
    
    from PYME.Acquire.Hardware import matchboxLaser
    scope.l405 = matchboxLaser.MatchboxLaser('l405',portname='COM5',scopeState = scope.state)
    scope.l405.register(scope)
    
    from PYME.Acquire.Hardware import phoxxLaserOLD
    scope.l647 = phoxxLaserOLD.PhoxxLaser('l647',portname='COM15',scopeState = scope.state)
    scope.StatusCallbacks.append(scope.l647.GetStatusText)
    scope.l647.register(scope)
    
    from PYME.Acquire.Hardware import cobaltLaser
    scope.l561 = cobaltLaser.CobaltLaser('l561',portname='COM10',minpower=0.1, maxpower=0.2,scopeState = scope.state)
    scope.l561.register(scope)
    scope.l488 = cobaltLaser.CobaltLaser('l488',portname='COM9',minpower=0.001, maxpower=0.2,scopeState = scope.state)
    scope.l488.register(scope)


@init_gui('Laser Control 1')
def laser_ctr1(MainFrame, scope):
    from PYME.Acquire import lasersliders
    lsf = lasersliders.LaserSliders(MainFrame.toolPanel, scope.lasers)
    MainFrame.time1.WantNotification.append(lsf.update)
    #lsf.update()
    MainFrame.camPanels.append((lsf, 'Laser Powers'))


@init_gui('Laser Control 2')
def laser_ctr2(MainFrame, scope):
    if 'lasers'in dir(scope):
        from PYME.Acquire.Hardware import LaserControlFrame
        lcf = LaserControlFrame.LaserControlLight(MainFrame,scope.lasers)
        MainFrame.time1.WantNotification.append(lcf.refresh)
        MainFrame.camPanels.append((lcf, 'Laser Control'))

#temporarily take the DMD module out. For now we use the manufacturer's software to control the DMD - Ruisheng
# do we get errors if this is not present ?
# @init_hardware('DMD')
# def dmd(scope):
#     from PYME.Acquire.Hardware import TiLightCrafter

#     scope.LC = TiLightCrafter.LightCrafter()
#     scope.LC.Connect()
#     scope.LC.SetDisplayMode(scope.LC.DISPLAY_MODE.DISP_MODE_IMAGE)
#     scope.LC.SetStatic(255)

# # do we get errors if this is not present ?
# @init_gui('DMDGui')
# def dmd_gui(MainFrame, scope):
#     from PYME.Acquire.Hardware import DMDGui
#     DMDModeSelectionPanel = DMDGui.DMDModeChooserPanel(MainFrame, scope)
#     DMDtpPanel = DMDGui.DMDTestPattern(MainFrame, scope.LC)
#     DMDsiPanel = DMDGui.DMDStaticImage(MainFrame, scope.LC)
#     DMDseqPanel = DMDGui.DMDImageSeq(MainFrame, scope.LC)
#     MainFrame.camPanels.append((DMDModeSelectionPanel, 'select DMD Mode'))
#     MainFrame.camPanels.append((DMDtpPanel, 'select test pattern'))
#     MainFrame.camPanels.append((DMDsiPanel, 'select static image'))
#     MainFrame.camPanels.append((DMDseqPanel, 'select image sequence'))


@init_gui('Arclamp')
def arclamp(MainFrame, scope):
    from PYME.Acquire.Hardware import priorLumen, arclampshutterpanel
    try:
        scope.arclampshutter = priorLumen.PriorLumen('Arc lamp shutter', portname='COM23')
        scope.shuttercontrol = [scope.arclampshutter]
        acf = arclampshutterpanel.Arclampshutterpanel(MainFrame,scope.shuttercontrol)
        MainFrame.time1.WantNotification.append(acf.refresh)
        MainFrame.camPanels.append((acf, 'Shutter Control'))
    except:
        print 'Error starting arc-lamp shutter ...'


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
