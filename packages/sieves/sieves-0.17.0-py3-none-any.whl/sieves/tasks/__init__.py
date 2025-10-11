"""Tasks."""

from . import predictive, preprocessing
from .core import Task
from .postprocessing import DistillationFramework
from .predictive import (
    NER,
    Classification,
    InformationExtraction,
    PIIMasking,
    QuestionAnswering,
    SentimentAnalysis,
    Summarization,
    Translation,
)
from .predictive.core import PredictiveTask
from .preprocessing import Chunking, Ingestion

__all__ = [
    "Chunking",
    "Classification",
    "DistillationFramework",
    "NER",
    "InformationExtraction",
    "Ingestion",
    "SentimentAnalysis",
    "Summarization",
    "Translation",
    "QuestionAnswering",
    "PIIMasking",
    "Task",
    "predictive",
    "PredictiveTask",
    "preprocessing",
]
