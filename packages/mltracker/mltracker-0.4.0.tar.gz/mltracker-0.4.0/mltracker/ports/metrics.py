from abc import ABC, abstractmethod
from uuid import UUID
from typing import Protocol 
from typing import Optional
from typing import Any

class Metric(Protocol):

    @property
    def id(self) -> UUID:
        """
        The globally unique identifier of the metric.

        Returns:
            UUID: The ID of the metric.
        """

    @property
    def name(self) -> str:
        """
        A metric is categorized by it's name. 

        Returns:
            str: The name of the metric.
        """

    @property
    def value(self) -> Any:
        """
        A quantitative value representing the model's performance.

        Returns:
            Any: The value of the metric. 
        """

    @property
    def step(self) -> Optional[int]:
        """
        An step is a discrete unit of time that marks a transition between 
        successive states of a machine learning model. Each metric value is associated 
        with some stage of the model indexed by the step. 

        Returns:
            int: The step of the metric. 
        """

    @property
    def phase(self) -> Optional[str]:
        """
        The operational stage of the model when the metric was produced. The phase helps 
        interpret the metric in context of the model's lifecycle. 

        Returns:
            Optional[str]: The phase of the model in wich the metric was produced.
        """
        

class Metrics(ABC):
    
    @abstractmethod
    def log(self, name: str, value: Any, step: Optional[int] = None, phase: Optional[str] = None):
        """
        Add a metric to the collection. 
        
        Args:
            name (str): The name of the metric. 
            value (Any): The value of the metric.
            step (int): The step in wich the metric was produced. 
            phase (Optional[str]): The phase in wich the metric was produced. 
        """

    @abstractmethod
    def list(self, name: Optional[str] = None) -> list[Metric]:
        """
        Get a list of metrics in the collection. 

        Args:
            name (Optional[str]): The name of the metrics to be listed.  

        Returns:
            list[Metric]: The list of metric of the model. 
        """

    @abstractmethod
    def remove(self, metric: Metric):
        """
        Removes the given metric from the collection.        
        """

    @abstractmethod
    def clear(self):
        """
        Removes all metrics from the collection.
        """