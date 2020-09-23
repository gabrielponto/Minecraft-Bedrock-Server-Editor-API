FROM ubuntu:20.04
LABEL maintainer Gabriel Oliveira <contato@oliveiradigital.com.br>

ARG BEDROCK_SERVER_URL=https://minecraft.azureedge.net/bin-linux/bedrock-server-1.16.40.02.zip

RUN apt-get update && apt-get install -y supervisor \
	python3 \
	python3-virtualenv \
	unzip

WORKDIR /server

ADD app /app
ADD $BEDROCK_SERVER_URL /server/bedrock-server.zip
RUN unzip ./bedrock-server.zip && rm ./bedrock-server.zip

# Create worlds directory to be added to volumes
RUN mkdir -p /server/worlds
VOLUME /server/worlds

COPY deploy/server/server.properties /server/server.properties

WORKDIR /app
RUN virtualenv3 .venv --python python3 && .venv/bin/pip install -r requirements.txt