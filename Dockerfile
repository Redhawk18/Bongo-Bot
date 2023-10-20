FROM python:slim

WORKDIR /app
COPY requirements.txt requirements.txt
COPY src/ src/

RUN apt update
RUN apt install -y git
RUN pip3 install --no-cache-dir -r requirements.txt

CMD [ "python3","src/main.py", "--docker" ]
