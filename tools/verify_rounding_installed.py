'''Run with installed Python -I outside the checkout.'''
import importlib.util,json,sys
from pathlib import Path
root=Path(sys.argv[1]).resolve()
from submodlab.rounding import rounding_audit
origins={}
for name in ['submodlab','submodlab.core','submodlab.cli','submodlab.__main__','submodlab.rounding','submodlab.rounding_cli']:
    p=Path(importlib.util.find_spec(name).origin).resolve();assert root not in p.parents,(name,p);origins[name]=str(p)
for c in json.loads((root/'docs/rounding-audits.json').read_text()):assert rounding_audit(c['report']['spec'])==c['report'],c['name']
print(json.dumps({'rounding_cases':21,'module_origins':origins}))
