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

@init_hardware('Andor Zyla')
def init_zyla(scope):
    from PYME.Acquire.Hardware.AndorNeo import AndorZyla
    cam =  AndorZyla.AndorZyla(0)
    cam.Init()
    cam.port = 'R100'
    cam.orientation = dict(rotate=False, flipx=False, flipy=False)
    cam.DefaultEMGain = 0 #hack to make camera work with standard protocols
    cam.SetROI(512,512,1024,1024)
    #cam.SetSimpleGainMode('16-bit (low noise & high well capacity)')
    
    scope.register_camera(cam, 'Zyla')

    
@init_gui('Zyla Controls')
def zyla_controls(MainFrame,scope):
    from PYME.Acquire.Hardware.AndorNeo import ZylaControlPanel
    scope.camControls['Zyla'] = ZylaControlPanel.ZylaControl(MainFrame, scope.cameras['Zyla'], scope)
    MainFrame.camPanels.append((scope.camControls['Zyla'], 'sCMOS Properties'))


# @init_gui('sample database')
# def sample_db(MainFrame,scope):
#     from PYME.IO import MetaDataHandler
#     from PYME.Acquire import sampleInformationDjangoDirect as sampleInformation
#     sampPan = sampleInformation.slidePanel(MainFrame)
#     MetaDataHandler.provideStartMetadata.append(lambda mdh: sampleInformation.getSampleDataFailesafe(MainFrame,mdh))
#     MainFrame.camPanels.append((sampPan, 'Current Slide'))


# @init_gui('Focus Keys z')
# def focus_keys_z(MainFrame,scope):
#     from PYME.Acquire.Hardware import focusKeys
#     fk = focusKeys.FocusKeys(MainFrame, scope.piezos[0], scope=scope)
#     MainFrame.time1.WantNotification.append(fk.refresh)


#must be here!!!
joinBGInit() # wait for anything which was being done in a separate thread

scope.initDone = True
