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

@init_hardware('Z Piezo')
def pz(scope):
    from PYME.Acquire.Hardware.Piezos import piezo_e709, offsetPiezoREST

    scope._piFoc = piezo_e709.piezo_e709T('COM8', 400, 0, True)
    #scope.hardwareChecks.append(scope.piFoc.OnTarget)
    scope.CleanupFunctions.append(scope._piFoc.close)

    scope.piFoc = offsetPiezoREST.server_class()(scope._piFoc)
    scope.register_piezo(scope.piFoc, 'z', needCamRestart=True)

@init_gui('Focus Keys z')
def focus_keys_z(MainFrame,scope):
    from PYME.Acquire.Hardware import focusKeys
    fk = focusKeys.FocusKeys(MainFrame, scope.piezos[0], scope=scope)
    MainFrame.time1.WantNotification.append(fk.refresh)


@init_gui('Filter Wheel 2')
def filter_wheel(MainFrame,scope):
    from PYME.Acquire.Hardware.FilterWheel import WFilter, FiltFrame, FiltWheel
    filtList = [WFilter(1, 'GFP', 'GFP exciter', 0),
                WFilter(2, 'TxRed' , 'TxRed exciter', 0),
                WFilter(3, 'Cy5'  , 'Cy5 exciter'  , 0),
                WFilter(4, 'Cy5.5', 'Cy5.5 exciter', 0),
                WFilter(5, 'Cy7'  , 'Cy7 exciter'  , 0),
                WFilter(6, 'ND4'  , 'UVND 4'  , 0)]
    try:
        scope.filterWheel = FiltWheel(filtList, 'COM7')
        #scope.filterWheel.SetFilterPos("LF488")
        scope.filtPan = FiltFrame(MainFrame, scope.filterWheel)
        MainFrame.toolPanels.append((scope.filtPan, 'Filter Wheel'))
    except:
        print('Error starting filter wheel ...')


#must be here!!!
joinBGInit() # wait for anything which was being done in a separate thread

scope.initDone = True
