
import json,urllib.request,time,datetime
B="https://api.taskmarket.dev/api"
def g(p):
    for i in range(3):
        try:
            r=urllib.request.Request(B+p,headers={"User-Agent":"tm-visualizer/1.0","Accept":"application/json"})
            return json.loads(urllib.request.urlopen(r,timeout=60).read())
        except Exception as e: err=str(e); time.sleep(2)
    return {"error":err}
def tasks(cid):
    out=[];cur=None
    for _ in range(40):
        q=f"/tasks?chainId={cid}&limit=100"+(f"&cursor={cur}" if cur else "")
        d=g(q)
        items=d if isinstance(d,list) else (d.get("tasks") or d.get("items") or d.get("data") or [])
        for t in items: out.append({k:t.get(k) for k in ("requester","createdAt","status","mode","reward")})
        cur=None if isinstance(d,list) else (d.get("nextCursor") or d.get("cursor") or (d.get("pagination") or {}).get("nextCursor"))
        if not cur or not items: break
    return out
def weekly(ts):
    w={}
    for t in ts:
        try: d=datetime.date.fromisoformat((t["createdAt"] or "")[:10])
        except Exception: continue
        k=(d-datetime.timedelta(days=d.weekday())).isoformat()
        w.setdefault(k,set()).add((t.get("requester") or "").lower())
    return [{"week":k,"posters":len(v)} for k,v in sorted(w.items())]
D={"generatedAt":datetime.datetime.utcnow().isoformat()+"Z","chains":{}}
for cid in (4217,8453):
    c={"stats":g(f"/market/stats?chainId={cid}"),"breakdowns":g(f"/stats/breakdowns?chainId={cid}"),
       "heatmap":g(f"/stats/activity-heatmap?chainId={cid}&range=30d&dimension=hourOfWeek"),
       "feed":g(f"/stats/activity-feed?chainId={cid}&limit=30"),"series":{}}
    for rg in ("7d","30d","90d","all"):
        c["series"][rg]=g(f"/stats/platform-time-series?chainId={cid}&range={rg}&bucket={'week' if rg in ('90d','all') else 'day'}")
    ts=tasks(cid); c["taskCount"]=len(ts); c["postersWeekly"]=weekly(ts)
    D["chains"][str(cid)]=c
json.dump(D,open("data.json","w"),separators=(",",":"))
print("ok",{k:v["taskCount"] for k,v in D["chains"].items()})
