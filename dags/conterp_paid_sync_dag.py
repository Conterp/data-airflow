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
    dag_id="conterp_paid_sync",
    default_args=default_args,
    description=(
        "Pipeline de sincronizacao de Pagamentos Realizados "
        "Alterdata (Bimer) -> Monday"
    ),
    start_date=pendulum.datetime(2026, 7, 22, 0, 0, tz=local_tz),
    schedule="0 4,10,19 * * 1-6",
    catchup=False,
    max_active_runs=1,
    tags=[
        "producao",
        "financeiro",
        "pagamentos",
        "conterp_paid_sync",
    ],
) as dag:

    run_conterp_paid_sync_pipeline = BashOperator(
        task_id="run_conterp_paid_sync_pipeline",
        bash_command="""
          docker run --rm \
            --env-file /opt/automations/conterp-paid-sync/.env \
            conterp-paid-sync-app:latest
        """,
        execution_timeout=timedelta(minutes=30),
    )