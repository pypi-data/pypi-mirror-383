from tinydb import TinyDB, where  

class Steps:
    def __init__(self, db: TinyDB, path: str):
        self.db = db
        self.path = path
        self.table = self.db.table(path) 
        if not self.table.all():
            self.table.insert({"value": 0})

    def get(self) -> int:
        record = self.table.get(doc_id=1)
        return record["value"] if record else 0

    def set(self, value: int):
        if self.table.get(doc_id=1):
            self.table.update({"value": value}, doc_ids=[1])
        else:
            self.table.insert({"value": value})

    def drop(self):
        self.db.drop_table(self.path)