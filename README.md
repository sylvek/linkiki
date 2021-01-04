
# Linkiki

Linkiki allows to share your PAPP [Linky](https://fr.wikipedia.org/wiki/Linky) data over MQTT.

```
> npm install paho-mqtt pyserial
> python main.py </path/to/serial> <mqtt host>
```

Or…

```
> docker build -t linkiki .
> docker run --privileged -v /dev:/dev linkiki </path/to/serial> <mqtt host>
```