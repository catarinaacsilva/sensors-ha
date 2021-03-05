FROM python:3.8-alpine
RUN apk update \
  && apk add \
    build-base
RUN mkdir /usr/src/sensor
WORKDIR /usr/src/sensor
COPY ./requirements.txt .
RUN pip install -r requirements.txt
ENV PYTHONUNBUFFERED 1
COPY ./mock_temp_hum_replay.py .
COPY ./room_climate-location_A-measurement01.csv .
ENTRYPOINT [ "python", "./mock_temp_hum_replay.py", "./room_climate-location_A-measurement01.csv" ]