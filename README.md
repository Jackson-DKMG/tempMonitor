# tempMonitor

Generates a graph on a webpage with temperature readings in different rooms of the house + exterior over the past 48h, using an array of Raspberry Pi Zero W with DS18b20 sensors.

Python3 + D3.js V4

The Nest API is used to start the heating at night when the temperature drops below a certain value in one of the rooms (due to a thermal bridge, presumably, the temperature there drops much faster than anywhere else, and it's a child room).
This is a central heating so the activation is general, however the room is small and it heats up within minutes.

API credentials aren't included here.
