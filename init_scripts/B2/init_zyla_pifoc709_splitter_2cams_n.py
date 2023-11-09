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

# Set a microscope name which describes this hardware configuration (e.g. a room number or similar)
# Used with the splitting ratio database and in other places where a microscope identifier is required.
scope.microscope_name = 'Nikon-B2' # Nikon System Bern number 2

from PYME.IO import MetaDataHandler
# here we are trying some hard coded sample info
def samplemdh_append(mdh):
    mdh['Sample.Specimen'] = 'red beads in PBS'
    mdh.setEntry('Sample.Labelling',[('beads','RedBeads')])
    
MetaDataHandler.provideStartMetadata.append(samplemdh_append)

@init_hardware('Andor sCMOS 1')
def init_scmos1(scope):
    from PYME.Acquire.Hardware.AndorNeo import AndorZyla
    cam =  AndorZyla.AndorZyla(0)
    cam.Init()
    cam.orientation = dict(rotate=False, flipx=False, flipy=False)
    cam.DefaultEMGain = 0 #hack to make camera work with standard protocols
    # cam.SetROI(512,512,1024,1024)
    hdmodes = [ match for match in cam.PixelEncodingForGain.keys() if match.startswith('16-bit')]
    if len(hdmodes) > 0:
        cam.SetSimpleGainMode(hdmodes[0])

    if cam.CameraModel.getValue().startswith('ZYLA'):
        cam.port = 'L100'
        modelname = 'Zyla'
    elif cam.CameraModel.getValue().startswith('SONA'):
        cam.port = 'R100'
        modelname = 'Sona'

    scope.register_camera(cam, modelname)
    scope.StatusCallbacks.append(cam.TemperatureStatusText)
    
@init_hardware('Andor sCMOS 2')
def init_scmos2(scope):
    from PYME.Acquire.Hardware.AndorNeo import AndorZyla
    cam =  AndorZyla.AndorZyla(1)
    cam.Init()
    cam.orientation = dict(rotate=False, flipx=False, flipy=False)
    cam.DefaultEMGain = 0 #hack to make camera work with standard protocols
    # cam.SetROI(512,512,1024,1024)
    hdmodes = [ match for match in cam.PixelEncodingForGain.keys() if match.startswith('16-bit')]
    if len(hdmodes) > 0:
        cam.SetSimpleGainMode(hdmodes[0])

    if cam.CameraModel.getValue().startswith('ZYLA'):
        cam.port = 'L100'
        modelname = 'Zyla'
    elif cam.CameraModel.getValue().startswith('SONA'):
        cam.port = 'R100'
        modelname = 'Sona'

    scope.register_camera(cam, modelname)
    scope.StatusCallbacks.append(cam.TemperatureStatusText)

@init_gui('Zyla Controls')
def zyla_controls(MainFrame,scope):
    from PYME.Acquire.Hardware.AndorNeo import ZylaControlPanel
    scope.camControls['Zyla'] = ZylaControlPanel.ZylaControl(MainFrame, scope.cameras['Zyla'], scope)
    MainFrame.camPanels.append((scope.camControls['Zyla'], 'Zyla Properties'))

@init_gui('Sona Controls')
def sona_controls(MainFrame,scope):
    from PYME.Acquire.Hardware.AndorNeo import ZylaControlPanel
    scope.camControls['Sona'] = ZylaControlPanel.ZylaControl(MainFrame, scope.cameras['Sona'], scope)
    MainFrame.camPanels.append((scope.camControls['Sona'], 'Sona Properties'))

@init_hardware('Z Piezo')
def zpiezo(scope):
    from PYME.Acquire.Hardware.Piezos import piezo_e709, offsetPiezoREST

    scope._piFoc = piezo_e709.piezo_e709T('COM11')
    scope.CleanupFunctions.append(scope._piFoc.close)

    scope.piFoc = offsetPiezoREST.server_class()(scope._piFoc)
    scope.register_piezo(scope.piFoc, 'z', needCamRestart=True) # David's code has an extra ...,needCamRestart=True)

@init_gui('splitter')
def ini_splitter(MainFrame,scope):
    from PYME.Acquire.Hardware import splitter
    constrainwidth = 550 # we constrain the width of the ROI region to 550 pixels; maximum is 1024 for the whole width
    chipwidth = scope.cameras['Zyla'].GetCCDWidth()
    scope.splt = splitter.Splitter(MainFrame, scope, scope.cameras['Zyla'],
                                   flipChan = 0, dichroic = 'BS50-50',
                                   transLocOnCamera = 'Left', flip=False,
                                   dir='left_right', constrain=False, border=int(int(chipwidth/2)-constrainwidth))

@init_gui('Focus Keys')
def focus_keys(MainFrame, scope):
    from PYME.Acquire.Hardware import focusKeys
    fk = focusKeys.FocusKeys(MainFrame, scope.piezos[0])
    MainFrame.time1.WantNotification.append(fk.refresh)

@init_gui('Analysis Settings')
def analysis_settings(MainFrame, scope):
    from PYME.Acquire.ui import AnalysisSettingsUI
    AnalysisSettingsUI.Plug(scope, MainFrame)


#must be here!!!
joinBGInit() #wait for anyhting which was being done in a separate thread

#scope.SetCamera('A')

time.sleep(.5)
scope.initDone = True
