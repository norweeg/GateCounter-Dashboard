FROM python:3
WORKDIR /usr/src/app
RUN pip install --no-cache-dir sqlalchemy RPi.GPIO mysqlclient Adafruit-MCP3008 Adafruit-GPIO
ENTRYPOINT [ "python3" ]
