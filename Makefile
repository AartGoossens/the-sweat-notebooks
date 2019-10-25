build:
	docker-compose -f docker/docker-compose.yml build

serve:
	docker-compose -f docker/docker-compose.yml up

create_database:
	docker-compose -f docker/docker-compose.yml run app python create_database.py

build_test:
	docker-compose -f docker/docker-compose.test.yml build

test: build_test
	docker-compose -f docker/docker-compose.test.yml up -V
