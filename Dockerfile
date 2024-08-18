FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt ./

# TODO: More config to add (?)
# RUN apk --no-cache add --virtual .build-dependencies build-base postgresql-dev libffi-dev cargo \
#     && apk --no-cache add libpq \
#     && pip install --no-cache -r requirements.txt \
#     && apk del .build-dependencies \
#     && rm -rf /root/.cargo/

RUN pip install -U -r requirements.txt

COPY main.py ./
COPY .env.production ./.env
COPY logging.conf ./
COPY alembic.ini ./

COPY api ./api/
COPY db ./db/
COPY migrations ./migrations/
COPY logic ./logic/
COPY schemas ./schemas/
COPY services ./services/

RUN mkdir logs

EXPOSE 7000

COPY entrypoint.sh ./

RUN chmod +x ./entrypoint.sh

CMD ["./entrypoint.sh"]
