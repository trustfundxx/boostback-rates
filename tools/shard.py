# python3 tools/shard.py K N  -> prints the stores for part K of N (1-based) as JSON:
#   {"Store": {"cashbackindex": url-or-null, "capitalone": url-or-null}, ...}
# Every store in tools/sources.json or tools/capitalone_sources.json lands in exactly one part.
import json, sys
k, n = int(sys.argv[1]), int(sys.argv[2])
a = json.load(open('tools/sources.json')); b = json.load(open('tools/capitalone_sources.json'))
names = sorted(set(a) | set(b))
part = {s: {'cashbackindex': a.get(s), 'capitalone': b.get(s)} for i, s in enumerate(names) if i % n == k - 1}
print(json.dumps(part, indent=1, ensure_ascii=False))
