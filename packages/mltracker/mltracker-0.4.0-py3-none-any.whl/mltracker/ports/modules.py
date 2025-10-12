from uuid import UUID
from abc import ABC, abstractmethod
from typing import Any
from typing import Protocol
from typing import Optional


class Module(Protocol):

    @property
    def name(self) -> str:
        """
        Defines a non unique identifier for a module owned by a model.

        Returns:
            str: The name of the module.
        """

    @property
    def attributes(self) -> dict[str, Any]: 
        """
        Returns a dictionary of the module's attributes.

        Attributes provide metadata or configuration details relevant 
        to the module. Keys should be strings, and values can be of 
        any type depending on the attribute.

        Returns:
            dict[str, Any]: A mapping of attribute names to their values.
        """


class Modules(ABC):

    @abstractmethod
    def log(self, name: str, attributes: Optional[dict[str, Any]] = None):
        """
        Adds a module to the modules collection.

        Args:
            name (str): The name of the module
            attributes (Optional[dict[str, Any]], optional): Relevant attributes of the module. Defaults to None.
        """
        ...

    @abstractmethod
    def list(self) -> list[Module]:
        """
        A list of the modules owned by the model.

        Returns:
            list[Module]: The modules owned by the model as a list.
        """

    @abstractmethod
    def remove(self, module: Module):
        """
        Removes a module from the collection.
        """

    @abstractmethod
    def clear(self):
        """
        Removes all modules from the collection
        """