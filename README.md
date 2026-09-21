# pico-pot-bar

A B10K potentiometer shown as a live bar on an SSD1306 128×32 OLED, on a
Raspberry Pi Pico. This is the **isolated, verified-working configuration** —
just the pot and the display, nothing else — kept separate from the larger
password-vault project.

Verified on hardware: full range **0 % (raw ~280) to 99 % (raw ~65530)**,
smooth, and stable to a few counts when held still.

## Wiring

| Signal | Pico pin | Label |
| --- | --- | --- |
| OLED SDA | 1 | `GP0` |
| OLED SCL | 2 | `GP1` |
| OLED VCC | 36 | `3V3(OUT)` |
| OLED GND | 38 | `GND` |
| Pot wiper (middle) | 31 | `GP26` / ADC0 |
| Pot end 1 | 36 | `3V3` |
| Pot end 2 | 38 | `GND` |

## Run

```bash
mpremote connect auto cp ssd1306.py pot_bar.py :
mpremote connect auto run pot_bar.py
```

Turn the knob; the OLED shows the position as a percentage and a filled bar.
Stop with Ctrl-C (it blanks the display on exit).

## Two things learned getting this working

Both cost real time, so they are written into the top of `pot_bar.py` too.

**I²C runs at 100 kHz, not 400 kHz.** On breadboard jumpers the display is
unreliable at 400 kHz — a bus scan false-ACKs *every* address (all 112) while
the lines still idle high, because the longer wires don't hold the fast edges.
At 100 kHz the scan returns a clean single `0x3c`. 100 kHz is plenty for a
128×32 panel.

**If the bar won't reach 0 %, the pot's GND-end leg is loose.** A marginal
ground floors the wiper high — seen stuck at 11 %, then 54 % after a bad reseat
(a floating ADC input sits near mid-scale). Reseating that one outer leg to
`GND` fixed it to a clean 0 %. The wiper and the 3V3 end were never the problem;
the reading reaching 99 % at the top proves those two.

## Files

```
pot_bar.py    the live bar (runs on the Pico)
ssd1306.py    display driver (micropython-lib, MIT)
```

## License

MIT. `ssd1306.py` is from
[micropython-lib](https://github.com/micropython/micropython-lib), also MIT.
