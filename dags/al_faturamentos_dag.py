from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator

local_tz = pendulum.timezone("America/Sao_Paulo")

default_args = {
    "owner": "conterp",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

with DAG(
    dag_id="al_faturamentos_sync",
    default_args=default_args,
    description="Pipeline de sincronizacao AL_FATURAMENTOS -> Monday",
    start_date=pendulum.datetime(2026, 4, 24, 0, 0, tz=local_tz),
    
    # Seg-Sex: 10:40, 13:20, 17:00
    schedule="40 10,13,17 * * 1-5",
    
    catchup=False,
    tags=["producao", "painel_gerencial", "al_faturamentos"],
) as dag:

    run_al_faturamentos_pipeline = BashOperator(
        task_id="run_al_faturamentos_pipeline",
        bash_command="""
          docker run --rm \
            --env-file /opt/automations/al_faturamentos/.env \
            conterp-al-faturamentos-app:latest
        """,
    )