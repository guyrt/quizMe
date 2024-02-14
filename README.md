I do all python dev in Docker, so only Docker needs to be installed.

To run:
```shell
docker compose up
```

To force rebuild your images:
```shell
docker compose up --force-recreate --build # this will force newest code in.
```

To run a single service in a way that will catch breakpoints:
```shell
docker compose run --rm --service-ports web
```

To run management command, figure out the currently running image for web and exec in:
```shell
> docker ps
CONTAINER ID   IMAGE                         COMMAND                  CREATED      STATUS         PORTS                    NAMES
d5cfd127c1ec   flexindex.azurecr.io/web      "python manage.py ru…"   5 days ago   Up 6 seconds   0.0.0.0:8000->8000/tcp   financeexplorer-web-1
213aab17c615   pgvector/pgvector:pg15        "docker-entrypoint.s…"   5 days ago   Up 8 seconds   5432/tcp                 financeexplorer-pgsql-1
e4bc7c46c444   flexindex.azurecr.io/worker   "python manage.py rq…"   5 days ago   Up 8 seconds   8000/tcp                 financeexplorer-worker-1
```
# Contaienr d5cfd runs web
```shell
docker exec -it d5c bash
```

To build the front end: [front end readme](./browser_extension/README.md)
