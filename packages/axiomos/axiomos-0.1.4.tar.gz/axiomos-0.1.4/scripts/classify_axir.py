import pathlib, shutil, re
from pathlib import Path
inv_dir = Path("axiomos/reports"); inv_dir.mkdir(parents=True, exist_ok=True)
canonical = Path("axiomos/canonical"); canonical.mkdir(parents=True, exist_ok=True)
candidates = Path("axiomos/candidates"); candidates.mkdir(parents=True, exist_ok=True)
deprecated = Path("axiomos/deprecated"); deprecated.mkdir(parents=True, exist_ok=True)

# copie brute selon nom
for p in Path(".").rglob("*.axir.json"):
    name = p.name.lower()
    target = deprecated if re.search(r"(bak|backup|fixed)", name) else candidates
    dest = target / p.name
    if p.resolve() != dest.resolve():
        dest.write_bytes(p.read_bytes())

# picks = échantillon minimal (ajuste la liste si besoin)
PICKS = ["vector_add", "saxpy", "matmul_", "softmax2d", "layernorm2d"]
for p in candidates.glob("*.axir.json"):
    if any(k in p.name.lower() for k in PICKS):
        (canonical / p.name).write_bytes(p.read_bytes())
print("Classified → canonical / candidates / deprecated")
