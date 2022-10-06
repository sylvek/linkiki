
# Linkiki

Linkiki publishes current electricity power consumption of a [Linky](https://fr.wikipedia.org/wiki/Linky) over MQTT.

Basically, it broadcasts on two topics :

|topic|retain|description|
|---|---|---|
|sensors/linky/watt|no|current Watt consumption (integer)
|sensors/linky/state|yes|1 for HCHP / 0 for HCHC - sent only during switching


```
> npm install paho-mqtt pyserial
> python main.py </path/to/serial> <mqtt host>
```

Or…

```
> docker build -t linkiki .
> docker run --privileged -v /dev:/dev linkiki </path/to/serial> <mqtt host>
```