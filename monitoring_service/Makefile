IMAGE_NAME = ${MONITORING_SERVICE_IMG}

build_image:
	docker build --tag ${IMAGE_NAME} -f ./deployment/Dockerfile .

run_image:
	docker compose  --env-file ./deployment/.env -f ./deployment/docker-compose.yml up -d

down_image:
	docker-compose --env-file ./deployment/.env -f ./deployment/docker-compose.yml down