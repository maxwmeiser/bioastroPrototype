import sys
import zmq
# we need a serializer (dont know what this is)
import msgpack
#slow down messages
import time

import inspect


ctx = zmq.Context()
# The REQ talks to Pupil remote and receives the session unique IPC SUB PORT
pupil_remote = ctx.socket(zmq.REQ)

ip = 'localhost'  # If you talk to a different machine use its IP.
port = 50020  # The port defaults to 50020. Set in Pupil Capture GUI.

pupil_remote.connect(f'tcp://{ip}:{port}')

# Request 'SUB_PORT' for reading data
pupil_remote.send_string('SUB_PORT')
sub_port = pupil_remote.recv_string()

# Request 'PUB_PORT' for writing data
pupil_remote.send_string('PUB_PORT')
pub_port = pupil_remote.recv_string()

# Assumes `sub_port` to be set to the current subscription port
subscriber = ctx.socket(zmq.SUB)
subscriber.connect(f'tcp://{ip}:{sub_port}')
subscriber.subscribe('surfaces.s1') # receive all surface.s1 messages
#different topics and all documentation: https://docs.pupil-labs.com/developer/core/network-api/#ipc-backbone-message-format

writeFile = open("Stats.txt","w")
floats = []
ints = []
timeB = 0
i = 0
while i < 1001:
    timeA = time.time()
    topic, payload = subscriber.recv_multipart()
    message = msgpack.loads(payload)
    #print(f"{topic}: {message}")
    toPrint = message.get(b'gaze_on_surfaces')
   
    #record difference in times betwwen messages in floats list, number of t/f in ints list
    #minimizing operations to see how fast messages are sent
    if timeB != 0:
        floats.append(timeA - timeB)
        ints.append(len(toPrint))
    timeB = timeA
    i = i + 1

stats = []

minMsg = 1000
maxMsg = 0
minState = 1000
maxState = 0
minTime = 1000
maxTime = 0
index = 0

for num in floats:
    #need to divide every float by the following int to get average time per t/f state
    stats.append((num / ints[index]))

    #finding minimum/maximum msg time
    if num > maxMsg:
        maxMsg = num
    if num < minMsg:
        minMsg = num
    
    #finding min/max number of states
    if ints[index] > maxState:
        maxState = ints[index]
    if ints[index] < minState:
        minState = ints[index]

    #find min/max time per state
    if stats[index] > maxTime:
        maxTime = stats[index]
    if stats[index] < minTime:
        minTime = stats[index]

    index = index + 1
        
#writing data out to file
writeFile.write('Surface Data Message Statistics\nRange Stats...\nHighest number of states per message: ' + str(maxState) + ' -- Lowest number of states per message:' + str(minState) + ' -- Range: ' + str(maxState - minState))
writeFile.write('\nHighest time between messages: ' + str(maxMsg) + ' -- Lowest time between messages: ' + str(minMsg) + ' -- Range: ' + str(maxMsg - minMsg))
writeFile.write('\nHighest time per state: ' + str(maxTime) + ' -- Lowest time per state: ' + str(minTime) + ' -- Range: ' + str(maxTime - minTime))
writeFile.write('\n\nAverages...')
writeFile.write('\nAverage time between messages: ' + str(sum(floats) / len(floats)))
averageStateTime = sum(stats) / len(stats)
writeFile.write('\nAverage time per T/F state: ' + str(averageStateTime))
averageStateNum = sum(ints) / len(ints)
writeFile.write('\nAverage number of states per message: ' + str(averageStateNum))

writeFile.write('\n\nRaw data...\n Time between messages | number of states')
index = 0
for num in floats:
    writeFile.write('\n' + str(num) + ' - ' + str(ints[index]))
    index = index + 1




#https://realpython.com/python-pyqt-qthread/




