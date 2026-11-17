import json,os,sys
from urllib.request import*
U=os.environ.get("MAKEFUN_ENV_URL","")
def post(p,d):
 try:return json.load(urlopen(Request(U+p,json.dumps(d).encode(),{"Content-Type":"application/json"}),timeout=30))
 except Exception as e:sys.exit(e)
def s2i(s):return(10-int(s[1]))*10+ord(s[0])-96
def i2s(i):return chr(i%10+96)+str(10-i//10)
def pf(fen):
 b=[99]*120
 for i in range(21,99):
  if 0<i%10<9:b[i]=0
 p=fen.split();r,c=2,1
 for x in p[0]:
  if x=='/':r+=1;c=1
  elif x.isdigit():c+=int(x)
  else:b[r*10+c]=("PNBRQK".index(x.upper())+1)*(1-2*(x>'Z'));c+=1
 stm=p[1]!='w';cs=0
 for x in p[2]:cs|={'K':1,'Q':2,'k':4,'q':8}.get(x,0)
 ep=s2i(p[3])if p[3]!='-'else 0
 return b,stm,cs,ep
N=(-21,-19,-12,-8,8,12,19,21)
B=(-11,-9,9,11)
R=(-10,-1,1,10)
Q=B+R
V=(0,100,320,330,500,900,0)
def att(b,sq,sd):
 s=1-2*sd
 for d in N:
  if b[sq+d]==2*s:return 1
 for ds,ps in((B,(3*s,5*s)),(R,(4*s,5*s))):
  for d in ds:
   t=sq+d
   while b[t]==0:t+=d
   if b[t]in ps:return 1
 for d in Q:
  if b[sq+d]==6*s:return 1
 d=1-2*sd;return b[sq+d*11]==s or b[sq+d*9]==s
def fk(b,sd):
 k=6-12*sd
 for i in range(21,99):
  if 0<i%10<9 and b[i]==k:return i
 return 0
def gm(b,stm,cs,ep):
 mv=[];sg=1-2*stm
 for i in range(21,99):
  if i%10<1 or i%10>8:continue
  p=b[i]
  if p*sg<=0:continue
  t=abs(p)
  if t==1:
   d=-10*sg
   if b[i+d]==0:
    if i//10==8-5*(sg>0):
     for q in(5,4,3,2):mv+=(i,i+d,q*sg),
    else:
     mv+=(i,i+d,0),
     if i//10==3+5*(sg>0)and b[i+2*d]==0:mv+=(i,i+2*d,0),
   for cd in(d-1,d+1):
    j=i+cd
    if b[j]==99:continue
    if b[j]*sg<0 or(j==ep and ep):
     if j//10==9-7*(sg>0):
      for q in(5,4,3,2):mv+=(i,j,q*sg),
     else:mv+=(i,j,0),
  elif t in(2,6):
   for d in(N if t==2 else Q):
    if b[i+d]!=99 and b[i+d]*sg<=0:mv+=(i,i+d,0),
  else:
   ds=B if t==3 else R if t==4 else Q
   for d in ds:
    j=i+d
    while b[j]==0:mv+=(i,j,0),;j+=d
    if b[j]!=99 and b[j]*sg<0:mv+=(i,j,0),
 return mv
def mk(b,stm,cs,ep,f,t,pr):
 n=b[:];p=n[f];n[t]=pr or p;n[f]=0
 if p*p==1 and t==ep and ep:n[t+10-20*stm]=0
 if p*p==36 and abs(f-t)==2:
  if t>f:n[f+1],n[f+3]=n[f+3],0
  else:n[f-1],n[f-4]=n[f-4],0
 nc=cs
 for x in(f,t):nc&={91:13,98:14,95:12,21:7,28:11,25:3}.get(x,15)
 ne=(f+t)//2 if p*p==1 and abs(f-t)==20 else 0
 return n,1-stm,nc,ne
def ev(b):
 s=0
 for i in range(21,99):
  p=b[i]
  if 0<(a:=abs(p))<7:s+=V[a]*(p//a)
 return s
D=3;QD=8
def qs(b,stm,cs,ep,a,bt,qd):
 se=ev(b)*(1-2*stm)
 if se>=bt:return bt
 if se>a:a=se
 if qd<1:return a
 for f,t,pr in gm(b,stm,cs,ep):
  if not(b[t]or pr or(abs(b[f])==1 and t==ep and ep)):continue
  nb,ns,nc,ne=mk(b,stm,cs,ep,f,t,pr)
  if att(nb,fk(nb,stm),1-stm):continue
  v=-qs(nb,ns,nc,ne,-bt,-a,qd-1)
  if v>=bt:return bt
  if v>a:a=v
 return a
def ab(b,stm,cs,ep,d,a,bt):
 if d==0:return qs(b,stm,cs,ep,a,bt,QD)
 mvs=gm(b,stm,cs,ep);mvs.sort(key=lambda m:-V[abs(b[m[1]])])
 lg=0
 for f,t,pr in mvs:
  nb,ns,nc,ne=mk(b,stm,cs,ep,f,t,pr)
  if att(nb,fk(nb,stm),1-stm):continue
  lg+=1;v=-ab(nb,ns,nc,ne,d-1,-bt,-a)
  if v>=bt:return bt
  if v>a:a=v
 if not lg:
  if att(b,fk(b,stm),1-stm):return-30000+D-d
  return 0
 return a
def best(fen,legal):
 b,stm,cs,ep=pf(fen);bm=legal[0];bs=-99999
 for m in legal:
  f,t=s2i(m[:2]),s2i(m[2:4]);pr=0
  if len(m)==5:pr=("nbrq".index(m[4])+2)*(1-2*stm)
  nb,ns,nc,ne=mk(b,stm,cs,ep,f,t,pr)
  if att(nb,fk(nb,stm),1-stm):continue
  v=-ab(nb,ns,nc,ne,D-1,-99999,99999)
  if v>bs:bs=v;bm=m
 return bm
if __name__=="__main__":
 if not U:sys.exit("MAKEFUN_ENV_URL not set")
 while 1:
  g=post("/game",{})
  if g["status"]=="done":break
  while g["status"]=="your_move":
   g=post("/move",{"game":g["game"],"move":best(g["fen"],g["legal_moves"])})
 print(g.get('wins',0),'W',g.get('losses',0),'L',file=sys.stderr)
