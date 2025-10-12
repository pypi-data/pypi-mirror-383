# Glyph Forge

A comprehensive platform for managing and deploying glyph-based applications.

## Development Setup

### Prerequisites

- Git
- Python 3.9+
- Docker
- AWS CLI

### Initial Setup

1. Install Docker

2. Dev mode:

- docker build -f app/Dockerfile.dev -t glyph-dev .

- docker run --rm -it -p 8000:8000 glyph-dev

- Visit http://localhost:8000/health

3 Lambda mode:

- docker build --no-cache -f app/Dockerfile.lambda -t glyph-lambda .

- docker run --rm -p 9000:8080 glyph-lambda

- Invoke with the curl command shown above

(Optional) Use docker compose to avoid long commands and run either service by name.
(see app/readme.md)

### Working with Submodules
If you are just using docker.dev you the container already handles this so you dont have to worry about it.

The `sdk/` directory contains the glyph-sdk submodule tracking the `dev` branch.
(see .gitmodules)


#### Update submodule to latest dev branch:
```bash
git submodule update --remote --merge sdk
```

#### Update all submodules:
```bash
git submodule update --remote --merge
```

#### After pulling changes that update submodule references:
```bash
git submodule update --init --recursive
```

## Project Structure

- `app/` - Main application code
- `infra/` - AWS CDK infrastructure code
- `sdk/` - Glyph SDK submodule (tracks dev branch)
- `tests/` - Test suite
- `scripts/` - Deployment and utility scripts