#!/usr/bin/python

##################
# init_cubicle_PHY_AMG_nooffsetpiezo.py
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

from PYME.Acquire.Hardware.AndorIXon import AndorIXon
from PYME.Acquire.Hardware.AndorNeo import AndorZyla


from PYME.Acquire.Hardware.Simulator import fakeCam, fakePiezo
from PYME.Acquire.Hardware import fakeShutters
import time
import os
import sys
import scipy

def GetComputerName():
    if sys.platform == 'win32':
        return os.environ['COMPUTERNAME']
    else:
        return os.uname()[1]




InitBG('Andor Zyla', """
scope.cameras['Zyla'] =  AndorZyla.AndorZyla(0)
scope.cam = scope.cameras['Zyla']
scope.cameras['Zyla'].Init()
scope.cameras['Zyla'].port = 'R100'
scope.cameras['Zyla'].orientation = dict(rotate=False, flipx=False, flipy=False)
scope.cameras['Zyla'].DefaultEMGain = 0 #hack to make camera work with standard protocols
""")

InitBG('EMCCD Cameras', """
scope.cameras['Ixon'] = AndorIXon.iXonCamera(0)
scope.cameras['Ixon'].SetShutter(False)
scope.cameras['Ixon'].SetActive(False)
scope.cameras['Ixon'].port = 'L100'
""")

InitGUI("""
from PYME.Acquire.Hardware.AndorNeo import ZylaControlPanel
scope.camControls['Zyla'] = ZylaControlPanel.ZylaControl(MainFrame, scope.cameras['Zyla'], scope)
camPanels.append((scope.camControls['Zyla'], 'sCMOS Properties'))

from PYME.Acquire.Hardware.AndorIXon import AndorControlFrame
scope.camControls['Ixon'] = AndorControlFrame.AndorPanel(MainFrame, scope.cameras['Ixon'], scope)
camPanels.append((scope.camControls['Ixon'], 'EMCCD Properties'))
""")

InitGUI("""
from PYME.IO import MetaDataHandler
from PYME.Acquire import sampleInformationDjangoDirect as sampleInformation
sampPan = sampleInformation.slidePanel(MainFrame)
MetaDataHandler.provideStartMetadata.append(lambda mdh: sampleInformation.getSampleDataFailesafe(MainFrame,mdh))
camPanels.append((sampPan, 'Current Slide'))
""")

#setup for the channels to aquire - b/w camera, no shutters
# class chaninfo:
#     names = ['bw']
#     cols = [1] #1 = b/w, 2 = R, 4 = G1, 8 = G2, 16 = B
#     hw = [fakeShutters.CH1] #unimportant - as we have no shutters
#     itimes = [100]

# scope.chaninfo = chaninfo
# scope.shutters = fakeShutters

InitGUI("""
from PYME.Acquire import sarcSpacing
ssp = sarcSpacing.SarcomereChecker(MainFrame, menuBar1, scope)
""")


InitBG('Z Piezo', """
from PYME.Acquire.Hardware.Piezos import piezo_e816

scope.piFoc = piezo_e816.piezo_e816('COM22', 400, 0, False)

scope.register_piezo(scope.piFoc, 'z')
#scope.piezos.append((scope.piFoc, 1, 'PIFoc'))
#scope.positioning['z'] = (scope.piFoc, 1, 1)



#scope.state.registerHandler('Positioning.z', lambda : scope.piFoc.GetPos(1), lambda v : scope.piFoc.MoveTo(1, v))
 """)


InitBG('Stage Stepper Motors', """
from PYME.Acquire.Hardware.Mercury import mercuryStepper
scope.stage = mercuryStepper.mercuryStepper(comPort=21, baud=38400, axes=['A', 'B'], steppers=['M-229.25S', 'M-229.25S'])
scope.stage.SetSoftLimits(0, [1.06, 20.7])
scope.stage.SetSoftLimits(1, [.8, 17.6])
#scope.piezos.append((scope.stage, 0, 'Stage X'))
#scope.piezos.append((scope.stage, 1, 'Stage Y'))
scope.joystick = scope.stage.joystick
scope.joystick.Enable(True)
scope.CleanupFunctions.append(scope.stage.Cleanup)

scope.register_piezo(scope.stage, 'x', channel=0, multiplier=1000)
scope.register_piezo(scope.stage, 'y', channel=1, multiplier=-1000)
#scope.positioning['x'] = (scope.stage, 0, 1000)
#scope.positioning['y'] = (scope.stage, 1, -1000)

#scope.state.registerHandler('Positioning.x', lambda : 1000*scope.stage.GetPos(0), lambda v : scope.stage.MoveTo(0, v*1e-3))
#scope.state.registerHandler('Positioning.y', lambda : -1000*scope.stage.GetPos(1), lambda v : scope.stage.MoveTo(1, -v*1e-3))
""")


InitGUI("""
from PYME.Acquire import positionTracker
pt = positionTracker.PositionTracker(scope, time1)
pv = positionTracker.TrackerPanel(MainFrame, pt)
MainFrame.AddPage(page=pv, select=False, caption='Track')
time1.WantNotification.append(pv.draw)
""")


InitGUI("""
from PYME.Acquire.Hardware import splitter
splt = splitter.Splitter(MainFrame, scope, scope.cameras['Ixon'], flipChan = 0, transLocOnCamera = 'bottom', flip=False, dir='up_down', constrain=False)
""")


InitGUI("""
from PYME.Acquire.Hardware import NikonTi, NikonTiGUI
scope.dichroic = NikonTi.FilterChanger()
scope.lightpath = NikonTi.LightPath()

TiPanel = NikonTiGUI.TiPanel(MainFrame, scope.dichroic, scope.lightpath)
toolPanels.append((TiPanel, 'Nikon Ti'))
#time1.WantNotification.append(TiPanel.SetSelections)
time1.WantNotification.append(scope.dichroic.Poll)
time1.WantNotification.append(scope.lightpath.Poll)

MetaDataHandler.provideStartMetadata.append(scope.dichroic.ProvideMetadata)
MetaDataHandler.provideStartMetadata.append(scope.lightpath.ProvideMetadata)
""")


InitGUI("""
from PYME.Acquire.Hardware import focusKeys
fk = focusKeys.FocusKeys(MainFrame, scope.piezos[0], scope=scope)
time1.WantNotification.append(fk.refresh)
""")

InitGUI("""
from PYME.Acquire.Hardware import focusKeys
Posk = focusKeys.PositionKeys(MainFrame, menuBar1, scope.piezos[1], scope.piezos[2], scope=scope)
#time1.WantNotification.append(fk.refresh)
""")


InitGUI("""
from PYME.Acquire.Hardware.FilterWheel import WFilter, FiltFrame, FiltWheel
filtList = [WFilter(1, 'EMPTY', 'EMPTY', 0),
    WFilter(2, 'ND.5' , 'UVND 0.5', 0.5),
    WFilter(3, 'ND1'  , 'UVND 1'  , 1),
    WFilter(4, 'ND2', 'UVND 2', 2),
    WFilter(5, 'ND3'  , 'UVND 3'  , 3),
    WFilter(6, 'ND4'  , 'UVND 4'  , 4)]
try:
    scope.filterWheel = FiltWheel(filtList, 'COM18')
    #scope.filterWheel.SetFilterPos("LF488")
    scope.filtPan = FiltFrame(MainFrame, scope.filterWheel)
    toolPanels.append((scope.filtPan, 'Filter Wheel'))
except:
    print 'Error starting filter wheel ...'
""")


InitGUI("""
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
    toolPanels.append((scope.exciterPan, 'Exciter Wheel'))
except:
    print 'Error starting exciter wheel ...'
""")



from PYME.Acquire.Hardware import lasers
sb = lasers.SBox('COM20')
scope.l671 = lasers.SerialSwitchedLaser('l671',sb,0)

from PYME.Acquire.Hardware import phoxxLaser
scope.l642 = phoxxLaser.PhoxxLaser('l642',portname='COM24')
scope.CleanupFunctions.append(scope.l642.Close)

from PYME.Acquire.Hardware import cobaltLaser
scope.l561 = cobaltLaser.CobaltLaser('l561',portname='COM23')
scope.l405 = cobaltLaser.CobaltLaser('l405',portname='COM25')

scope.lasers = [scope.l405,scope.l561,scope.l642,scope.l671]


InitGUI("""
from PYME.Acquire import lasersliders
lsf = lasersliders.LaserSliders(toolPanel, scope.lasers)
time1.WantNotification.append(lsf.update)
#lsf.update()
camPanels.append((lsf, 'Laser Powers'))
""")

InitGUI("""
if 'lasers'in dir(scope):
    from PYME.Acquire.Hardware import LaserControlFrame
    lcf = LaserControlFrame.LaserControlLight(MainFrame,scope.lasers)
    time1.WantNotification.append(lcf.refresh)
    camPanels.append((lcf, 'Laser Control'))
""")



InitGUI("""
from PYME.Acquire.ui import actionUI

ap = actionUI.ActionPanel(MainFrame, scope.actions, scope)
MainFrame.AddPage(ap, caption='Queued Actions')
""")

InitGUI("""
from PYME.Acquire.ui import AnalysisSettingsUI
AnalysisSettingsUI.Plug(scope, MainFrame)
""")


#must be here!!!
joinBGInit() #wait for anyhting which was being done in a separate thread


time.sleep(.5)
scope.initDone = True
