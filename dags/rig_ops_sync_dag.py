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
    dag_id="rig_ops_sync",
    default_args=default_args,
    description="Pipeline de sincronização Rig -> Monday",
    start_date=pendulum.datetime(2026, 2, 28, 0, 0, tz=local_tz),
    schedule="0 3,15 * * *",
    catchup=False,
    tags=["producao", "rig", "monday"],
) as dag:

    run_rig_pipeline = BashOperator(
        task_id="run_rig_pipeline",
        bash_command="""
        docker run --rm \
          --env-file /opt/automations/conterp-rig-ops-sync/.env \
          conterp-rig-ops-sync-app
        """,
    )