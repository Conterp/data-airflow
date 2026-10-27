
from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator


local_tz = pendulum.timezone("America/Sao_Paulo")

default_args = {
    "owner": "conterp",
    "depends_on_past": False,
    "retries": 0,
}


with DAG(
    dag_id="purchase_orders_sync",
    default_args=default_args,
    description="Pipeline de sincronizacao de pedidos de compra Bimer -> Monday",
    start_date=pendulum.datetime(2026, 10, 27, 0, 0, tz=local_tz),
    schedule="30 7,15 * * 1-6",
    catchup=False,
    max_active_runs=1,
    tags=["producao", "bimer", "monday", "compras"],
) as dag:

    run_purchase_orders_sync_pipeline = BashOperator(
        task_id="run_purchase_orders_sync_pipeline",
        bash_command="""
docker run --rm \
  --env-file /opt/automations/purchase-orders-sync/.env \
  conterp-purchase-orders-sync-app:latest
""",
        execution_timeout=timedelta(hours=1),
    )
