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

COPY deploy/supervisor/* /etc/supervisor/conf.d/
COPY deploy/supervisor.conf /etc/supervisor/supervisord.conf

COPY deploy/init.sh /init
RUN mkdir /var/log/supervisor
RUN chmod +x /init
CMD ["/init"]

# make log links
RUN ln -s /dev/stderr /var/log/supervisor/app_error.log
RUN ln -s /dev/stdout /var/log/supervisor/app.log
RUN ln -s /dev/stderr /var/log/supervisor/bedrock.err
RUN ln -s /dev/stdout /var/log/supervisor/bedrock.out

EXPOSE 80 19132