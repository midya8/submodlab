'''Separate CLI; original audit contract unchanged.'''
import argparse,json,sys
from pathlib import Path
from .cli import strict
from .rounding import rounding_audit

def main():
    p=argparse.ArgumentParser(description='Exact finite multilinear expectation and deterministic cardinality rounding');p.add_argument('--spec',required=True);p.add_argument('--json',required=True);a=p.parse_args()
    try:
        b=Path(a.spec).read_bytes()
        if len(b)>32768:raise ValueError('Input limit 32KiB')
        s=json.loads(b,object_pairs_hook=strict,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('Nonfinite JSON token')));r=rounding_audit(s);Path(a.json).write_text(json.dumps(r,indent=2)+'\n');print('rounding allowed' if r['rounding_allowed'] else 'rounding withheld');return 0
    except (ValueError,OSError) as e:print('ERROR '+str(e),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
