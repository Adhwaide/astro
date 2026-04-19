"""Quick endpoint test for all new API routes."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import httpx

BASE = "http://127.0.0.1:8000/api"
DATA = {"dob":"2004-02-28","tob":"01:15","place":"Kochi, Kerala, India"}

# 1. Divisional D9
r = httpx.post(f"{BASE}/divisional", json={**DATA, "chart_type": "D9"})
d = r.json()
print("=== /api/divisional (D9) ===")
print(f"  Status: {r.status_code}")
print(f"  D9 Lagna: {d['lagna']['sign_name']}")
print(f"  Planets: {len(d['planets'])}")

# 2. Report
r2 = httpx.post(f"{BASE}/report", json=DATA)
rp = r2.json()
print("\n=== /api/report ===")
print(f"  Status: {r2.status_code}")
for section in ["health", "career", "relationships", "spirituality", "current_period_summary"]:
    s = rp[section]
    nf = len(s["key_factors"])
    print(f"  {section}: {nf} factors | {s['summary'][:70]}...")

# 3. Dasha 5-level
r3 = httpx.post(f"{BASE}/dasha", json=DATA)
dd = r3.json()
cp = dd["current_period"]
print("\n=== /api/dasha (5-level) ===")
print(f"  Status: {r3.status_code}")
print(f"  Maha:      {cp.get('mahadasha',{}).get('lord_name','?')}")
print(f"  Antar:     {cp.get('antardasha',{}).get('lord_name','?')}")
print(f"  Pratyantar:{cp.get('pratyantardasha',{}).get('lord_name','?')}")
print(f"  Sookshma:  {cp.get('sookshmadasha',{}).get('lord_name','?')}")
print(f"  Prana:     {cp.get('pranadasha',{}).get('lord_name','?')}")

# Verify nesting depth
m0 = dd["mahadasha"][0]
a0 = m0["antardasha"][0]
p0 = a0["pratyantardasha"][0]
s0 = p0["sookshmadasha"][0]
pr0 = s0["pranadasha"][0]
print(f"\n  Nesting: {m0['lord']} > {a0['lord']} > {p0['lord']} > {s0['lord']} > {pr0['lord']}")
print("  5-level depth: OK")

print("\n=== ALL ENDPOINTS VERIFIED ===")
