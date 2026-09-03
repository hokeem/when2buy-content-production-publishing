#!/usr/bin/env python3
"""Create original, source-attributed 1:1 market-radar packages for new sources."""
import re, sys
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills'/'when2buy-content-publisher'/'scripts'))
import state

FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
REG='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
LOGO=ROOT/'skills/when2buy-content-publisher/assets/when2buy-logo-reference.png'
def clean(text): return re.sub(r'\s+',' ',re.sub(r'https?://\S+','',text)).strip()
def slug(text): return re.sub(r'[^a-z0-9]+','-',text.lower()).strip('-')[:48] or 'market-radar'
def wrap(draw,text,font,width):
 out=[]; line=''
 for word in text.split():
  if draw.textlength((line+' '+word).strip(),font=font)<=width: line=(line+' '+word).strip()
  else: out.append(line);line=word
 return out+[line] if line else out
def art(path,title,account):
 im=Image.new('RGB',(1080,1080),(7,8,10));d=ImageDraw.Draw(im); bold=ImageFont.truetype(FONT,76); small=ImageFont.truetype(FONT,27); body=ImageFont.truetype(REG,31)
 d.rectangle((58,80,72,330),fill=(231,42,59)); d.text((104,82),'QUICK MARKET\nRADAR',font=small,fill='white',spacing=8)
 y=215
 for line in wrap(d,title.upper(),bold,850)[:4]: d.text((104,y),line,font=bold,fill='white');y+=88
 d.text((104,860),f'REPORTED BY @{account.upper()}',font=small,fill=(239,73,86))
 d.text((104,908),'NOT INDEPENDENTLY VERIFIED',font=body,fill=(170,175,184))
 logo=Image.open(LOGO).convert('RGBA');logo.thumbnail((100,100));im.paste(logo,(920,920),logo);path.parent.mkdir(parents=True,exist_ok=True);im.save(path)
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
