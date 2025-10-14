import sys
import os
import json
import numpy as np

def main():
    print("🧩 AXIOMOS — PyTorch → AXIR (minimal)")

    # Torch optional
    try:
        import torch
    except Exception as e:
        print("❌ PyTorch not installed. Install with: pip install torch")
        sys.exit(1)

    # Tiny example: 1×3 softmax
    x = torch.tensor([[1.0, 2.0, 3.0]], dtype=torch.float32)
    y = torch.softmax(x, dim=1).detach().cpu().numpy().astype(np.float32)

    graph = {
        "name": "pytorch_softmax_demo",
        "buffers": {
            "hX": {"shape": [1, 3], "data": x.numpy().astype(np.float32).tolist()},
            "hY": {"shape": [1, 3], "data": y.tolist()}
        },
        "ops": [
            {"op": "softmax2d", "x": "hX", "out": "hY"}
        ]
    }

    out_dir = os.path.join(os.getcwd(), "examples")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "pytorch_softmax.axir.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    print(f"✅ Wrote: {out_path}")
    print("Run verification:")
    print("  python -m axiomos.verify examples\\pytorch_softmax.axir.json --buffer hY --backend-a cpu --backend-b opencl --seed 0")

if __name__ == "__main__":
    main()
