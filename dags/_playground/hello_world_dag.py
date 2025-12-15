from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

def hello():
    print("Hello from Airflow! Minha primeira DAG está rodando 🚀")
    print("Este é um teste para validar o ambiente.")
    print("Automação da Conterp")

default_args = {
    "owner": "devadmin",
}

with DAG(
    dag_id="hello_world",
    description="DAG de teste para validar o ambiente",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["exemplo"],
    default_args=default_args,
) as dag:

    tarefa_hello = PythonOperator(
        task_id="say_hello",
        python_callable=hello,
    )
