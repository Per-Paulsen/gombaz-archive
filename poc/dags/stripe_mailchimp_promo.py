"""Promotion workflow: Stripe coupon -> promotion code -> Mailchimp campaign.

Demonstrates a four-step DAG with data dependencies between Stripe and
Mailchimp, passed through Airflow XComs.

Steps:
  1. Create a percentage-off coupon in Stripe.
  2. Wrap the coupon in a human-readable promotion code.
  3. Create an empty Mailchimp campaign targeting a list.
  4. Inject the promotion code into the campaign content.
  5. Send the campaign.
"""

import os
from datetime import datetime

import requests
from airflow import DAG
from airflow.operators.python_operator import PythonOperator


STRIPE_KEY = os.environ["STRIPE_API_KEY"]
MAILCHIMP_KEY = os.environ["MAILCHIMP_API_KEY"]
MAILCHIMP_DC = os.environ["MAILCHIMP_DC"]
MAILCHIMP_LIST_ID = os.environ["MAILCHIMP_LIST_ID"]
MAILCHIMP_FROM_NAME = os.environ["MAILCHIMP_FROM_NAME"]
MAILCHIMP_REPLY_TO = os.environ["MAILCHIMP_REPLY_TO"]

STRIPE_AUTH = (STRIPE_KEY, "")
MAILCHIMP_AUTH = ("anything", MAILCHIMP_KEY)
MAILCHIMP_BASE = f"https://{MAILCHIMP_DC}.api.mailchimp.com/3.0"


with DAG(
    "stripe_mailchimp_promo",
    start_date=datetime(2021, 1, 1),
    schedule_interval=None,
) as dag:

    def create_coupon(**context):
        res = requests.post(
            "https://api.stripe.com/v1/coupons",
            params={"percent_off": 5, "name": "Summer Promo"},
            auth=STRIPE_AUTH,
        )
        context["ti"].xcom_push(key="coupon_id", value=res.json()["id"])

    def create_promotion_code(**context):
        coupon_id = context["ti"].xcom_pull(key="coupon_id")
        res = requests.post(
            "https://api.stripe.com/v1/promotion_codes",
            params={"coupon": coupon_id, "code": "SUMMER1"},
            auth=STRIPE_AUTH,
        )
        context["ti"].xcom_push(key="promo_code", value=res.json()["code"])

    def create_campaign(**context):
        payload = {
            "type": "plaintext",
            "recipients": {"list_id": MAILCHIMP_LIST_ID},
            "settings": {
                "subject_line": "Summer Promo",
                "title": "Summer Promo",
                "from_name": MAILCHIMP_FROM_NAME,
                "reply_to": MAILCHIMP_REPLY_TO,
            },
        }
        res = requests.post(f"{MAILCHIMP_BASE}/campaigns", json=payload, auth=MAILCHIMP_AUTH)
        context["ti"].xcom_push(key="campaign_id", value=res.json()["id"])

    def set_campaign_content(**context):
        campaign_id = context["ti"].xcom_pull(key="campaign_id")
        promo_code = context["ti"].xcom_pull(key="promo_code")
        requests.put(
            f"{MAILCHIMP_BASE}/campaigns/{campaign_id}/content",
            json={"plain_text": f"Promotion Code: {promo_code}"},
            auth=MAILCHIMP_AUTH,
        )

    def send_campaign(**context):
        campaign_id = context["ti"].xcom_pull(key="campaign_id")
        requests.post(
            f"{MAILCHIMP_BASE}/campaigns/{campaign_id}/actions/send",
            auth=MAILCHIMP_AUTH,
        )

    t_coupon = PythonOperator(task_id="create_coupon", python_callable=create_coupon, provide_context=True)
    t_promo = PythonOperator(task_id="create_promotion_code", python_callable=create_promotion_code, provide_context=True)
    t_campaign = PythonOperator(task_id="create_campaign", python_callable=create_campaign, provide_context=True)
    t_content = PythonOperator(task_id="set_campaign_content", python_callable=set_campaign_content, provide_context=True)
    t_send = PythonOperator(task_id="send_campaign", python_callable=send_campaign, provide_context=True)

    t_coupon >> t_promo >> t_content
    t_campaign >> t_content >> t_send
