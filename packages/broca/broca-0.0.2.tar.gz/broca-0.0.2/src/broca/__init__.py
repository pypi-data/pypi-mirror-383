from typing import List

from ..clients import BrocaClient
from ..models import BrocaModel
from ..util.url_to_model import url_to_model
from ..util.client_from_model import get_client_from_model
from threading import Lock

class Broca:

    # make the Broca client a singleton
    _instance = None
    _lock = Lock()
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance


    _models:List[BrocaModel] = []

    @staticmethod
    def from_url(url:str)-> BrocaClient:
        """
        Get a Broca instance from a URL.
        :param url: The definition url the client should be constructed from.
        :return: The Broca client model.
        """
        model = url_to_model(url)
        Broca._models.append(model)
        return Broca.from_model(model)

    @staticmethod
    def from_model(model:BrocaModel) -> BrocaClient:
        """
        Get a Broca instance from a model.
        :param model: The model the client should be constructed from.
        :return: The Broca client.
        """
        return get_client_from_model(model)


    @staticmethod
    def from_label(label:str)-> BrocaClient:
        """
        Get a Broca client instance from a label.
        Only works if the model was used previously added using a defining model.
        :param label: The label to search for.
        :return: A Broca client.
        """
        model = next((model for model in Broca._models if model.label == label), None)
        return Broca.from_model(model)

__all__ = ['Broca']