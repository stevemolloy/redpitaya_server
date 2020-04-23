from redpitaya.overlay.mercury import mercury as FPGA
from time import sleep

overlay = FPGA()
GPIO = FPGA.gpio

togglepin = GPIO('p', 7, 'out')
togglepin.write(False)
bitpins = [GPIO('n', bit, 'out') for bit in reversed(range(6))]
LATCH_TIME = 0.1

def dectobinlist(num):
    "Returns a list of Booleans corresponding to the binary representation of the numerical input"
    return [(num & 2**digit) > 0 for digit in range(5, -1, -1)]

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
    if val<0.5:
        val = 0.5
    elif val>31.5:
        val = 31.5

    set_pins(int(val*2))
    latchnewval()

    return val

if __name__=="__main__":
    for i in range(64):
        atten = i/2
        set_atten(atten)

    del(overlay)

