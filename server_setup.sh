#!/usr/bin/bash

#install dependencies
sudo apt install openjdk-17-jdk -y

#make lavalink dir
mkdir lavalink
cd lavalink

#download lavalink
wget https://github.com/freyacodes/Lavalink/releases/download/3.5-rc2/Lavalink.jar

echo "Lavalink setup complete"