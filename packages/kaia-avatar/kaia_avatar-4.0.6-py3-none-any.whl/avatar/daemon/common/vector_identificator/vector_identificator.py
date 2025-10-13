import os
from pathlib import Path
from brainbox.framework import FileLike
from typing import Callable
from yo_fluq import FileIO
import numpy as np
import pandas as pd
from .straregies import IStrategy
from dataclasses import dataclass

def cosine_distances(X, Y):
    X = np.array(X, dtype=float)
    Y = np.array(Y, dtype=float)

    X_norm = X / np.linalg.norm(X, axis=1, keepdims=True)
    Y_norm = Y / np.linalg.norm(Y, axis=1, keepdims=True)

    sim = np.dot(X_norm, Y_norm.T)
    return 1.0 - sim


class VectorIdentificator:
    def __init__(self,
                 folder: Path,
                 strategy: IStrategy,
                 sample_to_vector: Callable[[FileLike.Type], list[float]],
                 content_retriever: Callable[[str], bytes]
                 ):
        self.folder = folder
        self.strategy = strategy
        self.sample_to_vector = sample_to_vector
        self.content_retriever = content_retriever
        self.df: pd.DataFrame|None = None
        self.base: dict | None = None



    def initialize(self):
        base_file = self.folder/'base.json'
        if not base_file.is_file():
            base = {}
        else:
            base = FileIO.read_json(base_file)

        for class_name in os.listdir(self.folder):
            subfolder = self.folder/class_name
            if not subfolder.is_dir():
                continue
            if class_name not in base:
                base[class_name] = {}
            for file in os.listdir(subfolder):
                file_path = subfolder/file
                if not file_path.is_file():
                    continue
                if file not in base[class_name]:
                    base[class_name][file] = self.sample_to_vector(file_path)

        FileIO.write_json(base, base_file)
        array = []
        classes = []
        for class_name, data in base.items():
            for filename, vector in data.items():
                array.append(vector)
                classes.append(class_name)
        self.base = base
        self.df = pd.DataFrame(array, index=classes)

    def analyze(self, file: FileLike.Type) -> str|None:
        if self.df is None:
            return None
        vector = self.sample_to_vector(file)
        if vector is None:
            return None
        distances = cosine_distances(self.df.values, np.array(vector).reshape(1, -1)).flatten()
        s = pd.Series(distances, self.df.index)
        winner = self.strategy.get_winner(s)
        return winner

    def add_sample(self, class_name, filename: str):
        content = self.content_retriever(filename)
        FileIO.write_bytes(
            content,
            self.folder / class_name / filename
        )









