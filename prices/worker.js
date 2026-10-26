// Boost Back price search. GET /?q=loreal+conditioner  ->  {query, results:[{store, title, price, link, thumbnail}]}
// The SerpAPI key lives in a Cloudflare secret (SERPAPI_KEY), never in the app.
// Google Shopping seller name (starts with)  ->  store name used in the app.
// Matches "Walmart", "Walmart - Seller", "Amazon.com", "Amazon.com - Seller", "CVS Pharmacy", "Walgreens.com", etc.
const STORES = [['walmart', 'Walmart'], ['target', 'Target'], ['amazon', 'Amazon'], ['ulta', 'Ulta Beauty'],
  ['cvs', 'CVS'], ['walgreens', 'Walgreens'], ['sephora', 'Sephora'], ['macy', "Macy's"],
  ['nordstrom rack', 'Nordstrom Rack'], ['nordstrom', 'Nordstrom'], ['bloomingdale', "Bloomingdale's"]];
// Resale / marketplace sellers are skipped (used items, random third-party sellers).
const SKIP = ['mercari', 'poshmark', 'ebay', 'aliexpress', 'temu', 'depop', 'facebook', 'etsy', 'editorialist', 'walmart - seller', 'amazon.com - seller'];
const storeFor = src => {
  const s = String(src || '').toLowerCase().trim();
  if (!s || s === '?' || SKIP.some(k => s.startsWith(k))) return null;
  const m = STORES.find(([k]) => s.startsWith(k));
  return m ? m[1] : String(src).replace(/\.com$/i, '').trim();   // any other store: the app decides if it knows it
};
const CORS = { 'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json' };

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname === '/rates') {  // backup route for the daily rates file
      const r = await fetch('https://raw.githubusercontent.com/trustfundxx/boostback-rates/main/rates.json', { cf: { cacheTtl: 300 } });
      return new Response(await r.text(), { status: r.status, headers: { ...CORS, 'Cache-Control': 'public, max-age=300' } });
    }
    if (url.pathname === '/flights') return flights(url, env, ctx);
    if (url.pathname === '/book') return book(url, env);
    const q = (url.searchParams.get('q') || '').trim().slice(0, 100);
    if (!q) return new Response(JSON.stringify({ error: 'missing q' }), { status: 400, headers: CORS });
    if (env.APP_TOKEN && url.searchParams.get('t') !== env.APP_TOKEN)
      return new Response(JSON.stringify({ error: 'forbidden' }), { status: 403, headers: CORS });

    // same search within 6 hours is answered from cache, so it doesn't use up searches
    const cacheKey = new Request('https://cache.boostback/v2/' + encodeURIComponent(q.toLowerCase()));
    const cache = caches.default;
    const debug = url.searchParams.get('debug') === '1';
    const hit = debug ? null : await cache.match(cacheKey);
    if (hit) return hit;

    const api = 'https://serpapi.com/search.json?engine=google_shopping&gl=us&hl=en&num=60&q='
      + encodeURIComponent(q) + '&api_key=' + env.SERPAPI_KEY;
    const r = await fetch(api);
    if (!r.ok) return new Response(JSON.stringify({ error: 'price lookup failed', status: r.status }), { status: 502, headers: CORS });
    const data = await r.json();
    const all = [...(data.shopping_results || []), ...(data.inline_shopping_results || [])];
    for (const c of (data.categorized_shopping_results || [])) all.push(...(c.shopping_results || []));
    const best = {};
    const add = (store, title, price, link, thumbnail, same) => {
      if (!store || typeof price !== 'number') return;
      // a price for the SAME product (from its store list) beats a look-alike from the general results
      const cur = best[store];
      if (!cur || (same && !cur.same) || (same === cur.same && price < cur.price))
        best[store] = { store, title: title || '', price, link: link || '', thumbnail: thumbnail || '', same: !!same };
    };
    // Step 2: open the top product's own page on Google Shopping, which lists every store selling that exact item.
    const top = all.find(it => it.immersive_product_page_token && storeFor(it.source)) || all.find(it => it.immersive_product_page_token);
    let stores = [];
    if (top) {
      try {
        const r2 = await fetch('https://serpapi.com/search.json?engine=google_immersive_product&page_token='
          + encodeURIComponent(top.immersive_product_page_token) + '&api_key=' + env.SERPAPI_KEY);
        if (r2.ok) {
          const d2 = await r2.json();
          stores = ((d2.product_results || {}).stores || []);
          for (const st of stores) {
            const price = typeof st.extracted_price === 'number' ? st.extracted_price
              : parseFloat(String(st.price || '').replace(/[^0-9.]/g, ''));
            add(storeFor(st.name), (d2.product_results || {}).title || top.title, isNaN(price) ? null : price, st.link, top.thumbnail, true);
          }
        }
      } catch (e) {}
    }
    if (debug) return new Response(JSON.stringify({ query: q, top: top ? top.title : null,
      product_stores: stores.map(st => (st.name || '?') + ' | ' + (st.extracted_price ?? st.price ?? '')),
      other_results: all.slice(0, 40).map(it => (it.source || '?') + ' | ' + (it.extracted_price ?? '') + ' | ' + (it.title || '')) }), { headers: CORS });
    for (const it of all) add(storeFor(it.source), it.title, typeof it.extracted_price === 'number' ? it.extracted_price : null,
      it.link || it.product_link, it.thumbnail, false);
    let picked = Object.values(best);
    // Google's list for the exact item often leaves out big stores (Sephora, Ulta...). Keep a big store from the
    // general results too when its listing has every word of the search in its title.
    const norm = t => String(t || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
    const words = norm(q).split(/[^a-z0-9]+/).filter(w => w.length > 1);
    const major = new Set(STORES.map(([, n]) => n));
    const matches = x => words.every(w => norm(x.title).includes(w));
    if (picked.filter(x => x.same).length >= 2) picked = picked.filter(x => x.same || (major.has(x.store) && matches(x)));
    const results = picked.sort((a, b) => a.price - b.price).map(({ same, ...x }) => ({ ...x, sameItem: same }));
    const res = new Response(JSON.stringify({ query: q, checked: new Date().toISOString(), results }),
      { headers: { ...CORS, 'Cache-Control': 'public, max-age=21600' } });
    if (results.length) ctx.waitUntil(cache.put(cacheKey, res.clone()));  // never cache an empty answer
    return res;
  }
};

// Flights: GET /flights?from=SYR&to=MCO&date=2026-11-20[&ret=2026-11-27]  (cash fares from Google Flights)
const IATA = /^[A-Z]{3}$/, DAY = /^\d{4}-\d{2}-\d{2}$/;
async function flights(url, env, ctx) {
  const g = k => (url.searchParams.get(k) || '').trim().toUpperCase();
  const CAB = { ECONOMY: 1, PREMIUM: 2, BUSINESS: 3, FIRST: 4 }, cabin = CAB[g('cabin')] ? g('cabin') : 'ECONOMY';
  const from = g('from'), to = g('to'), date = (url.searchParams.get('date') || '').trim(), ret = (url.searchParams.get('ret') || '').trim();
  if (!IATA.test(from) || !IATA.test(to) || !DAY.test(date) || (ret && !DAY.test(ret)))
    return new Response(JSON.stringify({ error: 'Use 3-letter airport codes and dates like 2026-11-20' }), { status: 400, headers: CORS });
  const cacheKey = new Request('https://cache.boostback/flights/' + [from, to, date, ret, cabin].join('/'));
  const cache = caches.default;
  const hit = await cache.match(cacheKey);
  if (hit) return hit;
  const api = 'https://serpapi.com/search.json?engine=google_flights&hl=en&gl=us&currency=USD'
    + '&departure_id=' + from + '&arrival_id=' + to + '&outbound_date=' + date
    + '&travel_class=' + CAB[cabin] + (ret ? '&return_date=' + ret + '&type=1' : '&type=2') + '&api_key=' + env.SERPAPI_KEY;
  const r = await fetch(api);
  if (!r.ok) return new Response(JSON.stringify({ error: 'flight lookup failed', status: r.status }), { status: 502, headers: CORS });
  const d = await r.json();
  const list = [...(d.best_flights || []), ...(d.other_flights || [])];
  const results = list.filter(f => typeof f.price === 'number' && (f.flights || []).length).slice(0, 25).map(f => {
    const legs = f.flights;
    return {
      price: f.price,
      airlines: [...new Set(legs.map(l => l.airline).filter(Boolean))],
      flightNumbers: legs.map(l => l.flight_number).filter(Boolean),
      depart: (legs[0].departure_airport || {}).time || '',
      arrive: (legs[legs.length - 1].arrival_airport || {}).time || '',
      stops: legs.length - 1,
      duration: f.total_duration || null,
      logo: f.airline_logo || legs[0].airline_logo || '',
      token: f.booking_token || ''
    };
  });
  const link0 = (d.search_metadata || {}).google_flights_url || ('https://www.google.com/travel/flights?q=' + encodeURIComponent('flights from ' + from + ' to ' + to + ' on ' + date));
  const link = link0;
  const self = url.origin + '/book?from=' + from + '&to=' + to + '&date=' + date + '&cabin=' + cabin + '&g=' + encodeURIComponent(link) + '&token=';
  for (const x of results) { x.link = x.token ? self + encodeURIComponent(x.token) : link; delete x.token; }
  const res = new Response(JSON.stringify({ from, to, date, ret, cabin: cabin.toLowerCase(), roundTrip: !!ret, checked: new Date().toISOString(), link, results }),
    { headers: { ...CORS, 'Cache-Control': 'public, max-age=21600' } });
  if (results.length) ctx.waitUntil(cache.put(cacheKey, res.clone()));
  return res;
}

// Book: opens the airline's booking page with this exact flight picked (Google Flights' "Book with ..." button).
// One-way only; anything that fails falls back to the Google Flights search for that date.
async function book(url, env) {
  const g = k => (url.searchParams.get(k) || '').trim();
  const back = g('g').startsWith('https://www.google.com/') ? g('g') : 'https://www.google.com/travel/flights';
  const go = u => Response.redirect(u, 302);
  const from = g('from').toUpperCase(), to = g('to').toUpperCase(), date = g('date'), token = g('token');
  const CAB = { ECONOMY: 1, PREMIUM: 2, BUSINESS: 3, FIRST: 4 }, cabin = CAB[g('cabin').toUpperCase()] || 1;
  if (!IATA.test(from) || !IATA.test(to) || !DAY.test(date) || !token) return go(back);
  try {
    const r = await fetch('https://serpapi.com/search.json?engine=google_flights&hl=en&gl=us&currency=USD&type=2'
      + '&departure_id=' + from + '&arrival_id=' + to + '&outbound_date=' + date + '&travel_class=' + cabin
      + '&booking_token=' + encodeURIComponent(token) + '&api_key=' + env.SERPAPI_KEY);
    if (!r.ok) return go(back);
    const d = await r.json();
    const opts = (d.booking_options || []).map(o => o.together || o.departing || {}).filter(o => o.booking_request && o.booking_request.url);
    if (!opts.length) return go(back);
    const airline = ((((d.selected_flights || [])[0] || {}).flights || [])[0] || {}).airline || '';
    const pick = opts.find(o => airline && String(o.book_with || '').toLowerCase().startsWith(airline.toLowerCase().split(' ')[0])) || opts[0];
    const req = pick.booking_request;
    if (!req.post_data) return go(req.url);
    const esc = s => String(s).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');
    const inputs = [...new URLSearchParams(req.post_data)].map(([k, v]) => '<input type="hidden" name="' + esc(k) + '" value="' + esc(v) + '">').join('');
    return new Response('<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Opening ' + esc(pick.book_with || 'booking') + '</title></head>'
      + '<body style="font-family:-apple-system,sans-serif;padding:24px"><p>Opening ' + esc(pick.book_with || 'the booking site') + '…</p>'
      + '<form id="f" method="POST" action="' + esc(req.url) + '">' + inputs + '<button>Continue</button></form>'
      + '<script>document.getElementById("f").submit()</script></body></html>', { headers: { 'Content-Type': 'text/html; charset=utf-8' } });
  } catch (e) { return go(back); }
}
