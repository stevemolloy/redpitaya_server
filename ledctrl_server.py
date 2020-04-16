#!/usr/bin/python3

import asyncio
from redpitaya.overlay.mercury import mercury as FPGA

overlay = FPGA()
leds = [FPGA.led(i, 0) for i in range(8)]

HOST = '127.0.0.1'
PORT = 65432

@asyncio.coroutine
def handle_echo(reader, writer):
    data = yield from reader.read(100)
    message = data.decode()
    try:
        lednumber = int(message)
        leds[lednumber].write(not leds[lednumber].read())
    except ValueError:
        pass
    addr = writer.get_extra_info('peername')
    print("Received %r from %r" % (message, addr))

    print("Send: %r" % message)
    writer.write(data)
    yield from writer.drain()

    print("Close the client socket")
    writer.close()

loop = asyncio.get_event_loop()
coro = asyncio.start_server(handle_echo, HOST, PORT, loop=loop)
print('Starting the server coroutine')
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()

