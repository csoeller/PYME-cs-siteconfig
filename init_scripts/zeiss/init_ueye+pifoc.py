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

#from PYME.Acquire.Hardware.AndorIXon import AndorIXon
from PYME.Acquire.Hardware.AndorIXon import AndorControlFrame

from PYME.Acquire.Hardware.uc480 import uCam480

from PYME.Acquire.Hardware import fakeShutters
import time

InitBG('EMCCD Cameras', '''
uCam480.init(cameratype='ueye')
scope.cameras['A - Left'] = uCam480.uc480Camera(0,nbits=12)
scope.cam = scope.cameras['A - Left']
''')

InitGUI('''
scope.camControls['A - Left'] = AndorControlFrame.AndorPanel(MainFrame, scope.cameras['A - Left'], scope)
camPanels.append((scope.camControls['A - Left'], 'EMCCD A Properties'))
''')

scope.lasers = [] # we need that for most protocols

InitGUI('''
from PYME.Acquire import sampleInformation
sampPan = sampleInformation.slidePanel(MainFrame)
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


InitBG('Z Piezo', '''
from PYME.Acquire.Hardware.Piezos import piezo_e709

scope.piFoc = piezo_e709.piezo_e709T('COM6', 400, 0, True)
#scope.hardwareChecks.append(scope._piFoc.OnTarget)
#scope.CleanupFunctions.append(scope._piFoc.close)
#scope.piFoc = offsetPiezo.piezoOffsetProxy(scope._piFoc)
scope.piezos.append((scope.piFoc, 1, 'PIFoc'))
scope.positioning['z'] = (scope.piFoc, 1, 1)

''')

InitGUI('''
from PYME.Acquire.Hardware import focusKeys
fk = focusKeys.FocusKeys(MainFrame, menuBar1, scope.piezos[0], scope=scope)
time1.WantNotification.append(fk.refresh)
''')

#must be here!!!
joinBGInit() #wait for anyhting which was being done in a separate thread

#scope.SetCamera('A')

time.sleep(.5)
scope.initDone = True
