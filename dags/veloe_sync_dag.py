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
    dag_id="veloe_sync",
    default_args=default_args,
    description="Pipeline de sincronizacao Veloe -> Monday",
    start_date=pendulum.datetime(2026, 6, 19, 0, 0, tz=local_tz),
    schedule="0 5,9,16 * * *",
    catchup=False,
    tags=["producao", "veloe", "gestao_frotas"],
) as dag:

    run_veloe_sync_pipeline = BashOperator(
        task_id="run_veloe_sync_pipeline",
        bash_command="""
docker run --rm \
  --env-file /opt/automations/veloe_sync/.env \
  conterp-veloe-sync-app:latest
""",
    )