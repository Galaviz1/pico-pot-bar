# Potentiometer bar on an SSD1306 128x32 - verified working configuration.
#
# Turn a B10K pot; the OLED shows the position as a percentage and a filled bar.
# This is the isolated, confirmed-good setup, kept separate from the vault.
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

i2c = SoftI2C(sda=Pin(0), scl=Pin(1), freq=I2C_HZ)
oled = SSD1306_I2C(128, 32, i2c, addr=0x3C)
pot = ADC(Pin(26))


def read_pot():
    total = 0
    for _ in range(OVERSAMPLE):
        total += pot.read_u16()
    return total // OVERSAMPLE


try:
    while True:
        raw = read_pot()
        pct = raw * 100 // 65535
        oled.fill(0)
        oled.text("Potentiometer", 0, 0)
        oled.text("%3d %%" % pct, 0, 11)
        oled.rect(0, 23, 128, 9, 1)                 # bar outline
        oled.fill_rect(0, 23, pct * 128 // 100, 9, 1)  # fill
        oled.show()
        time.sleep_ms(70)
except KeyboardInterrupt:
    oled.fill(0)
    oled.show()
