build:
	docker-compose -f docker/docker-compose.yml build

serve:
	docker-compose -f docker/docker-compose.yml up

build_test:
	docker-compose -f docker/docker-compose.test.yml build

test: build_test
	docker-compose -f docker/docker-compose.test.yml up
