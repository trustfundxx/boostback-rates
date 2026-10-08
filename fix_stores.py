# Boost Back: load store rates from GitHub, show 12 featured chips, fix store names with apostrophes,
# and bump the app version for the store update.
import os, re
home = os.path.expanduser("~/tally-native")
p = home + "/www/index.html"
h = open(p, encoding="utf-8").read()
if "RATES_URL" in h:
    print("Store update already in. OK")
else:
    swaps = [
      ("let storeNames = Object.keys(DATA);",
       "let storeNames = Object.keys(DATA);\nconst RATES_URL = 'https://raw.githubusercontent.com/trustfundxx/boostback-rates/main/rates.json';\nlet FEATURED = [];"),
      ("""    const res = await fetch('rates.json', { cache: 'no-store' });
    if(!res.ok) throw new Error('rates.json not found');
    const json = await res.json();
    PROGRAMS = json.programs;
    DATA = json.stores;
    storeNames = Object.keys(DATA);""",
       """    let json = null;
    try {
      const r = await fetch(RATES_URL, { cache: 'no-store' });
      if(r.ok) json = await r.json();
    } catch(e){}
    if(!json){
      const res = await fetch('rates.json', { cache: 'no-store' });
      if(!res.ok) throw new Error('rates.json not found');
      json = await res.json();
    }
    PROGRAMS = json.programs;
    DATA = json.stores;
    storeNames = Object.keys(DATA);
    FEATURED = (json.featured || []).filter(s => DATA[s]);"""),
      ("""  document.getElementById('chips').innerHTML = storeNames.map(s =>
    `<button onclick="selectStore('${s}')">${s}</button>`).join('');""",
       """  const list = FEATURED.length ? FEATURED : storeNames.slice(0, 12);
  document.getElementById('chips').innerHTML = list.map(s =>
    `<button onclick="selectStore(storeNames[${storeNames.indexOf(s)}])">${s}</button>`).join('');"""),
      ("""box.innerHTML = matches.map(s => `<button onclick="selectStore('${s}')">${s}</button>`).join('');""",
       """box.innerHTML = matches.map(s => `<button onclick="selectStore(storeNames[${storeNames.indexOf(s)}])">${s}</button>`).join('');"""),
    ]
    missing = [a[:50] for a, b in swaps if h.count(a) != 1]
    if missing:
        print("Could not find the spot. Nothing changed.", missing)
        raise SystemExit(1)
    open(p + ".bak4", "w", encoding="utf-8").write(h)
    for a, b in swaps:
        h = h.replace(a, b, 1)
    open(p, "w", encoding="utf-8").write(h)
    print("Store update added. OK")
    bump = True

if "bump" in dir():
    x = home + "/ios/App/App.xcodeproj/project.pbxproj"
    t = open(x).read()
    t = re.sub(r"CURRENT_PROJECT_VERSION = (\d+);", lambda m: "CURRENT_PROJECT_VERSION = %d;" % (int(m.group(1)) + 1), t)
    t = t.replace("MARKETING_VERSION = 1.0;", "MARKETING_VERSION = 1.1;")
    open(x, "w").write(t)
    print("iOS:", sorted(set(re.findall(r"MARKETING_VERSION = [^;]+;|CURRENT_PROJECT_VERSION = \d+;", t))))
    g = home + "/android/app/build.gradle"
    t = open(g).read()
    t = re.sub(r"versionCode (\d+)", lambda m: "versionCode %d" % (int(m.group(1)) + 1), t, count=1)
    t = t.replace('versionName "1.0"', 'versionName "1.1"')
    open(g, "w").write(t)
    print("Android:", re.findall(r'versionCode \d+|versionName "[^"]+"', t))

# search that ignores apostrophes, accents and spaces (kiehls -> Kiehl's, estee -> Estée)
h = open(p, encoding="utf-8").read()
if "function norm(" in h:
    print("Search update already in. OK")
else:
    sw = [
      ("const RATES_URL", "function norm(s){ return String(s).normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]/g,''); }\nconst RATES_URL"),
      ("const matches = storeNames.filter(s => s.toLowerCase().includes(q));",
       "const nq = norm(q);\n  const matches = nq ? storeNames.filter(s => norm(s).includes(nq)) : [];"),
      ("""  const match = storeNames.find(s => s.toLowerCase() === q.toLowerCase())
    || storeNames.find(s => s.toLowerCase().includes(q.toLowerCase()));""",
       """  const nq = norm(q);
  const match = storeNames.find(s => norm(s) === nq)
    || (nq ? storeNames.find(s => norm(s).includes(nq)) : null);"""),
    ]
    bad = [a[:40] for a, b in sw if h.count(a) != 1]
    if bad:
        print("Search update: could not find the spot. Nothing changed.", bad)
    else:
        for a, b in sw: h = h.replace(a, b, 1)
        open(p, "w", encoding="utf-8").write(h)
        print("Search update added. OK")
