# Project Overview
Mobile access to Claude Code CLI via local WiFi. FastAPI streams terminal I/O over WebSocket.

**Core concept**: Access Mac's Claude Code from phone - zero cloud, zero auth, zero cost.

# Code Quality Standards
- **Enterprise-grade**: Production-ready, scalable architecture from day one
- **Right first time**: Test-driven development with comprehensive validation before commit
- **Zero external dependencies**: Build custom solutions over paid services (avoid vendor lock-in)
- **Technical debt**: Prevent, don't accumulate - refactor proactively, never "later"
- **Type safety**: TypeScript/Python type hints everywhere - catch errors at compile time
- **Documentation**: Code is self-documenting, comments explain "why" not "what"

# Core Implementation Rules
- **Never** modify legacy/ directory (backward compatibility sacred)
- **Always** use async/await for all I/O operations (never block event loop)
- **Always** bind to LAN interface only, never 0.0.0.0 (security by default)
- **Always** handle WebSocket reconnection with exponential backoff (max 30s)
- **Always** validate input at API boundary (trust nothing from client)
- **Never** use external databases - SQLite only when persistence needed
- **Never** gate core features behind payment (monetize convenience, not capability)
- **Never** log sensitive data (tokens, passwords, session IDs)

# Architecture
claude-on-the-go/
├── legacy/          # DO NOT MODIFY
├── core/            # pty_manager.py, session_store.py, discovery.py
├── server/          # websocket.py, api.py, static/
├── client/pwa/      # Progressive Web App
└── integrations/    # notifications.py, tailscale.py, qr_generator.py

# Code Style
- FastAPI with async/await throughout
- WebSocket for terminal streaming (low latency)
- SQLite with async wrapper (no PostgreSQL/MySQL)
- Type hints required on all function signatures
- Explicit try/except, never bare except
- snake_case (Python), camelCase (JavaScript), 100 char max
- **See VIEWS.md for all UI/UX, CSS, and mobile-first design**

# Key Components
core/pty_manager.py: spawn_claude(), read_output(), write_input(), resize_terminal()
server/websocket.py: stream_output(), handle_reconnect()
core/session_store.py: save_chunk(), get_session()

# API Endpoints
POST   /api/session/start              # {"command": "claude", "cols": 80, "rows": 24}
GET    /api/session/{id}               # Session history with chunks
DELETE /api/session/{id}               # Kill session gracefully
WS     /ws/{session_id}?token={token}  # Terminal stream (authenticated)
GET    /api/qr                         # Connection QR code (PNG)
GET    /api/status                     # {"status": "healthy", "sessions": 3}

# WebSocket Protocol
Client → Server: {"type": "input|resize|ping", "data": "..."}
Server → Client: {"type": "output|status|pong", "data": "..."}

# Performance Targets
First byte < 200ms | Keystroke echo < 50ms | Reconnect < 2s
Memory < 50MB/session | SQLite < 100MB | WebSocket latency < 16ms

# Development Workflow

## Test-Driven Development (TDD)
1. Red: Write failing test that captures requirement
2. Green: Implement minimal code to pass test
3. Refactor: Improve code quality without changing behavior
4. Validate: Use MCP servers to verify UI/UX before committing
5. Commit: Only if all tests pass and MCP validation succeeds

## MCP Server Integration

Frog and Toad MCP Server (local): [specify capabilities when defined]

Chrome DevTools MCP Server:
- Use for: Real-time UI validation, network inspection, console monitoring, profiling
- Workflow: Start dev → Connect → Navigate all routes → Screenshot (320px/768px/1024px) → Check console (zero errors) → Network tab (verify 200s) → CLS < 0.1 → ARIA labels + keyboard nav

## Automation Strategy
Pre-commit: Unit tests, integration tests, lint, type check, security scan, UI validation (Chrome DevTools MCP)
Pre-push: All pre-commit + e2e tests, performance audit (Lighthouse > 95), dependency audit, docs sync

## Error Prevention Patterns
- Type safety: TypeScript strict mode, Python mypy --strict, no any types
- Input validation: API boundary, allow-lists, length limits, rate limiting (100 req/min)
- Error boundaries: Component level catch, user-friendly messages, technical logs
- Graceful degradation: Feature detection, fallbacks (WebSocket → SSE → Polling)
- Idempotency: All API ops safe to retry with idempotency keys
- Circuit breakers: Fail fast, exponential backoff with jitter, health checks

## Code Review Checklist
- [ ] Tests passing + zero console errors (Chrome DevTools MCP validated)
- [ ] Mobile-responsive (320px/768px/1024px) + TypeScript/Python type hints
- [ ] Error handling + performance targets met + no security issues
- [ ] Accessibility (ARIA, keyboard nav) + documentation updated
- [ ] Zero technical debt introduced, existing debt reduced if touched

# Commands
python legacy/server.py              # Legacy server
claude-on-the-go start               # New architecture
claude-on-the-go --dev               # Hot reload
claude-on-the-go qr                  # Connection QR
claude-on-the-go sessions            # List sessions
claude-on-the-go sessions --clean    # Remove expired
pytest tests/                        # All tests
pytest tests/unit/                   # Unit only
pytest --cov=core --cov-report=html  # Coverage

# Environment Variables
CLAUDE_CODE_PATH=/usr/local/bin/claude  # Required: Claude Code binary path
PORT=8000                               # Server port (default: 8000)
HOST=192.168.1.100                      # Bind address (auto-detect)
SQLITE_PATH=./sessions.db               # Session persistence
REQUIRE_PASSWORD=false                  # Password auth
SESSION_EXPIRE_DAYS=7                   # Auto-cleanup
PUSHOVER_USER_KEY=                      # Pushover notifications
NTFY_TOPIC=                             # ntfy.sh notifications
TELEGRAM_BOT_TOKEN=                     # Telegram bot
TAILSCALE_AUTHKEY=                      # Tailscale remote access

# Security
- Network isolation: Bind to LAN only, never 0.0.0.0
- No auth by default: Trust local network
- Optional password: REQUIRE_PASSWORD env var for shared networks
- Read-only sharing: Time-limited tokens (1 hour expiry)
- CORS: Restricted to local origins (192.168.*, 10.*, localhost)
- Rate limiting: 100 req/min per IP
- No logging sensitive data: Tokens, passwords, session content

# Git Commit Guidelines
- NEVER add "Co-Authored-By: Claude" or similar AI attribution
- NEVER add comments like "Generated by Claude" or "AI-written"
- ALWAYS commit as repository owner (your name only)
- ALWAYS write commits as if you wrote the code yourself
- Code should appear professionally written without AI markers
- Use conventional commits: feat:, fix:, refactor:, docs:, test:

# Mobile UI Requirements
- Terminal: xterm.js, 14px min font, pinch-to-zoom enabled
- Virtual keyboard: handle viewport resize without content shift
- PWA: installable with offline page, wake lock to prevent sleep
- Gestures: swipe for history, long-press for copy
- **See VIEWS.md for complete UI/UX specifications**

# Integration Priorities
1. QR code: qrcode lib for http://{local_ip}:{port} (instant connection)
2. Tailscale: Detect tailscale0 interface for remote access
3. Push notifications: Pushover/ntfy for Claude prompts (when input needed)
4. Voice input: Web Speech API for mobile (hands-free commands)

# Error Handling
- PTY spawn failures: Clear error message, check CLAUDE_CODE_PATH
- WebSocket drops: Auto-reconnect backoff (1s → 2s → 4s → 8s → 16s → 30s max)
- Claude not found: Check multiple paths (/usr/local/bin, /opt/homebrew/bin, ~/.local/bin)
- Network issues: Queue messages for retry (max 100 messages, 5 min expiry)

# Common Issues
- Can't connect from phone: Check firewall allows port 8000, ensure same WiFi
- Terminal text too small: Use PWA "Add to Home Screen" or pinch-to-zoom
- Connection drops on sleep: Enable auto-reconnect, check WiFi power saving
- Claude Code not found: Set CLAUDE_CODE_PATH explicitly in .env
- PTY spawn fails: Verify installation with which claude
- WebSocket won't connect: Check CORS settings, no proxy blocking upgrade
- High memory usage: Reduce SESSION_EXPIRE_DAYS, implement cleanup cron
