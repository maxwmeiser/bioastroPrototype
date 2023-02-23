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
subscriber1 = ctx.socket(zmq.SUB)
subscriber1.connect(f'tcp://{ip}:{sub_port}')
subscriber1.subscribe('surfaces.s2')
subscriber2 = ctx.socket(zmq.SUB)
subscriber2.connect(f'tcp://{ip}:{sub_port}')
subscriber2.subscribe('surfaces.s3')
# subscriber.subscribe('surfaces.s2')
# subscriber.subscribe('surfaces.s3')
#different topics and all documentation: https://docs.pupil-labs.com/developer/core/network-api/#ipc-backbone-message-format

#writeFile = open("RecordVR.txt","w")
states = []
i = 0
while i < 1:
    states.append(time.time())
    topic, payload = subscriber.recv_multipart()
    message = msgpack.loads(payload)
    print(f"{topic}: {message}")
    topic, payload = subscriber1.recv_multipart()
    message = msgpack.loads(payload)
    print(f"{topic}: {message}")
    topic, payload = subscriber2.recv_multipart()
    message = msgpack.loads(payload)
    print(f"{topic}: {message}")
    # toPrint = message.get(b'gaze_on_surfaces')
    
    # for msg in toPrint:
    #     states.append(toPrint.get(b'on_surf'))
    i = i + 1


# for obj in states:
#     if obj is not bool:
#     #timestamp, newline, then print
#         writeFile.write("\n" + str(obj))
#     else:
#         writeFile.write(str(obj))





#https://realpython.com/python-pyqt-qthread/




