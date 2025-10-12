#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, sys, glob
from jsonschema.validators import Draft202012Validator  # <= IMPORTANT
from jsonschema.exceptions import ValidationError

SCHEMA = r".\tools\axir.schema.json"  # adapte le chemin si besoin

def load_json(path: str):
    # utf-8-sig => accepte (et retire) un éventuel BOM
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def main():
    try:
        schema = load_json(SCHEMA)
    except Exception as e:
        print(f"[ERR] schema: {e}")
        sys.exit(2)

    validator = Draft202012Validator(schema)

    files = glob.glob(r".\AXIR\*.axir.json")  # pas de (?i), on reste simple
    ok = 0; fail = 0
    for p in files:
        try:
            doc = load_json(p)
            # Option: ne valider que les fichiers “nouvelle spec”
            # if "version" not in doc: continue
            validator.validate(doc)
            print(f"[OK ] {p}")
            ok += 1
        except ValidationError as ve:
            print(f"[FAIL] {p}\n  - schema: {ve.message}")
            fail += 1
        except Exception as e:
            print(f"[ERR]  {p}: {e}")
            fail += 1
    print(f"\nRésumé: OK={ok}  FAIL={fail}")
    sys.exit(1 if fail else 0)

if __name__ == "__main__":
    main()
