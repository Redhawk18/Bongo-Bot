FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt requirements.txt
COPY src/ src/

# If git releases of libraries are used
RUN apt update
RUN apt install -y build-essential git
RUN pip3 install --no-cache-dir -r requirements.txt

CMD [ "python3","src/main.py", "--docker" ]
