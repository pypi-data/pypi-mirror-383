# MLTracker: Lightweight Machine Learning Experiment Tracker

MLTracker is a lightweight library for tracking machine learning experiments, models and metrics. It is a simple data model built on **TinyDB**. I create this for personal use but feel free to use it as you want.

📖 Full documentation: [API Reference](https://entropy-flux.github.io/MLTracker)   

## Installation

```bash
pip install mltracker
```

## Usage

### Create an Experiment

```python
from mltracker import getExperiment

experiment = getExperiment("my-experiment") # get or creates an experiment
print(experiment.id, experiment.name)
```

Add a model to track:

```python
model = experiment.models.create(hash="123456", name="model1")
model.modules.add(name="conv_layer", attributes={"type": "conv", "layers": 3})
model.modules.add(name="actv_layer", attributes={"type": "relu"})
model.modules.add(name="linear_layer", attributes={"in_size": 256, "out_size": 10})
```

Track metrics:

```python
model.metrics.add(name="accuracy", value=0.85, step=1, phase="train")
model.metrics.add(name="loss", value=0.25, step=1, phase="train") 
model.metrics.add(name="accuracy", value=0.87, step=1, phase="test")
model.metrics.add(name="loss", value=0.24, step=1, phase="test")
model.step += 1

model.metrics.add(name="accuracy", value=0.89, step=2, phase="train")
model.metrics.add(name="loss", value=0.29, step=2, phase="train")
model.metrics.add(name="accuracy", value=0.88, step=2, phase="test")
model.metrics.add(name="loss", value=0.26, step=2, phase="test")
model.step += 1
```

Track extra metadata:

```python
iteration = model.iterations.create(step=2)
iteration.modules.add(name="SGD", attributes={"lr"=0.01})
```

Then just retrieve what you need.

```python
model = experiment.models.read(hash="123456")
print(model.step)

for module in model.modules.list():
    print(module.name, module.attributes)

for metric in model.metrics.list(): 
    print(metric.name, metric.value)
```

This is MIT Licensed, feel free to use it as you please. 
