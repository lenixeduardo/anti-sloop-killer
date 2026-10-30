#!/usr/bin/env python3
"""Pixel-level before/after screenshot checks; no automatic aesthetic scoring.

Requires Pillow. Report change ratio and build a visual diff. The baseline must be
approved or intentionally supplied; changes exceeding tolerance require review.
No claim of AI-slop removal or pixel perfection follows solely from this test.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from PIL import Image, ImageChops, ImageEnhance

VIEWPORTS=('desktop','tablet','mobile')

def compare(before:Path, after:Path, diff:Path, *, channel_tolerance:int=12, max_changed_ratio:float=.01) ->dict:
    if not (0<=channel_tolerance<=255) or not (0<=max_changed_ratio<=1):
        raise ValueError('Tolerance out of range')
    with Image.open(before) as b,Image.open(after) as a:
        x,y=b.convert('RGB'),a.convert('RGB')
    result={'before':str(before),'after':str(after),'size_before':list(x.size),'size_after':list(y.size),
            'channel_tolerance':channel_tolerance,'max_changed_ratio':max_changed_ratio}
    if x.size!=y.size:
        result.update(status='different_dimensions',passed=False,changed_ratio=None)
        return result
    if x.width*x.height>35_000_000:
        raise ValueError('Image too large for pixel diff')
    delta=ImageChops.difference(x,y)
    # Binary mask: flag any pixel with a channel change above tolerance.
    combined=delta.convert('L').point(lambda _: 0) # create clean mask
    from PIL import Image as PILImage
    rgb=delta.split()
    channels=[c.point(lambda v:255 if v>channel_tolerance else 0) for c in rgb]
    mask=channels[0]
    for channel in channels[1:]:
        mask=ImageChops.lighter(mask,channel)
    changed=sum(mask.histogram()[1:])
    ratio=changed/(x.width*x.height)
    # Red highlights in diff for changed pixels; unchanged pixels remain gray.
    base=ImageEnhance.Brightness(x.convert('L').convert('RGB')).enhance(.55)
    red=PILImage.new('RGB',x.size,(255,45,56))
    overlay=PILImage.composite(red,base,mask)
    diff.parent.mkdir(parents=True,exist_ok=True)
    overlay.save(diff)
    result.update(status='pass' if ratio<=max_changed_ratio else 'review_required',
                  passed=ratio<=max_changed_ratio,changed_ratio=round(ratio,6),diff=str(diff))
    return result


def run(before_dir:Path,after_dir:Path,out:Path,*,channel_tolerance=12,max_changed_ratio=.01)->dict:
    out.mkdir(parents=True,exist_ok=True)
    results={}
    for name in VIEWPORTS:
        before,after=before_dir/f'{name}.png',after_dir/f'{name}.png'
        if not before.is_file() or not after.is_file():
            results[name]={'status':'missing_evidence','passed':False,'before':str(before),'after':str(after)}
            continue
        results[name]=compare(before,after,out/f'{name}-diff.png',channel_tolerance=channel_tolerance,max_changed_ratio=max_changed_ratio)
    report={'tool':'anti-ai-slop/visual-compare-1','status':'pass' if all(r['passed'] for r in results.values()) else 'review_required',
            'results':results,'warning':'Approved baseline and manual composition/identity review are still required.'}
    (out/'visual-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--before',type=Path,required=True)
    p.add_argument('--after',type=Path,required=True)
    p.add_argument('--out',type=Path,default=Path('reports/visual'))
    p.add_argument('--channel-tolerance',type=int,default=12)
    p.add_argument('--max-changed-ratio',type=float,default=.01)
    args=p.parse_args()
    try:report=run(args.before,args.after,args.out,channel_tolerance=args.channel_tolerance,max_changed_ratio=args.max_changed_ratio)
    except Exception as e:p.error(str(e))
    print(json.dumps(report,indent=2,ensure_ascii=False))
    return 0 if report['status']=='pass' else 1

if __name__=='__main__':raise SystemExit(main())
