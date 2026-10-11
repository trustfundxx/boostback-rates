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

# show the date the rates were last refreshed
h = open(p, encoding="utf-8").read()
if "updated ' +" in h:
    print("Date update already in. OK")
else:
    a = """    const ageHrs = (Date.now() - new Date(json.generated_at)) / 3600000;
    document.getElementById('freshness').textContent = 'Estimated rates';"""
    b = """    const upd = new Date(json.generated_at);
    document.getElementById('freshness').textContent = isNaN(upd) ? 'Estimated rates' : 'Estimated rates · updated ' + upd.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });"""
    if h.count(a) == 1:
        open(p, "w", encoding="utf-8").write(h.replace(a, b, 1))
        print("Date update added. OK")
    else:
        print("Date update: could not find the spot. Nothing changed.")

# wording: "Today's posted rates · updated <date>" (label can be changed later from rates.json), clearer disclaimer
h = open(p, encoding="utf-8").read()
if "json.label" in h:
    print("Wording update already in. OK")
else:
    sw = [
      ("""document.getElementById('freshness').textContent = isNaN(upd) ? 'Estimated rates' : 'Estimated rates · updated ' + upd.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });""",
       """const lbl = json.label || "Today's posted rates";
    document.getElementById('freshness').textContent = isNaN(upd) ? lbl : lbl + ' · updated ' + upd.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });"""),
      ("""    document.getElementById('freshness').textContent = 'Estimated rates';""",
       """    document.getElementById('freshness').textContent = 'Posted rates';"""),
      ("""Rates are estimates, not live, and can change daily. Confirm the rate on the program's own site before you buy.""",
       """Rates are checked every morning from what each program posts and can change during the day. Confirm the rate on the program's own site before you buy."""),
    ]
    bad = [a[:50] for a, b in sw if h.count(a) != 1]
    if bad:
        print("Wording update: could not find the spot. Nothing changed.", bad)
    else:
        for a, b in sw: h = h.replace(a, b, 1)
        open(p, "w", encoding="utf-8").write(h)
        print("Wording update added. OK")
        x = home + "/ios/App/App.xcodeproj/project.pbxproj"
        t = open(x).read()
        t = re.sub(r"CURRENT_PROJECT_VERSION = (\d+);", lambda m: "CURRENT_PROJECT_VERSION = %d;" % (int(m.group(1)) + 1), t)
        t = t.replace("MARKETING_VERSION = 1.1;", "MARKETING_VERSION = 1.2;")
        open(x, "w").write(t)
        print("iOS:", sorted(set(re.findall(r"MARKETING_VERSION = [^;]+;|CURRENT_PROJECT_VERSION = \d+;", t))))
        g = home + "/android/app/build.gradle"
        t = open(g).read()
        t = re.sub(r"versionCode (\d+)", lambda m: "versionCode %d" % (int(m.group(1)) + 1), t, count=1)
        t = t.replace('versionName "1.1"', 'versionName "1.2"')
        open(g, "w").write(t)
        print("Android:", re.findall(r'versionCode \d+|versionName "[^"]+"', t))

# 1.3: a button on every program that opens that store's page in that program (links come from rates.json)
h = open(p, encoding="utf-8").read()
if "function linkFor(" in h:
    print("Link buttons already in. OK")
else:
    sw = [
      ("""  .winner-note{margin-top:14px; font-size:12.5px; line-height:1.5; color:var(--paper-dim);}""",
       """  .winner-note{margin-top:14px; font-size:12.5px; line-height:1.5; color:var(--paper-dim);}
  .go-btn{display:block; margin-top:16px; background:var(--gold); color:var(--ink); text-align:center;
    padding:12px 14px; font-size:15px; font-weight:600; text-decoration:none; border-radius:3px;}
  .go-link{display:inline-block; margin-top:4px; font-size:12.5px; color:var(--gold-deep);
    font-weight:600; text-decoration:none;}"""),
      ("""        <p class="winner-note" id="winnerNote"></p>""",
       """        <p class="winner-note" id="winnerNote"></p>
        <a class="go-btn" id="winnerGo" href="#" style="display:none;"></a>"""),
      ("""async function loadRates(){""",
       """let DOMAINS = {};
function linkFor(store, id){
  const e = (DATA[store] || {})[id] || {};
  const p = PROGRAMS[id] || {};
  if(e.url) return e.url;
  const dm = DOMAINS[store];
  if(p.storeUrl && (dm || p.storeUrl.indexOf('{domain}') < 0))
    return p.storeUrl.replace('{domain}', dm || '').replace('{q}', encodeURIComponent(store));
  return p.home || '';
}
async function loadRates(){"""),
      ("""    DATA = json.stores;\n""",
       """    DATA = json.stores;\n    DOMAINS = json.domains || {};\n"""),
      ("""  document.getElementById('winnerNote').textContent = winner.note || '';""",
       """  document.getElementById('winnerNote').textContent = winner.note || '';
  const wGo = document.getElementById('winnerGo');
  const wUrl = linkFor(currentStore, winner.id);
  wGo.href = wUrl || '#';
  wGo.textContent = 'Go to ' + winner.name + ' ›';
  wGo.style.display = wUrl ? 'block' : 'none';"""),
      ("""          ${r.note ? `<div class="note">${r.note}</div>` : ''}
        </div>""",
       """          ${r.note ? `<div class="note">${r.note}</div>` : ''}
          ${linkFor(currentStore, r.id) ? `<a class="go-link" href="${linkFor(currentStore, r.id)}">Go to ${r.name} ›</a>` : ''}
        </div>"""),
    ]
    bad = [a[:50] for a, b in sw if h.count(a) != 1]
    if bad:
        print("Link buttons: could not find the spot. Nothing changed.", bad)
    else:
        for a, b in sw: h = h.replace(a, b, 1)
        open(p, "w", encoding="utf-8").write(h)
        print("Link buttons added. OK")
        x = home + "/ios/App/App.xcodeproj/project.pbxproj"
        t = open(x).read()
        t = re.sub(r"CURRENT_PROJECT_VERSION = (\d+);", lambda m: "CURRENT_PROJECT_VERSION = %d;" % (int(m.group(1)) + 1), t)
        t = t.replace("MARKETING_VERSION = 1.2;", "MARKETING_VERSION = 1.3;")
        open(x, "w").write(t)
        print("iOS:", sorted(set(re.findall(r"MARKETING_VERSION = [^;]+;|CURRENT_PROJECT_VERSION = \d+;", t))))
        g = home + "/android/app/build.gradle"
        t = open(g).read()
        t = re.sub(r"versionCode (\d+)", lambda m: "versionCode %d" % (int(m.group(1)) + 1), t, count=1)
        t = t.replace('versionName "1.2"', 'versionName "1.3"')
        open(g, "w").write(t)
        print("Android:", re.findall(r'versionCode \d+|versionName "[^"]+"', t))

# 1.3 (part 2): real coupon codes and "New to X? Sign up" links, both read from rates.json
h = open(p, encoding="utf-8").read()
if "json.coupons" in h:
    print("Coupons + sign-up links already in. OK")
else:
    sw = [
      ("""  .coupon-desc{font-size:12.5px; color:#5a5648; margin:8px 0 0;}""",
       """  .coupon-desc{font-size:12.5px; color:#5a5648; margin:8px 0 0;}
  .coupon-item{padding:10px 0; border-top:1px dashed var(--line);}
  .coupon-item:first-of-type{border-top:none; padding-top:2px;}
  .coupon-exp{font-size:11px; color:#a39d8c; margin-top:3px;}
  .join-link{display:inline-block; margin-top:3px; font-size:12px; color:#5a5648; text-decoration:underline;}
  .winner-card .join-link{display:block; text-align:center; margin-top:10px; color:var(--paper-dim);}"""),
      ("""        <a class="go-btn" id="winnerGo" href="#" style="display:none;"></a>""",
       """        <a class="go-btn" id="winnerGo" href="#" style="display:none;"></a>
        <a class="join-link" id="winnerJoin" href="#" style="display:none;"></a>"""),
      ("""let DOMAINS = {};""",
       """let DOMAINS = {};
let LIVE_COUPONS = {};
function esc(s){ return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function joinFor(id){ const s = (PROGRAMS[id] || {}).signup; return s && s.url ? s : null; }
function copyCode(btn, code){
  try { if(navigator.clipboard) navigator.clipboard.writeText(code).catch(function(){}); } catch(e){}
  btn.textContent = 'COPIED';
  setTimeout(function(){ btn.textContent = 'COPY'; }, 1200);
}"""),
      ("""    DOMAINS = json.domains || {};\n""",
       """    DOMAINS = json.domains || {};\n    LIVE_COUPONS = json.coupons || {};\n"""),
      ("""  wGo.style.display = wUrl ? 'block' : 'none';""",
       """  wGo.style.display = wUrl ? 'block' : 'none';
  const wJoin = document.getElementById('winnerJoin');
  const wj = joinFor(winner.id);
  wJoin.href = wj ? wj.url : '#';
  wJoin.textContent = wj ? (wj.label || ('New to ' + winner.name + '? Sign up here ›')) : '';
  wJoin.style.display = wj ? 'block' : 'none';"""),
      ("""          ${linkFor(currentStore, r.id) ? `<a class="go-link" href="${linkFor(currentStore, r.id)}">Go to ${r.name} ›</a>` : ''}""",
       """          ${linkFor(currentStore, r.id) ? `<a class="go-link" href="${linkFor(currentStore, r.id)}">Go to ${r.name} ›</a>` : ''}
          ${joinFor(r.id) ? `<br><a class="join-link" href="${esc(joinFor(r.id).url)}">${esc(joinFor(r.id).label || ('New to ' + r.name + '? Sign up here ›'))}</a>` : ''}"""),
      ("""  const coupon = SHOW_DEALS ? COUPONS[currentStore] : null;
  const couponCard = document.getElementById('couponCard');
  if(coupon){
    document.getElementById('couponCode').textContent = coupon.code;
    document.getElementById('couponDesc').textContent = coupon.desc;
    couponCard.style.display = 'block';
  } else {
    couponCard.style.display = 'none';
  }""",
       """  const codes = (LIVE_COUPONS[currentStore] || []).filter(c => c && c.code).slice(0, 3);
  const couponCard = document.getElementById('couponCard');
  if(codes.length){
    couponCard.innerHTML = `<div class="coupon-label">COUPON CODES</div>` + codes.map(c => {
      const code = String(c.code).replace(/[^A-Za-z0-9_-]/g, '');
      return `<div class="coupon-item">
        <div class="coupon-row">
          <div class="coupon-code">${code}</div>
          <button class="coupon-copy" onclick="copyCode(this,'${code}')">COPY</button>
        </div>
        ${c.desc ? `<p class="coupon-desc">${esc(c.desc)}</p>` : ''}
        ${c.exp ? `<div class="coupon-exp">${esc(c.exp)}</div>` : ''}
      </div>`;
    }).join('') + `<p class="coupon-exp" style="margin-top:8px;">Codes found this morning. Some only work on certain items or for store members.</p>`;
    couponCard.style.display = 'block';
  } else {
    couponCard.style.display = 'none';
  }"""),
    ]
    bad = [a[:50] for a, b in sw if h.count(a) != 1]
    if bad:
        print("Coupons + sign-up links: could not find the spot. Nothing changed.", bad)
    else:
        for a, b in sw: h = h.replace(a, b, 1)
        open(p, "w", encoding="utf-8").write(h)
        print("Coupons + sign-up links added. OK")

# 1.3 (part 3): partner deal card (e.g. Hooga Health) read from rates.json "partners"
h = open(p, encoding="utf-8").read()
if "partnerBox" in h:
    print("Partner deals already in. OK")
else:
    sw = [
      ("""  .coupon-exp{font-size:11px; color:#a39d8c; margin-top:3px;}""",
       """  .coupon-exp{font-size:11px; color:#a39d8c; margin-top:3px;}
  .partner-card{border-style:solid; border-color:var(--gold); margin-bottom:6px;}
  .partner-name{font-family:var(--font-display); font-size:19px; color:var(--ink); margin:2px 0 4px;}
  .partner-card .go-btn{margin-top:12px;}"""),
      ("""    <div class="empty-state" id="notCovered" style="display:none;">""",
       """    <div id="partnerBox"></div>

    <div class="empty-state" id="notCovered" style="display:none;">"""),
      ("""    LIVE_COUPONS = json.coupons || {};\n""",
       """    LIVE_COUPONS = json.coupons || {};\n    PARTNERS = (json.partners || []).filter(x => x && x.name && x.url);\n    renderPartners();\n"""),
      ("""let LIVE_COUPONS = {};""",
       """let LIVE_COUPONS = {};
let PARTNERS = [];
function renderPartners(){
  const box = document.getElementById('partnerBox');
  if(!box) return;
  box.innerHTML = PARTNERS.map(x => {
    const code = x.code ? String(x.code).replace(/[^A-Za-z0-9_-]/g, '') : '';
    return `<div class="coupon-card partner-card">
      <div class="coupon-label">${esc(x.label || 'PARTNER DEAL')}</div>
      <div class="partner-name">${esc(x.name)}</div>
      ${x.desc ? `<p class="coupon-desc" style="margin-top:0;">${esc(x.desc)}</p>` : ''}
      ${code ? `<div class="coupon-row" style="margin-top:10px;"><div class="coupon-code">${code}</div><button class="coupon-copy" onclick="copyCode(this,'${code}')">COPY</button></div>` : ''}
      <a class="go-btn" href="${esc(x.url)}">${esc(x.button || ('Shop ' + x.name + ' ›'))}</a>
      <div class="coupon-exp" style="margin-top:8px;">Boost Back may earn a commission from this partner.</div>
    </div>`;
  }).join('');
}"""),
      ("""  if(match){ selectStore(match); return; }
  showNotCovered(q);""",
       """  if(match){ selectStore(match); return; }
  const pm = PARTNERS.find(x => norm(x.name).includes(nq) || nq.includes(norm(x.name)));
  if(pm){
    currentStore = null;
    document.getElementById('suggestions').classList.remove('open');
    document.getElementById('result').style.display = 'none';
    document.getElementById('notCovered').style.display = 'none';
    document.getElementById('emptyState').style.display = 'none';
    input.blur();
    document.getElementById('partnerBox').scrollIntoView({behavior:'smooth', block:'center'});
    return;
  }
  showNotCovered(q);"""),
    ]
    bad = [a[:50] for a, b in sw if h.count(a) != 1]
    if bad:
        print("Partner deals: could not find the spot. Nothing changed.", bad)
    else:
        for a, b in sw: h = h.replace(a, b, 1)
        open(p, "w", encoding="utf-8").write(h)
        print("Partner deals added. OK")
