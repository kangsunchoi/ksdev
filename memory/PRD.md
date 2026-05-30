# NetConfig Builder - PRD

## Problem Statement
Production-grade web app for network engineers to automatically generate Cisco network device configurations and validate them before output. Supports IOS-XE platforms (IE3300/3400/9320, Catalyst 9200/9300/9500, WLC 9800).

## Architecture
- **Frontend**: React 19 + TailwindCSS + Shadcn/UI + React Router
- **Backend**: FastAPI + Motor (async MongoDB driver)
- **Database**: MongoDB (real persistence)
- **Theme**: Dark-only, engineering-focused industrial IDE aesthetic

## User Personas
- Network engineers configuring Cisco switches
- OT/Industrial engineers deploying IE-series switches in factory environments
- NOC teams generating standardized configs for campus deployments

## Core Requirements (Static)
1. Template-based config generation for IOS-XE (no AI hallucination)
2. Smart validation engine (IP, VLAN, interface, feature support checks)
3. Platform-separated logic (IE vs Catalyst vs WLC)
4. 4-output format: clean config, annotated, validation report, checklist
5. Industrial OT metadata for IE platforms
6. Export: TXT, JSON, YAML
7. Template library with lock/duplicate/tag support
8. Revision history with snapshots and side-by-side diff
9. JSON/YAML bulk import for project creation
10. DHCP relay (ip helper-address) generation for L3 platforms

## What's Been Implemented

### 2026-03-21
**Backend**
- Full CRUD API for projects and templates
- Platform profiles for 7 device families with feature support matrix
- Validation engine: IP/subnet, VLAN, interface, feature support, SNMP, AAA checks
- Config renderer: real IOS-XE CLI (hostname, service, AAA, users, VLANs, STP, access/trunk/port-channel, SVIs, routing, NTP, syslog, SNMP, SSH, banner, line con/vty)
- WLC 9800 stub with honest "limited support" notice
- Export API: JSON, YAML, TXT
- Revision history with snapshots on update
- Seed data: 3 templates + 1 sample project
- Create project from template API

**Frontend**
- Dashboard with stats + recent projects table
- Multi-step wizard (7 steps): Device/Mgmt, VLANs, Interfaces, Routing/Services, Security, Industrial OT, Review
- Project detail with tabs: Clean Config, Annotated, Validation, Checklist, Export
- Template library with filter, duplicate, lock, use
- Sidebar navigation, dark theme, JetBrains Mono for config, IBM Plex Sans for UI

### 2026-05-30 — C Plan
- **DHCP Relay** (P0): backend renderer `_dhcp_relay`, validation `_validate_dhcp_relay` (helper IP / VLAN / platform feature check), `DhcpRelay` model, wizard UI subsection in Routing & Services step
- **JSON/YAML Import** (P0): `/api/projects/import` now accepts `{format, content}` payload (and backward-compatible raw dict). Dashboard hidden file picker → POST → navigate to imported project
- **Revision Diff Viewer** (P1): new `Revisions` tab in ProjectDetail with revision list + side-by-side diff table (add/remove/change rows)
- **Export UI verified** (P0): TXT (post-generate) / JSON / YAML download buttons working end-to-end via `/api/projects/{id}/export/{format}`

## Prioritized Backlog

### P1
- DOCX/PDF export (python-docx, reportlab)
- HSRP/VRRP template for L3 Catalyst switches
- IE3400 L3 specific templates
- Config search within generated output
- WLC 9800 full WLAN/SSID/policy rendering

### P2
- JWT authentication + role-based access
- Nexus NX-OS platform support
- PTP/REP/CIP industrial protocol modeling per platform
- AI-assisted custom config generation (with strict validation gate)
- Drag-and-drop import zone + paste-from-clipboard import
- Extract `buildProjectDiff()` to `/lib/diff.js` for unit testing
- Split NewProject.jsx Step* sub-components into separate files (file >900 lines)

## Next Tasks
1. HSRP/VRRP template for Catalyst 9300/9500 distribution
2. DOCX/PDF export (deferred from MVP)
3. WLC 9800 full WLAN profile rendering
4. Drag-and-drop file import zone on Dashboard
5. Refactor NewProject.jsx into smaller files
