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
        
@init_hardware('UEye Camera')
def ueye_cam(scope):
    import logging
    import pprint
    from PYME.Acquire.Hardware.ueye import UEyeCamera

    def findcamID_startswith(modelname):
        if cl['count'] <= 0:
            raise RuntimeError('no suitable camera found')

        for cam in range(cl['count']):
            if cl['cameras'][cam]['model'].startswith(modelname):
                id = cl['cameras'][cam]['DeviceID']
                logging.info('found model %s with ID %d' % (cl['cameras'][cam]['model'],id))
                return id

        return None

    cam = UEyeCamera(0, 12)
    cam.SetGain(50)
    scope.register_camera(cam, 'UEye')

@init_gui('Camera controls')
def cam_control(MainFrame, scope):
    from PYME.Acquire.Hardware.uc480 import ucCamControlFrame
    scope.camControls['UEye'] = ucCamControlFrame.ucCamPanel(MainFrame, scope.cameras['UEye'], scope)
    MainFrame.camPanels.append((scope.camControls['UEye'], 'UEye Properties'))

scope.lasers = [] # we need that for most protocols

# @init_gui('Sample database')
# def samp_db(MainFrame, scope):
#     from PYME.Acquire import sampleInformation
#     sampPan = sampleInformation.slidePanel(MainFrame)
#     MainFrame.camPanels.append((sampPan, 'Current Slide'))


#must be here!!!
joinBGInit() #wait for anyhting which was being done in a separate thread

scope.initDone = True
