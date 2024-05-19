FROM python:3.8.2-alpine AS builder

# porta sulla quale sarà in ascolto il back
EXPOSE 8000
# imposto directory di lavoro
WORKDIR /app

# installo le dipendenze necessarie nel sistema operativo Alpine
RUN apk add --no-cache bash \
    && apk add --no-cache --virtual .build-deps \
        build-base \
        jpeg-dev \
        zlib-dev

# Crea un utente non root e passa ad esso
RUN adduser -D myuser
USER myuser

# copio file del progetto nel container
COPY server .
COPY requirements.txt .

# copy script nel container
COPY setup.sh /app/setup.sh
COPY wait-it.sh /app/wait-it.sh

# rendo gli script eseguibili
#RUN chmod +x /app/setup.sh
#RUN chmod +x /app/wait-it.sh

# comando che verra eseguito all'avvio del container
ENTRYPOINT [ "/app/setup.sh" ]