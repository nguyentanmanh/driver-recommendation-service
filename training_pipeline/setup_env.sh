export TRAINING_PIPELINE_DIR=$(pwd)
export MLFLOW_TRACKING_URI="http://localhost:5000"

export RANDOM_SEED="17"
export TEST_SIZE="0.2"
export TARGET_COL="trip_completed"
 
export EXPERIMENT_NAME="elastic-net"
export ALPHA="0.5"
export L1_RATIO="0.1"
export MLFLOW_TRACKING_URI="http://localhost:5000"
 
export RMSE_THRESHOLD="0.2"
export MAE_THRESHOLD="0.2"
export REGISTERED_MODEL_NAME="sklearn-elastic-net-reg"
