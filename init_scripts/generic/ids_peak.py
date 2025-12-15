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
        
@init_hardware('IDSpeak Camera')
def ueye_cam(scope):
    import logging
    import pprint
    from PYME.Acquire.Hardware.ids_peak_cam import IDS_Camera

    # note that model name and serno are byte type, so checks should be done aginst byte literals, e.g. b'UI306x'
    # note sure if this will work with python 2 though?
    cam = IDS_Camera(0, nbits=12)
    scope.register_camera(cam, 'IDSpeak')

@init_gui('Camera controls')
def cam_control(MainFrame, scope):
    from PYME.Acquire.Hardware.uc480 import ucCamControlFrame
    scope.camControls['IDSpeak'] = ucCamControlFrame.ucCamPanel(MainFrame, scope.cameras['IDSpeak'], scope)
    MainFrame.camPanels.append((scope.camControls['IDSpeak'], 'IDSpeak Properties'))

scope.lasers = [] # we need that for most protocols

# @init_gui('Sample database')
# def samp_db(MainFrame, scope):
#     from PYME.Acquire import sampleInformation
#     sampPan = sampleInformation.slidePanel(MainFrame)
#     MainFrame.camPanels.append((sampPan, 'Current Slide'))


#must be here!!!
joinBGInit() #wait for anyhting which was being done in a separate thread

scope.initDone = True
