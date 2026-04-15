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
    dag_id="al_payments_sync",
    default_args=default_args,
    description="Pipeline de sincronizacao AL_PAYMENTS -> Monday",
    start_date=pendulum.datetime(2026, 4, 15, 0, 0, tz=local_tz),
    schedule="10 9,21 * * 1-6",  # seg-sab: 09:10 e 21:10
    catchup=False,
    tags=["producao", "painel_gerencial", "al_payments"],
) as dag:


    run_al_payments_pipeline = BashOperator(
        task_id="run_al_payments_pipeline",
        bash_command="""
          docker run --rm \
            --env-file /opt/automations/al_payments/.env \
            conterp-al-payments-app:latest
        """,
    )
