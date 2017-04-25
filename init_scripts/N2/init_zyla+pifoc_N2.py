#!/usr/bin/python

##################
# init_zyla+pifoc_N2.py
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

from PYME.Acquire.Hardware.AndorNeo import AndorZyla

import scipy
from PYME.Acquire.Hardware.Simulator import fakeCam, fakePiezo
from PYME.Acquire.Hardware import fakeShutters
import time

InitBG('Andor Zyla', """
scope.cameras['Zyla'] =  AndorZyla.AndorZyla(0)
scope.cam = scope.cameras['Zyla']
scope.cameras['Zyla'].Init()
scope.cameras['Zyla'].port = 'R100'
scope.cameras['Zyla'].orientation = dict(rotate=False, flipx=False, flipy=False)
scope.cameras['Zyla'].DefaultEMGain = 0 #hack to make camera work with standard protocols
""")

InitGUI("""
from PYME.Acquire.Hardware.AndorNeo import ZylaControlPanel
scope.camControls['Zyla'] = ZylaControlPanel.ZylaControl(MainFrame, scope.cameras['Zyla'], scope)
camPanels.append((scope.camControls['Zyla'], 'sCMOS Properties'))
""")


InitBG('Z Piezo', """
from PYME.Acquire.Hardware.Piezos import piezo_e709

scope.piFoc = piezo_e709.piezo_e709T('COM20', 400, 0, True)
scope.hardwareChecks.append(scope.piFoc.OnTarget)
scope.CleanupFunctions.append(scope.piFoc.close)

scope.register_piezo(scope.piFoc, 'z')
#scope.piezos.append((scope.piFoc, 1, 'PIFoc'))
#scope.positioning['z'] = (scope.piFoc, 1, 1)



#scope.state.registerHandler('Positioning.z', lambda : scope.piFoc.GetPos(1), lambda v : scope.piFoc.MoveTo(1, v))
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
from PYME.Acquire.Hardware import spacenav
scope.spacenav = spacenav.SpaceNavigator()
scope.CleanupFunctions.append(scope.spacenav.close)
scope.ctrl3d = spacenav.SpaceNavPiezoCtrl(scope.spacenav, scope.piFoc, scope.xystage)
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

#must be here!!!
joinBGInit() #wait for anyhting which was being done in a separate thread

time.sleep(.5)
scope.initDone = True
