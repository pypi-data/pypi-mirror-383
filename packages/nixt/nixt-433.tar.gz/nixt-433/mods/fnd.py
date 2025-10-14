# This file is placed in the Public Domain.


"find"


import time


from nixt.caching import find
from nixt.methods import fmt
from nixt.utility import elapsed, fntime
from nixt.workdir import long, skel, types


def fnd(event):
    skel()
    if not event.rest:
        res = sorted([x.split('.')[-1].lower() for x in types()])
        if res:
            event.reply(",".join(res))
        else:
            event.reply("no data yet.")
        return
    otype = event.args[0]
    clz = long(otype)
    nmr = 0
    for fnm, obj in list(find(clz, event.gets)):
        event.reply(f"{nmr} {fmt(obj)} {elapsed(time.time()-fntime(fnm))}")
        nmr += 1
    if not nmr:
        event.reply("no result")
