#!/usr/bin/env python3
"""Create original, source-attributed 1:1 market-radar packages for new sources."""
import re, sys, subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills'/'when2buy-content-publisher'/'scripts'))
import state

FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
REG='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
LOGO=ROOT/'skills/when2buy-content-publisher/assets/when2buy-logo-reference.png'
def clean(text): return re.sub(r'\s+',' ',re.sub(r'https?://\S+','',text)).strip()
def slug(text): return re.sub(r'[^a-z0-9]+','-',text.lower()).strip('-')[:48] or 'market-radar'
def art(path,title,account):
 # A compact entity badge makes each original visual event-specific while
 # keeping third-party source media out of the finished artwork.
 entity=(re.search(r'\$[A-Za-z]{1,8}',title) or re.search(r'\b[A-Z][A-Za-z]+\b',title))
 entity=entity.group(0).upper() if entity else 'MARKET'
 lines=[]; words=title.upper().split(); line=''
 for word in words:
  candidate=(line+' '+word).strip()
  if len(candidate)>23 and line: lines.append(line); line=word
  else: line=candidate
 if line: lines.append(line)
 path.parent.mkdir(parents=True,exist_ok=True)
 command=['convert','-size','1080x1080','xc:#07080a','-fill','#e72a3b','-draw','rectangle 58,78 72,948','-fill','#15191f','-stroke','#e72a3b','-strokewidth','5','-draw','circle 885,205 1007,205','-stroke','none','-font',FONT,'-fill','white','-pointsize','28','-annotate','+112+118','QUICK MARKET RADAR','-pointsize','34','-gravity','NorthEast','-annotate','+118+185',entity[:10],'-gravity','NorthWest','-pointsize','70']
 for i,line in enumerate(lines[:4]): command.extend(['-annotate',f'+112+{315+i*91}',line])
 command.extend(['-fill','#3a4048','-draw','line 112,785 968,785','-fill','#ef4956','-pointsize','28','-annotate','+112+850',f'REPORTED BY @{account.upper()}','-fill','#aab0ba','-pointsize','31','-annotate','+112+905','NOT INDEPENDENTLY VERIFIED',str(LOGO),'-resize','100x100','-gravity','SouthEast','-geometry','+70+70','-composite',str(path)])
 subprocess.run(command,check=True)
def main():
 s=state.load_state(); covered={str(x.get('benchmarkPostId')) for x in s['packages']}; newest=max((p.get('capturedAt','') for p in s['benchmarkPosts']),default='')
 posts=[p for p in s['benchmarkPosts'] if p.get('capturedAt')==newest and str(p.get('id')) not in covered]
 for p in posts:
  raw=clean(p['text']); title=raw[:100]; package_id=f"pkg-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{slug(raw)}-{p['id'][-5:]}"; folder=Path('deliverables')/package_id; image=folder/'when2buy-market-radar.png';art(ROOT/image,title,p['account'])
  copy=f"Market radar: @{p['account']} reports: {raw[:70]}\n\nUnverified source claim—watch context, not a trade.\n\nMarket radar — reported by @{p['account']}; not independently verified. Not investment advice."
  s['packages'].append({'id':package_id,'benchmarkPostId':p['id'],'benchmarkPostUrl':p['url'],'title':title,'status':'ready','postText':copy,'mirroredFacts':[f"Source-attributed report from @{p['account']}",raw],'verificationSources':[p['url']],'imagePath':str(image),'sourceDisclosure':f"Market radar — reported by @{p['account']}; not independently verified.",'createdAt':datetime.now(timezone.utc).isoformat()})
 s['runs'].append({'id':f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce-attributed",'mode':'produce','status':'succeeded','startedAt':datetime.now(timezone.utc).isoformat(),'completedAt':datetime.now(timezone.utc).isoformat(),'summary':f'Created {len(posts)} original attributed market-radar package(s).','reason':''})
 errors=state.validate(s)
 if errors: raise SystemExit('\n'.join(errors))
 state.atomic_write(s);print(f'Created {len(posts)} package(s).')
if __name__=='__main__': main()
