from airflow.models import DAG
from datetime import datetime, timedelta
from airflow.operators.python_operator import PythonOperator
from src.model_training.train import DiabetesReadmissionTrainer

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 11, 4),
    'email': ['kashyap3881@gmail.com', 'aaron-nicholson-ai@gmail.com'],
    'email_on_failure': False,
    'max_active_runs': 1,
    'email_on_retry': False,
    'retry_delay': timedelta(minutes=5)
}

dg = DAG('patient-readmission-model-retraining',
          schedule_interval=None,
          default_args=default_args,
          catchup=False
          )

def run_trainer(**kwargs):
    original_data_filename = kwargs['dag_run'].conf['original_data_filename']
    new_data_filename = kwargs['dag_run'].conf['new_data_filename']
    # bucket_name = kwargs['dag_run'].conf['bucket_name']
    model_dir = kwargs['dag_run'].conf['model_dir']
    
    trainer = DiabetesReadmissionTrainer(
        original_data_filename=original_data_filename,
        new_data_filename=new_data_filename,
        model_dir=model_dir
    )
    
    result = trainer.train_and_evaluate_model()
    return result

retrain_model = PythonOperator(
    task_id='retrain_model',
    python_callable=run_trainer,
    provide_context=True,
    dag=dg
)

retrain_model