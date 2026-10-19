# python3 tools/apply_coupons.py rates.json <coupons.json>
# coupons.json: {"Store": [{"code","desc","exp"?}, ...]} for every store whose page LOADED today.
# A store listed with [] has its codes removed; stores not listed keep yesterday's codes.
# A store from tools/new_stores.json that has no posted rate yet goes live as soon as it has a coupon code
# (shown with the Fetch receipt-scan row); it then stays, and its rates appear once a program posts one.
import json, sys, os
f, src = sys.argv[1], sys.argv[2]
d = json.load(open(f)); new = json.load(open(src)); C = d.setdefault('coupons', {})
NEWF = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'new_stores.json')
NEW = set(json.load(open(NEWF))) if os.path.exists(NEWF) else set()
FETCH_ROW = {'base': 0, 'flat': 0.025, 'note': 'Scan any receipt for at least 25 points (about 3¢). Bigger offers show in the Fetch app.'}
added = []
for store, codes in new.items():
    codes = [c for c in codes if c.get('code')][:3]
    if store not in d['stores'] and store in NEW and codes:
        d['stores'][store] = {'fetch': dict(FETCH_ROW)}; added.append(store)
    if store not in d['stores']: continue
    if codes: C[store] = codes
    else: C.pop(store, None)
json.dump(d, open(f, 'w'), indent=1, ensure_ascii=False)
print('stores with coupons:', len(C), '| new stores live via coupons:', added)
