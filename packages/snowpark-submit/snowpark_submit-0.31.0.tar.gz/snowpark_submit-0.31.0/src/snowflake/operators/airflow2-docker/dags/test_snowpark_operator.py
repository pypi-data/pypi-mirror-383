
from datetime import datetime, timedelta
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.hooks.base import BaseHook
from snowflake.operators.snowpark_submit import SnowparkSubmitOperator, SnowparkSubmitStatusOperator
import os

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'snowpark_submit_example',
    default_args=default_args,
    description='Example DAG using SnowparkSubmitOperator',
    schedule_interval=None,
    catchup=False,
) as dag:
    
    snowflake_conn = BaseHook.get_connection('snowflake_default')
    
    snowflake_config = {
        'account': snowflake_conn.extra_dejson.get('account'),
        'host': snowflake_conn.host,
        'user': snowflake_conn.login,
        'password': snowflake_conn.password,
        'role': snowflake_conn.extra_dejson.get('role'),
        'warehouse': snowflake_conn.extra_dejson.get('warehouse'),
        'schema': snowflake_conn.schema,
        'database': snowflake_conn.extra_dejson.get('database'),
        'compute_pool': snowflake_conn.extra_dejson.get('compute_pool'),
    }
    
    submit_spark_job = SnowparkSubmitOperator(
        task_id='submit_spark_job',
        file=os.path.dirname(os.path.abspath(__file__)) + '/simple-main.py',
        connections_config=snowflake_config,
        comment='My Spark job submitted via Airflow',
    )
    
    # Check the job status
    check_job_status = SnowparkSubmitStatusOperator(
        task_id='check_job_status',
        snowflake_workload_name="{{ ti.xcom_pull(task_ids='submit_spark_job', key='service_name') }}",
        connections_config=snowflake_config,
        display_logs=True,
        wait_for_completion=True,
        fail_on_error=True,
    )
    
    # Set up task dependencies
    submit_spark_job >> check_job_status
