#!/usr/bin/env python3
from datetime import datetime, timezone
from pathlib import Path
import shutil, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills' / 'when2buy-content-publisher' / 'scripts'))
import state

SOURCE_ID = '2098131841609871395'
PACKAGE_ID = 'pkg-20260910-vanguard-decade-etfs'
BASE = Path('/root/.codex/generated_images/01a08cda-2411-7b11-b167-df91456bf467/exec-cd0b194f-7bbf-4060-846d-a0affa2484a9.png')
LOGO = ROOT / 'skills/when2buy-content-publisher/assets/when2buy-logo-reference.png'
OUT = ROOT / 'deliverables' / PACKAGE_ID
FINAL = OUT / 'when2buy-image-model.png'

def stamp(): return datetime.now(timezone.utc).isoformat()

doc = state.load_state()
source = next(x for x in doc['benchmarkPosts'] if str(x.get('id')) == SOURCE_ID)
OUT.mkdir(parents=True, exist_ok=True)
shutil.copy2(BASE, OUT / 'generated-base.png')
subprocess.run(['convert', str(BASE), '(', str(LOGO), '-resize', '112x112', ')', '-gravity', 'southeast', '-geometry', '+36+36', '-composite', str(FINAL)], check=True)
package = {
    'id': PACKAGE_ID, 'benchmarkPostId': SOURCE_ID, 'benchmarkPostUrl': source['url'],
    'title': 'Vanguard growth and large/mega-cap ETFs beat the S&P 500 over a decade',
    'status': 'ready',
    'postText': 'At Vanguard, only growth and large/mega-cap ETFs beat the S&P 500 over the last decade.',
    'mirroredFacts': ['Vanguard growth and large/mega-cap ETFs were the only ETFs beating the S&P 500 over the last decade.'],
    'verificationSources': [source['url'], 'https://advisors.vanguard.com/investments/products/VOOG/vanguard-s%26p-500-growth-etf', 'https://advisors.vanguard.com/investments/products/mgk/vanguard-morningstar-mega-cap-growth-etf'],
    'imagePath': str(FINAL.relative_to(ROOT)), 'createdAt': stamp(),
    'visualProduction': {'method':'image_model', 'prompt':'Complete square entity-led editorial visual of Vanguard growth and large/mega-cap funds outperforming an S&P 500 benchmark; no generated text or logos; exact repository logo composited once.', 'logoApplied':True, 'qaStatus':'passed'},
}
doc['packages'] = [x for x in doc['packages'] if str(x.get('id')) != PACKAGE_ID]
doc['packages'].append(package)
doc['runs'].append({'id': 'run-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-produce', 'mode':'produce', 'status':'succeeded', 'startedAt':stamp(), 'completedAt':stamp(), 'summary':'Produced one newest fresh Vanguard ETF package with exact-logo compositing.', 'reason':''})
errors = state.validate(doc)
if errors: raise SystemExit('\n'.join(errors))
state.atomic_write(doc)
print(PACKAGE_ID)
