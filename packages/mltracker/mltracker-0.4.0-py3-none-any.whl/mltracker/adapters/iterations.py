from uuid import UUID, uuid4
from typing import Optional, Any, List
from typing import override
from dataclasses import dataclass
from tinydb import TinyDB, where
from mltracker.ports.iterations import Iterations as Collection
from mltracker.adapters.modules import Modules

@dataclass
class Iteration:
    id: UUID
    step: int
    modules: Modules


class Iterations(Collection): 
    def __init__(self, db: TinyDB, path: str):
        self.db = db
        self.path  = path
        self.table = self.db.table(path)

    def build(self, id: UUID | str, step: int) -> Iteration:
        return Iteration(
            id=id if isinstance(id, UUID) else UUID(id),
            step=step, 
            modules = Modules(self.db, f"/iterations/{str(id)}/modules"),
        )

    @override
    def create(self, step: int) -> Iteration:
        id = uuid4()
        self.table.insert({
            "id": str(id), 
            "step": step, 
        })
        return self.build(id, step)

    @override
    def get(self, step: int) -> Optional[Iteration]:
        result = self.table.get(where("step") == step)
        if result:
            return self.build(result["id"], result["step"])
        return None

    @override
    def list(self) -> list[Iteration]:
        records = self.table.all()
        return [ self.build(
            id=record["id"], 
            step=record["step"], 
        ) for record in records ]

    @override
    def remove(self, iteration: Iteration): 
        iteration.modules.clear()
        self.table.remove(where("id") == str(iteration.id)) 

    @override
    def clear(self):
        for item in self.table.all():
            iteration = self.build(item["id"], item["step"])
            iteration.modules.clear()
        self.db.drop_table(self.path)