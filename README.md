# 🌬️ data-airflow

> Stack de **orquestração de pipelines em produção** usando **Apache Airflow**, executando em uma **EC2 na AWS** via **Docker Compose**, com metadata store em **RDS PostgreSQL** e suporte a **remote logging em S3**.

- **Ambiente de desenvolvimento**: GitHub Codespaces (`docker-compose.dev.yml`)
- **Ambiente de produção**: EC2 na AWS (`docker-compose.prod.yml`)

---

## 🚀 Visão geral

Este repositório mantém um Airflow “sempre ligado” para:

- Agendar e executar **DAGs de dados** (pipelines ETL/ELT, integrações, automações)
- Monitorar execuções via **Airflow UI**
- Persistir estado/execuções em um **PostgreSQL gerenciado (RDS)**
- Centralizar logs (opcional) em **S3** para auditoria e troubleshooting

---

## 🧠 Principais recursos

- 🐳 **Deploy em produção** com Docker Compose em EC2
- 🗄️ **Metadata store em RDS PostgreSQL**
- 🔐 **Configuração segura via ****.env** (segredos fora do Git)
- 🧾 **Inicialização automatizada** (migrações + criação de usuário admin)
- ☁️ **Remote Logging em S3** (opcional, recomendado)
- 🧩 Estrutura simples para evoluir DAGs em `dags/`

---

## 🏗️ Arquitetura

- **EC2**: executa `airflow-webserver` e `airflow-scheduler`
- **RDS PostgreSQL**: metadados do Airflow (`AIRFLOW__DATABASE__SQL_ALCHEMY_CONN`)
- **S3 (opcional)**: armazenamento de logs remotos (`AIRFLOW__LOGGING__REMOTE_*`)
- **IAM Role na EC2 (recomendado)**: acesso ao S3

```
┌────────────────┐        ┌─────────────────────────┐
│ Navegador      │ -----> │ Airflow Webserver :8080 │
└────────────────┘        └────────────┬────────────┘
                                       │
                                       v
                             ┌───────────────────────┐
                             │ Airflow Scheduler     │
                             └──────────┬────────────┘
                                        │
                                        v
                          ┌───────────────────────────┐
                          │ RDS PostgreSQL (metadata) │
                          └───────────────────────────┘

(Logs)  Airflow -> S3 (remote logging)
```

---

## 🧩 Estrutura do projeto

```text
data-airflow/
├── .env.example
├── .gitignore
├── dags/                       # DAGs do Airflow
├── logs/                       # logs locais (dev/fallback)
├── plugins/                    # plugins (se houver)
└── docker/
    └── docker-compose.prod.yml # stack de produção
```

---

## ⚙️ Configuração

### 1) Variáveis de ambiente

Copie o arquivo de exemplo e preencha os valores:

```bash
cp .env.example .env
```

#### Obrigatórios

- `AIRFLOW__CORE__FERNET_KEY`
- `AIRFLOW__WEBSERVER__SECRET_KEY`
- `AIRFLOW__DATABASE__SQL_ALCHEMY_CONN`
- `AIRFLOW_ADMIN_PASSWORD`
- `AIRFLOW_ADMIN_EMAIL`

Exemplo de conexão (RDS PostgreSQL):

```text
postgresql+psycopg2://usuario:senha@endpoint-rds:5432/airflow
```

Gerar Fernet Key:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

> ✅ O `.env` está no `.gitignore` e não deve ser versionado.

---

## 🚢 Deploy em produção (AWS EC2)

### Pré-requisitos

- EC2 Linux com Docker + Docker Compose
- RDS PostgreSQL acessível pela EC2 (porta 5432 liberada no Security Group)
- (Opcional) Bucket S3 para logs remotos
- (Recomendado) IAM Role anexada à EC2 com permissão no bucket de logs

### 1) Clonar o repositório

```bash
git clone <URL_DO_REPO>
cd data-airflow
```

### 2) Criar `.env`

```bash
cp .env.example .env
nano .env
```

### 3) Subir webserver e scheduler

```bash
cd docker

docker compose -f docker-compose.prod.yml up -d airflow-webserver airflow-scheduler
```

### 4) Inicializar Airflow (migrações + usuário admin)

```bash
docker compose -f docker-compose.prod.yml run --rm airflow-init
```

### 5) Acessar a UI

- URL: `http://<IP_PUBLICO_DA_EC2>:8080`
- Usuário: `AIRFLOW_ADMIN_USERNAME` (default: `admin`)
- Senha: `AIRFLOW_ADMIN_PASSWORD`

---

## ☁️ Remote logging no S3

O `docker-compose.prod.yml` já está preparado para logs remotos:

- `AIRFLOW__LOGGING__REMOTE_LOGGING=True`
- `AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER=s3://...`
- `AIRFLOW__LOGGING__REMOTE_LOG_CONN_ID=<id_da_conexao>`

Durante o `airflow-init`, a stack tenta **criar/garantir** a conexão AWS do Airflow:

- `airflow connections add "${AIRFLOW__LOGGING__REMOTE_LOG_CONN_ID}" --conn-uri "aws://@/?region_name=${AWS_REGION}"`

### Recomendação

- Em produção, use **IAM Role** na EC2.
- Garanta permissão no bucket (ListBucket/GetObject/PutObject) para o prefixo configurado.

---

## 🧭 Operação e manutenção

### Ver logs dos serviços

```bash
cd docker

docker compose -f docker-compose.prod.yml logs -f airflow-webserver
# ou

docker compose -f docker-compose.prod.yml logs -f airflow-scheduler
```

### Reiniciar serviços

```bash
cd docker

docker compose -f docker-compose.prod.yml restart airflow-webserver airflow-scheduler
```

### Atualizar a imagem do Airflow

1. Ajuste a tag da imagem em `docker-compose.prod.yml` (ex.: `apache/airflow:2.9.3`)
2. Atualize:

```bash
cd docker

docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

---

## 🧠 Como adicionar novas DAGs

1. Adicione/edite arquivos em `dags/`
2. Commit + push
3. Na EC2, atualize o repo e reinicie o scheduler (se necessário):

```bash
git pull
cd docker

docker compose -f docker-compose.prod.yml restart airflow-scheduler
```

---

## 🔒 Segurança

- Não versionar `.env` e segredos (já protegido no `.gitignore`).
- `FERNET_KEY` e `SECRET_KEY` devem ser únicos por ambiente.
- Restrinja o acesso à porta **8080** (Security Group / VPN / proxy).
- Prefira IAM Role em vez de chaves AWS.

---

## 🧯 Troubleshooting

- **UI não abre**: verifique Security Group, porta 8080 e logs do `airflow-webserver`.
- **Scheduler não executa DAGs**: verifique logs do `airflow-scheduler` e conectividade com RDS.
- **Permissão em volumes (Linux)**: configure `AIRFLOW_UID` ou mantenha `user: "${AIRFLOW_UID:-50000}:0"` no compose.

---

## 🤝 Autor

**João Carser**
