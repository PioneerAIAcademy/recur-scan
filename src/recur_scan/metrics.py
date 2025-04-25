from dataclasses import dataclass


@dataclass
class LabelerMetrics:
    fp: int  # false positives
    fn: int  # false negatives
    tp: int  # true positives
    tn: int  # true negatives
    precision: float  # precision
    recall: float  # recall
    score: float  # f1 score
