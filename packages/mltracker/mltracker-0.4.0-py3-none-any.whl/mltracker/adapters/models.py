from uuid import uuid4, UUID
from typing import Optional
from typing import override
from dataclasses import dataclass
from tinydb import TinyDB, where 
from mltracker.ports.models import Models as Collection 
from mltracker.adapters.metrics import Metrics
from mltracker.adapters.modules import Modules
from mltracker.adapters.iterations import Iterations
from mltracker.adapters.steps import Steps

@dataclass
class Model:
    id: UUID
    hash: str
    name: Optional[str]
    description: Optional[str]
    metrics: Metrics
    modules: Modules
    iterations: Iterations
    steps: Steps

    @property
    def step(self) -> int:
        return self.steps.get()
    
    @step.setter
    def step(self, value: int):
        self.steps.set(value)

class Models(Collection):

    def __init__(self, db: TinyDB, path: str):
        self.db = db
        self.path = path
        self.table = self.db.table(path)

    def build(self, id: str | UUID, hash: str, name: Optional[str], description: Optional[str]) -> Model:
        return Model(
            id = id if isinstance(id, UUID) else UUID(id),  
            hash = hash, 
            name = name,
            description=description,
            metrics = Metrics(self.db, f"/models/{str(id)}/metrics"),
            modules = Modules(self.db, f"/models/{str(id)}/modules"),
            iterations = Iterations(self.db, f"/models/{str(id)}/iterations"),
            steps = Steps(self.db, f"/models/{str(id)}/steps")
        )
    
    @override
    def create(self, hash: str, name: Optional[str] = None, description: Optional[str] = None) -> Model:    
        if self.table.get(where("hash") == hash):
            raise ValueError(f"Experiment with hash '{hash}' already exists")
        
        id = uuid4() 
        self.table.insert({
            "id": str(id),  
            "hash": hash,
            "name": name,
            "description": description
        })
        return self.build(id, hash, name, description)
        
    @override
    def read(self, hash: str) -> Optional[Model]:
        result = self.table.get(where("hash") == hash)
        if result:
            return self.build(result["id"], result["hash"], result["name"], result["description"])
        return None

    @override
    def update(self, hash: str, name: Optional[str] = None, description: Optional[str] = None): 
        result = self.table.get(where("hash") == hash) 
        if result:
            if name:    
                self.table.update({"name": name}, doc_ids=[result.doc_id])
            if description:
                self.table.update({"description": description}, doc_ids=[result.doc_id])

    @override
    def delete(self, id: UUID):
        result = self.table.get(where("id") == str(id))
        if result:
            model = self.build(result["id"], result["hash"], result["name"], result["description"])
            model.metrics.clear() 
            model.modules.clear()
            model.iterations.clear()
            model.steps.drop()
            self.table.remove(doc_ids=[result.doc_id])

    @override
    def list(self) -> list[Model]:
        models = []
        for item in self.table.all():
            model = self.build(item["id"], item["hash"], item["name"], item["description"])
            models.append(model)
        return models 
    
    @override
    def clear(self):   
        for item in self.table.all():
            model = self.build(item["id"], item["hash"], item["name"], item["description"])
            model.metrics.clear() 
            model.modules.clear()
            model.iterations.clear()
            model.steps.drop()
        self.db.drop_table(self.path)