from tinydb import TinyDB
from mltracker.ports.experiments import Experiments, Experiment
from mltracker.adapters.experiments import Experiments as TinyDBExperiments

def getallExperiments(path = 'data/db.json') -> Experiments:
    db = TinyDB(path)
    return TinyDBExperiments(db)

def getExperiment(name: str, path = 'data/db.json') -> Experiment:
    db = TinyDB(path)
    rep = TinyDBExperiments(db)
    exp = rep.read(name)
    if not exp:
        exp = rep.create(name)
    return exp