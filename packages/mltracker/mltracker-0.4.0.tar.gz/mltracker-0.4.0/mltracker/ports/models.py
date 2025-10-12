from uuid import UUID
from abc import ABC, abstractmethod
from typing import Any
from typing import Protocol
from typing import Optional

from mltracker.ports.metrics import Metrics
from mltracker.ports.modules import Modules
from mltracker.ports.iterations import Iterations

class Model(Protocol):

    @property
    def id(self) -> UUID:
        """A globally unique identifier for the models that can be used for 
        referencing the model outside the experiment namespace. 

        Returns:
            Any: The id of the model.
        """

    @property
    def hash(self) -> str:
        """A hash is a fixed length value that uniquely represents information. It acts
        as a locally unique identifier for a model under an experiment namespace. 

        Returns:
            str: The hash of the model.
        """

    @property
    def name(self) -> Optional[str]:
        """A human redable non unique identifier for a model type. 

        Returns:
            Optional[str]: The name of the model if any.
        """

    @property
    def description(self) -> Optional[str]:
        """A brief textual explanation that provides additional context or details 
        about the model. It can include information such as the models purpose, 
        configuration, architecture, or any other relevant metadata that helps 
        describe its role within an experiment.

        Returns:
            Optional[str]: The description of the model if available.
        """
 
    @property
    def step(self) -> Optional[int]:
        """An step is a unit of time that marks a transition between 
        successive states of the model. 

        Returns:
            Optional[int]: The steps that the model have been iterated if
            stored.
        """

    @step.setter
    def step(self, value):
        """Set the step of the model to the given value."""


    @property
    def metrics(self) -> Metrics:
        """Each model owns a collection of metrics. 

        Returns:
            Metrics: The collection of metrics of the model.
        """

    @property
    def modules(self) -> Modules:
        """
        A model is an aggregate of modules.

        Returns:
            Modules: The modules of the model.
        """


    @property
    def iterations(self) -> Iterations:
        """
        Each model owns a collection of iterations that represents discrete steps 
        in the model's training or evaluation process, typically corresponding to 
        one step.

        This accessor provides management of these iterations, allowing creation,
        retrieval, and listing of iterations that capture the model's progression
        over time.

        Returns:
            Iterations: The collection of iterations for this model.
        """


class Models(ABC):
    
    @abstractmethod
    def create(self, hash: str, name: Optional[str] = None, description: Optional[str] = None) -> Model:
        """
        Creates a record of a model in the database, retrieving
        an instance of the entity representing it. 

        Args:
            hash (Any): A locally unique identifier for the model. 
            name (Optional[str]): The name of the model.
            description (Optional[str]): Optional description for the model.

        Returns:
            Model: The entity representing a model. 
        """

    @abstractmethod
    def read(self, hash: str) -> Optional[Model]:
        """
        Retrieves a model with a given hash if any. 

        Args:
            hash (str): The hash of the model. 

        Returns:
            Optional[Model]: The model found if any. 
        """

    @abstractmethod
    def update(self, hash: str, name: str):
        """
        Update the name of a model for with the given hash. 

        Args:
            hash (str): The hash of the model.
            name (str): The new name of the model.
        """

    @abstractmethod
    def delete(self, id: Any):
        """
        Deletes the experiment with the given ID.

        Args:
            id (Any): The ID of the model to delete. 
        """

    @abstractmethod
    def list(self) -> list[Model]:
        """Retrieves a list of models."""