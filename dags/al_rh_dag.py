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
    dag_id="al_rh_sync",
    default_args=default_args,
    description="Pipeline de sincronizacao AL_RH -> Monday",
    start_date=pendulum.datetime(2026, 5, 1, 0, 0, tz=local_tz),

    # Dias 9-15 de cada mês às 06:20
    schedule="20 6 9-15 * *",

    catchup=False,
    tags=["producao", "painel_gerencial", "al_rh"],
) as dag:

    run_al_rh_pipeline = BashOperator(
        task_id="run_al_rh_pipeline",
        bash_command="""
          docker run --rm \
            --env-file /opt/automations/al_rh/.env \
            conterp-al-rh-app:latest
        """,
    )