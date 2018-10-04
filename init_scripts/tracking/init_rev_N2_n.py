#!/usr/bin/python

##################
# init_rev_N2.py
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

    cam = uCam480.uc480Camera(findcamID_startswith('UI327x'),nbits=12, isDeviceID=True)
    cam.SetGain(50)
    scope.register_camera(cam, 'UEye')


@init_gui('Camera controls')
def cam_control(MainFrame, scope):
    from PYME.Acquire.Hardware.uc480 import ucCamControlFrame
    scope.camControls['UEye'] = ucCamControlFrame.ucCamPanel(MainFrame, scope.cameras['UEye'], scope)
    MainFrame.camPanels.append((scope.camControls['UEye'], 'UEye Properties'))


@init_hardware('Z Piezo')
def init_zpiezo(scope):
    from PYME.Acquire.Hardware.Piezos import offsetPiezo
    scope.piFoc = offsetPiezo.getClient('PHY-LMIC1')
    scope.register_piezo(scope.piFoc, 'z')


@init_gui('Drift tracking')
def init_driftTracking(MainFrame,scope):
    # we changed this to PYMEcs, i.e. our extra code
    from PYMEcs.Acquire.Hardware import driftTracking, driftTrackGUI
    scope.dt = driftTracking.correlator(scope, scope.piFoc)
    dtp = driftTrackGUI.DriftTrackingControl(MainFrame, scope.dt)
    MainFrame.camPanels.append((dtp, 'Focus Lock'))
    MainFrame.time1.WantNotification.append(dtp.refresh)



#must be here!!!
joinBGInit() #wait for anyhting which was being done in a separate thread

scope.initDone = True


