#!/usr/bin/env bash
# Seed a KIRA workspace with the sample documents.
# Requires: the stack running (npm run infra:up) and `curl`. (No jq needed.)
#
#   EMAIL=demo@kira.example.com PASSWORD=password123 ./seed.sh
#
# Best-effort seeding (continues past individual failures).

API="${API:-http://localhost:8000/api/v1}"
EMAIL="${EMAIL:-demo@kira.example.com}"
PASSWORD="${PASSWORD:-password123}"
ORG="${ORG:-KIRA Demo Refinery}"
DIR="$(cd "$(dirname "$0")" && pwd)"

# Extract a top-level JSON string field without jq.
json_field() { grep -oE "\"$1\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" | head -1 | sed -E 's/.*:[[:space:]]*"([^"]*)"/\1/'; }

echo "→ Registering / logging in $EMAIL"
reg=$(curl -s -X POST "$API/auth/register" -H "Content-Type: application/json" \
  -d "{\"organization_name\":\"$ORG\",\"email\":\"$EMAIL\",\"full_name\":\"KIRA Demo\",\"password\":\"$PASSWORD\"}" || true)
token=$(echo "$reg" | json_field access_token)

if [ -z "$token" ]; then
  echo "  (already registered — logging in)"
  login=$(curl -s -X POST "$API/auth/login" -H "Content-Type: application/json" \
    -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")
  token=$(echo "$login" | json_field access_token)
fi
[ -n "$token" ] && [ "$token" != "null" ] || { echo "✗ auth failed"; exit 1; }
AUTH=(-H "Authorization: Bearer $token")
echo "✓ authenticated"

echo "→ Creating equipment"
create_equipment() {
  curl -s -o /dev/null -w "  %{http_code} $1\n" -X POST "$API/equipment" "${AUTH[@]}" \
    -H "Content-Type: application/json" \
    -d "{\"tag\":\"$1\",\"name\":\"$2\",\"equipment_type\":\"$3\",\"criticality\":\"$4\"}"
}
create_equipment "P-101" "Crude Feed Pump" "Centrifugal Pump" "critical"
create_equipment "C-200" "Recycle Gas Compressor" "Centrifugal Compressor" "critical"
create_equipment "V-2003" "Knockout Drum" "Pressure Vessel" "high"
create_equipment "PSV-4501" "Pressure Safety Valve" "Relief Valve" "critical"
create_equipment "T-500" "Atmospheric Distillation Column" "Column" "critical"

echo "→ Creating project"
curl -s -o /dev/null -w "  %{http_code} project\n" -X POST "$API/projects" "${AUTH[@]}" \
  -H "Content-Type: application/json" \
  -d '{"name":"Turnaround 2026","description":"Major overhaul and inspection campaign"}'

echo "→ Uploading + processing documents"
cd "$DIR"  # use relative paths so curl -F opens files reliably on Windows
for f in maintenance_records.csv incident_reports.csv compliance_register.csv inspection_log.csv equipment_register.csv; do
  echo "  • $f"
  doc=$(curl -s -X POST "$API/documents/upload" "${AUTH[@]}" -F "file=@$f;type=text/csv")
  id=$(echo "$doc" | json_field id)
  [ -n "$id" ] || { echo "    ✗ upload failed: $doc"; continue; }
  curl -s -o /dev/null "$API/documents/$id/process" "${AUTH[@]}" -X POST
  curl -s -o /dev/null "$API/documents/$id/analyze" "${AUTH[@]}" -X POST
  curl -s -o /dev/null "$API/documents/$id/embed"   "${AUTH[@]}" -X POST
  echo "    ✓ processed → analyzed → embedded"
done

echo "→ Syncing knowledge graph"
curl -s -o /dev/null -w "  %{http_code} graph sync\n" -X POST "$API/graph/sync" "${AUTH[@]}"

echo
echo "✓ Seed complete. Sign in at http://localhost:3000 as $EMAIL / $PASSWORD"
echo "  Try the Copilot: \"What is the root cause of the P-101 pump seal failure?\""
