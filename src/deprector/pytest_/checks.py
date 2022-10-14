from pathlib import Path
from typing import (
    List,
    Dict,
    Iterable,
)

import pytest

from .. import (
    depr,
    util,
    source,
    report,
)


class DeprecationsDetectedInLine(Exception):
    def __init__(
        self,
        filename: str,
        lineno: int,
        records_by_message: Dict[depr.Message, depr.Record],
    ):
        
        lines = [
            f"{filename}:L{lineno} is the probable source of {len(records_by_message)} deprecation(s):"
        ]
        for msg, records in records_by_message.items():
            lines.append(f"\t{msg} (detected {len(records)} time(s))")
        super().__init__("\n".join(lines))
        self.filename = filename
        self.lineno = lineno
        self.records_by_message = records_by_message


class SourceLine(pytest.Item):
    def __init__(self, *, filename: str, lineno: int, records, **kwargs):
        super().__init__(**kwargs)
        self._filename = filename
        self._lineno = lineno
        self._records = records

    def runtest(self):
        if self._records:
            raise DeprecationsDetectedInLine(
                filename=self._filename,
                lineno=self._lineno,
                records_by_message=util.groupby(self._records, "message")
            )

    def repr_failure(self, excinfo):
        exc = excinfo.value
        if isinstance(exc, DeprecationsDetectedInLine):
            msg = str(exc)
            code = source.get_valid_snippet(exc.filename, exc.lineno)
            msg += f"\n{code}"
            return msg
        return str(exc)

    def __str__(self):
        return f"{self._filename}:L{self._lineno}"

    def reportinfo(self):
        return self._filename, 0, str(self)


class SourceFile(pytest.Item):
    def __init__(
            self,
            *,
            path: Path,
            records: Iterable[report.SourceRecord],
            **kwargs,
        ):
            super().__init__(**kwargs)
            self.path = path
            self._records_by_line = util.groupby(records, "lineno")
            self.add_marker(pytest.mark.unit)

    def runtest(self):
        if self._records_by_line:
            raise DeprecationsDetectedInFile(
                filename=str(self.path),
                records_by_line=self._records_by_line,
            )

    def repr_failure(self, excinfo):
        return str(excinfo.value)

    def reportinfo(self):
        return self.path, 0, str(self)


class DeprecationsDetectedInFile(Exception):
    def __init__(
        self,
        filename: str,
        records_by_line: Dict[int, depr.Record],
    ):
        msg_lines = []
        msg_lines.append(f"{filename} contains {len(records_by_line)} probable source(s) of deprecations:")
        for lineno, records in records_by_line.items():
            by_msg = util.groupby(records, "message")
            for msg, msg_records in by_msg.items():
                msg_lines.append(f"\tL{lineno}: {msg} (detected {len(msg_records)} time(s))")
        exc_msg = "\n".join(msg_lines)
        super().__init__(exc_msg)
        self.filename = filename
        self.records_by_line = records_by_line


class SourceFileChecks(pytest.File):

    def __init__(
            self,
            *,
                records: Iterable[depr.Record],
                **kwargs,
            ):
                super().__init__(**kwargs)
                self._records_by_lineno = util.groupby(records, "lineno")
                self.add_marker(pytest.mark.unit)

    def __getitem__(self, key):
        return self._records_by_lineno[key]

    def collect(self):
        if not self._records_by_lineno:
            yield SourceFile.from_parent(
                self,
                path=self.path,
                name=f"{self.path}",
                records=[],
            )
        else:
            lines = self.path.read_text().splitlines()
            for lineno, line in enumerate(lines, start=1):
                recs_for_line = self[lineno]
                yield SourceLine.from_parent(
                    self,
                    name=f"L{lineno}",
                    filename=str(self.path),
                    lineno=lineno,
                    records=recs_for_line,
                )
