#!/usr/bin/env python3
import argparse,csv,html,os,sys
def main():
    ap=argparse.ArgumentParser(description="Convert AXIR CSV bench → HTML table")
    ap.add_argument("--csv",required=True,help="Input CSV (e.g., build/axir_gemm_bench.csv)")
    ap.add_argument("--out",default=None,help="Output HTML (default: same dir, .html)")
    a=ap.parse_args()
    if not os.path.exists(a.csv): sys.exit(f"CSV not found: {a.csv}")
    rows=[]
    with open(a.csv,newline="",encoding="utf-8") as f:
        for r in csv.reader(f): rows.append([html.escape(c) for c in r])
    if not rows: sys.exit("Empty CSV.")
    head,body=rows[0],rows[1:]
    out=a.out or os.path.splitext(a.csv)[0]+".html"
    css="table{border-collapse:collapse;font-family:ui-sans-serif,system-ui}th,td{border:1px solid #ddd;padding:8px}th{background:#f6f6f6;text-align:left}caption{font-weight:600;margin:8px 0}"
    html_doc=f"""<!doctype html><meta charset="utf-8"><title>AXIR Bench</title>
<style>{css}</style>
<table><caption>AXIR GEMM Bench</caption>
<thead><tr>{''.join(f'<th>{c}</th>' for c in head)}</tr></thead>
<tbody>
{''.join('<tr>'+''.join(f'<td>{c}</td>' for c in row)+'</tr>' for row in body)}
</tbody></table>"""
    with open(out,"w",encoding="utf-8") as f: f.write(html_doc)
    print(f"[bench_to_html] wrote: {out}")
if __name__=="__main__": main()
