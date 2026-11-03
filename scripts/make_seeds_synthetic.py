"""Synthetic merchants, subscriptions and payments for a POS SaaS. Seeded."""
import csv,random,datetime as dt
r=random.Random(42); plans={"starter":89,"standard":189,"advanced":339}
M=[];S=[];P=[]
for i in range(1,801):
    reg=r.choice(["CA","US","EU","AU"]); seg=r.choice(["retail","restaurant","golf"]); start=dt.date(2024,1,1)+dt.timedelta(days=r.randint(0,600))
    M.append([i,reg,seg,start]); plan=r.choice(list(plans)); end=None if r.random()<0.75 else start+dt.timedelta(days=r.randint(60,500))
    S.append([i,i,plan,plans[plan]*(1+r.randint(0,3)),start,end or ""])
    d=start
    while d<=(end or dt.date(2025,12,31)) and d<=dt.date(2025,12,31):
        P.append([len(P)+1,i,d,round(r.lognormvariate(5,1),2),r.choice(["card","card","card","cash"])]); d+=dt.timedelta(days=r.randint(5,40))
for n,h,rows in [("raw_merchants",["merchant_id","region","segment","signup_date"],M),("raw_subscriptions",["subscription_id","merchant_id","plan","mrr","start_date","end_date"],S),("raw_payments",["payment_id","merchant_id","payment_date","gpv","method"],P)]:
    w=csv.writer(open(f"seeds/{n}.csv","w",newline="")); w.writerow(h); w.writerows(rows)
print(len(M),len(S),len(P))
