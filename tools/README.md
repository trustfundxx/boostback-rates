# Daily rate refresh

1. For each store in `tools/sources.json`, open its page and read today's posted rates in this one-line format
   (portals in percent, airlines in miles/points per $, `u` prefix for "up to", blank if not listed, ignore flat-dollar offers):
   `rakuten=;topcashback=;befrugal=;gocashback=;goodshop=;rebatesme=;pricecom=;extrabux=;delta=;american=;united=;southwest=;alaska=`
   Write one line per store to a results file as `Store Name|<that line>` (store names exactly as in sources.json).
1b. Capital One Shopping: for each store in `tools/capitalone_sources.json`, open its page (WebFetch; if blocked for
   provenance, WebSearch with allowed_domains ["capitaloneshopping.com"] for "<store> capital one shopping" first).
   The rate is the line "Get X% back on purchases when you shop on <Store>". Add `;capitalone=X` to that store's line
   (`u` prefix for "up to"; if only a flat-dollar offer is shown, use the % shown for most purchases, or omit the key).
   Use `capitalone=` (empty) ONLY when the page loaded and shows no rate — that removes Capital One for the store.
   If the page could not be loaded, leave the key out so yesterday's rate stays.
   Stores that are only on the Capital One list still get a line: `Store Name|capitalone=X`.
2. `python3 tools/apply_rates.py rates.json <results file>` — replaces only the portal and airline entries for stores with
   fresh data, sets Capital One's posted rate (keeping a targeted-offer boost only if higher), keeps everything else (Fetch, Ibotta, Amex, Chase, Honey, Active Junky, RetailMeNot, Mr. Rebates),
   and stamps `generated_at` (the app shows it as "updated <date>").
3. `python3 tools/validate.py` must print OK before committing.
4. Commit and push to `main`. The app reads
   https://raw.githubusercontent.com/trustfundxx/boostback-rates/main/rates.json on every launch.

## Links ("Go to <program>" buttons, app 1.3+)
- `programs.<id>.home` = program homepage; `programs.<id>.storeUrl` = per-store template ({domain} from top-level `domains`, {q} = store name).
- `stores.<name>.<id>.url` overrides both for one store. Change any of these here; no app update needed.
- Airline portals (Delta, American, United, Southwest, Alaska/Atmos) share store IDs: `.../me____.htm?gmid=<id>` (Target 18, Kohl's 1792).
