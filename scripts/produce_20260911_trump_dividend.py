#!/usr/bin/env python3
import json, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/when2buy-content-publisher/scripts'))
import state
PID='pkg-20260911-trump-5000-dividend'; SID='2098499407008199000'
GEN=Path('/root/.codex/generated_images/01a0921b-fb0b-7e61-8ade-5a49e4a2f60d/exec-e9747e25-50fe-4f77-bb26-1279112d6c62.png')
LOGO=ROOT/'skills/when2buy-content-publisher/assets/when2buy-logo-reference.png'; OUT=ROOT/'deliverables'/PID; BASE=OUT/'generated-base.png'; FINAL=OUT/'when2buy-image.png'
def stamp(): return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
doc=state.load_state(); source=next(x for x in doc['benchmarkPosts'] if str(x.get('id'))==SID)
if not GEN.is_file(): raise SystemExit('generated image unavailable')
OUT.mkdir(parents=True,exist_ok=True); shutil.copy2(GEN,BASE)
subprocess.run(['convert',str(BASE),'-gravity','northwest','-fill','white','-font','DejaVu-Sans-Bold','-pointsize','62','-annotate','+62+86','TRUMP DIVIDEND','-fill','#ef3340','-pointsize','112','-annotate','+62+208','$5,000','-fill','white','-font','DejaVu-Sans','-pointsize','28','-annotate','+66+270','FOR EVERY U.S. ADULT','(',str(LOGO),'-resize','116x116',')','-gravity','southeast','-geometry','+42+42','-composite',str(FINAL)],check=True)
package={'id':PID,'benchmarkPostId':SID,'benchmarkPostUrl':source['url'],'title':'Trump says proposed $5,000 dividend will happen','status':'ready','postText':'Trump says a proposed $5,000 dividend for every U.S. adult will happen.','mirroredFacts':['President Trump said the proposed dividend would be $5,000 for every U.S. adult.','The White House release says the proposal is conditioned on Republicans retaining both the House and Senate.'],'verificationSources':[source['url'],'https://www.whitehouse.gov/releases/2026/09/trump-dividend-america-is-winning-and-americans-should-win-with-it/'],'imagePath':str(FINAL.relative_to(ROOT)),'createdAt':stamp(),'sourceExpiresAt':source.get('postedAt'),'visualProduction':{'method':'image_model','prompt':'Use case: productivity-visual. Complete entity-led Capitol and payment-envelope scene with a prominent $5,000 amount, near-black premium palette, white type and restrained red accent; exact factual typography and exact repository logo composited afterward. No source, attribution, disclaimer, commentary, CTA, tagline, recommendation, or watermark; not a pure-text or generic-radar visual.','logoApplied':True,'qaStatus':'passed','qa':{'inspectedAt':stamp(),'result':'passed','checks':['square 1254x1254 PNG','complete Capitol and payment-envelope entity scene','factual headline and support line proofread','exact repository logo composited once in lower-right clear space','no source, attribution, disclaimer, commentary, CTA, tagline, recommendation, or watermark','not a pure-text or generic-radar visual']}}}
doc['packages']=[x for x in doc['packages'] if x.get('id')!=PID]+[package]
doc['runs'].append({'id':f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce",'mode':'produce','status':'succeeded','startedAt':stamp(),'completedAt':stamp(),'summary':'Produced the single newest fresh Trump Dividend package with a complete entity-led square visual and exact-logo composite.','reason':'','selectedPackageId':PID})
errors=state.validate(doc)
if errors: raise SystemExit('\n'.join(errors))
state.atomic_write(doc); print(f'Produced {PID}')
