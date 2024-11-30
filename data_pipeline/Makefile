IMAGE_NAME="driver-recommendation/data_pipeline:0.0"

build_image:
	docker build --tag ${IMAGE_NAME} -f ./deployment/Dockerfile .

run_image:
	docker run --network redis_default --hostname feastapp -p 8000:8000 -t driver-recommendation/data_pipeline:0.0