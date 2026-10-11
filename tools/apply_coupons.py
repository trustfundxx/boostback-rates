# python3 tools/apply_coupons.py rates.json <coupons.json>
# coupons.json: {"Store": [{"code","desc","exp"?}, ...]} for every store whose page LOADED today.
# A store listed with [] has its codes removed; stores not listed keep yesterday's codes.
import json, sys
f, src = sys.argv[1], sys.argv[2]
d = json.load(open(f)); new = json.load(open(src)); C = d.setdefault('coupons', {})
for store, codes in new.items():
    if store not in d['stores']: continue
    codes = [c for c in codes if c.get('code')][:3]
    if codes: C[store] = codes
    else: C.pop(store, None)
json.dump(d, open(f, 'w'), indent=1, ensure_ascii=False)
print('stores with coupons:', len(C))
