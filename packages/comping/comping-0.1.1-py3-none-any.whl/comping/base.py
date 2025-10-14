class BaseDriftDetector:
    def detect(self, **kwargs) -> dict:
        """
        Detect drift based on streaming error or prediction data.
        Returns:
            dict: {
                'drift_flag': bool,
                'drift_length': int,
                'meta': dict (optional)
            }
        """
        raise NotImplementedError("This method should be implemented by subclass.")
    
class BaseDriftAdapter:
    def adapt(self, **kwargs) -> dict:
        """
        Output drift length.
        Returns:
            dict: {
                'drift length': int
                'meta': dict (optional)
            }
        """
        raise NotImplementedError("This method should be implemented by subclass.")