"""Stripe customer-portal session + Mandrill notification.

Creates a single-use URL into the Stripe billing portal for a known customer
and sends them a transactional Mandrill mail with the link.
"""

import os
from datetime import datetime

import requests
from airflow import DAG
from airflow.operators.python_operator import PythonOperator


STRIPE_AUTH = (os.environ["STRIPE_API_KEY"], "")
STRIPE_CUSTOMER_ID = os.environ["STRIPE_CUSTOMER_ID"]
STRIPE_PORTAL_CONFIG_ID = os.environ["STRIPE_PORTAL_CONFIG_ID"]
STRIPE_PORTAL_RETURN_URL = os.environ["STRIPE_PORTAL_RETURN_URL"]

MANDRILL_API_KEY = os.environ["MANDRILL_API_KEY"]
MANDRILL_FROM_EMAIL = os.environ["MANDRILL_FROM_EMAIL"]
MANDRILL_TO_EMAIL = os.environ["MANDRILL_TO_EMAIL"]


with DAG(
    "stripe_portal_session_mandrill",
    start_date=datetime(2021, 1, 1),
    schedule_interval=None,
) as dag:

    def create_portal_session(**context):
        res = requests.post(
            "https://api.stripe.com/v1/billing_portal/sessions",
            data={
                "customer": STRIPE_CUSTOMER_ID,
                "return_url": STRIPE_PORTAL_RETURN_URL,
                "configuration": STRIPE_PORTAL_CONFIG_ID,
            },
            auth=STRIPE_AUTH,
        )
        context["ti"].xcom_push(key="session_url", value=res.json()["url"])

    def send_mandrill_mail(**context):
        session_url = context["ti"].xcom_pull(key="session_url")
        payload = {
            "key": MANDRILL_API_KEY,
            "message": {
                "from_email": MANDRILL_FROM_EMAIL,
                "subject": "Manage your subscription",
                "text": f"You can change your subscription at any time: {session_url}",
                "to": [{"email": MANDRILL_TO_EMAIL, "type": "to"}],
            },
        }
        requests.post("https://mandrillapp.com/api/1.0/messages/send", json=payload)

    t_session = PythonOperator(task_id="create_portal_session", python_callable=create_portal_session, provide_context=True)
    t_mail = PythonOperator(task_id="send_mandrill_mail", python_callable=send_mandrill_mail, provide_context=True)

    t_session >> t_mail
