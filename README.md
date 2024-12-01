# driver-recommendation-service

## 1. Setup environment variable

bash setup_env.sh

## 2. Run infra setup

cd infra && bash run.sh all up && cd ..

## 3. Init feature store Feast

cd data_pipeline && pip install -r deployment/requirements.txt && feast init && cd ..

cd data_pipeline/feature_repo && feast apply && cd ../..

## 4. Deploy feasture store service

cd data_pipeline && make build_image && make run_image

## 5. Deploy DAGs for data pipeline

## 6. Run DAGs: db_to_offline_store, materalize_offline_to_online, stream_to_store

## 7. Build image for training pipeline

bash training_pipeline/setup_env.sh && cd training_pipeline && make build_image && cd ..

## 8. Copy DAGs in training_pipeline to airflow

## 9. Run DAGs in airflow: training_pipeline

## 10. Build image for batch serving 

## 11. Copy DAGs in batch_serving to airflow

## 12. Run DAGs: batch_serving_pipeline