from uuid import UUID
from uuid import uuid4
from typing import Any
from typing import Optional
from typing import override
from dataclasses import dataclass
from mltracker.ports.modules import Modules as Collection
from tinydb import TinyDB, where

@dataclass
class Module:
    id: UUID
    name: str
    attributes: dict[str, Any]

class Modules(Collection):

    def __init__(self, db: TinyDB, path: str):
        self.db = db
        self.table = self.db.table(path)

    def build(self, id: UUID | str, name: str, attributes: Optional[dict[str, Any]]) -> Module:
        return Module(
            id=id if isinstance(id, UUID) else UUID(id),
            name=name,
            attributes=attributes or {}
        )
    
    @override
    def log(self, name: str, attributes: Optional[dict[str, Any]] = None):
        id = uuid4()
        self.table.insert({
            'id': str(id),
            'name': name,
            'attributes': attributes
        })
 
    @override
    def list(self) -> list[Module]:
        records = self.table.all() 
        return [ self.build(
            id=record["id"], 
            name =record["name"], 
            attributes=record["attributes"]
        ) for record in records ]
  
    @override
    def remove(self, module: Module):
        self.table.remove(where("id") == str(module.id))
 
    @override
    def clear(self):
        self.table.truncate()