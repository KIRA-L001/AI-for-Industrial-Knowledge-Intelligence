# KIRA — Sample data

Realistic industrial sample documents to populate your KIRA workspace so the
knowledge graph, search, analytics, and AI Copilot all light up.

All files are **CSV** (a fully supported upload type) and are deliberately rich
in **equipment tags** (`P-101`, `C-200`, `V-2003`, `PSV-4501`, `T-500`, …) and
**compliance standards** (`OISD-STD-105`, `PESO`, `Factory Act`, `API 610`,
`API 617`, `API 682`, `ISO 10816`, …) so the entity/relationship extractor and
the graph populate meaningfully.

| File | Use it for |
|------|-----------|
| `equipment_register.csv` | The asset list (also create these on the **Equipment** page) |
| `maintenance_records.csv` | Maintenance history → Maintenance agent |
| `incident_reports.csv` | Incidents → RCA agent |
| `compliance_register.csv` | Compliance items → Compliance agent |
| `inspection_log.csv` | Inspection findings → Knowledge / Lessons Learned |

## Add them through the website

1. Open http://localhost:3000 and sign in.
2. **Equipment** page → add a few assets from `equipment_register.csv`
   (e.g. tag `P-101`, name "Crude Feed Pump", criticality `critical`).
3. **Projects** page → create a project, e.g. "Turnaround 2026".
4. **Documents** page → upload each CSV from this folder. Each one moves through
   `uploaded → processing` automatically.
5. For each document, run **Process** (extract text), **Analyze** (chunk +
   extract entities/relationships), then **Embed** (index for search). *(The
   Documents page exposes these actions; or use the seed script below to do all
   of it at once.)*
6. **Knowledge Graph** page → click **Sync**, then explore — you'll see pumps,
   compressors, vessels and the standards that govern them.
7. **AI Copilot** page → ask the questions below.

## Example Copilot questions (each routes to the right agent)

- **RCA:** *"What is the root cause of the P-101 pump seal failure?"*
- **Maintenance:** *"What maintenance has been done on compressor C-200 and what should we do next?"*
- **Compliance:** *"Are we compliant with OISD and PESO requirements, and what gaps remain?"*
- **Knowledge:** *"Which equipment is governed by API 617?"*
- **Lessons Learned:** *"What recurring failure patterns appear across our incidents?"*
- **Document Intelligence:** *"Summarize the inspection log findings."*

Every answer comes back with a **confidence score** and **citations** pointing
to the exact rows/passages in your uploaded documents.

## One-command seed (optional)

Instead of clicking through, `seed.sh` registers a workspace, creates the
equipment, uploads every CSV, and runs process → analyze → embed → graph sync
via the API.

```bash
# requires the stack running (npm run infra:up) and `curl` (no jq needed)
cd samples
EMAIL=demo@kira.example.com PASSWORD=password123 bash seed.sh
```

Then open the web app, sign in with those credentials, and explore.
