#!/usr/bin/python

##################
# standard488.py
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

#import all the stuff to make this work
from PYME.Acquire.protocol import *
import numpy

#define a list of tasks, where T(when, what, *args) creates a new task
#when is the frame number, what is a function to be called, and *args are any
#additional arguments
# protocol in which CoolLED will be switched on and off in loop
# power of CoolLED <0, 1>
pe4000_power = 0.02
# time in s
integrationTime = 1.0
pe4000_on_every_x_seconds = 4
total_time = 600
# in number of frames
total_num_of_frames = numpy.ceil(total_time / integrationTime).astype('int')
switching_pe4000_freq = numpy.ceil(pe4000_on_every_x_seconds / integrationTime).astype('int')
nFrames_with_pe4000_on = 3
frame_to_turnOn_pe4000 = 1

# create task list
taskList = [
    T(-1, scope.state.update, {
        'Camera.IntegrationTime': integrationTime
    }),
    T(-1, scope.pe4000.TurnOff),
    T(-1, scope.pe4000.SetPower, pe4000_power),
    #T(1, SetCameraShutter, True),
    T(1, scope.pe4000.TurnOn)
]

# add loop to turn on and off pe400
for f in range(numpy.max([frame_to_turnOn_pe4000, 1]),
               total_num_of_frames+numpy.max([frame_to_turnOn_pe4000, 1]),
               switching_pe4000_freq):
   
    taskList.append(T(f, scope.pe4000.TurnOn,duration=2.0))
    taskList.append(T(f+nFrames_with_pe4000_on, scope.pe4000.TurnOff))

frameNum = f + nFrames_with_pe4000_on
taskList.append(T(frameNum, scope.pe4000.TurnOff))


# turn off pe4000 after stopping the protocol
taskList.append(T(maxint, scope.pe4000.TurnOff))

#optional - metadata entries
metaData = []

#must be defined for protocol to be discovered
PROTOCOL = TaskListProtocol(taskList, metaData)
PROTOCOL_STACK = ZStackTaskListProtocol(taskList, 20, 100, metaData, randomise = False)














