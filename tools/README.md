# Daily rate refresh

1. For each store in `tools/sources.json`, open its page and read today's posted rates in this one-line format
   (portals in percent, airlines in miles/points per $, `u` prefix for "up to", blank if not listed, ignore flat-dollar offers):
   `rakuten=;topcashback=;befrugal=;gocashback=;goodshop=;rebatesme=;pricecom=;extrabux=;delta=;american=;united=;southwest=;alaska=`
   Write one line per store to a results file as `Store Name|<that line>` (store names exactly as in sources.json).
2. `python3 tools/apply_rates.py rates.json <results file>` — replaces only the portal and airline entries for stores with
   fresh data, keeps everything else (Capital One, Fetch, Ibotta, Amex, Chase, Honey, Active Junky, RetailMeNot, Mr. Rebates),
   and stamps `generated_at` (the app shows it as "updated <date>").
3. `python3 tools/validate.py` must print OK before committing.
4. Commit and push to `main`. The app reads
   https://raw.githubusercontent.com/trustfundxx/boostback-rates/main/rates.json on every launch.
