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
        
# we need to get a way to get the camera ID into the InitBG call

@init_hardware('UEye Camera')
def ueye_cam(scope):
    from PYME.Acquire.Hardware.uc480 import uCam480

    uCam480.init(cameratype='ueye')
    cl = uCam480.GetCameraList()

    if cl['count'] <= 0:
        raise RunTimeError('no cameras')

    id = -1
    for cam in range(cl['count']):
        if cl['cameras'][cam]['model'].startswith('UI306x'):
            id = cl['cameras'][cam]['ID']
            print 'ID is %d' % id

    cam = uCam480.uc480Camera(0,nbits=12)
    # cam.port = 
    scope.register_camera(cam, 'UEye')

@init_gui('Camera controls')
def cam_control(MainFrame, scope):
    from PYME.Acquire.Hardware.uc480 import ucCamControlFrame
    scope.camControls['UEye'] = ucCamControlFrame.ucCamPanel(MainFrame, scope.cameras['UEye'], scope)
    MainFrame.camPanels.append((scope.camControls['UEye'], 'UEye Properties'))

scope.lasers = [] # we need that for most protocols

@init_gui('Sample database')
def samp_db(MainFrame, scope):
    from PYME.Acquire import sampleInformation
    sampPan = sampleInformation.slidePanel(MainFrame)
    MainFrame.camPanels.append((sampPan, 'Current Slide'))


#must be here!!!
joinBGInit() #wait for anyhting which was being done in a separate thread

scope.initDone = True
