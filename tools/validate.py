# Checks rates.json before it is published. Exits non-zero if anything looks wrong.
import json, sys, subprocess
d = json.load(open('rates.json'))
P, S = d['programs'], d['stores']
prev = json.loads(subprocess.run(['git', 'show', 'HEAD:rates.json'], capture_output=True, text=True).stdout or '{"stores":{}}')
problems = []
if len(S) < len(prev.get('stores', {})): problems.append(f"store count dropped {len(prev['stores'])} -> {len(S)}")
for n, e in S.items():
    if not e: problems.append(f"{n}: no programs")
    for k, v in e.items():
        if k not in P: problems.append(f"{n}: unknown program {k}")
        b = v.get('base', v.get('boost'))
        if b is None or not (0 <= b <= 60): problems.append(f"{n}/{k}: odd value {b}")
    if not any(P[k]['connection'] != 'full' for k in e if k in P): problems.append(f"{n}: nothing usable")
for f in d.get('featured', []):
    if f not in S: problems.append(f"featured store missing: {f}")
print('OK' if not problems else '\n'.join(problems)); sys.exit(1 if problems else 0)
