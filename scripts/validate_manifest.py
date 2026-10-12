import json
import sys
from pathlib import Path

EXPECTED_PROJECTS = 40
EXPECTED_POINTS = 316
EXPECTED_PARTITION = {"CONSOLIDATE": 33, "ACTIVE_SPRINT": 0, "ARCHIVE": 7}
EXPECTED_HISTOGRAMS = {
    "Quantum": {9: 8, 3: 2},
    "Linguistics": {9: 8, 3: 2},
    "Color Physics": {9: 9, 2: 1},
    "Invariants": {9: 8, 3: 1, 2: 1},
}
EXPECTED_BATCH_COUNT = 14
EXPECTED_BATCH_TS = "2026-10-12T16:52:04.940Z"

def validate(path="audit_manifest.json"):
    p = Path(path)
    if not p.exists():
        print(f"[FAIL] {p} not found")
        sys.exit(1)
    d = json.load(open(p, encoding="utf-8"))
    projects = d.get("projects", [])
    if len(projects) != EXPECTED_PROJECTS:
        print(f"[FAIL] Expected {EXPECTED_PROJECTS} projects, found {len(projects)}")
        sys.exit(1)

    pts = sum(int(x.get("passedChecksCount", 0)) for x in projects)
    tally = {"CONSOLIDATE": 0, "ACTIVE_SPRINT": 0, "ARCHIVE": 0}
    track_pts = {}
    track_hists = {
        "Quantum": {},
        "Linguistics": {},
        "Color Physics": {},
        "Invariants": {}
    }
    batch_ts = set()
    batch_count = 0

    for x in projects:
        disp = x.get("disposition")
        tally[disp] = tally.get(disp, 0) + 1
        score = int(x.get("passedChecksCount", 0))
        t = x.get("assignedTrack") or x.get("track") or "Unknown"
        track_pts[t] = track_pts.get(t, 0) + score

        if t not in track_hists:
            track_hists[t] = {}
        track_hists[t][score] = track_hists[t].get(score, 0) + 1

        if x.get("promotedInBatch"):
            batch_count += 1
            batch_ts.add(x.get("updatedAt"))

    print(f"[-] Points: {pts}/360 | Partition: {tally} | Batch: {batch_count}")
    assert pts == EXPECTED_POINTS, f"Point mismatch: {pts} != {EXPECTED_POINTS}"
    assert tally == EXPECTED_PARTITION, "Partition mismatch"
    assert batch_count == EXPECTED_BATCH_COUNT, "Batch count mismatch"
    assert batch_ts == {EXPECTED_BATCH_TS}, f"Batch TS mismatch: {batch_ts}"
    assert track_hists == EXPECTED_HISTOGRAMS, f"Histogram mismatch: {track_hists}"
    print("[SUCCESS] Manifest is mathematically reconciled and schema-compliant.")

if __name__ == "__main__":
    validate(sys.argv[1] if len(sys.argv) > 1 else "audit_manifest.json")
