# tempMonitor

Generates a graph on a webpage with temperature readings in different rooms of the house + exterior over the past 48h, using an array of Raspberry Pi Zero W with DS18b20 sensors.

Python3 + D3.js V4 <br>

Would have been much easier to do with Matplotlib, yes.<br>

The main script queries the satellite RPis every 2 minutes by default (10 minutes for the exterior sensor), executing local scripts similar to the included <code>getLocalTemp.py</code> but called <code>getTemp.py</code>.

The exterior sensor is connected to one of the RPi which has also an interior sensor, so it has two scripts specifying the sensor ID
(they're 1-wire sensors so you can chain as many as you want. Technically, this whole thing could work with just one RPi and all the sensors connected to it, but it would be somewhat impractical to have a wire running throughout the house.):

<code>from w1thermsensor import W1ThermSensor</code><br>
<code>temp = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "00000992a512").get_temperature()</code><br>
<code>print(round(temp, 2))</code>
<br><br>
Sensor IDs can be obtained with <code>W1ThermSensor.get_available_sensors()</code>.
<br><br>
The Nest API is used to start the heating at night when the temperature drops below a certain value in one of the rooms (due to a thermal bridge, presumably, the temperature there drops much faster than anywhere else, and it's a child room).
This is a central heating so the activation is general, however the room is small and it heats up within minutes.
<br>
API credentials aren't included here.
