from uuid import uuid4, UUID
from typing import Optional
from typing import override
from dataclasses import dataclass
from tinydb import TinyDB, where
from mltracker.ports import Experiments as Repository
from mltracker.adapters.models import Models 

@dataclass
class Experiment:
    id: UUID
    name: str
    models: Models

class Experiments(Repository):

    def __init__(self, db: TinyDB):
        self.db = db
        self.table = self.db.table("/experiments")

    def build(self, id: UUID | str, name: str) -> Experiment:
        return Experiment(
            id=id if isinstance(id, UUID) else UUID(id), 
            name=name, 
            models=Models(self.db, f"/experiments/{str(id)}/models")
        )

    @override
    def create(self, name: str) -> Experiment:  
        if self.table.get(where("name") == name):
            raise ValueError(f"Experiment with name '{name}' already exists")
        
        id = uuid4()
        self.table.insert({
            "id": str(id),  
            "name": name
        })        
        return self.build(id, name)

    @override
    def read(self, name: str) -> Optional[Experiment]:
        result = self.table.get(where("name") == name)
        if result:
            return self.build(result["id"], result["name"]) 
        return None

    @override
    def update(self, id: UUID, name: str):
        result = self.table.get(where("id") == str(id))
        if result:
            self.table.update({"name": name}, doc_ids=[result.doc_id])

    @override
    def delete(self, id: UUID):
        result = self.table.get(where("id") == str(id))
        if result:
            experiments = self.build(result["id"], result["name"])
            experiments.models.clear()
            self.table.remove(doc_ids=[result.doc_id])

    @override
    def list(self) -> list[Experiment]:
        experiments = []
        for item in self.table.all():
            experiment = self.build(item["id"], item["name"])
            experiments.append(experiment)
        return experiments