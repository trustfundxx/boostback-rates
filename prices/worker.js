// Boost Back price search. GET /?q=loreal+conditioner  ->  {query, results:[{store, title, price, link, thumbnail}]}
// The SerpAPI key lives in a Cloudflare secret (SERPAPI_KEY), never in the app.
const STORES = {            // Google Shopping seller name  ->  store name used in the app
  'walmart': 'Walmart', 'walmart.com': 'Walmart', 'target': 'Target', 'amazon': 'Amazon', 'amazon.com': 'Amazon',
  'ulta': 'Ulta Beauty', 'ulta beauty': 'Ulta Beauty', 'cvs': 'CVS', 'cvs pharmacy': 'CVS', 'walgreens': 'Walgreens',
};
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
      const store = STORES[String(it.source || '').toLowerCase().trim()];
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
