# Potentiometer bar on an SSD1306 128x32 - verified working configuration.
#
# Turn a B10K pot; the OLED shows the position as a percentage and a filled bar.
# When the pot reaches 100%, "ParadoxTransistor" appears and blinks once, then
# the bar returns. It re-arms after you turn back below full.
#
# VERIFIED ON HARDWARE:
#   full range 0% (raw ~280) to 99% (raw ~65530), smooth, stable at rest.
#
# WIRING (Raspberry Pi Pico):
#   OLED  SDA -> GP0 (pin 1)   SCL -> GP1 (pin 2)
#         VCC -> 3V3 (pin 36)  GND -> GND (pin 38)
#   Pot   wiper (middle) -> GP26 / ADC0 (pin 31)
#         one end -> 3V3 (pin 36)   other end -> GND (pin 38)
#
# TWO THINGS LEARNED GETTING THIS WORKING:
#   * I2C runs at 100 kHz, not 400 kHz. On breadboard jumpers the display
#     is unreliable at 400 kHz (a scan false-ACKs every address). 100 kHz
#     is rock solid and plenty for this panel.
#   * If the bar won't reach 0%, the pot's GND-end leg is loose. A marginal
#     ground floors the wiper high (seen: stuck at 11%, then 54%); reseating
#     that one wire fixed it to a clean 0%.

from machine import Pin, SoftI2C, ADC
from ssd1306 import SSD1306_I2C
import time

I2C_HZ = 100_000
OVERSAMPLE = 16          # calms the RP2040 ADC noise
FULL_PCT = 99            # the wiper tops out at ~99% (raw maxes near 65530),
                         # so treat 99%+ as "full" and fire the message there.

i2c = SoftI2C(sda=Pin(0), scl=Pin(1), freq=I2C_HZ)
oled = SSD1306_I2C(128, 32, i2c, addr=0x3C)
pot = ADC(Pin(26))


def read_pot():
    total = 0
    for _ in range(OVERSAMPLE):
        total += pot.read_u16()
    return total // OVERSAMPLE


def draw_bar(pct):
    oled.fill(0)
    oled.text("Potentiometer", 0, 0)
    oled.text("%3d %%" % pct, 0, 11)
    oled.rect(0, 23, 128, 9, 1)
    oled.fill_rect(0, 23, pct * 128 // 100, 9, 1)
    oled.show()


def show_name(on):
    # "ParadoxTransistor" is 17 chars - too wide for 128 px on one line,
    # so it stacks as two centred lines.
    oled.fill(0)
    if on:
        oled.text("Paradox", (128 - 7 * 8) // 2, 6)
        oled.text("Transistor", (128 - 10 * 8) // 2, 18)
    oled.show()


def blink_name_once():
    show_name(True)
    time.sleep_ms(500)
    show_name(False)      # off
    time.sleep_ms(250)
    show_name(True)       # back on = one blink
    time.sleep_ms(600)


armed = True              # ready to fire the message when we next hit full

try:
    while True:
        raw = read_pot()
        pct = raw * 100 // 65535
        if pct >= FULL_PCT and armed:
            blink_name_once()
            armed = False          # don't repeat until we leave full
        elif pct < FULL_PCT:
            armed = True           # re-arm once turned back down
        draw_bar(pct)
        time.sleep_ms(70)
except KeyboardInterrupt:
    oled.fill(0)
    oled.show()
