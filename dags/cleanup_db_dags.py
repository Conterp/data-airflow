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

LOG_BASE_PATH = "/opt/automations/data-airflow/logs"

with DAG(
    dag_id="airflow_db_cleanup",
    default_args=default_args,
    description="Limpeza Semanal Metadados RDS e EC2",
    start_date=pendulum.datetime(2026, 4, 1, tz=local_tz),
    schedule="0 4 * * 0",  # domingo às 04:00
    catchup=False,
    tags=["producao", "airflow", "db", "cleanup"],
) as dag:

    cleanup_metadata = BashOperator(
        task_id="cleanup_metadata",
        bash_command="""
        set -euo pipefail

        step_start=$(date +%s)

        echo "======================"
        echo "ETAPA 1 - METADADOS RDS"
        echo "======================"
        echo "CKPT START step=rds_metadata_cleanup"

        echo "delete rows" | airflow db clean \
          --clean-before-timestamp "$(date -d '30 days ago' '+%Y-%m-%d %H:%M:%S')" \
          --skip-archive

        step_end=$(date +%s)
        step_dur=$((step_end - step_start))

        echo "CKPT END step=rds_metadata_cleanup planned=1 success=1 error=0 dur_s=${step_dur}"
        """,
    )

    cleanup_local_logs = BashOperator(
        task_id="cleanup_local_logs",
        bash_command=f"""
        set -euo pipefail

        step_start=$(date +%s)

        echo "======================"
        echo "ETAPA 2 - LOGS EC2"
        echo "======================"

        size_before=$(du -sh "{LOG_BASE_PATH}" 2>/dev/null | awk '{{print $1}}')
        old_logs=$(find "{LOG_BASE_PATH}" -type f -mtime +30 | wc -l | tr -d ' ')

        echo "CKPT START step=ec2_old_logs_cleanup size_before=${{size_before:-0}}"

        find "{LOG_BASE_PATH}" -type f -mtime +30 -delete

        size_after=$(du -sh "{LOG_BASE_PATH}" 2>/dev/null | awk '{{print $1}}')

        step_end=$(date +%s)
        step_dur=$((step_end - step_start))

        echo "CKPT END step=ec2_old_logs_cleanup planned=${{old_logs}} success=${{old_logs}} error=0 size_after=${{size_after:-0}} dur_s=${{step_dur}}"
        """,
    )

    cleanup_empty_dirs = BashOperator(
        task_id="cleanup_empty_dirs",
        bash_command=f"""
        set -euo pipefail

        step_start=$(date +%s)

        echo "======================"
        echo "ETAPA 3 - EMPTY DIRS"
        echo "======================"

        empty_dirs=$(find "{LOG_BASE_PATH}" -type d -empty | wc -l | tr -d ' ')

        echo "CKPT START step=empty_dirs_cleanup"

        find "{LOG_BASE_PATH}" -type d -empty -delete

        step_end=$(date +%s)
        step_dur=$((step_end - step_start))

        echo "CKPT END step=empty_dirs_cleanup planned=${{empty_dirs}} success=${{empty_dirs}} error=0 dur_s=${{step_dur}}"
        """,
    )

    cleanup_metadata >> cleanup_local_logs >> cleanup_empty_dirs