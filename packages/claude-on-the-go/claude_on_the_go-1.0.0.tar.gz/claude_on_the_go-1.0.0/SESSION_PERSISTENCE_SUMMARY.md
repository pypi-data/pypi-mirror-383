# Session Persistence - Research Summary

**Date**: 2025-10-10
**Task**: Research and plan session persistence feature
**Status**: Planning Complete - Ready for Implementation

---

## Executive Summary

This document summarizes the research and design for enabling **persistent terminal sessions** in claude-on-the-go. Users will be able to disconnect from their Claude Code CLI session and reconnect hours/days later without losing terminal history or state.

**Full Technical Design**: See [docs/SESSION_PERSISTENCE.md](docs/SESSION_PERSISTENCE.md)
**Implementation Timeline**: See [ROADMAP.md](ROADMAP.md) - Week 3-4

---

## 1. Current Architecture Findings

### What Works Today
The system already has **partial session persistence**:

- **Sessions survive WebSocket disconnections** (in-memory)
- **Session IDs** (UUIDs) allow reconnection within same server session
- **SessionStore module exists** (`core/session_store.py`) with SQLite support
- **PTY manager** (`core/pty_manager.py`) handles Claude process lifecycle

### Current Limitations
- **No scrollback buffer persistence** - Terminal history lost on disconnect
- **In-memory storage only** - All sessions lost on server restart
- **No PTY state serialization** - Cannot resume exact cursor position
- **SessionStore not integrated** - Exists but unused by legacy backend
- **Short timeout** - 1 hour inactivity timeout (user wants "no time-limit")

### Key Discovery
The `core/session_store.py` module (419 LOC) **already implements** everything we need:
- SQLite persistence with gzip compression
- Session CRUD operations
- Automatic cleanup
- Scrollback buffer storage

**Problem**: Legacy backend (`legacy/backend/app.py`) uses in-memory `SessionManager` instead.

**Solution**: Replace in-memory storage with SQLite SessionStore (straightforward integration).

---

## 2. Proposed Design Approach

### 2.1 Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│  WebSocket Connection                                     │
│  ┌────────────────────────────────────────────────────┐  │
│  │ 1. Connect with session_id                         │  │
│  │ 2. SessionStore checks SQLite for existing session │  │
│  │ 3. If found: Replay scrollback buffer              │  │
│  │ 4. Resume live streaming from current position     │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  PTY Manager (core/pty_manager.py)                       │
│  ┌────────────────────────────────────────────────────┐  │
│  │ • Reads output from Claude process (4KB chunks)    │  │
│  │ • Streams to WebSocket (real-time)                 │  │
│  │ • Persists to SessionStore (SQLite, batched)       │  │
│  │ • Compresses when buffer > 10KB (gzip)             │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  SQLite Database (sessions.db)                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │ sessions table:                                     │  │
│  │ - id (UUID)                                         │  │
│  │ - pid (Claude process ID)                           │  │
│  │ - history (compressed scrollback buffer, BLOB)      │  │
│  │ - created_at, last_activity (timestamps)            │  │
│  │ - rows, cols (terminal dimensions)                  │  │
│  │ - alive (is Claude process still running?)          │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### 2.2 Key Components

**1. Enhanced SQLite Schema** (add to existing table):
```sql
ALTER TABLE sessions ADD COLUMN pid INTEGER;
ALTER TABLE sessions ADD COLUMN alive INTEGER DEFAULT 1;
ALTER TABLE sessions ADD COLUMN max_history_bytes INTEGER DEFAULT 52428800;
```

**2. PTY Output Persistence** (modify `PTYManager._read_loop()`):
```python
# Capture all output to SessionStore
output = process.read_nonblocking(4096)
await session_store.save_output(session_id, output)  # Persists to SQLite
await websocket.send(output)  # Real-time streaming
```

**3. Reconnection Flow** (modify `ConnectionManager.connect()`):
```python
if session_id:
    session = await session_store.get_session(session_id)
    if session and session.alive:
        # Replay scrollback buffer
        history = session.get_history()  # Decompresses if needed
        await websocket.send({"type": "output", "text": history, "is_replay": True})
        # Resume live streaming...
```

**4. REST API** (new endpoints):
```python
GET /sessions              # List all sessions
DELETE /sessions/{id}      # Delete session and kill process
GET /sessions/{id}/history # Export scrollback buffer
```

### 2.3 Mobile UX Flow

**Scenario**: User disconnects and reconnects 2 hours later.

1. **Client**: Sends `session_id` from localStorage in WebSocket connection
2. **Server**: Finds session in SQLite, checks if Claude process still alive
3. **Server**: Sends "Reconnecting..." message to client
4. **Server**: Replays full scrollback buffer (decompressed from SQLite)
5. **Client**: Clears terminal, writes replayed history
6. **Client**: Shows notification: "Reconnected to session (2h old)"
7. **Server**: Resumes live streaming from current position

**Latency target**: < 2 seconds for 10MB scrollback buffer

---

## 3. Key Technical Challenges

### Challenge 1: PTY Reattachment
**Problem**: `pexpect` doesn't support reattaching to existing PTY processes.

**Solution**: Don't reattach - just replay scrollback buffer. The visual effect is identical to the user. If Claude process died, mark session as dead and prompt user to start new session.

---

### Challenge 2: Scrollback Buffer Size
**Problem**: Long sessions (days) could accumulate gigabytes of output.

**Solution**:
- Enforce max history per session (default: 50MB uncompressed)
- Trim oldest data when limit exceeded (FIFO)
- Gzip compression (typical 10:1 ratio for terminal output)
- Configurable via `MAX_SESSION_HISTORY_MB` env var

---

### Challenge 3: Database Write Performance
**Problem**: Writing to SQLite on every 4KB output chunk would be slow.

**Solution**: Batched writes
- Buffer output in memory
- Flush to SQLite every 1 second or 10KB (whichever first)
- Use async wrapper (`asyncio.to_thread()`) to avoid blocking PTY reads
- Enable SQLite WAL mode for concurrent reads during writes

---

### Challenge 4: Orphaned PTY Processes
**Problem**: Server crashes, Claude processes left running, no way to reattach.

**Solution**: Cleanup on startup
- Scan sessions table for `alive=1` entries
- Check if each PID still exists (`os.kill(pid, 0)`)
- If process dead, mark session as `alive=0`
- Optionally kill orphaned processes

---

### Challenge 5: Session Timeout Policy
**User requirement**: "No time-limit on your session"

**Solution**:
- **Active sessions** (client connected): No timeout
- **Idle sessions** (client disconnected): 24 hour timeout (configurable)
- **Dead sessions** (Claude process died): 1 hour grace period for debugging
- Cleanup task runs every 5 minutes

---

## 4. Implementation Timeline

### Week 3: Core Infrastructure (5 days)

**Day 1-2: Schema & Integration**
- Add new columns to SQLite schema
- Replace in-memory SessionManager with SessionStore
- Write migration script for existing sessions

**Day 3-4: PTY Persistence**
- Modify PTYManager to persist output to SessionStore
- Implement batched database writes
- Add history size limits and trimming

**Day 5: Edge Cases**
- Orphaned session cleanup
- Database corruption fallback
- Session expiry logic

### Week 4: WebSocket & API (5 days)

**Day 6-7: Reconnection Flow**
- Update ConnectionManager for session reconnection
- Implement scrollback buffer replay
- Add reconnection UI indicators

**Day 8: REST API**
- `/sessions` endpoint (list)
- `/sessions/{id}` endpoint (delete)
- `/sessions/{id}/history` endpoint (export)

**Day 9: Client Updates**
- Persist session ID in localStorage
- Reconnection notifications
- Mobile UX testing

**Day 10: Testing & Docs**
- End-to-end tests (reconnection scenarios)
- Performance benchmarks
- Documentation updates

---

## 5. Success Metrics

### Functional Requirements
- [ ] Sessions survive server restarts (100% success rate)
- [ ] Reconnection works within 24h of disconnect (95%+ success)
- [ ] No scrollback data loss (history replay accurate)
- [ ] Expired sessions cleaned up automatically

### Performance Requirements
- [ ] Scrollback replay: < 2s for 10MB buffer
- [ ] Database write latency: < 10ms per batch
- [ ] Memory overhead: < 20MB for 100 sessions
- [ ] Compression ratio: > 8:1 for typical output

### User Experience
- [ ] Reconnection feels seamless (no visible lag)
- [ ] Clear UI indicators for reconnection state
- [ ] Session ID persists in browser (localStorage)
- [ ] Mobile keyboards don't obstruct reconnection

---

## 6. Risk Assessment

### Low Risk
- **Backward compatibility**: New SQLite columns added with defaults (no breaking changes)
- **Module reuse**: `SessionStore` already exists and tested
- **Incremental rollout**: Can deploy behind feature flag

### Medium Risk
- **Performance**: Batched writes should prevent slowdown, but needs benchmarking
- **Storage growth**: Need monitoring for disk usage, may need cleanup policies

### Mitigation
- Deploy to staging first with 24h soak test
- Monitor SQLite database size growth
- Add metrics for reconnection success rate
- Feature flag for easy rollback if issues

---

## 7. Open Questions (To Decide)

1. **Session naming**: Should users name sessions (e.g., "Project X")?
   - **Decision**: Not in MVP, add in v2.1 if requested

2. **Cursor position tracking**: Track exact cursor for seamless resume?
   - **Decision**: No (requires complex ANSI parsing), rely on scrollback replay

3. **Max sessions per user**: Enforce limit (e.g., 10 sessions)?
   - **Decision**: No limit initially, monitor resource usage

4. **History encryption**: Encrypt scrollback buffers at rest?
   - **Decision**: Not in MVP (local-only), add if cloud sync added

---

## 8. Next Steps

**Immediate (This Week)**:
1. Review this summary and technical design
2. Create GitHub issues for each implementation task
3. Set up feature branch: `feature/session-persistence`

**Week 3 (Starting Monday)**:
1. Begin schema migration (Day 1-2 tasks)
2. Daily standups to track progress
3. Code reviews for each component

**Week 4**:
1. Complete WebSocket reconnection flow
2. End-to-end testing on mobile devices
3. Documentation and demo video

**Post-Implementation**:
1. Deploy to staging for 24h soak test
2. Monitor metrics (reconnection rate, DB size)
3. Production deployment with gradual rollout

---

## Conclusion

The session persistence feature is **well-scoped** and **low-risk**. The core infrastructure (`SessionStore`) already exists - we just need to integrate it with the legacy backend and add reconnection logic.

**Estimated effort**: 10 days (2 weeks)
**Risk level**: Low
**User impact**: High (addresses key pain point: "no time-limit on session")

**Key insight**: This isn't building from scratch - it's **connecting existing pieces** (PTYManager → SessionStore → WebSocket reconnection).

---

**Documents Created**:
1. `/Users/wwjd_._/Code/claude-on-the-go/docs/SESSION_PERSISTENCE.md` - Full technical design (12,000 words)
2. `/Users/wwjd_._/Code/claude-on-the-go/ROADMAP.md` - Implementation timeline with tasks
3. `/Users/wwjd_._/Code/claude-on-the-go/SESSION_PERSISTENCE_SUMMARY.md` - This summary

**Ready for implementation**: Yes
**Approval needed**: Product review, then proceed to implementation
