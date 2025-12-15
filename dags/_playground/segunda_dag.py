from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

def mensagem():
    print("Segunda DAG rodando ✅")
    print("Ambiente de desenvolvimento Airflow testado com sucesso!")

default_args = {
    "owner": "devadmin",
}

with DAG(
    dag_id="segundo_teste",
    description="Outra DAG simples para testar múltiplas DAGs no ambiente",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["teste", "exemplo"],
    default_args=default_args,
) as dag:

    tarefa_mensagem = PythonOperator(
        task_id="exibir_mensagem",
        python_callable=mensagem,
    )
