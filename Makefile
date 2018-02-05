all: requirements start

pyclean:
	find . -name *.pyc -delete

clean: pyclean
	rm -rf venv

venv: clean
	virtualenv -p python3 venv

params:
	test -f src/main/params.py || cp src/main/params-sample.py src/main/params.py

migrate: params
	./src/manage.py migrate

start: runserver run

run: migrate
	./src/manage.py run

runserver:
	./src/manage.py runserver 0.0.0.0:8000 &

requirements:
	pip install -r requirements.txt

grafana:
	docker run -d -p 3000:3000 -e "GF_SECURITY_ADMIN_PASSWORD=secret" grafana/grafana:4.6.2

influx:
	influxd -config /usr/local/etc/influxdb.conf

dev: clean venv requirements grafana influx

build-amr:
	docker-compose build --force-rm --no-cache --file docker-compose-amr.yml

build:
	docker-compose build --force-rm --no-cache

up:
	docker-compose up
