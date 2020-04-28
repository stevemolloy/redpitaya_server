#!/usr/bin/python3

from asyncio import coroutine, get_event_loop, start_server
from redpitaya.overlay.mercury import mercury as overlay
from time import sleep

togglepin = overlay.gpio('p', 7, 'out')
togglepin.write(False)
bitpins = [overlay.gpio('n', bit, 'out') for bit in reversed(range(5))]
LATCH_TIME = 0.1
HOST = '127.0.0.1'
PORT = 65432
 
def dectobinlist(num):
    "Returns a list of Booleans corresponding to the binary representation of the numerical input"
    return [(num & 2**digit) > 0 for digit in range(4, -1, -1)]

def set_pins(val):
    for chan, state in zip(bitpins, dectobinlist(val)):
        chan.write(state)

def latchnewval():
    sleep(LATCH_TIME)
    togglepin.write(True)
    sleep(LATCH_TIME)
    togglepin.write(False)
    sleep(LATCH_TIME)

def set_atten(val):
    "Sets the attenuation of the ZX76-31R5A-PNS+ to val."
    if val<1.0:
        val = 1.0
    elif val>31.0:
        val = 31.0

    setval = int(val)
    set_pins(setval)
    latchnewval()

    return setval

fpga = overlay()
digitisers = [fpga.osc(0, 1.0), fpga.osc(1, 1.0)]
for digi in digitisers:
    digi.decimation = 1
    digi.trigger_pre = 0
    digi.trigger_post = digi.buffer_size
    digi.trig_src = 0

@coroutine
def handle_echo(reader, writer):
    for digitiser in digitisers:
        digitiser.reset()
        digitiser.start()
        digitiser.trigger()

    data = yield from reader.read(100)
    # message = data.decode()
    # addr = writer.get_extra_info('peername')
    # print("Received %r from %r" % (message, addr))

    message_list = data.decode().split(':')
    cmd = message_list[0]

    if cmd=='digi':
        param = int(message_list[1])
        if param==0 or param==1:
            digitiser = digitisers[param]
            # wait for data
            while (digitiser.status_run()):
                pass
            # print ('triggered')
            osc_data = digitiser.data()
            writer.write(osc_data.tobytes())
            yield from writer.drain()
        else:
            print('Channel', param, 'not valid')
    elif cmd=='atten':
        param = float(message_list[1])
        val = set_atten(param)
        writer.write(str(val).encode())

    writer.close()

if __name__=="__main__":
    loop = get_event_loop()
    coro = start_server(handle_echo, HOST, PORT, loop=loop)
    print('Starting the server coroutine')
    server = loop.run_until_complete(coro)
    
    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    print('Ctrl-c to kill')
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    
    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

