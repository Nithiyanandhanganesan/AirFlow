import os
from datetime import datetime, timedelta
from airflow import models
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': [''],
    'email_on_failure': True,
    'email_on_success': True,
    'email_on_retry': True,
    'retries': 10,
    'retry_delay': timedelta(minutes=10),
    'sla': timedelta(hours=10)
}

with models.DAG(
        'test_branching',
        default_args=default_args,
        description='test_branching',
        start_date=datetime(2021, 12, 17),
        schedule_interval=None,
        catchup=False,
        tags=['test_branching','OnDemand'],
        params={"destType": "False"}
) as dag:


    step1 = BashOperator(
        task_id="step1",
        bash_command='/home/airflow/dags/scripts/test.sh ',
        sla=timedelta(hours=1)
    )

    step2 = BashOperator(
        task_id='step2',
        trigger_rule="one_success",
        bash_command='/home/airflow/dags/scripts/test.sh '
    )

    def dummy_test(**kwargs):
        print(kwargs['skipFlag'])
        skipFlag = kwargs['skipFlag']
        print(skipFlag)
        if skipFlag == "true":
          return 'step3'
        else:
          return 'step4'

    branch_task = BranchPythonOperator(
        task_id='branch_task',
        python_callable=dummy_test,
        op_kwargs={'skipFlag': '{{ params.destType }}'},
        dag=dag
    )

    join = DummyOperator(
        task_id='join',
        trigger_rule='one_success',
        dag=dag
    )

    step3 = BashOperator(
        task_id='step3',
        trigger_rule="one_success",
        bash_command='/home/airflow/dags/scripts/test.sh '
    )

    step4 = BashOperator(
        task_id='step4',
        trigger_rule="one_success",
        bash_command='/home/airflow/dags/scripts/test.sh '
    )

    step5 = BashOperator(
        task_id='step5',
        trigger_rule="one_success",
        bash_command='/home/airflow/dags/scripts/test.sh '
    )


    step1.set_downstream(step2)
    step2.set_downstream(branch_task)
    branch_task.set_downstream(step3)
    branch_task.set_downstream(step4)
    step3.set_downstream(join)
    step4.set_downstream(join)
    join.set_downstream(step5)
