#!/bin/bash
cd ..
zip -r Skedule.zip Skedule # zip project
scp Skedule.zip root@skedule.ru:/root # copy files

ssh root@skedule.ru "
rm -r Skedule;
docker stop \$(docker ps -a --filter=name=skedule-telegram --format=\"{{.ID}}\");
docker rm \$(docker ps -a --filter=name=skedule-telegram --format=\"{{.ID}}\");
docker image rm \$(docker images --filter=reference=skedule-telegram --format \"{{.ID}}\");

unzip Skedule.zip;
cd Skedule;
docker build -t skedule-telegram .;
docker run -d --name skedule-telegram skedule-telegram"
