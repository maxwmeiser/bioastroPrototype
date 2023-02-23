"""
Attempting to get real time data from pupil labs
"""
import zmq

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
subscriber.subscribe('surfaces.s1')
#different topics and all documentation: https://docs.pupil-labs.com/developer/core/network-api/#ipc-backbone-message-format

# we need a serializer (dont know what this is)
import msgpack

#slow down messages
import time

i = 0
while i < 1:
    topic, payload = subscriber.recv_multipart()
    message = msgpack.loads(payload)
    print(f"{topic}: {message}")
    # time.sleep(2)
    i += 1