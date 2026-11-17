import unittest,os,sys,json,subprocess as sp,socket,threading
import main as M
def L(fen):
 b,s,c,e=M.pf(fen)
 return[M.i2s(f)+M.i2s(t)+"nbrq"[abs(p)-2]*(p!=0)for f,t,p in M.gm(b,s,c,e)if not M.att((n:=M.mk(b,s,c,e,f,t,p)[0]),M.fk(n,s),1-s)]
def _sv(rs):
 s=socket.socket();s.bind(('127.0.0.1',0));s.listen(1);rq=[]
 def go():
  for sc,bd in rs:
   c,_=s.accept();d=b''
   while b'\r\n\r\n' not in d:d+=c.recv(65536)
   h,_,rb=d.partition(b'\r\n\r\n')
   cl=int(h[h.lower().find(b'ength:')+6:].split(b'\r\n')[0])if b'ength:'in h.lower()else 0
   while len(rb)<cl:rb+=c.recv(4096)
   rq.append((h.split()[1].decode(),json.loads(rb or b'{}')))
   c.sendall(f'HTTP/1.0 {sc} X\r\n\r\n'.encode()+(json.dumps(bd).encode()if bd else b''));c.close()
  s.close()
 threading.Thread(target=go,daemon=1).start();return s.getsockname()[1],rq
class T(unittest.TestCase):
 def test_start(self):
  F="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
  b,s,c,e=M.pf(F)
  assert s==0 and c==15 and b[95]==6
  assert len(L(F))==20 and M.ev(b)==0
  assert "f5e6" in L("rnbqkbnr/pppp1ppp/8/4pP2/8/8/PPPPP1PP/RNBQKBNR w KQkq e6 0 3")
  m=L("8/4P3/8/8/8/3k4/8/4K3 w - - 0 1")
  assert "e7e8q" in m and "e7e8n" in m
 def test_mate(self):
  f="rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"
  assert len(L(f))==0;b,s,c,e=M.pf(f)
  assert M.att(b,M.fk(b,s),1-s)
  assert M.ab(b,s,c,e,1,-99999,99999)<-20000
  f="5k2/5P2/5K2/8/8/8/8/8 b - - 0 1"
  assert len(L(f))==0;b,s,c,e=M.pf(f)
  assert not M.att(b,M.fk(b,s),1-s)
 def test_search(self):
  f="4k3/8/8/3r4/5N2/8/8/4K3 w - - 0 1"
  lm=["f4e2","f4g2","f4d3","f4h3","f4d5","f4h5","f4e6","f4g6","e1d1","e1d2","e1e2","e1f2","e1f1"]
  assert M.best(f,lm)=="f4d5"
  f="rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
  lm=["a7a6","b7b5","d7d5","e7e6","g8f6","b8c6"]
  assert M.best(f,lm)==M.best(f,lm)
 def test_bytes(self):
  t=0
  for f in sp.check_output(['git','ls-files'],text=1).split():
   sz=os.path.getsize(f);assert sz<=4096,f;t+=sz
  assert t<=8192
  try:ls=[l.split()for l in sp.check_output(['git','ls-tree','-rl','HEAD'],text=1).split('\n')if l]
  except Exception:ls=[]
  for x in ls:assert int(x[3])<=4096,x[4]
  assert sum(int(x[3])for x in ls)<=8192
 def test_http(self):
  G={"status":"your_move","game":1,"fen":"4k3/8/8/8/8/8/8/R3K3 w - - 0 1","legal_moves":["a1a2"]}
  OK=[(200,G),(200,{"status":"over"}),(200,{"status":"done"})]
  def R(u):return sp.run([sys.executable,'main.py'],capture_output=1,timeout=15,env=dict(os.environ,MAKEFUN_ENV_URL=u))
  def S(rs):p,rq=_sv(rs);r=R(f'http://127.0.0.1:{p}');return r,rq
  r,rq=S(OK);assert r.returncode==0
  assert[x[0]for x in rq]==['/game','/move','/game']
  assert rq[1][1]['move']=='a1a2'
  assert S([(200,G),(400,None)])[0].returncode!=0
  assert R('http://127.0.0.1:1').returncode!=0
  r2,rq2=S(OK);assert[x[1]for x in rq]==[x[1]for x in rq2]
if __name__=='__main__':unittest.main()
