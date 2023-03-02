FROM python:3.9.16-slim-bullseye

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

#ENV .env .env
COPY . .

CMD [ "python3","src/main.py" ]
