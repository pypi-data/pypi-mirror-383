# Competitive Strategy: claude-on-the-go vs Omnara

## Executive Summary

Omnara (YC S25) just launched with mobile Claude Code access. We have technical advantages but need to execute on UX/polish to compete.

## Omnara Analysis

**What they have:**
- ✅ Native iOS app (App Store ready)
- ✅ Web dashboard for session management
- ✅ Push notifications when Claude needs input
- ✅ One-tap approval for changes
- ✅ Professional UX/UI polish
- ✅ YC backing & marketing muscle
- ✅ `pip install omnara` (easy install)

**What they DON'T have:**
- ❌ Local-only privacy (sends data to cloud)
- ❌ Zero cost (will monetize later)
- ❌ Terminal theme sync
- ❌ Clipboard bidirectional sync
- ❌ Self-hosted option

## Our Competitive Advantages

### 1. **Privacy-First Architecture**
- **Them**: Data flows through their cloud servers
- **Us**: 100% local WiFi, zero cloud, zero data leaks
- **Market**: Privacy-conscious developers, enterprises with strict data policies

### 2. **Zero Recurring Costs**
- **Them**: Free now, but YC-backed = eventual SaaS pricing
- **Us**: Free forever, self-hosted, no vendor lock-in
- **Market**: Individual developers, small teams, cost-sensitive users

### 3. **Technical Depth**
- **Them**: Basic terminal mirroring
- **Us**: Terminal theme detection, clipboard sync, session persistence
- **Market**: Power users who want their exact setup on mobile

### 4. **Open Source**
- **Them**: Proprietary (GitHub repo is client-only wrapper)
- **Us**: Fully open source, hackable, extensible
- **Market**: OSS enthusiasts, teams wanting customization

## Implementation Roadmap

### Week 1: Fix Mobile UX ✅ DONE
- [x] Fix scrolling issues (40% → 100% responsive)
- [x] Switch to canvas renderer for performance
- [x] Proper iOS keyboard handling
- [x] Smooth momentum scrolling

### Week 2: PWA Implementation
**Priority: P0 - Critical for mobile competition**

**Tasks:**
- [ ] Create proper PWA manifest with icons
- [ ] Implement service worker for offline support
- [ ] Add "Add to Home Screen" prompt
- [ ] iOS splash screens
- [ ] Push notification support (Web Push API)

**Files to create:**
- `client/pwa/manifest.json`
- `client/pwa/sw.js` (service worker)
- `client/pwa/icons/` (app icons 192x192, 512x512)

### Week 3: Push Notifications
**Priority: P0 - Match Omnara's killer feature**

**Tasks:**
- [ ] Detect when Claude needs input (prompt detection)
- [ ] Web Push API integration
- [ ] Notification permission flow
- [ ] One-tap to open app from notification
- [ ] Badge count on app icon

**Implementation:**
```javascript
// Detect Claude prompts in terminal output
if (output.includes('?') || output.includes('(y/n)')) {
    sendPushNotification({
        title: 'Claude needs your input',
        body: output.substring(0, 100),
        tag: sessionId,
        requireInteraction: true
    });
}
```

### Week 4: Easy Installation
**Priority: P1 - Match their `pip install omnara` UX**

**Tasks:**
- [ ] Create PyPI package: `pip install claude-on-the-go`
- [ ] Auto-start on install
- [ ] QR code shows immediately
- [ ] Detect Claude CLI automatically

**Install flow:**
```bash
pip install claude-on-the-go
claude-on-the-go start  # Auto-opens QR code
```

### Week 5-6: Native App (Capacitor)
**Priority: P1 - App Store presence**

**Tasks:**
- [ ] Wrap PWA with Capacitor
- [ ] Native keyboard improvements
- [ ] Biometric auth (Touch ID/Face ID)
- [ ] Background session sync
- [ ] Submit to App Store

**Advantages over their app:**
- Privacy-first messaging in App Store description
- "No cloud, no tracking, no subscriptions"
- Open source trust

### Week 7-8: Web Dashboard
**Priority: P2 - Nice to have**

**Tasks:**
- [ ] Session history viewer
- [ ] Multi-session management
- [ ] Session sharing (time-limited QR codes)
- [ ] Analytics dashboard (local only)

## Messaging Strategy

### Positioning

**Tagline:** "Claude Code in Your Pocket — Zero Cloud, Zero Cost"

**Key Messages:**
1. **Privacy**: "Your code never leaves your WiFi network"
2. **Cost**: "Free forever, no subscriptions, no surprises"
3. **Control**: "Self-hosted, fully hackable, open source"
4. **Performance**: "< 50ms latency on local WiFi vs cloud routing"

### Target Audiences

**Primary:**
- Privacy-conscious developers
- Open source enthusiasts
- Self-hosting advocates
- Cost-sensitive indie developers

**Secondary:**
- Enterprise teams (strict data policies)
- Remote workers (want mobile access)
- Students (can't afford SaaS tools)

### Content Strategy

**Hacker News Post:**
```
Show HN: claude-on-the-go — Open source alternative to Omnara (zero cloud, zero cost)

We built this before Omnara launched, focused on privacy & self-hosting.

Key differences:
- 100% local WiFi (no cloud servers)
- Free forever (no VC to monetize for)
- Terminal theme sync (iTerm2, Ghostty, etc.)
- Fully open source

We just fixed mobile scrolling to compete with their UX.
Try it: https://github.com/MatthewJamisonJS/claude-on-the-go
```

**Reddit r/programming:**
```
PSA: You don't need Omnara's cloud for mobile Claude access

claude-on-the-go does the same thing, but:
✅ Zero cloud (privacy-first)
✅ Zero cost (self-hosted)
✅ Open source
✅ Works with any terminal theme

Just fixed mobile UX to match their quality.
```

## Feature Comparison Matrix

| Feature | Omnara | claude-on-the-go | Advantage |
|---------|--------|------------------|-----------|
| **Mobile Access** | ✅ iOS App | 🚧 PWA → Native | Tie (soon) |
| **Push Notifications** | ✅ Yes | 🚧 Week 3 | Them (temp) |
| **Installation** | ✅ `pip install` | 🚧 Week 4 | Them (temp) |
| **Privacy** | ❌ Cloud routing | ✅ Local WiFi only | **Us** |
| **Cost** | ❓ TBD (free now) | ✅ Free forever | **Us** |
| **Terminal Themes** | ❌ No | ✅ 6 terminals | **Us** |
| **Clipboard Sync** | ❓ Unknown | ✅ Bidirectional | **Us** |
| **Open Source** | ❌ No | ✅ MIT License | **Us** |
| **Session Persistence** | ✅ Yes | ✅ Yes | Tie |
| **Web Dashboard** | ✅ Yes | 🚧 Week 7 | Them (temp) |
| **Multi-device** | ✅ Yes | 🚧 Session sharing | Them (temp) |

## Go-to-Market Timeline

### Month 1 (Current)
- Week 1: Fix mobile UX ✅
- Week 2: PWA implementation
- Week 3: Push notifications
- Week 4: PyPI package

### Month 2
- Week 5-6: Native app (Capacitor)
- Week 7-8: Web dashboard

### Month 3
- Launch marketing campaign
- App Store submission
- HN/Reddit posts
- Product Hunt launch

## Success Metrics

**Technical:**
- [ ] < 50ms touch latency (beat their cloud routing)
- [ ] 60fps scrolling (match native app feel)
- [ ] < 2s session reconnection
- [ ] Lighthouse PWA score > 95

**Growth:**
- [ ] 1,000 GitHub stars (community validation)
- [ ] 500 PyPI installs/month
- [ ] App Store: 1,000 downloads
- [ ] HN front page (500+ upvotes)

**Retention:**
- [ ] 50% weekly active (vs. install base)
- [ ] < 10% churn rate
- [ ] 5+ contributors (sustainability)

## Risk Mitigation

### Risk: Omnara has YC funding for fast iteration
**Mitigation:**
- Focus on privacy/cost angles (can't compete)
- Build loyal OSS community
- Enterprise partnerships (data policy requirements)

### Risk: They have better UX/polish
**Mitigation:**
- Hire designer (Fiverr, $500 budget)
- Copy their best patterns (legal for UX)
- Get early user feedback

### Risk: App Store approval delays
**Mitigation:**
- PWA works great (80% use case)
- TestFlight beta first
- Have backup distribution (direct IPA)

## Action Items (Next 48 Hours)

**Immediate:**
- [ ] Start PWA manifest (`client/pwa/manifest.json`)
- [ ] Design app icons (Figma/Canva)
- [ ] Implement service worker basics
- [ ] Test "Add to Home Screen" on iPhone

**Short-term:**
- [ ] Set up push notification server
- [ ] Create PyPI package structure
- [ ] Draft HN/Reddit posts
- [ ] Record demo video (mobile scroll, clipboard, themes)

**Marketing:**
- [ ] Update README with Omnara comparison
- [ ] Create PRIVACY.md (highlight our advantage)
- [ ] Screenshots for App Store/Product Hunt
- [ ] Testimonial from early users

## The Moat

**What Omnara can't copy:**
1. **Privacy architecture** - Rebuilding for local-only = different product
2. **Zero cost** - Their VC funding requires monetization
3. **Open source trust** - Can't open-source with investors

**What we can't copy (easily):**
1. **YC network effects** - But we don't need their scale
2. **Marketing budget** - But OSS/HN gives free reach
3. **Team size** - But focus = feature advantage

## Conclusion

We have a **defensible moat** (privacy, cost, OSS) and can catch up on UX in 4-6 weeks.

**Key insight:** Omnara targets VC-scale market. We target privacy/cost-conscious developers who will be our evangelists.

**Next steps:** Execute on PWA → Push → PyPI → Native app → Web dashboard.

**Win condition:** When developers say "Omnara for enterprise, claude-on-the-go for privacy/freedom"
