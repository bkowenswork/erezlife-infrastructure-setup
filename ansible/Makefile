all: venv

venv: bootstrap-requirements.txt requirements.txt
	python3 -m venv $@
	$@/bin/pip install -r $<
	$@/bin/pip-sync $^
	touch $@

.PHONY: credentials
credentials: venv
	venv/bin/python scripts/get-credentials -c scripts/s3_config.json -b erezlife-credentials

.PHONY: test-credentials
test-credentials: venv
	venv/bin/python scripts/get-credentials -c scripts/s3_config_test.json -b ext-development-credentials

.PHONY: update-packages
update-packages: venv
	venv/bin/pip-compile --upgrade --allow-unsafe --generate-hashes -o bootstrap-requirements.txt bootstrap-requirements.in
	venv/bin/pip-compile --upgrade --allow-unsafe --generate-hashes -o requirements.txt requirements.in

.PHONY: lint
lint: venv
	venv/bin/flake8
	venv/bin/isort --check-only --diff .

.PHONY: generate-passwords
generate-passwords: venv
	venv/bin/python scripts/generate-passwords -i hosts
