import io
import json
from typing import TYPE_CHECKING, Iterator, Literal, Optional, Union

import pyarrow as pa

from odp.tabular_v2.util import vars_to_json

if TYPE_CHECKING:
    from odp.tabular_v2.client import Table


class Raw:
    def __init__(self, table: "Table"):
        self.table = table

    def list(self, query: Optional[str] = None, vars: Optional[dict] = None) -> list:
        res = self.table.cli.request(
            "/api/table/v2/raw/list",
            params={
                "table_id": self.table._id,
            },
            data={
                "query": query,
                "vars": vars_to_json(vars),
            },
        )
        body = res.json()
        return body["files"]

    def list_batches(self, query: Optional[str] = None, vars: Optional[dict] = None) -> pa.Table:
        res = self.table.cli.request(
            "/api/table/v2/raw/batch-list",
            params={"table_id": self.table._id},
            data={"query": query, "vars": vars_to_json(vars)},
        )
        reader = pa.ipc.open_stream(res.reader())
        batches = [batch for batch in reader]
        return pa.Table.from_batches(batches, schema=reader.schema)

    def upload(self, name: str, data: Union[bytes, io.IOBase]) -> str:
        res = self.table.cli.request(
            "/api/table/v2/raw/upload",
            params={"table_id": self.table._id, "name": name},
            data=data,
            retry=False,
        )
        body = res.json()
        return body["raw_id"]

    def update_meta(self, identifier: str, data: dict) -> dict:
        res = self.table.cli.request(
            "/api/table/v2/raw/update_meta",
            params={"table_id": self.table._id, "id": identifier},
            data=json.dumps(data).encode("utf-8"),
            retry=False,
        )
        return res.json()

    def download(self, id: str) -> Iterator[bytes]:
        res = self.table.cli.request(
            "/api/table/v2/raw/download",
            params={"table_id": self.table._id, "id": id},
        )
        return res.iter()

    def delete(self, id: str) -> None:
        self.table.cli.request(
            "/api/table/v2/raw/delete",
            params={"table_id": self.table._id, "id": id},
            retry=False,
        )

    def ingest(self, id: str, opt: Literal["append", "truncate", "drop"] = "append") -> None:
        """
        Ingest a raw file into the table.

        :param id: The identifier of the raw file to ingest.
        :param opt: The ingestion option. Can be "append", "truncate", or "drop".
                - "append": Add new data to the existing table.
                - "truncate": Remove all existing data and add new data.
                - "drop": Drop the existing table and create a new one with the new data.
        """
        self.table.cli.request(
            "/api/table/v2/raw/ingest",
            params={"table_id": self.table._id, "id": id, "opt": opt},
            data={},
            retry=False,
        )
