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
    scope.StatusCallbacks.append(cam.TemperatureStatusText)
    
@init_gui('Zyla Controls')
def zyla_controls(MainFrame,scope):
    from PYME.Acquire.Hardware.AndorNeo import ZylaControlPanel
    scope.camControls['Zyla'] = ZylaControlPanel.ZylaControl(MainFrame, scope.cameras['Zyla'], scope)
    MainFrame.camPanels.append((scope.camControls['Zyla'], 'sCMOS Properties'))


@init_gui('Nikon Stand')
def nikon_stand(MainFrame,scope):
    from PYME.IO import MetaDataHandler
    from PYME.Acquire.Hardware import NikonTi, NikonTiGUI
    scope.dichroic = NikonTi.FilterChanger()
    scope.lightpath = NikonTi.LightPath()

    TiPanel = NikonTiGUI.TiPanel(MainFrame, scope.dichroic, scope.lightpath)
    MainFrame.toolPanels.append((TiPanel, 'Nikon Ti'))

    MainFrame.time1.WantNotification.append(scope.dichroic.Poll)
    MainFrame.time1.WantNotification.append(scope.lightpath.Poll)

    MetaDataHandler.provideStartMetadata.append(scope.dichroic.ProvideMetadata)
    MetaDataHandler.provideStartMetadata.append(scope.lightpath.ProvideMetadata)

#must be here!!!
joinBGInit() # wait for anything which was being done in a separate thread

scope.initDone = True
