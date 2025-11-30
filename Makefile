.PHONY: help install test deploy logs status restart

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install package locally
	pip install -e .

test:  ## Run tests
	pytest tests/ -v

deploy:  ## Deploy to thin client
	@./scripts/deploy.sh

logs:  ## Tail logs from thin client
	@./scripts/remote-logs.sh

status:  ## Check service status on thin client
	@./scripts/remote-status.sh

restart:  ## Restart service on thin client
	@./scripts/remote-restart.sh
