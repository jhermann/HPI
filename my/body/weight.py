'''
Weight data (manually logged)
'''

from datetime import datetime
from typing import NamedTuple, Iterator

from ..common import LazyLogger
from ..error import Res
from ..notes import orgmode

from mycfg import weight as config


log = LazyLogger('my.body.weight')


class Entry(NamedTuple):
    dt: datetime
    value: float
    # TODO comment??


Result = Res[Entry]


# TODO cachew?
def from_orgmode() -> Iterator[Result]:
    orgs = orgmode.query()
    for o in orgs.query_all(lambda o: o.with_tag('weight')):
        try:
            # TODO ?? Result type?
            created = o.created
            heading = o.heading
        except Exception as e:
            log.exception(e)
            yield e
            continue
        try:
            w = float(heading)
        except ValueError as e:
            log.exception(e)
            yield e
            continue
        # TODO not sure if it's really necessary..
        created = config.default_timezone.localize(created)
        yield Entry(
            dt=created,
            value=w,
            # TODO add org note content as comment?
        )


def dataframe():
    import pandas as pd # type: ignore
    entries = from_orgmode()
    def it():
        for e in from_orgmode():
            if isinstance(e, Exception):
                yield {
                    'error': str(e),
                }
            else:
                yield {
                    'dt'    : e.dt,
                    'weight': e.value,
                }
    df = pd.DataFrame(it())
    df.set_index('dt', inplace=True)
    df.index = pd.to_datetime(df.index, utc=True)
    return df
