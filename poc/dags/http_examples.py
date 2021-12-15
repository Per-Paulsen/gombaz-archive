"""Minimal SimpleHttpOperator examples.

These run against the local httpbin sidecar (set up an Airflow connection
named `httpbin_local` pointing at http://httpbin:80) so you can poke the
DAG without burning real API credits.
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.operators.python_operator import PythonOperator


default_args = {
    "owner": "gombaz",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "http_examples",
    default_args=default_args,
    start_date=datetime(2021, 1, 1),
    schedule_interval=None,
    tags=["example"],
) as dag:

    fetch = SimpleHttpOperator(
        task_id="fetch_get",
        method="GET",
        http_conn_id="httpbin_local",
        endpoint="/get",
        headers={},
        xcom_push=True,
    )

    def echo_payload(**context):
        payload = context["ti"].xcom_pull(task_ids="fetch_get")
        print(payload)

    show = PythonOperator(
        task_id="echo_payload",
        python_callable=echo_payload,
        provide_context=True,
    )

    fetch >> show
