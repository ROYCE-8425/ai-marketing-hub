.PHONY: up backend frontend install stop logs clean status push

up:
	@echo "🚀 Starting AI Marketing Hub..."
	@echo "   Backend:  http://localhost:8000"
	@echo "   Frontend: http://localhost:5173"
	@echo ""
	@$(MAKE) -j2 backend frontend

backend:
	@echo "⚡ Starting Backend..."
	@cd backend && . venv/bin/activate && python main.py

frontend:
	@echo "🎨 Starting Frontend..."
	@cd frontend && npm run dev

install:
	@echo "📦 Installing Backend..."
	@cd backend && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	@echo "📦 Installing Frontend..."
	@cd frontend && npm install
	@echo "✅ Done! Run 'make up' to start."

stop:
	@echo "🛑 Stopping..."
	@-pkill -f "uvicorn" 2>/dev/null || true
	@-pkill -f "python main.py" 2>/dev/null || true
	@-pkill -f "vite" 2>/dev/null || true
	@echo "✅ Stopped."

status:
	@echo "📊 Status:"
	@echo -n "   Backend:  " && (curl -s http://localhost:8000/health 2>/dev/null || echo "❌ Not running")
	@echo ""
	@echo -n "   Frontend: " && (curl -s http://localhost:5173/ > /dev/null 2>&1 && echo "✅ Running" || echo "❌ Not running")

logs:
	@cat backend/data/usage_history.json 2>/dev/null | python3 -m json.tool | tail -50 || echo "No logs."

clean:
	@-rm -rf frontend/node_modules/.cache backend/__pycache__ backend/core/__pycache__ backend/routers/__pycache__
	@echo "✅ Cleaned."

push:
	@git add -A && git commit -m "update: $$(date '+%Y-%m-%d %H:%M')" && git push origin main
