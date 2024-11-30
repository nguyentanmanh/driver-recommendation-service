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

## 6. Run DAGs in airflow in UI