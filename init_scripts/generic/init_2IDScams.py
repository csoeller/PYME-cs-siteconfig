#!/usr/bin/python

##################
# init_ui306x.py
#
# Copyright David Baddeley, 2009
# d.baddeley@auckland.ac.nz
# 
# Copyright Christian Soeller, 2017
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

@init_hardware('UEye Cameras')
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
    print uCam480.GetCameraList()
    cl = uCam480.GetCameraList()
    pprint.pprint(cl)

    cam = uCam480.uc480Camera(findcamID_startswith('UI324x'),
                              nbits=12, isDeviceID=True)
    scope.register_camera(cam, 'UEye UI324x')

    cam = uCam480.uc480Camera(findcamID_startswith('UI306x'),
                              nbits=12, isDeviceID=True)
    scope.register_camera(cam, 'UEye UI306x')
    scope.cam = cam # make this one the startup cam
    

# note: without camControls for both cams we have an issue when switching!
@init_gui('Camera controls')
def cam_control(MainFrame, scope):
    from PYME.Acquire.Hardware.uc480 import ucCamControlFrame
    scope.camControls['UEye UI306x'] = ucCamControlFrame.ucCamPanel(MainFrame,
                                                                     scope.cameras['UEye UI306x'],
                                                                     scope)
    MainFrame.camPanels.append((scope.camControls['UEye UI306x'], 'UI306x Properties'))

    scope.camControls['UEye UI324x'] = ucCamControlFrame.ucCamPanel(MainFrame,
                                                                     scope.cameras['UEye UI324x'],
                                                                     scope)
    MainFrame.camPanels.append((scope.camControls['UEye UI324x'], 'UI324x Properties'))

scope.lasers = [] # we need that for most protocols

@init_gui('Sample database')
def samp_db(MainFrame, scope):
    from PYME.Acquire import sampleInformation
    sampPan = sampleInformation.slidePanel(MainFrame)
    MainFrame.camPanels.append((sampPan, 'Current Slide'))


#must be here!!!
joinBGInit() #wait for anyhting which was being done in a separate thread

scope.initDone = True
