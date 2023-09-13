FROM python:3.11.5-slim

WORKDIR /app
COPY requirements.txt requirements.txt
COPY src/ src/

RUN pip3 install --no-cache-dir -r requirements.txt

CMD [ "python3","src/main.py", "--docker" ]
