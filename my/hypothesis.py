from pathlib import Path

from my_configuration import paths
import my_configuration.repos.hypexport.model as hypexport

def get_model() -> hypexport.Model:
    export_dir = Path(paths.hypexport.export_dir)
    sources = list(sorted(export_dir.glob('*.json')))
    model = hypexport.Model(sources)
    return model


Annotation = hypexport.Annotation


from typing import Dict, List, NamedTuple, Optional, Sequence
from pathlib import Path
from datetime import datetime

from .common import group_by_key, the, cproperty


class Page(NamedTuple):
    """
    Represents annotated page along with the annotations
    """
    annotations: Sequence[Annotation]

    @cproperty
    def link(self):
        return the(h.link for h in self.annotations)

    @cproperty
    def title(self):
        return the(h.title for h in self.annotations)

    @cproperty
    def dt(self) -> datetime:
        return min(h.dt for h in self.annotations)


def _iter():
    yield from get_model().iter_annotations()


def get_pages() -> List[Page]:
    grouped = group_by_key(_iter(), key=lambda e: e.link)
    pages = []
    for link, group in grouped.items():
        sgroup = tuple(sorted(group, key=lambda e: e.dt))
        pages.append(Page(annotations=sgroup))
    pages = list(sorted(pages, key=lambda p: p.dt))
    # TODO fixme page tag??
    return pages


def get_highlights():
    return list(_iter())


def test():
    get_pages()
    get_highlights()


def _main():
    for page in get_pages():
        print(page)

if __name__ == '__main__':
    _main()
