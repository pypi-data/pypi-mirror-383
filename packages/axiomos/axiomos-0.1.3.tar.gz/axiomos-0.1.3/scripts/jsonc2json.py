import sys, json, re, pathlib
def strip_jsonc(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    s = re.sub(r"(?m)^\s*//.*?$", "", s)
    s = re.sub(r"(?m)(?<!:)//.*?$", "", s)
    return s
inp = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2]) if len(sys.argv)>2 else inp.with_suffix("")
out = out if out.suffix == ".json" else out.with_suffix(".json")
data = json.loads(strip_jsonc(inp.read_text(encoding="utf-8")))
out.write_text(json.dumps(data, indent=2), encoding="utf-8")
print(f"Wrote {out}")
