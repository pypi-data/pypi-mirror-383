import json, sys

# usage: python scripts/export_softmax2d.py M N OUT.axir.json
if len(sys.argv) != 4:
    print("usage: python scripts/export_softmax2d.py M N OUT.axir.json"); sys.exit(2)

M = int(sys.argv[1]); N = int(sys.argv[2]); out = sys.argv[3]

d = {
  "version": "0.1.1",
  "meta": {"source_lang":"AXIR"},
  "types": {
    "scalars": {
      "M": {"dtype":"i32","value": M},
      "N": {"dtype":"i32","value": N}
    }
  },
  "buffers": {
    "hX": {"role":"host","dtype":"float32","size":"M*N"},
    "hC": {"role":"host","dtype":"float32","size":"M*N"}
  },
  "ops": [
    {"op":"HostMake","name":"hX","dtype":"float32","shape":["M","N"],"fill":"ones"},
    {"op":"HostMake","name":"hC","dtype":"float32","shape":["M","N"],"fill":"zeros"},
    {"op":"DeviceMallocLike","dst":"&dX","like":"hX"},
    {"op":"DeviceMallocLike","dst":"&dY","like":"hC"},
    {"op":"Memcpy","dst":"dX","src":"hX","kind":"H2D"},
    {
      "op":"KernelLaunch",
      "kernel":"softmax2d_row",
      "grid":["M",1,1],
      "block":[1,1,1],
      "args":["&dX","&dY","M","N"]
    },
    {"op":"Memcpy","dst":"hC","src":"dY","kind":"D2H"}
  ]
}

with open(out, "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2)
print("WROTE", out)
