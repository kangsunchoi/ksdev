# NetConfig Builder - PRD

## Problem Statement
Production-grade web app for network engineers to automatically generate Cisco network device configurations and validate them before output. Supports IOS-XE platforms (IE3300/3400/9320, Catalyst 9200/9300/9500, WLC 9800).

## Architecture
- **Frontend**: React 19 + TailwindCSS + Shadcn/UI + React Router
- **Backend**: FastAPI + Motor (async MongoDB driver)
- **Database**: MongoDB
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
8. Revision history with snapshots

## What's Been Implemented (2026-03-21)
### Backend
- Full CRUD API for projects and templates
- Platform profiles for 7 device families with feature support matrix
- Validation engine: IP/subnet, VLAN, interface, feature support, SNMP, AAA checks
- Config renderer: generates real IOS-XE CLI commands (hostname, service, AAA, users, VLANs, STP, access/trunk/port-channel interfaces, SVIs, routing, NTP, syslog, SNMP, SSH, banner, line con/vty)
- WLC 9800 stub with honest "limited support" notice
- Export API: JSON, YAML, TXT
- Revision history with snapshots on update
- Seed data: 3 templates (IE3300, Cat9300, WLC9800) + 1 sample project
- Create project from template API

### Frontend
- Dashboard with stats + recent projects table
- Multi-step wizard (7 steps): Device/Mgmt, VLANs, Interfaces, Routing/Services, Security, Industrial OT, Review
- Project detail with 5 tabs: Clean Config, Annotated, Validation, Checklist, Export
- Template library with filter, duplicate, lock, use actions
- Sidebar navigation
- Dark theme, JetBrains Mono for config output, IBM Plex Sans for UI

## Prioritized Backlog
### P0 (Next)
- JSON/YAML import for bulk project creation
- DHCP relay configuration support
- HSRP template for L3 Catalyst switches

### P1
- DOCX/PDF export (python-docx, reportlab)
- Side-by-side diff viewer for revision history
- IE3400 L3 specific templates
- Config search within generated output

### P2
- JWT authentication + role-based access
- Nexus NX-OS platform support
- Full WLC 9800 WLAN/SSID/policy config generation
- PTP/REP/CIP industrial protocol modeling per platform
- AI-assisted custom config generation (with strict validation)
- Drag-and-drop JSON import zone

## Next Tasks
1. Implement JSON/YAML import UI
2. Add revision diff viewer (side-by-side)
3. Add DOCX/PDF export
4. Implement authentication layer
5. Expand WLC 9800 config rendering
