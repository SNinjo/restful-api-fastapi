# restful-api-fastapi &middot; ![Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen)

A RESTful API server includes

* Framework: FastAPI
* OpenAPI: Swagger
* Database: MongoDB
* MongoDB Driver: Motor
* Test: Pytest
* Environment: Docker
* Deployment: Docker Compose

## Usage

### Build Database

```shell
docker-compose up -d mongo mongo-express
```

[Mongo Express](http://localhost:8081)

* username: root
* password: pass

### Develop

```shell
uvicorn main:app --reload
```

[Swagger](http://localhost:8000/docs)

### Test

```shell
pytest --cov=./ --cov-report term-missing
```

### Deploy

```shell
docker build . -t restful-api-fastapi
docker-compose up -d
```
