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
    dag_id="al_afs_geradas_sync",
    default_args=default_args,
    description="Pipeline de sincronizacao AL_AFS_GERADAS -> Monday",
    start_date=pendulum.datetime(2026, 4, 7, 0, 0, tz=local_tz),
    schedule="30 9,11,14,16,17 * * 1-6",  # seg-sab: 09:30,11:30,14:30,16:30,17:30
    catchup=False,
    tags=["producao", "monday", "al_afs_geradas"],
) as dag:

    run_al_afs_geradas_pipeline = BashOperator(
        task_id="run_al_afs_geradas_pipeline",
        bash_command="""
        docker run --rm \
          --env-file /opt/automations/al_afs_geradas/.env \
          al_afs_geradas-app
        """,
    )
