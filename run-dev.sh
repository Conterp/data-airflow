#!/usr/bin/env bash
set -euo pipefail

# sempre começar na raiz do projeto (onde está este arquivo)
cd "$(dirname "$0")"

# entrar na pasta docker
cd docker

# subir o Airflow em modo dev
docker compose -f docker-compose.dev.yml up
