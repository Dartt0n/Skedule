#!/bin/bash
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' skedule-database-container
