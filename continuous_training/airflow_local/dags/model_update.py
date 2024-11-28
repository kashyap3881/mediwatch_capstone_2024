from airflow.models import DAG
from datetime import datetime, timedelta
from airflow.operators.python_operator import PythonOperator
from src.model_training.train import DiabetesReadmissionTrainer

TRAINING_DATA_PATH = "/home/ubuntu/mediwatch_capstone_2024/continuous_training/airflow_local/src/input_data/dataset_diabetes/diabetic_data.csv"

NEW_DATA_PATH = "/home/ubuntu/mediwatch_capstone_2024/continuous_training/airflow_local/src/new_data/new_data.csv"

MODEL_PATH = "/home/ubuntu/mediwatch_capstone_2024/continuous_training/airflow_local/src/models/best_model"

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
    dag_run = kwargs.get('dag_run')
    if dag_run and dag_run.conf:
        #original_data_filename = dag_run.conf.get('original_data_filename', cfg.TRAINING_DATA_PATH)
        original_data_filename = kwargs['dag_run'].conf['original_data_filename']
        #new_data_filename = dag_run.conf.get('new_data_filename', cfg.NEW_DATA_PATH)
        new_data_filename = kwargs['dag_run'].conf['new_data_filename']
        #model_dir = dag_run.conf.get('model_dir', cfg.MODEL_PATH)
        model_dir = kwargs['dag_run'].conf['model_dir']
    else:
        original_data_filename = TRAINING_DATA_PATH
        new_data_filename = NEW_DATA_PATH
        model_dir = MODEL_PATH
    # original_data_filename = kwargs['dag_run'].conf['original_data_filename']
    # new_data_filename = kwargs['dag_run'].conf['new_data_filename']
    # # bucket_name = kwargs['dag_run'].conf['bucket_name']
    # model_dir = kwargs['dag_run'].conf['model_dir']
    
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