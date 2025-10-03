FROM --platform=linux/amd64 python:3.11-alpine

ARG MONGO_URL
ARG GUNICORN_WORKERS
ARG GUNICORN_TIMEOUT
ARG GUNICORN_PORT

ENV MONGO_URL=$MONGO_URL
ENV GUNICORN_WORKERS=$GUNICORN_WORKERS
ENV GUNICORN_TIMEOUT=$GUNICORN_TIMEOUT
ENV GUNICORN_PORT=$GUNICORN_PORT

WORKDIR /app

RUN apk update && apk add --no-cache tzdata

ENV TZ=America/Bogota

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

ENV DEBUG=false
CMD ["python", "main.py"]
# CMD gunicorn -w $GUNICORN_WORKERS -b "0.0.0.0:$GUNICORN_PORT" --timeout $GUNICORN_TIMEOUT "main:app"
