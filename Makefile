.PHONY: help install install-backend install-frontend backend frontend dev clean

# Colors
GREEN  := \033[0;32m
YELLOW := \033[0;33m
CYAN   := \033[0;36m
RESET  := \033[0m

help: ## Show this help
	@echo ""
	@echo "$(CYAN)Kanban Agent - Available Commands$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(RESET) %s\n", $$1, $$2}'
	@echo ""

# =============================================================================
# Installation
# =============================================================================

install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install backend Python dependencies
	@echo "$(YELLOW)Installing backend dependencies...$(RESET)"
	cd backend && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	@echo "$(GREEN)Backend dependencies installed!$(RESET)"

install-frontend: ## Install frontend dependencies
	@echo "$(YELLOW)Installing frontend dependencies...$(RESET)"
	cd frontend && npm install
	@echo "$(GREEN)Frontend dependencies installed!$(RESET)"

# =============================================================================
# Development
# =============================================================================

backend: ## Run backend server (port 3001)
	@echo "$(CYAN)Starting backend server...$(RESET)"
	cd backend && . venv/bin/activate && python -m src.main

frontend: ## Run frontend dev server (port 5173)
	@echo "$(CYAN)Starting frontend dev server...$(RESET)"
	cd frontend && npm run dev

dev: ## Run both backend and frontend (requires tmux or run in separate terminals)
	@echo "$(YELLOW)Starting development servers...$(RESET)"
	@echo "$(CYAN)Use 'make backend' and 'make frontend' in separate terminals$(RESET)"
	@echo "$(CYAN)Or use: make dev-parallel$(RESET)"

dev-parallel: ## Run both servers in parallel (background)
	@echo "$(YELLOW)Starting servers in parallel...$(RESET)"
	@trap 'kill 0' EXIT; \
	(cd backend && . venv/bin/activate && python -m src.main) & \
	(cd frontend && npm run dev) & \
	wait

# =============================================================================
# Build
# =============================================================================

build-frontend: ## Build frontend for production
	@echo "$(YELLOW)Building frontend...$(RESET)"
	cd frontend && npm run build
	@echo "$(GREEN)Frontend built!$(RESET)"

# =============================================================================
# Utilities
# =============================================================================

clean: ## Clean all dependencies and build artifacts
	@echo "$(YELLOW)Cleaning...$(RESET)"
	rm -rf backend/venv
	rm -rf backend/__pycache__
	rm -rf backend/src/__pycache__
	rm -rf frontend/node_modules
	rm -rf frontend/dist
	@echo "$(GREEN)Cleaned!$(RESET)"

check-backend: ## Check if backend is running
	@curl -s http://localhost:3001/health && echo "" || echo "$(YELLOW)Backend not running$(RESET)"

check-frontend: ## Check if frontend is running
	@curl -s http://localhost:5173 > /dev/null && echo "$(GREEN)Frontend is running$(RESET)" || echo "$(YELLOW)Frontend not running$(RESET)"
