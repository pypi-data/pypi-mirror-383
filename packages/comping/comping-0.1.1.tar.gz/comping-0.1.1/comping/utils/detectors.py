import pandas as pd
from ..base import BaseDriftDetector

class BLIND_DETECTOR(BaseDriftDetector):
    def __init__(self, index_type, day_of_month, period):
        self.index_type = index_type
        self.day_of_month = day_of_month        # detection schedule
        self.period = period                    # detection interval
        self.counter = 0 
        self._triggered_days = {}

    def detect(self, indices, batch_size):

        drift_flag = False

        ## number index (periodic detection)
        if self.index_type == 'int':
            self.counter += batch_size

            if self.counter >= self.period:
                drift_flag = True
                self.counter = 0  
            else:
                drift_flag = False

            return {'drift_flag': drift_flag}
        

        ## datetime index (periodic detection / schedule-based detection)
        if self.index_type == 'datetime':

            # periodic detection
            if self.day_of_month is None:
                self.counter += batch_size

                if self.counter >= self.period:
                    drift_flag = True
                    self.counter = 0  
                else:
                    drift_flag = False

                return {'drift_flag': drift_flag}
            
            # schedule-based detection
            else:
                doms = set(self.day_of_month)

                for time_stamp in indices:

                    y, m, d = time_stamp.year, time_stamp.month, time_stamp.day
                    if d not in doms:
                        continue

                    key = (y, m)
                    if key not in self._triggered_days:
                        self._triggered_days[key] = set()

                    # 이 (연,월)에서 d가 처음 등장하면 트리거
                    if d not in self._triggered_days[key]:
                        self._triggered_days[key].add(d)
                        drift_flag = True

                return {'drift_flag': drift_flag}
