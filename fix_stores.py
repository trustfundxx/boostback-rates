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

# 1.4: search by product -> cheapest price after cashback at Walmart, Target, Amazon, Ulta, CVS, Walgreens
h = open(p, encoding="utf-8").read()
if "PRICES_URL" in h:
    print("Product search already in. OK")
else:
    sw = [
      ("""  .suggestions{""",
       """  .mode-toggle{display:flex; gap:6px; margin-bottom:8px;}
  .mode-toggle button{flex:1; padding:8px 0; font-size:13px; letter-spacing:0.3px; font-family:var(--font-body);
    background:transparent; border:1.5px solid var(--ink); color:var(--ink); border-radius:2px; cursor:pointer;}
  .mode-toggle button.on{background:var(--ink); color:var(--paper);}
  .price-row{display:flex; justify-content:space-between; align-items:flex-start; gap:10px; padding:13px 0; border-bottom:1px solid var(--line);}
  .price-row .t{font-size:12px; color:#8a8577; margin-top:2px;}
  .price-row .v{font-family:var(--font-mono); font-size:15px; color:var(--sage); white-space:nowrap; text-align:right;}
  .price-row .v small{display:block; font-size:11px; color:#a39d8c; font-family:var(--font-body);}
  .suggestions{"""),
      ("""    <div class="search-wrap">
      <div class="search-box">""",
       """    <div class="search-wrap">
      <div class="mode-toggle">
        <button id="modeStores" class="on" onclick="setMode('stores')">Stores</button>
        <button id="modeProducts" onclick="setMode('products')">Products</button>
      </div>
      <div class="search-box">"""),
      ("""    <div id="result" style="display:none;">""",
       """    <div id="productResult" style="display:none;"></div>

    <div id="result" style="display:none;">"""),
      ("""const input = document.getElementById('storeInput');
input.addEventListener('input', () => {
""",
       """const input = document.getElementById('storeInput');
input.addEventListener('input', () => {
  if(searchMode === 'products') return;
"""),
      ("""function handleSearch(){
  const q = input.value.trim();
  if(!q) return;""",
       """const PRICES_URL = 'https://boostback-prices.boostback.workers.dev/';
let searchMode = 'stores';
const STORE_SEARCH = {
  'Walmart': 'https://www.walmart.com/search?q=', 'Target': 'https://www.target.com/s?searchTerm=',
  'Amazon': 'https://www.amazon.com/s?k=', 'Ulta Beauty': 'https://www.ulta.com/search?search=',
  'CVS': 'https://www.cvs.com/search?searchTerm=', 'Walgreens': 'https://www.walgreens.com/search/results.jsp?Ntt=',
  'Sephora': 'https://www.sephora.com/search?keyword=', "Macy's": 'https://www.macys.com/shop/search?keyword=',
  'Nordstrom': 'https://www.nordstrom.com/sr?keyword=', 'Nordstrom Rack': 'https://www.nordstromrack.com/sr?keyword=',
  "Bloomingdale's": 'https://www.bloomingdales.com/shop/search?keyword='
};
function setMode(m){
  searchMode = m;
  document.getElementById('modeStores').classList.toggle('on', m === 'stores');
  document.getElementById('modeProducts').classList.toggle('on', m === 'products');
  input.placeholder = m === 'products' ? "What are you buying? (e.g. L'Oreal conditioner)" : 'Where are you shopping?';
  input.value = '';
  document.getElementById('suggestions').classList.remove('open');
  document.getElementById('chips').style.display = m === 'products' ? 'none' : '';
  document.getElementById('result').style.display = 'none';
  document.getElementById('notCovered').style.display = 'none';
  document.getElementById('productResult').style.display = 'none';
  document.getElementById('emptyState').style.display = m === 'products' ? 'none' : 'block';
  currentStore = null;
}
function bestReward(store){
  if(!DATA[store]) return null;
  const rows = buildRows(store).filter(r => !r.locked && r.value > 0).sort((a, b) => b.value - a.value);
  return rows[0] || null;
}
async function productSearch(q){
  if(PAYWALL_ENABLED && !hasProAccess){
    input.blur();
    rcReady.then(() => { if(hasProAccess) productSearch(q); else showPaywall(); });
    return;
  }
  const box = document.getElementById('productResult');
  document.getElementById('result').style.display = 'none';
  document.getElementById('notCovered').style.display = 'none';
  document.getElementById('emptyState').style.display = 'none';
  box.style.display = 'block';
  box.innerHTML = `<div class="empty-state"><p>Checking prices at Walmart, Target, Amazon, Ulta, Sephora, Macy's, Kohl's and more…</p></div>`;
  input.blur();
  let json = null;
  try {
    const r = await fetch(PRICES_URL + '?q=' + encodeURIComponent(q));
    if(r.ok) json = await r.json();
  } catch(e){}
  if(!json){ box.innerHTML = `<div class="empty-state"><p>Couldn't load prices right now. Try again in a minute.</p></div>`; return; }
  const known = {};
  storeNames.forEach(n => { known[norm(n)] = n; });
  Object.keys(STORE_SEARCH).forEach(n => { known[norm(n)] = known[norm(n)] || n; });
  const seen = {};
  const items = (json.results || []).map(x => ({ ...x, store: known[norm(x.store)] || null }))
    .filter(x => x.store && !seen[x.store] && (seen[x.store] = true)).map(x => {
    const rw = bestReward(x.store);
    const back = rw ? x.price * rw.value / 100 : 0;
    return { ...x, rw, back, net: x.price - back };
  }).sort((a, b) => a.net - b.net);
  if(!items.length){ box.innerHTML = `<div class="empty-state"><p>No prices found at these stores for "${esc(q)}". Try fewer words or the brand name.</p></div>`; return; }
  const w = items[0];
  const shop = x => (x.link && x.link.indexOf('google.') < 0) ? x.link : (STORE_SEARCH[x.store] ? STORE_SEARCH[x.store] + encodeURIComponent(x.title || q) : (DOMAINS[x.store] ? 'https://' + (DOMAINS[x.store].split('.').length > 2 ? '' : 'www.') + DOMAINS[x.store] : ''));
  const wGo = w.rw ? linkFor(w.store, w.rw.id) : '';
  box.innerHTML = `
    <div class="store-strip"><h2>${esc(q)}</h2></div>
    <div class="winner-card" style="margin-top:16px;">
      <div class="winner-name">${esc(w.store)}</div>
      <p class="winner-sub">${esc(w.title)}</p>
      <div class="winner-figures"><div>
        <div class="big">$${w.net.toFixed(2)}</div>
        <div class="label">AFTER CASHBACK${w.rw ? ' · $' + w.price.toFixed(2) + ' minus $' + w.back.toFixed(2) + ' from ' + esc(w.rw.name) : ''}</div>
      </div></div>
      ${wGo ? `<a class="go-btn" href="${wGo}">Go to ${esc(w.rw.name)} first ›</a>` : ''}
      ${shop(w) ? `<a class="join-link" href="${shop(w)}">See it at ${esc(w.store)} ›</a>` : ''}
    </div>
    <div class="rest-label">OTHER STORES, CHEAPEST FIRST</div>
    <div class="alt-list">${items.slice(1).map(x => `
      <div class="price-row">
        <div>
          <div class="name">${esc(x.store)}</div>
          <div class="t">${esc(x.title)}</div>
          ${x.rw ? `<a class="go-link" href="${linkFor(x.store, x.rw.id)}">Go to ${esc(x.rw.name)} ›</a>` : ''}
          ${shop(x) ? `<br><a class="join-link" href="${shop(x)}">See it at ${esc(x.store)} ›</a>` : ''}
        </div>
        <div class="v">$${x.net.toFixed(2)}<small>$${x.price.toFixed(2)}${x.rw ? ' − $' + x.back.toFixed(2) : ''}</small></div>
      </div>`).join('')}
    </div>
    <p class="disclaimer">Prices from Google Shopping, checked just now. Sizes and versions can differ between stores, so check the product name. Open the cashback program first, then shop, so the cashback counts.</p>`;
}

function handleSearch(){
  const q = input.value.trim();
  if(!q) return;
  if(searchMode === 'products'){ productSearch(q); return; }"""),
    ]
    bad = [a[:50] for a, b in sw if h.count(a) != 1]
    if bad:
        print("Product search: could not find the spot. Nothing changed.", bad)
    else:
        for a, b in sw: h = h.replace(a, b, 1)
        open(p, "w", encoding="utf-8").write(h)
        print("Product search added. OK")
        x = home + "/ios/App/App.xcodeproj/project.pbxproj"
        t = open(x).read()
        t = re.sub(r"CURRENT_PROJECT_VERSION = (\d+);", lambda m: "CURRENT_PROJECT_VERSION = %d;" % (int(m.group(1)) + 1), t)
        t = t.replace("MARKETING_VERSION = 1.3;", "MARKETING_VERSION = 1.4;")
        open(x, "w").write(t)
        print("iOS:", sorted(set(re.findall(r"MARKETING_VERSION = [^;]+;|CURRENT_PROJECT_VERSION = \d+;", t))))
        g = home + "/android/app/build.gradle"
        t = open(g).read()
        t = re.sub(r"versionCode (\d+)", lambda m: "versionCode %d" % (int(m.group(1)) + 1), t, count=1)
        t = t.replace('versionName "1.3"', 'versionName "1.4"')
        open(g, "w").write(t)
        print("Android:", re.findall(r'versionCode \d+|versionName "[^"]+"', t))

# 1.4 (part 2): flat-dollar rewards ("Get up to $35 back") shown as dollars, not percent
h = open(p, encoding="utf-8").read()
if "e.flat" in h:
    print("Dollar rewards already in. OK")
else:
    sw = [
      ("""function renderResult(){""",
       """function applyFlat(store, rows){
  const amount = Math.max(1, Number(document.getElementById('amountInput').value) || 100);
  rows.forEach(r => {
    const e = (DATA[store] || {})[r.id] || {};
    if(e.flat && !r.locked && !r.boosted){ r.value = e.flat / amount * 100; r.flat = e.flat; }
  });
  return rows;
}

function renderResult(){"""),
      ("""  const rows = buildRows(currentStore).sort((a,b) => {""",
       """  const rows = applyFlat(currentStore, buildRows(currentStore)).sort((a,b) => {"""),
      ("""  const rows = buildRows(store).filter(r => !r.locked && r.value > 0).sort((a, b) => b.value - a.value);""",
       """  const rows = buildRows(store).filter(r => !r.locked && r.value > 0 && !((DATA[store] || {})[r.id] || {}).flat).sort((a, b) => b.value - a.value);"""),
    ]
    bad = [a[:50] for a, b in sw if h.count(a) != 1]
    if bad:
        print("Dollar rewards: could not find the spot. Nothing changed.", bad)
    else:
        for a, b in sw: h = h.replace(a, b, 1)
        open(p, "w", encoding="utf-8").write(h)
        print("Dollar rewards added. OK")
        x = home + "/ios/App/App.xcodeproj/project.pbxproj"
        t = open(x).read()
        t = re.sub(r"CURRENT_PROJECT_VERSION = (\d+);", lambda m: "CURRENT_PROJECT_VERSION = %d;" % (int(m.group(1)) + 1), t)
        open(x, "w").write(t)
        print("iOS:", sorted(set(re.findall(r"MARKETING_VERSION = [^;]+;|CURRENT_PROJECT_VERSION = \d+;", t))))
        g = home + "/android/app/build.gradle"
        t = open(g).read()
        t = re.sub(r"versionCode (\d+)", lambda m: "versionCode %d" % (int(m.group(1)) + 1), t, count=1)
        open(g, "w").write(t)
        print("Android:", re.findall(r'versionCode \d+|versionName "[^"]+"', t))

# 1.5: iPhone fix - download the daily file and prices through the phone's own network layer when the web view can't
h = open(p, encoding="utf-8").read()
if "getJSON(" in h:
    print("iPhone download fix already in. OK")
else:
    sw = [
      ("""async function loadRates(){""",
       """const RATES_BACKUPS = [
  'https://cdn.jsdelivr.net/gh/trustfundxx/boostback-rates@main/rates.json',
  'https://boostback-prices.boostback.workers.dev/rates'
];
async function getJSON(url){
  // 1) normal web request
  try {
    const r = await fetch(url, { cache: 'no-store' });
    if(r.ok){ const j = await r.json(); if(j) return j; }
  } catch(e){}
  // 2) native request (works on iPhone where the web view is blocked)
  try {
    const H = window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.CapacitorHttp;
    if(H){
      const res = await H.get({ url: url, headers: { 'Accept': 'application/json' } });
      if(res && res.status >= 200 && res.status < 300){
        const d = typeof res.data === 'string' ? JSON.parse(res.data) : res.data;
        if(d) return d;
      }
    }
  } catch(e){}
  return null;
}
async function loadRates(){"""),
      ("""      const r = await fetch(RATES_URL, { cache: 'no-store' });
      if(r.ok) json = await r.json();""",
       """      json = await getJSON(RATES_URL);
      for(let i = 0; !json && i < RATES_BACKUPS.length; i++) json = await getJSON(RATES_BACKUPS[i]);"""),
      ("""    const r = await fetch(PRICES_URL + '?q=' + encodeURIComponent(q));
    if(r.ok) json = await r.json();""",
       """    json = await getJSON(PRICES_URL + '?q=' + encodeURIComponent(q));"""),
    ]
    bad = [a[:50] for a, b in sw if h.count(a) != 1]
    if bad:
        print("iPhone download fix: could not find the spot. Nothing changed.", bad)
    else:
        for a, b in sw: h = h.replace(a, b, 1)
        open(p, "w", encoding="utf-8").write(h)
        print("iPhone download fix added. OK")
        x = home + "/ios/App/App.xcodeproj/project.pbxproj"
        t = open(x).read()
        t = re.sub(r"CURRENT_PROJECT_VERSION = (\d+);", lambda m: "CURRENT_PROJECT_VERSION = %d;" % (int(m.group(1)) + 1), t)
        t = t.replace("MARKETING_VERSION = 1.4;", "MARKETING_VERSION = 1.5;")
        open(x, "w").write(t)
        print("iOS:", sorted(set(re.findall(r"MARKETING_VERSION = [^;]+;|CURRENT_PROJECT_VERSION = \d+;", t))))
        g = home + "/android/app/build.gradle"
        t = open(g).read()
        t = re.sub(r"versionCode (\d+)", lambda m: "versionCode %d" % (int(m.group(1)) + 1), t, count=1)
        t = t.replace('versionName "1.4"', 'versionName "1.5"')
        open(g, "w").write(t)
        print("Android:", re.findall(r'versionCode \d+|versionName "[^"]+"', t))

# 1.5 (part 2): ask for an App Store / Play Store review after a few store lookups (Apple/Google decide when to actually show it)
h = open(p, encoding="utf-8").read()
if "InAppReview" in h:
    print("Review prompt already in. OK")
else:
    sw = [
      ("""function selectStore(store){""",
       """function maybeAskForReview(){
  try {
    const n = (parseInt(localStorage.getItem('bb_lookups') || '0', 10) || 0) + 1;
    localStorage.setItem('bb_lookups', String(n));
    if([3, 20, 50].indexOf(n) < 0) return;
    const cap = window.Capacitor;
    if(!cap) return;
    const plug = (cap.Plugins && cap.Plugins.InAppReview) || (typeof cap.registerPlugin === 'function' ? cap.registerPlugin('InAppReview') : null);
    if(plug && plug.requestReview) setTimeout(() => { plug.requestReview().catch(() => {}); }, 1500);
  } catch(e){}
}

function selectStore(store){"""),
      ("""  document.getElementById('result').style.display = 'block';
  renderResult();""",
       """  document.getElementById('result').style.display = 'block';
  renderResult();
  maybeAskForReview();"""),
    ]
    bad = [a[:50] for a, b in sw if h.count(a) != 1]
    if bad:
        print("Review prompt: could not find the spot. Nothing changed.", bad)
    else:
        for a, b in sw: h = h.replace(a, b, 1)
        open(p, "w", encoding="utf-8").write(h)
        print("Review prompt added. OK")

# 1.5 (part 3): new prices on the paywall, $1.99/month and $14.99/year (must match App Store Connect / Play Console)
h = open(p, encoding="utf-8").read()
if "$1.99/mo" in h and "$14.99/y" in h:
    print("Prices already $1.99 / $14.99. OK")
elif h.count("$2.99/mo<") == 1 and h.count("$2.99/month") == 1 and h.count("$19.99/yr") == 1 and h.count("$19.99/year") == 1:
    h = (h.replace("$2.99/mo<", "$1.99/mo<").replace("$2.99/month", "$1.99/month")
          .replace("$19.99/yr", "$14.99/yr").replace("$19.99/year", "$14.99/year")
          .replace("Best value · Save 44%", "Best value · Save 37%"))
    open(p, "w", encoding="utf-8").write(h)
    print("Prices changed to $1.99/month and $14.99/year. OK")
else:
    print("Prices: could not find the spot. Nothing changed.")

# 1.6: Flights tab - cash fares from Google Flights + which points programs and cards can book each airline
h = open(p, encoding="utf-8").read()
if "flightSearch(" in h:
    print("Flights already in. OK")
else:
    sw = [
      ("""  .suggestions{""",
       """  .flight-form{display:none; gap:6px; flex-wrap:wrap; margin-bottom:8px;}
  .flight-form input{flex:1 1 40%; min-width:0; padding:11px 10px; font-size:15px; border:1.5px solid var(--ink); border-radius:2px;
    background:transparent; color:var(--ink); font-family:var(--font-body);}
  .flight-form label{flex:1 1 40%; font-size:11px; color:#8a8577; letter-spacing:0.3px;}
  .flight-form label input{display:block; width:100%; box-sizing:border-box; margin-top:3px;}
  .flight-form button{flex:1 1 100%; padding:12px 0; font-size:15px; background:var(--ink); color:var(--paper); border:none; border-radius:2px; cursor:pointer;}
  .pts{font-size:12px; color:#5d6b57; margin-top:4px; line-height:1.45;}
  .suggestions{"""),
      ("""        <button id="modeProducts" onclick="setMode('products')">Products</button>""",
       """        <button id="modeProducts" onclick="setMode('products')">Products</button>
        <button id="modeFlights" onclick="setMode('flights')">Flights</button>
      </div>
      <div class="flight-form" id="flightForm">
        <input id="fFrom" maxlength="3" placeholder="From (SYR)" autocapitalize="characters">
        <input id="fTo" maxlength="3" placeholder="To (MCO)" autocapitalize="characters">
        <label>Leave<input id="fDate" type="date"></label>
        <label>Return (optional)<input id="fRet" type="date"></label>
        <select id="fCabin" style="flex:1 1 100%; padding:10px; font-size:15px; border:1.5px solid var(--ink); border-radius:2px; background:transparent; color:var(--ink);">
          <option value="economy">Economy</option><option value="premium">Premium economy</option>
          <option value="business">Business</option><option value="first">First</option>
        </select>
        <button onclick="flightSearch()">Find flights</button>"""),
      ("""  document.getElementById('modeProducts').classList.toggle('on', m === 'products');""",
       """  document.getElementById('modeProducts').classList.toggle('on', m === 'products');
  document.getElementById('modeFlights').classList.toggle('on', m === 'flights');
  document.getElementById('flightForm').style.display = m === 'flights' ? 'flex' : 'none';
  document.querySelector('.search-box').style.display = m === 'flights' ? 'none' : '';"""),
      ("""  document.getElementById('chips').style.display = m === 'products' ? 'none' : '';""",
       """  document.getElementById('chips').style.display = m !== 'stores' ? 'none' : '';"""),
      ("""  document.getElementById('emptyState').style.display = m === 'products' ? 'none' : 'block';""",
       """  document.getElementById('emptyState').style.display = m !== 'stores' ? 'none' : 'block';"""),
      ("""function handleSearch(){
  const q = input.value.trim();""",
       """let TRAVEL = null;
async function flightSearch(){
  if(PAYWALL_ENABLED && !hasProAccess){
    rcReady.then(() => { if(hasProAccess) flightSearch(); else showPaywall(); });
    return;
  }
  const v = id => document.getElementById(id).value.trim();
  const from = v('fFrom').toUpperCase(), to = v('fTo').toUpperCase(), date = v('fDate'), ret = v('fRet'), cabin = v('fCabin') || 'economy';
  const box = document.getElementById('productResult');
  document.getElementById('result').style.display = 'none';
  document.getElementById('notCovered').style.display = 'none';
  document.getElementById('emptyState').style.display = 'none';
  box.style.display = 'block';
  if(!/^[A-Z]{3}$/.test(from) || !/^[A-Z]{3}$/.test(to) || !date){
    box.innerHTML = `<div class="empty-state"><p>Type 3-letter airport codes (like SYR and MCO) and pick a date.</p></div>`; return;
  }
  if(document.activeElement) document.activeElement.blur();
  box.innerHTML = `<div class="empty-state"><p>Checking flights ${from} → ${to}…</p></div>`;
  if(!TRAVEL){ const j = await getJSON(RATES_URL); TRAVEL = (j && j.travel) || {programs:{}, airlines:{}}; }
  const json = await getJSON(PRICES_URL + 'flights?from=' + from + '&to=' + to + '&date=' + date + (ret ? '&ret=' + ret : '') + '&cabin=' + cabin);
  if(!json || !json.results){ box.innerHTML = `<div class="empty-state"><p>Couldn't load flights right now. Check the airport codes and try again.</p></div>`; return; }
  if(!json.results.length){ box.innerHTML = `<div class="empty-state"><p>No flights found for ${from} → ${to} on that date.</p></div>`; return; }
  const progsFor = names => {
    const ids = [];
    names.forEach(a => Object.keys(TRAVEL.airlines || {}).forEach(k => {
      if(a.toLowerCase().indexOf(k.toLowerCase()) === 0) (TRAVEL.airlines[k] || []).forEach(id => { if(ids.indexOf(id) < 0) ids.push(id); });
    }));
    return ids.map(id => TRAVEL.programs[id]).filter(Boolean);
  };
  const t = s => (s || '').split(' ')[1] || '';
  const ymd = d => d.slice(2).replace(/-/g, '');
  const dur = m => m ? Math.floor(m / 60) + 'h ' + (m % 60) + 'm' : '';
  const rows = json.results.slice().sort((a, b) => a.price - b.price);
  box.innerHTML = `
    <div class="store-strip"><h2>${from} → ${to}</h2></div>
    <p class="winner-sub" style="margin-top:6px;">${esc(date)}${ret ? ' · return ' + esc(ret) + ' · round-trip prices' : ' · one way'} · ${cabin === 'premium' ? 'premium economy' : cabin}</p>
    <div class="alt-list">${rows.map(f => {
      const ps = progsFor(f.airlines);
      return `<div class="price-row">
        <div>
          <div class="name">${esc(f.airlines.join(' + '))}</div>
          <div class="t">${t(f.depart)} → ${t(f.arrive)} · ${f.stops ? f.stops + (f.stops > 1 ? ' stops' : ' stop') : 'Nonstop'}${f.duration ? ' · ' + dur(f.duration) : ''}</div>
          ${ps.length ? `<div class="pts">Book with points: ${ps.map(p => esc(p.name) + ' (' + esc(p.cards.join(', ')) + ')').join('; ')}</div>` : ''}
        </div>
        <div class="v">$${f.price}</div>
      </div>`; }).join('')}
    </div>
    <a class="go-btn" href="${json.link}" style="margin-top:16px;">See these flights on Google Flights ›</a>
    <a class="join-link" href="https://www.skyscanner.com/transport/flights/${from.toLowerCase()}/${to.toLowerCase()}/${ymd(date)}/${ret ? ymd(ret) + '/' : ''}?cabinclass=${cabin === 'premium' ? 'premiumeconomy' : cabin}&adults=1">Compare on Skyscanner ›</a><br>
    <a class="join-link" href="https://www.kayak.com/flights/${from}-${to}/${date}${ret ? '/' + ret : ''}${cabin === 'economy' ? '' : '/' + cabin}">Compare on Kayak ›</a>
    <p class="disclaimer">Cash fares from Google Flights, checked just now. "Book with points" lists the mileage programs that can book that airline and the cards whose points move to them (ratio card:miles). Points prices change daily, so check the program's site.</p>`;
}

function handleSearch(){
  const q = input.value.trim();"""),
    ]
    bad = [a[:50] for a, b in sw if h.count(a) != 1]
    if bad:
        print("Flights: could not find the spot. Nothing changed.", bad)
    else:
        for a, b in sw: h = h.replace(a, b, 1)
        open(p, "w", encoding="utf-8").write(h)
        print("Flights added. OK")
        x = home + "/ios/App/App.xcodeproj/project.pbxproj"
        t = open(x).read()
        t = re.sub(r"CURRENT_PROJECT_VERSION = (\d+);", lambda m: "CURRENT_PROJECT_VERSION = %d;" % (int(m.group(1)) + 1), t)
        t = t.replace("MARKETING_VERSION = 1.5;", "MARKETING_VERSION = 1.6;")
        open(x, "w").write(t)
        print("iOS:", sorted(set(re.findall(r"MARKETING_VERSION = [^;]+;|CURRENT_PROJECT_VERSION = \d+;", t))))
        g = home + "/android/app/build.gradle"
        t = open(g).read()
        t = re.sub(r"versionCode (\d+)", lambda m: "versionCode %d" % (int(m.group(1)) + 1), t, count=1)
        t = t.replace('versionName "1.5"', 'versionName "1.6"')
        open(g, "w").write(t)
        print("Android:", re.findall(r'versionCode \d+|versionName "[^"]+"', t))

# 1.7: tap a flight to book it on the airline's own site (and the Google Flights search for that trip)
h = open(p, encoding="utf-8").read()
if "AIRSITE" in h:
    print("Flight booking links already in. OK")
else:
    sw = [
      ("""let TRAVEL = null;""",
       """let TRAVEL = null;
const AIRSITE = {'Delta': 'https://www.delta.com', 'United': 'https://www.united.com', 'American': 'https://www.aa.com',
  'Southwest': 'https://www.southwest.com', 'Alaska': 'https://www.alaskaair.com', 'JetBlue': 'https://www.jetblue.com',
  'Spirit': 'https://www.spirit.com', 'Frontier': 'https://www.flyfrontier.com', 'Allegiant': 'https://www.allegiantair.com',
  'Breeze': 'https://www.flybreeze.com', 'Sun Country': 'https://www.suncountry.com', 'Hawaiian': 'https://www.hawaiianairlines.com',
  'Air Canada': 'https://www.aircanada.com', 'Porter': 'https://www.flyporter.com', 'WestJet': 'https://www.westjet.com'};
const airSite = a => { const k = Object.keys(AIRSITE).find(k => (a || '').toLowerCase().indexOf(k.toLowerCase()) === 0); return k ? AIRSITE[k] : ''; };"""),
      ("""          <div class="name">${esc(f.airlines.join(' + '))}</div>""",
       """          <a class="name" style="display:block; color:inherit; text-decoration:none;" href="${airSite(f.airlines[0]) || json.link}">${esc(f.airlines.join(' + '))} ›</a>"""),
      ("""          ${ps.length ? `<div class="pts">Book with points:""",
       """          <a class="go-link" href="${airSite(f.airlines[0]) || json.link}">${airSite(f.airlines[0]) ? 'Book on ' + esc(airSite(f.airlines[0]).replace('https://www.', '')) : 'Book on Google Flights'} ›</a>
          ${ps.length ? `<div class="pts">Book with points:"""),
    ]
    bad = [a[:50] for a, b in sw if h.count(a) != 1]
    if bad:
        print("Flight booking links: could not find the spot. Nothing changed.", bad)
    else:
        for a, b in sw: h = h.replace(a, b, 1)
        open(p, "w", encoding="utf-8").write(h)
        print("Flight booking links added. OK")
        x = home + "/ios/App/App.xcodeproj/project.pbxproj"
        t = open(x).read()
        t = re.sub(r"CURRENT_PROJECT_VERSION = (\d+);", lambda m: "CURRENT_PROJECT_VERSION = %d;" % (int(m.group(1)) + 1), t)
        open(x, "w").write(t)
        print("iOS:", sorted(set(re.findall(r"MARKETING_VERSION = [^;]+;|CURRENT_PROJECT_VERSION = \d+;", t))))
        g = home + "/android/app/build.gradle"
        t = open(g).read()
        t = re.sub(r"versionCode (\d+)", lambda m: "versionCode %d" % (int(m.group(1)) + 1), t, count=1)
        open(g, "w").write(t)
        print("Android:", re.findall(r'versionCode \d+|versionName "[^"]+"', t))
