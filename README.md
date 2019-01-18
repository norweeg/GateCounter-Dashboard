# Gate Counter Dashboard

This repository contains code to implement the [HCCC Library GateCounter](https://github.com/squash-/HCCC-Library-GateCounter-Scripts) with [Grafana](https://grafana.com/) for data display

## Before You Begin

You will need a computer, preferably running Linux, but anything will do.  Download and install Docker and Docker-compose following the instructions for your OS

* [Docker](https://www.docker.com/community-edition) (or [Docker Toolbox](https://docs.docker.com/toolbox/toolbox_install_windows/) if you do not have Windows 10 Professional or Enterprise.  See description below.)
* [Docker-Compose](https://docs.docker.com/compose/install/)

Please also, in a developer's text editor e.g. NotePad++ or Microsoft Visual Studio Code, read through docker-compose.yaml to make sure you understand it.  Before starting your stack, you will need to

* Register for [DuckDNS](https://www.duckdns.org/) and have your subdomain name and token ready
* Make sure ports 80 and 443 are accessible on your host machine and your machine has a connection to the Internet
* Edit the files .env, .configs/traefik.toml, and .configs/grafana.ini, updating configuration values with your desired configuration
* Run `docker-compose config` from this directory to doublecheck that docker-compose.yaml file contains no syntax errors and that all your options from .env were correctly filled in

## Creating Your Stack

Run `docker-compose up -d` to start everything

## Starting/Stopping/Restarting your stack or parts of it

To Stop or (re)Start a container in your stack without removing it, run `docker-compose stop grafana` replacing stop and grafana with the command and name of the container you wish to stop/start/restart.

## Updating Containers in Your Stack

Run the following commands to update the images your containers use and recreate/restart the containers using them

```bash
docker-compose pull
docker-compose up -d
docker image prune -f
```

## Removing a Single Container Without Removing Data Persisted in Docker Volumes

Run `docker-compose rm -s grafana` replacing grafana with the name of the service you wish to stop and remove without removing its persistent data. `docker-compose rm -s -v grafana` will stop and remove the container and any unnamed (not specified in docker-compose.yaml file) volumes connected to it.  To remove just a named volume, run `docker volume rm grafana_provisioning` replacing grafana_provisioning with the name of the volume you want to remove.  You can view all volumes with `docker volume ls`.

## Removing Your Stack Completely

Run `docker-compose down` to stop and remove all containers in your stack without removing their persistent data in named volumes.  You can run `docker-compose down -v` to remove all containers AND all named volumes.  **WARNING:** this will permanently remove data stored in docker volumes, but not data stored in mapped folders/files.  If you don't want to lose this data, either back it up first, or follow the instructions in the above section.
