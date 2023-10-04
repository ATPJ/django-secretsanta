# Django SecretSanta

A fun project for giving gifts

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Documentations](#Documentations)

## Introduction

This is a restful API for a web application which has end-points for creating and managing users. Then users can make event for themselves and add their friends to the event.
After that the event creator (moderator of the event) can start that event, then the Event Start end-point will automaticlly chosse to which person should get gift for which person.
The Event attenders after that can see the person whome should get gift for them.

## Installation

For running this web application and testing first you should install Docker and Docker-Compose, then you can follow the instructions below:

1. Clone the repository:

   ```shell
   git clone https://github.com/ATPJ/django-secretsanta.git
    ```

1. Navigate to the project directory:

   ```shell
   cd django-secretsanta
   ```

1. Customize the configuration:

   You can change the environment variables of the 2 services which there are in docker-compose.yml with your credentials.

1. Build and run the Docker containers:

   ```shell
   docker-compose up -d
   ```

   This command will build the necessary Docker images and start the containers.


1. Access the web app:

   Once the containers are up and running, you can access the web app by visiting [127.0.0.1:80](http://127.0.0.1:80) in their web browser.
    > Note that you should change the port if you change that on docker-compose.yml

## Documentations

   You can access to the end-points documentations via [127.0.0.1:80/api/docs/](http://127.0.0.1:80/api/docs/)
   > You can try the API with the available GUI.


## TODO list

- [X] Implement base functionality
- [X] Update Readme
- [X] Implement Swagger UI for end-points
- [X] Write documentation
