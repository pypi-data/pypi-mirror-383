## Local Dev (hot reload)
docker build -f app/Dockerfile.dev -t glyph-dev . 
docker run --rm -it -p 8000:8000 glyph-dev
-> http://localhost:8000/health

## Local Lambda (emulated)
docker build --no-cache -f app/Dockerfile.lambda -t glyph-lambda .
docker run --rm -p 9000:8080 --name glyph-lambda glyph-lambda

# Invoke Lambda (posts an event to the Runtime API)
curl -s -X POST \
  "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{}'


# Compose (optional convenience)
docker compose -f app/docker-compose.yml up --build api-dev
docker compose -f app/docker-compose.yml up --build api-lambda
docker compose -f app/docker-compose.yml down


===========================================================================================================
Notes on the Lambda base image

public.ecr.aws/lambda/python:3.12 is a Lambda runtime image you can run anywhere Docker runs.

Locally, it emulates the Lambda Runtime API on port 8080. You don’t need AWS to test basic invocation semantics.