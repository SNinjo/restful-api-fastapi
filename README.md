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

### Develop

```shell
uvicorn main:app --reload
```

### Test

```shell
pytest --cov=./ --cov-report term-missing
```

### Build

```shell
docker build . -t restful-api-fastapi
docker-compose up -d
```

[Swagger](http://localhost:8000/docs)
