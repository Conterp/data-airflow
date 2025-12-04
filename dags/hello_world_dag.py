from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator


def hello():
    # Aqui entra a lógica que você quer rodar.
    # Por enquanto, só vamos escrever no log:
    print("Hello from Airflow! Minha primeira DAG está rodando 🚀")


with DAG(
    dag_id="hello_world",
    description="DAG de teste para validar o ambiente",
    start_date=datetime(2024, 1, 1),
    schedule=None,  # sem agendamento automático (vamos rodar na mão em dev)
    catchup=False,
    tags=["exemplo"],
) as dag:

    tarefa_hello = PythonOperator(
        task_id="say_hello",
        python_callable=hello,
    )
