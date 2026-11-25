import json,urllib.request,datetime,collections
B="https://api.taskmarket.dev/api"
def g(p):
    try:
        r=urllib.request.Request(B+p,headers={"User-Agent":"tm-visualizer","Accept":"application/json"})
        return json.loads(urllib.request.urlopen(r,timeout=60).read())
    except Exception as e: return {"error":str(e)}
def lst(x):
    if isinstance(x,list): return x
    if isinstance(x,dict):
        for k in("tasks","items","data","results","events","feed"):
            if isinstance(x.get(k),list): return x[k]
    return []
out={"updated":datetime.datetime.utcnow().isoformat()+"Z","chains":{}}
for c,n in((4217,"Tempo"),(8453,"Base")):
    d={"name":n,"stats":g(f"/market/stats?chainId={c}"),"breakdowns":g(f"/stats/breakdowns?chainId={c}"),"ts":{}}
    for rg in("7d","30d","90d","all"): d["ts"][rg]=g(f"/stats/platform-time-series?chainId={c}&range={rg}&bucket=day")
    d["heat"]=g(f"/stats/activity-heatmap?chainId={c}&range=30d&dimension=hourOfWeek")
    d["heatmode"]=g(f"/stats/activity-heatmap?chainId={c}&range=30d&dimension=mode")
    d["feed"]=lst(g(f"/stats/activity-feed?chainId={c}&limit=30"))[:30]
    wk=collections.defaultdict(set);cur=None
    for _ in range(30):
        x=g(f"/tasks?chainId={c}&limit=100"+(f"&cursor={cur}" if cur else ""));L=lst(x)
        for t in L:
            try:
                dt=datetime.datetime.fromisoformat(t["createdAt"].replace("Z","+00:00"));w=(dt-datetime.timedelta(days=dt.weekday())).date().isoformat()
                wk[w].add(t.get("requester"))
            except Exception: pass
        cur=x.get("nextCursor") or x.get("cursor") if isinstance(x,dict) else None
        if not cur or not L: break
    d["posters"]=sorted([[k,len(v)] for k,v in wk.items()])
    out["chains"][str(c)]=d
json.dump(out,open("data.json","w"))
