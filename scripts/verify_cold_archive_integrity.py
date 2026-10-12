import hashlib, sys
from pathlib import Path

archive_dir = Path("cold_archive")
if not archive_dir.exists():
    print("[FAIL] 'cold_archive' not found.")
    sys.exit(1)

checksum_file = archive_dir / "SHA256SUMS"
tarballs = sorted(archive_dir.glob("*.tar.gz"))
if len(tarballs) != 7:
    print(f"[FAIL] Expected 7 tarballs, found {len(tarballs)}.")
    sys.exit(1)

lines = []
for tb in tarballs:
    size = tb.stat().st_size
    if size < 1024:
        print(f"[FAIL] {tb.name} is too small ({size} bytes).")
        sys.exit(1)
    h = hashlib.sha256(tb.read_bytes()).hexdigest()
    lines.append(f"{h}  {tb.name}\n")
    print(f"  {tb.name:<45} ({size:>8} B) -> {h[:16]}...")

checksum_file.write_text("".join(lines), encoding="utf-8")
print(f"[SUCCESS] Verified and wrote {checksum_file}")
