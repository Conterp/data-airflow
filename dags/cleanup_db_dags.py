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
    dag_id="airflow_db_cleanup",
    default_args=default_args,
    description="Limpeza semanal de metadados do Airflow (30 dias)",
    start_date=pendulum.datetime(2026, 4, 1, tz=local_tz),
    schedule="0 4 * * 0",  # domingo às 04:00
    catchup=False,
    tags=["producao", "airflow", "db", "cleanup"],
) as dag:

    cleanup_metadata = BashOperator(
        task_id="cleanup_metadata",
        bash_command="""
        echo "delete rows" | airflow db clean \
        --clean-before-timestamp "$(date -d '30 days ago' '+%Y-%m-%d %H:%M:%S')" \
        --skip-archive \
        --verbose
        """,
    )

    cleanup_archived = BashOperator(
        task_id="drop_archived_tables",
        bash_command="""
        airflow db drop-archived
        """,
    )

    cleanup_metadata >> cleanup_archived