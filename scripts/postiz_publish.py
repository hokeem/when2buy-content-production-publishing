#!/usr/bin/env python3
"""Upload and publish one ready when2buy package through Postiz, then verify release."""
import argparse,json,mimetypes,os,subprocess,sys,time,uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'skills/when2buy-content-publisher/scripts')); import state
BASE=os.getenv('POSTIZ_BASE_URL','https://api.postiz.com/public/v1').rstrip('/'); EXPECTED=os.getenv('WHEN2BUY_POSTIZ_HANDLE','_When2buy')
def request(path, method='GET', data=None, content_type='application/json'):
 key=os.getenv('POSTIZ_API_KEY');
 if not key: raise SystemExit('POSTIZ_API_KEY is required; do not save it in this repository.')
 h={'Authorization':key};
 if data is not None: h['Content-Type']=content_type
 try:
  with urlopen(Request(BASE+path,data=data,headers=h,method=method),timeout=45) as r:return json.load(r)
 except HTTPError as x: raise SystemExit(f'Postiz HTTP {x.code}: {x.read(600).decode("utf-8","replace")}')
def upload(path):
 boundary='----when2buy'+uuid.uuid4().hex; mime=mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
 body=(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{path.name}"\r\nContent-Type: {mime}\r\n\r\n').encode()+path.read_bytes()+f'\r\n--{boundary}--\r\n'.encode()
 return request('/upload','POST',body,f'multipart/form-data; boundary={boundary}')
def main():
 p=argparse.ArgumentParser();p.add_argument('--package-id',required=True);p.add_argument('--confirm',action='store_true',help='required acknowledgement of current publishing authorization');p.add_argument('--wait-seconds',type=int,default=90);a=p.parse_args()
 if not a.confirm: raise SystemExit('Refusing to publish without --confirm.')
 s=state.load_state(); pkg=next((x for x in s['packages'] if x.get('id')==a.package_id),None)
 if not pkg or pkg.get('status')!='ready': raise SystemExit('Package must exist and be status=ready.')
 image=ROOT/pkg.get('imagePath','')
 if not image.is_file() or not pkg.get('postText') or not pkg.get('benchmarkPostUrl') or not pkg.get('mirroredFacts') or not pkg.get('verificationSources'): raise SystemExit('Ready package is missing required source, copy, verification, or image fields.')
 integrations=request('/integrations'); integ=next((x for x in integrations if x.get('identifier')=='x' and x.get('profile','').lstrip('@')==EXPECTED.lstrip('@') and not x.get('disabled')),None)
 if not integ: raise SystemExit(f'No enabled X integration for @{EXPECTED}.')
 media=upload(image); payload={'type':'now','date':datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z'),'shortLink':False,'tags':[],'posts':[{'integration':{'id':integ['id']},'value':[{'content':pkg['postText'],'image':[{'id':media['id'],'path':media['path']}]}],'settings':{'__type':'x','who_can_reply_post':'everyone'}}]}
 created=request('/posts','POST',json.dumps(payload).encode()); postiz_id=created[0]['postId']; deadline=time.time()+a.wait_seconds; released=None
 while time.time()<deadline:
  start=(datetime.now(timezone.utc)-timedelta(minutes=10)).isoformat().replace('+00:00','Z'); end=(datetime.now(timezone.utc)+timedelta(minutes=10)).isoformat().replace('+00:00','Z')
  for x in request(f'/posts?startDate={start}&endDate={end}').get('posts',[]):
   if x.get('id')==postiz_id:
    if x.get('state')=='PUBLISHED' and x.get('releaseURL'): released=x;break
    if x.get('state') in ('ERROR','FAILED'): raise SystemExit(f'Postiz delivery failed: {x}')
  if released: break
  time.sleep(5)
 if not released: raise SystemExit(f'Postiz queued {postiz_id}; no public release URL within {a.wait_seconds}s.')
 published_at=released['publishDate']; published_dt=datetime.fromisoformat(published_at.replace('Z','+00:00'))
 window_end=(published_dt+timedelta(hours=72)).isoformat(timespec='seconds').replace('+00:00','Z')
 pkg['status']='published';pkg['postizPostId']=postiz_id;pkg['publishedAt']=published_at; url=released['releaseURL'].replace('twitter.com','x.com')
 s['posts'].append({'id':str(released['releaseId']),'packageId':pkg['id'],'title':pkg.get('title',''),'status':'published','publishedAt':published_at,'url':url,'postizPostId':postiz_id,'metricsTracking':{'status':'active','windowStart':published_at,'windowEnd':window_end,'lastAttemptAt':None,'lastAttemptSource':None,'lastAttemptResult':None}})
 s['runs'].append({'id':f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-publish",'mode':'publish','status':'succeeded','startedAt':datetime.now(timezone.utc).isoformat(),'completedAt':datetime.now(timezone.utc).isoformat(),'summary':'Published through Postiz and verified a public X release URL.','reason':''})
 errors=state.validate(s)
 if errors: raise SystemExit('\n'.join(errors))
 state.atomic_write(s); subprocess.run([sys.executable, str(ROOT/'scripts'/'render_report.py')], check=True); subprocess.run([sys.executable, str(ROOT/'scripts'/'render_run_panel.py')], check=True); print(json.dumps({'postizPostId':postiz_id,'url':url}))
if __name__=='__main__': main()
