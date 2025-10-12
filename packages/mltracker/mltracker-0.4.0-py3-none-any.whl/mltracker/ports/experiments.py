from uuid import UUID
from abc import ABC, abstractmethod
from typing import Protocol
from typing import Optional 
from mltracker.ports.models import Models

class Experiment(Protocol):
    """Defines a namespace for organizing machine learning models with scoped uniqueness.
    
    An Experiment groups related models while ensuring model identifiers remain unique
    within its namespace. Provides globally unique identification via UUID and a 
    human-readable locally unique name.
    """

    @property
    def id(self) -> UUID:
        """Globally unique inmutable identifier for the experiment.

        Returns:
            UUID: Unique identifier that can be used across systems.
        """

    @property
    def name(self) -> str:
        """Human-readable identifier unique within the users's scope.
        
        Used for intuitive referencing an experiment while enforcing 
        uniqueness constraints at the user's level.

        Returns:
            str: The name of the experiment.
        """

    @property
    def models(self) -> Models:
        """Each experiment owns a collection of models. The models' identifiers
        are unique under an experiment namespace.

        Returns:
            Models: The collection of models owned by the experiment.
        """


class Experiments(ABC):
    """An abstract base class representing a collection of experiments. This class serves as 
    an interface for available backends or as a base class for a custom implementation.
    
    In order to create a concrete instance of an experiment collection, use the `getallexperiments`
    accessor.

    Methods:
        create:
            Creates a new experiment with the given name.
        
        read:
            Retrieves an experiment by its name if any.

        update:
            Updates an experiment's name.

        delete:
            Deletes an experiment by ID.

        list:
            List all experiments in the collection.
    """

    @abstractmethod
    def create(self, name: str) -> Experiment:
        """Creates an experiment with a given name

        Args:
            name (str): The name and unique identifier of the experiment

        Returns:
            Optional[Experiment]: The created experiment. 
        """

    @abstractmethod
    def read(self, name: str) -> Optional[Experiment]:
        """Retrieve an experiment by it's name

        Args:
            name (str): The name of the experiment to be retrieved.

        Returns:
            Optional[Experiment]: The experiment with the given name if any.
        """


    @abstractmethod
    def update(self, id: UUID, name: str):
        """Updates the name of an experiment.

        Args:
            id (UUID): The ID of the experiment to update.
            name (str): The new name of the experiment.
        """


    @abstractmethod
    def delete(self, id: UUID):
        """Deletes the experiment with the given ID. 

        Args:
            id (UUID): The ID of the experiment to be retrieved.                    
        """


    @abstractmethod
    def list(self) -> list[Experiment]:
        """List the experiments in the collection.

        Returns:
            List[Experiment]: The list of experiments in the collection.
        """