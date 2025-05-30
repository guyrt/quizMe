
## QuizMe was a little project I worked on to generate quizzes for web pages. It has a backend (django) and chrome extension. I moved on to other things, so there are a few rough edges.


I do all python dev in Docker, so only Docker needs to be installed.

To run django and the [webserve](./webserve) portion of the project:
A .env file in the format of [sample.env.txt](./webserve/sample.env.txt) needs to be populated with the needed values and placed in the webserve folder

## Basic Setup: 
#### A basic run:
```shell
docker compose up
```
#### Force Rebuild or first run
To force rebuild your images:
```shell
docker compose up --force-recreate --build # this will force newest code in.
```

#### To run a single service in a way that will catch breakpoints:
```shell
docker compose run --rm --service-ports web
```

#### To run management command, figure out the currently running image for web and exec in:
```shell
> docker ps
CONTAINER ID   IMAGE                         COMMAND                  CREATED      STATUS         PORTS                    NAMES
d5cfd127c1ec   flexindex.azurecr.io/web      "python manage.py ru…"   5 days ago   Up 6 seconds   0.0.0.0:8000->8000/tcp   financeexplorer-web-1
213aab17c615   pgvector/pgvector:pg15        "docker-entrypoint.s…"   5 days ago   Up 8 seconds   5432/tcp                 financeexplorer-pgsql-1
e4bc7c46c444   flexindex.azurecr.io/worker   "python manage.py rq…"   5 days ago   Up 8 seconds   8000/tcp                 financeexplorer-worker-1
```
Container d5cfd runs web
```shell
docker exec -it d5cfd127c1ec bash
```
#### All in one to do the prior tree steps in one-pass. Testing utility for a debug/run config in the editor:
```shell
#docker compose up -d --no-start &
docker compose up -d  &
sleep 5 
CONTAINER_ID=$(docker ps | grep web | awk '{print $1}')
docker exec -it ${CONTAINER_ID} bash

```

## Front End Setup: 
To build the front end: [front end readme](./browser_extension/README.md)

## Back End (python) Testing:
Back-end (pytest) [readme](./test/README.md)


## Azure Notes
This is the override for workers: `/bin/bash, -c, python /app/manage.py rqworker; echo hello; sleep 1000000`
You're running 4gb ram and 2 CPUs for worker.

You want to release with:

registry == registry.hub.docker.com
username == guyrt
password == 

then pick your image.

https://github.com/microsoft/azure-container-apps/issues/352

## Relevance Learnings
I ran some experiments in [doc_embedding](./webserve/parser_utils/webutils/doc_embedding.py) that produced a document embedding rather than a set of chunk embeddings. Not sure if I've got best also (SIF with mean correct) but relevant sucks for doc embedding compared to the chunk embed. Perhaps it's best to find the *best* chunk than to find a generally on topic doc?
