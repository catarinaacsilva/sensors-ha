FROM python:3.8-alpine
RUN apk update \
  && apk add \
    build-base
RUN mkdir /usr/src/sensor
WORKDIR /usr/src/sensor
COPY ./requirements.txt .
RUN pip install -r requirements.txt
ENV PYTHONUNBUFFERED 1
COPY ./mock_co2_light.py .
COPY ./iot_telemetry_data.csv .
ENTRYPOINT [ "python", "./mock_co2_light.py"]