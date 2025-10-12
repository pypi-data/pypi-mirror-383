from uuid import UUID, uuid4
from typing import Optional, Any, List
from typing import override
from dataclasses import dataclass
from tinydb import TinyDB, where
from mltracker.ports.metrics import Metrics as Collection

@dataclass
class Metric:
    id: UUID
    name: str
    value: Any
    step: Optional[int] = None
    phase: Optional[str] = None

class Metrics(Collection):
    
    def __init__(self, db: TinyDB, path: str):
        self.db = db
        self.path = path
        self.table = self.db.table(path)

    def build(self, id: UUID | str, name: str, value: Any, step: Optional[int], phase: Optional[str]):
        return Metric(
            id=id if isinstance(id, UUID) else UUID(id), 
            name=name, 
            value=value, 
            step=step, 
            phase=phase
        )        

    @override
    def log(self, name: str, value: Any, step: int, phase: Optional[str] = None):
        id = uuid4()
        self.table.insert({
            "id": str(id),
            "name": name,
            "value": value,
            "step": step,
            "phase": phase
        })

    @override
    def list(self, name: Optional[str] = None) -> List[Metric]:
        if name:
            records = self.table.search(where("name") == name)
        else:
            records = self.table.all() 
        return [ self.build(
            id=record["id"], 
            name =record["name"], 
            value=record["value"], 
            step=record.get("step"), 
            phase=record.get("phase")
        ) for record in records ]

    @override
    def remove(self, metric: Metric):
        self.table.remove(where("id") == str(metric.id))

    @override
    def clear(self):
        self.db.drop_table(self.path)