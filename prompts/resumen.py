"""Resume resultados.json de promptfoo: tasa de aprobación por versión y aserciones que fallan por caso."""
import json, sys, re
from collections import defaultdict
d = json.load(open(sys.argv[1] + "/resultados.json", encoding="utf-8"))
por = defaultdict(dict)
for r in d["results"]["results"]:
    v = re.search(r"(v[\w.]+)\.txt", r["prompt"]["label"]).group(1)
    fallos = [c["assertion"].get("metric", c["assertion"]["type"]) for c in r["gradingResult"]["componentResults"] if not c["pass"]]
    por[v][r["vars"]["id"]] = fallos
for v, casos in por.items():
    ok = sum(1 for f in casos.values() if not f)
    print(f"{v}: {ok}/{len(casos)} ({100*ok/len(casos):.1f} %)")
    for i, f in casos.items():
        if f: print(f"   {i}: fallan {', '.join(sorted(set(f)))}")
