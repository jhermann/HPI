#!/usr/bin/python3
import logging
import sqlite3
from datetime import datetime
from itertools import chain, islice
from pathlib import Path
from typing import Any, Dict, Iterable, NamedTuple, Set

from cachew import cachew

# TODO move to common??
from kython import dictify

# TODO vendorize in my. pkg? It's quite handy...
from kython.klogging import LazyLogger

from mycfg import paths

logger = LazyLogger('bluemaestro', level=logging.DEBUG)


def get_backup_files():
    return list(sorted(chain.from_iterable(d.glob('*.db') for d in paths.bluemaestro.export_paths)))


class Point(NamedTuple):
    dt: datetime
    temp: float


# TODO hmm, does cachew have py.typed?
@cachew(cache_path=paths.bluemaestro.cache)
def iter_points(dbs) -> Iterable[Point]:
    # I guess we can affort keeping them in sorted order
    points: Set[Point] = set()
    # TODO do some sanity check??
    for f in dbs:
            # err = f'{f}: mismatch: {v} vs {value}'
            # if abs(v - value) > 0.4:
            #     logger.warning(err)
            #     # TODO mm. dunno how to mark errors properly..
            #     # raise AssertionError(err)
            # else:
            #     pass
        with sqlite3.connect(str(f)) as db:
            datas = list(db.execute('select * from data'))
            for _, tss, temp, hum, pres, dew in datas:
                # TODO is that utc???
                tss = tss.replace('Juli', 'Jul').replace('Aug.', 'Aug')
                dt = datetime.strptime(tss, '%Y-%b-%d %H:%M')
                p = Point(
                    dt=dt,
                    temp=temp,
                    # TODO use pressure and humidity as well
                )
                if p in points:
                    continue
                points.add(p)
    for p in sorted(points, key=lambda p: p.dt):
        yield p

    # logger.info('total items: %d', len(merged))
    # TODO assert frequency?
    # for k, v in merged.items():
    #     # TODO shit. quite a few of them have varying values... how is that freaking possible????
    #     # most of them are within 0.5 degree though... so just ignore?
    #     if isinstance(v, set) and len(v) > 1:
    #         print(k, v)
    # for k, v in merged.items():
    #     yield Point(dt=k, temp=v) # meh?

# TODO does it even have to be a dict?
# @dictify(key=lambda p: p.dt)
def get_temperature(backups=get_backup_files()): # TODO misleading name
    return list(iter_points(backups))


def get_dataframe():
    """
    %matplotlib gtk
    from my.bluemaestro import get_dataframe
    get_dataframe().plot()
    """
    import pandas as pd # type: ignore
    return pd.DataFrame(p._asdict() for p in get_temperature()).set_index('dt')


def test():
    print(get_temperature(get_backup_files()[-1:]))

def main():
    ll = list(iter_points(get_backup_files()))
    print(len(ll))
    # print(get_temperature(get_backup_files()[-1:]))
        # print(type(t))


if __name__ == '__main__':
    main()
