build:
	docker-compose -f docker/docker-compose.dev.yml build

serve:
	docker-compose -f docker/docker-compose.dev.yml up

database:
	docker-compose -f docker/docker-compose.dev.yml run -w /app app python -c 'from app import create_database'

clean:
	sudo rm -rf data/
	mkdir data
	make database

build_test:
	docker-compose -f docker/docker-compose.test.yml build

test: build_test
	docker-compose -f docker/docker-compose.test.yml up -V -d
	docker attach fastapi-test-test

build_prod:
	docker-compose -f docker/docker-compose.prod.yml build

serve_prod:
	docker-compose -f docker/docker-compose.prod.yml up
