// Boost Back price search. GET /?q=loreal+conditioner  ->  {query, results:[{store, title, price, link, thumbnail}]}
// The SerpAPI key lives in a Cloudflare secret (SERPAPI_KEY), never in the app.
// Google Shopping seller name (starts with)  ->  store name used in the app.
// Matches "Walmart", "Walmart - Seller", "Amazon.com", "Amazon.com - Seller", "CVS Pharmacy", "Walgreens.com", etc.
const STORES = [['walmart', 'Walmart'], ['target', 'Target'], ['amazon', 'Amazon'], ['ulta', 'Ulta Beauty'],
  ['cvs', 'CVS'], ['walgreens', 'Walgreens']];
const storeFor = src => { const s = String(src || '').toLowerCase().trim(); const m = STORES.find(([k]) => s.startsWith(k)); return m ? m[1] : null; };
const CORS = { 'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json' };

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const q = (url.searchParams.get('q') || '').trim().slice(0, 100);
    if (!q) return new Response(JSON.stringify({ error: 'missing q' }), { status: 400, headers: CORS });
    if (env.APP_TOKEN && url.searchParams.get('t') !== env.APP_TOKEN)
      return new Response(JSON.stringify({ error: 'forbidden' }), { status: 403, headers: CORS });

    // same search within 6 hours is answered from cache, so it doesn't use up searches
    const cacheKey = new Request('https://cache.boostback/' + encodeURIComponent(q.toLowerCase()));
    const cache = caches.default;
    const hit = await cache.match(cacheKey);
    if (hit) return hit;

    const api = 'https://serpapi.com/search.json?engine=google_shopping&gl=us&hl=en&num=60&q='
      + encodeURIComponent(q) + '&api_key=' + env.SERPAPI_KEY;
    const r = await fetch(api);
    if (!r.ok) return new Response(JSON.stringify({ error: 'price lookup failed', status: r.status }), { status: 502, headers: CORS });
    const data = await r.json();
    const best = {};
    for (const it of (data.shopping_results || [])) {
      const store = storeFor(it.source);
      const price = typeof it.extracted_price === 'number' ? it.extracted_price : null;
      if (!store || price === null) continue;
      if (!best[store] || price < best[store].price)
        best[store] = { store, title: it.title || '', price, link: it.link || it.product_link || '', thumbnail: it.thumbnail || '' };
    }
    const results = Object.values(best).sort((a, b) => a.price - b.price);
    const res = new Response(JSON.stringify({ query: q, checked: new Date().toISOString(), results }),
      { headers: { ...CORS, 'Cache-Control': 'public, max-age=21600' } });
    ctx.waitUntil(cache.put(cacheKey, res.clone()));
    return res;
  }
};
