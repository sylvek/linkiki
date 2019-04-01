FROM python:2-alpine
RUN ["pip", "install", "paho-mqtt", "pyserial"]
COPY main.py /main.py
ENTRYPOINT [ "python", "./main.py" ]