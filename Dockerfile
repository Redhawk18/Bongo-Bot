FROM python:3.11.3-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN sudo apt install -y git
RUN pip3 install --no-cache-dir -r requirements.txt

COPY src/ src/

CMD [ "python3","src/main.py", "--docker" ]
