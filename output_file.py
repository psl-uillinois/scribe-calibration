from abc import ABC, abstractmethod

class OutputFile(ABC):
    @abstractmethod
    def __init__(self, filename):
        pass

    @abstractmethod
    def write_metadata(self, xsize, ysize, xarray, yarray, text):
        pass

    @abstractmethod
    def write_beginning(self):
        pass

    @abstractmethod
    def write_end(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def add_point(self, x, y, z, lp):
        pass

    @abstractmethod
    def write(self):
        pass

    @abstractmethod
    def move_sample(self, x, y):
        pass
