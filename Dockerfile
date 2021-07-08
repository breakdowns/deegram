FROM python:3-slim-buster

WORKDIR /app

COPY ./requirements.txt ./requirements.txt

RUN apk update \
    && apk add --no-cache gcc g++ musl-dev libffi-dev \
    && pip3 install --no-cache-dir -r requirements.txt \ 
    && apk del gcc g++ musl-dev libffi-dev

COPY . .

CMD python -m deegram
