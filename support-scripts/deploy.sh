#!/bin/bash
cd ..
zip -r Skedule.zip Skedule
scp Skedule.zip root@skedule.ru:/root

ssh root@skedule.ru "
if [[ -d Skedule  ]]
    then rm -r Skedule
fi

if (docker ps -a --filter=name=skedule-telegram --format=\"{{.ID}}\")
    then docker stop \$(docker ps -a --filter=name=skedule-telegram --format=\"{{.ID}}\");
fi

if (docker ps -a --filter=name=skedule-telegram --format=\"{{.ID}}\")
    then docker rm \$(docker ps -a --filter=name=skedule-telegram --format=\"{{.ID}}\");
fi

if (docker images --filter=reference=skedule-telegram --format \"{{.ID}}\")
    then docker image rm \$(docker images --filter=reference=skedule-telegram --format \"{{.ID}}\");
fi

unzip Skedule.zip;
cd Skedule;
docker build -t skedule-telegram .;
docker run -d --name skedule-telegram skedule-telegram"


