import ast
from collections import defaultdict
from typing import (
    Dict,
    List,
    Mapping,
)

from pydantic import validator, BaseModel
from pydantic.dataclasses import dataclass

from . import (
    depr,
)


@dataclass
class SourceRecord:
    "Information of a record associated with its source"
    filename: str
    lineno: int
    message: str
    record_id: int
    provenance: dict



RecordsBySource = Mapping[depr.Source, depr.Record]


class Slice:
    @classmethod
    def build(cls, records_by_source: RecordsBySource):
        raise NotImplementedError()


Filename = str
Message = str


@dataclass
class Location:
    lineno: int
    # code: str
    records: List[dict]


@dataclass
class Counts:
    sources: int
    records: int


@dataclass
class ByFileByMessage(Slice):

    @dataclass
    class FileInfo:
        items: Mapping[Message, List[Location]]

    items: Mapping[Filename, FileInfo]
    counts: Counts

    @property
    def locations_by_message(self) -> Dict[str, Location]:
        by_message = defaultdict(list)
        for src in self.sources:
            by_message[src.message].append(Location(src.lineno, src.records))
        return dict(by_message)

    @classmethod
    def build(cls, records_by_source: RecordsBySource):
        items = {}
        for src, records in records_by_source.items():
            item = items.setdefault(
                src.filename,
                cls(
                    src.filename,
                    sources=[]
                )
            )
            by_message = defaultdict[list]

            item.sources.append(
                cls.Source(
                    message=src.message,
                    lineno=src.lineno,
                    records=[
                        str(rec.provenance)
                        for rec in records
                    ]
                )
            )
        for item in items.values():
            yield item


@dataclass
class ByMessageByFile:
    message: Message
    locations: Mapping[str, Location]



