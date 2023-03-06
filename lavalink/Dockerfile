FROM eclipse-temurin:19-jre

WORKDIR /app

COPY application.yml application.yml

RUN curl -L -O https://github.com/freyacodes/Lavalink/releases/download/3.7.5/Lavalink.jar

CMD [ "java",  "-jar", "Lavalink.jar" ]