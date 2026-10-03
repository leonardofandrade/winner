.DEFAULT_GOAL := help

.PHONY: help dev-up dev-bot dev-down dev-ps dev-logs prod-up prod-down prod-ps prod-logs

help:
	@echo "Dev (http://localhost:8081, MySQL em localhost:3307)"
	@echo "  make dev-up      sobe API e MySQL, com reload do código"
	@echo "  make dev-bot     sobe o dev e o Telegram bot"
	@echo "  make dev-down    para o dev e mantém o banco"
	@echo "  make dev-ps      mostra os containers de dev"
	@echo "  make dev-logs    acompanha os logs (SERVICE=api para um serviço)"
	@echo ""
	@echo "Prod local (http://localhost)"
	@echo "  make prod-up     sobe MySQL, API e nginx; o bot entra se houver token"
	@echo "  make prod-down   para a prod local e mantém os volumes"
	@echo "  make prod-ps     mostra os containers de prod"
	@echo "  make prod-logs   acompanha os logs (SERVICE=api para um serviço)"

dev-up:
	./deploy/dev.sh up

dev-bot:
	./deploy/dev.sh up --with-bot

dev-down:
	./deploy/dev.sh down

dev-ps:
	./deploy/dev.sh ps

dev-logs:
	./deploy/dev.sh logs $(SERVICE)

prod-up:
	./deploy/prod.sh up

prod-down:
	./deploy/prod.sh down

prod-ps:
	./deploy/prod.sh ps

prod-logs:
	./deploy/prod.sh logs $(SERVICE)
