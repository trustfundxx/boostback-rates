import json, sys, datetime
f, src = sys.argv[1], sys.argv[2]
d = json.load(open(f)); P = d['programs']; S = d['stores']
P['delta']['name'] = 'Delta SkyMiles Shopping'
air = {'delta': ('Delta SkyMiles Shopping', 1.3, 'mile'), 'american': ('American AAdvantage eShopping', 1.5, 'mile'),
       'united': ('United MileagePlus Shopping', 1.3, 'mile'), 'southwest': ('Southwest Rapid Rewards Shopping', 1.3, 'point'),
       'alaska': ('Alaska Airlines Shopping', 1.5, 'mile')}
for k, (n, _, _) in air.items(): P[k] = {'name': n, 'type': 'miles', 'connection': 'none'}
portal = {'rakuten':'rakuten','topcashback':'topcash','befrugal':'befrugal','gocashback':'gocashback','goodshop':'goodshop',
          'rebatesme':'rebatesme','pricecom':'pricecom','extrabux':'extrabux'}
refresh_keys = set(portal.values()) | set(air)
missing = []
for line in open(src):
    line = line.strip()
    if not line: continue
    name, kv = line.split('|', 1)
    if name not in S: missing.append(name); continue
    fresh = {}; cap = None
    for pair in kv.split(';'):
        k, v = pair.split('=')
        if k == 'capitalone' and not v: cap = 'none'; continue
        if not v or '$' in v: continue
        up = v.startswith('u'); x = float(v.lstrip('u'))
        if k == 'capitalone':
            if x < 0.5: cap = 'none'; continue
            note = f"Up to {x:g}% — varies by category or new customers" if up else ("Often a new-customer or limited-time rate" if x >= 12 else "")
            old = S[name].get('cap1', {})
            cap = {'base': x, 'note': note}
            if old.get('boost', 0) > x:  # keep the targeted-offer boost only if it beats the posted rate
                cap['boost'] = old['boost']; cap['boostNote'] = old.get('boostNote', '')
            continue
        if k in air:
            if x <= 0: continue
            n, cents, unit = air[k]
            fresh[k] = {'base': round(x * cents, 2), 'note': f"{x:g} {unit}{'s' if x != 1 else ''}/$1, valued ~{cents:g}¢ each"}
        else:
            if x < 0.5: continue
            if up: note = f"Up to {x:g}% — varies by category or new customers"
            elif x >= 12: note = "Often a new-customer or limited-time rate"
            else: note = ""
            fresh[portal[k]] = {'base': x, 'note': note}
    if cap == 'none': S[name].pop('cap1', None)
    elif cap: S[name]['cap1'] = cap
    if not fresh: continue
    kept = {k: v for k, v in S[name].items() if k not in refresh_keys}
    S[name] = {**fresh, **kept}
d['generated_at'] = datetime.datetime.utcnow().isoformat() + 'Z'
json.dump(d, open(f, 'w'), indent=1, ensure_ascii=False)
withair = sum(1 for e in S.values() if any(k in e for k in air))
print('stores', len(S), '| with airline rates', withair, '| missing names', missing)
