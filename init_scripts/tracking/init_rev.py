#!/usr/bin/python

##################
# init_rev.py
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



from PYME.Acquire.Hardware.uc480 import uCam480

from PYME.Acquire.Hardware import fakeShutters
import time
import os
import sys

def GetComputerName():
    if sys.platform == 'win32':
        return os.environ['COMPUTERNAME']
    else:
        return os.uname()[1]



InitBG('EMCCD Cameras', """
uCam480.init(cameratype='uc480')
scope.cameras['A - Left'] = uCam480.uc480Camera(0)
#scope.cameras['B - Right'] = AndorIXon.iXonCamera(0)
#scope.cameras['B - Right'].SetShutter(False)
#scope.cameras['B - Right'].SetActive(False)
scope.cam = scope.cameras['A - Left']
""")



InitGUI("""
from PYME.Acquire.Hardware.AndorIXon import AndorControlFrame
scope.camControls['A - Left'] = AndorControlFrame.AndorPanel(MainFrame, scope.cameras['A - Left'], scope)
camPanels.append((scope.camControls['A - Left'], 'EMCCD A Properties'))
#
##scope.camControls['B - Right'] = AndorControlFrame.AndorPanel(MainFrame, scope.cameras['B - Right'], scope)
##camPanels.append((scope.camControls['B - Right'], 'EMCCD B Properties'))
#
""")


InitBG('PIFoc', """
from PYME.Acquire.Hardware.Piezos import offsetPiezo
scope.piFoc = offsetPiezo.getClient('PHY-AMG')# piezo_e816.piezo_e816('COM1', 400, 0, True)
scope.piezos.append((scope.piFoc, 1, 'PIFoc'))
""")

InitGUI("""
from PYME.Acquire.Hardware import driftTracking, driftTrackGUI
scope.dt = driftTracking.correlator(scope, scope.piFoc)
dtp = driftTrackGUI.DriftTrackingControl(MainFrame, scope.dt)
camPanels.append((dtp, 'Focus Lock'))
time1.WantNotification.append(dtp.refresh)
""")



#must be here!!!
joinBGInit() #wait for anyhting which was being done in a separate thread


time.sleep(.5)
scope.initDone = True
