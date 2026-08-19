.PHONY: setup download-data load-data benchmark report all

setup:
	pip install -r requirements.txt
	@echo "Setup complete. Please ensure you have copied .env.example to .env and filled in the credentials."

download-data:
	python -m src.data.download_dataset

load-data:
	python -m src.harness.loader

benchmark:
	python -m src.harness.runner

report:
	python -m src.report.generate_report

all: setup download-data load-data benchmark report
