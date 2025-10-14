import math
from ..base import BaseDriftAdapter

class SLIDING_ADAPTER(BaseDriftAdapter):
    def __init__(self, window_size):
        self.window_size = window_size

    def adapt(self, indices) -> dict:
        drift_length = self.window_size

        from_idx = indices[-1] - drift_length + 1
        to_idx = indices[-1]

        return  {
            'retrain_period': (
            from_idx,    # 시작 인덱스
            to_idx       # 마지막 인덱스
        )
        }
    