#!/usr/bin/env python3
"""Record the remade first five timestamp-first queue packages."""
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state

ITEMS = [
 ("2095933175557992763", "Tesla Cybercab interior: day one", "Tesla $TSLA's Cybercab interior gets its first day-one look.", ["Tesla $TSLA Cybercab interior is shown in a day-one look."], "deliverables/pkg-20260905-here-is-a-day-1-look-at-the-inside-of-tesla-s-ts-92763/when2buy-image-model-v2.png", "Use case: ads-marketing. Square entity-led Tesla Cybercab interior visual, premium near-black financial-news style, white type, controlled red accents, headline TESLA $TSLA and CYBERCAB: DAY 1, clean lower-right space; original image-model generation and exact supplied logo composited afterward."),
 ("2095924450411553152", "Tesla starts paid Cybercab rides", "Tesla $TSLA says paid public Cybercab rides start at 3 PM ET.", ["Tesla $TSLA said paid Cybercab rides to the public start at 3 PM ET."], "deliverables/pkg-20260905-tesla-tsla-just-said-that-paid-rides-to-the-publ-53152/when2buy-image-model-v2.png", "Use case: ads-marketing. Square entity-led Tesla Cybercab pickup visual, premium near-black financial-news style, white type, controlled red accents, headline TESLA $TSLA and PAID RIDES START 3 PM ET, clean lower-right space; original image-model generation and exact supplied logo composited afterward."),
 ("2095922527579115717", "September market calendar", "September still has CPI, an FOMC meeting and Micron $MU earnings ahead.", ["The month includes CPI.", "The month includes an FOMC meeting.", "Micron $MU earnings are also listed for the month."], "deliverables/pkg-20260905-here-are-some-of-the-events-to-watch-out-for-thi-15717/when2buy-image-model-v2.png", "Use case: productivity-visual. Square entity-led macro calendar with CPI, FOMC and Micron earnings objects, premium near-black financial-news style, white type, controlled red accents, headline SEPTEMBER MARKET CALENDAR and CPI • FOMC • MICRON, clean lower-right space; original image-model generation and exact supplied logo composited afterward."),
 ("2095918547742380358", "Howard Lutnick disclosed $250M+ income", "Howard Lutnick disclosed at least $250M in income last year, mostly tied to prior Cantor Fitzgerald ownership.", ["Howard Lutnick disclosed at least $250 million in income last year.", "The income was described as mostly tied to prior Cantor Fitzgerald ownership."], "deliverables/pkg-20260905-howard-lutnick-disclosed-making-at-least-250m-in-80358/when2buy-image-model-v2.png", "Use case: ads-marketing. Square person-led Howard Lutnick executive-disclosure image with filing document, premium near-black financial-news style, white type, controlled red accents, headline HOWARD LUTNICK and $250M+ INCOME, clean lower-right space; original image-model generation and exact supplied logo composited afterward."),
 ("2095913618835435660", "Fed's Hammack calls for higher rates", "Fed's Hammack says local contacts point to raising rates to curb inflation.", ["Fed's Hammack said local contacts indicate it is time to raise rates to curb inflation."], "deliverables/pkg-20260905-just-in-fed-s-hammack-says-local-contacts-indica-35660/when2buy-image-model-v2.png", "Use case: productivity-visual. Square person-led Federal Reserve policy visual with Beth Hammack, inflation chart and meeting documents, premium near-black financial-news style, white type, controlled red accents, headline FED: RAISE RATES and CURB INFLATION, clean lower-right space; original image-model generation and exact supplied logo composited afterward."),
]

def stamp(): return datetime.now(timezone.utc).isoformat()
def main():
    doc = state.load_state(); sources = {str(x["id"]): x for x in doc["benchmarkPosts"]}
    for source_id, title, copy, facts, image, prompt in ITEMS:
        old = next(x for x in doc["packages"] if str(x.get("benchmarkPostId")) == source_id)
        old.update({"title": title, "status": "ready", "postText": copy, "mirroredFacts": facts,
                    "verificationSources": [sources[source_id]["url"]], "imagePath": image,
                    "createdAt": stamp(), "visualProduction": {"method": "image_model", "prompt": prompt, "logoApplied": True, "qaStatus": "passed"}})
        old.pop("sourceDisclosure", None)
    doc["runs"].append({"id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": stamp(), "completedAt": stamp(), "summary": "Remade first five timestamp-first packages with original image-model visuals, exact-logo compositing, and visual QA.", "reason": ""})
    errors = state.validate(doc)
    if errors: raise SystemExit("\n".join(errors))
    state.atomic_write(doc)
if __name__ == "__main__": main()
