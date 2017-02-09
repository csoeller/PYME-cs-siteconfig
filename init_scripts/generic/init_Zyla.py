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

from PYME.Acquire.Hardware.AndorNeo import ZylaControlPanel
from PYME.Acquire.Hardware.AndorNeo import AndorZyla

from PYME.Acquire.Hardware import fakeShutters
import time

from PYME.IO import MetaDataHandler

InitBG('Andor Zyla', '''
scope.cameras['Zyla'] =  AndorZyla.AndorZyla(0)
scope.cam = scope.cameras['Zyla']
scope.cameras['Zyla'].Init()
scope.cameras['Zyla'].SetSimpleGainMode('16-bit (low noise & high well capacity)')
''')

InitGUI('''
scope.camControls['Zyla'] = ZylaControlPanel.ZylaControl(MainFrame, scope.cameras['Zyla'], scope)
camPanels.append((scope.camControls['Zyla'], 'sCMOS Properties'))
''')

InitGUI('''
from PYME.Acquire import sampleInformationDjangoDirect as sampleInformation
sampPan = sampleInformation.slidePanel(MainFrame)
MetaDataHandler.provideStartMetadata.append(lambda mdh: sampleInformation.getSampleDataFailesafe(MainFrame,mdh))
camPanels.append((sampPan, 'Current Slide'))
''')

#setup for the channels to aquire - b/w camera, no shutters
class chaninfo:
    names = ['bw']
    cols = [1] #1 = b/w, 2 = R, 4 = G1, 8 = G2, 16 = B
    hw = [fakeShutters.CH1] #unimportant - as we have no shutters
    itimes = [100]

scope.chaninfo = chaninfo
scope.shutters = fakeShutters


InitGUI('''
from PYME.Acquire.Hardware import focusKeys
fk = focusKeys.FocusKeys(MainFrame, menuBar1, scope.piezos[0], scope=scope)
time1.WantNotification.append(fk.refresh)
''')

scope.lasers = []

InitGUI('''
if 'lasers' in dir(scope):
    from PYME.Acquire.Hardware import LaserControlFrame
    lcf = LaserControlFrame.LaserControlLight(MainFrame,scope.lasers)
    time1.WantNotification.append(lcf.refresh)
    toolPanels.append((lcf, 'Laser Control'))
''')


#must be here!!!
joinBGInit() #wait for anyhting which was being done in a separate thread

time.sleep(.5)
scope.initDone = True
