from abc import ABC, abstractmethod

class extractor(ABC):
    @abstractmethod
    def extract(self, url: str) -> str:
        pass

class transformer(ABC):
    @abstractmethod
    def transform(self, url: str) -> str:
        pass

class loader(ABC):
    @abstractmethod
    def load(self, url: str) -> str:
        pass
