FROM python:3.11.3-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

#ENV .env .env
COPY src/ src/

CMD [ "python3","src/main.py", "--docker" ]
