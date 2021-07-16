# DOCKER
Reference: https://mariadb.com/kb/en/installing-and-using-mariadb-via-docker/
## Installing and preparing 

1) Install docker for your platform. Follow https://docs.docker.com/engine/install/

2) Start docker service, specificly for your platform.

3) Search for mariadb image:
    ```bash
    docker search mariadb
    ```
    In this guide I will use an official release of mariadb - `mariadb` image, but you can choose for your wish.
4) Get image:
    ```bash
    docker pull mariadb
    ```
## Creating a container

Create a Container with following command
    
    ```bash
    docker run --name mariadbcontainer -e MYSQL_ROOT_PASSWORD=12345 -p 3306:3306 -d maria db
    ```
    ! Use secure password instead of `12345`

## Automatic restart

When starting the container we can use `--restart` option to set an automatic restart policy.
Allowed values:
  - `no` - disable automatic restart
  - `on-failure` - restart on crash
  - `unless-stopped` - always restart the container unless it was stopped
  - `always` - always `(._.)`

## Control of the container

Restart:
  ```bash
  docker restart mariadbcontainer
  ```
Stop:
  ```bash
  docker stop mariadbcontainer
  ```
Destroy:
  ```bash
  docker rm mariadbcontainer
  ```
Destroy and delete /var/lib/mysql:
  ```bash
  docker rm -v mariadbcontainer
  ```
List of containers:
  ```bash
  docker ps
  ```
Command to get shell inside container:
  ```bash
  docker exec -it mariadbcontainer bash
  ```

## Connecting to mariadb inside the container
Find ip address assigned to the container:
  ```bash
  docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mariadbcontainer
  ```
  After that you can connect to the mariadb via tcp

