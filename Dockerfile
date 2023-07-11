FROM python:3.11.3-slim

WORKDIR /app
COPY requirements.txt requirements.txt
COPY src/ src/

RUN apt install -y git
RUN pip3 install --no-cache-dir -r requirements.txt

CMD [ "python3","src/main.py", "--docker" ]
