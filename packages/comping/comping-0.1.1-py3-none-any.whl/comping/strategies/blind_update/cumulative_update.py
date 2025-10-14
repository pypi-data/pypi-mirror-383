"""
Cumulative Update Strategy - Uses all historical data for retraining
"""
import numpy as np
import pandas as pd
from typing import Optional, Tuple, Any, List

from ...utils.data_handler import split_dataset, scale_fit, scale_transform, hit_ratio
from ...utils.detectors import BLIND_DETECTOR


class CumulativeUpdate:
    """
    Cumulative update strategy that uses all historical data for retraining.
    
    This strategy:
    1. Predicts in batches for efficiency
    2. Detects drift using time/index-based triggers
    3. Retrains using ALL data from start to current point
    
    Examples:
        >>> from comping.strategies.blind_update import CumulativeUpdate
        >>> from sklearn.linear_model import LogisticRegression
        >>> 
        >>> strategy = CumulativeUpdate(
        ...     model=LogisticRegression(),
        ...     period=1000,
        ...     batch_size=500
        ... )
        >>> y_pred, drift_flags = strategy.fit_predict(X, y, 0, 999)
    """
    
    def __init__(
        self,
        model: Any,
        period: int = 1000,
        batch_size: int = 500,
        index_type: str = 'int',
        day_of_month: Optional[List[int]] = None,
        scaler: Optional[Any] = None,
        measure: Optional[str] = 'ctq',
        verbose: bool = True
    ):
        """
        Initialize cumulative update strategy.
        
        Args:
            model: Sklearn-compatible model
            period: Retraining period (for index_type='int')
            batch_size: Samples to predict per batch
            index_type: 'int' or 'datetime'
            day_of_month: Days to trigger retraining (for datetime index)
            scaler: Data scaler (None for MinMaxScaler)
            measure: 'ctq' for regression, None for classification
            verbose: Print progress
        
        Raises:
            ValueError: If invalid parameters
        """
        if batch_size > period:
            raise ValueError(
                f"batch_size({batch_size}) cannot be greater than period({period})."
            )
        
        if index_type not in ('int', 'datetime'):
            raise ValueError(
                f"Invalid index_type: {index_type!r}. Must be 'int' or 'datetime'."
            )
        
        if day_of_month is not None:
            if any(d < 1 or d > 31 for d in day_of_month):
                raise ValueError("day_of_month must contain integers in [1, 31].")
        
        self.model = model
        self.period = period
        self.batch_size = batch_size
        self.index_type = index_type
        self.day_of_month = day_of_month if day_of_month is not None else [1]
        self.scaler = scaler
        self.measure = measure
        self.verbose = verbose
        
        # Initialize detector
        self.detector = BLIND_DETECTOR(index_type, day_of_month, period)
    
    def fit_predict(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        tr_start_idx: int,
        tr_end_idx: int
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Fit model and predict with cumulative retraining.
        
        Args:
            X: Feature DataFrame
            y: Target Series
            tr_start_idx: Initial training start index
            tr_end_idx: Initial training end index
        
        Returns:
            (predictions, drift_flags) tuple
        """
        if self.verbose:
            print("="*80)
            print("Cumulative Update Strategy")
            print(f"Period: {self.period}, Batch size: {self.batch_size}")
            print("="*80)
        
        y_pred = []
        drift_indices = []
        
        # Split train/test dataset
        X_tr, X_te, y_tr, y_te = split_dataset(
            X=X, y=y,
            start_idx=tr_start_idx,
            end_idx=tr_end_idx
        )
        
        # Create prediction DataFrame
        pred_df = pd.DataFrame(index=X_te.index)
        pred_df['y_true'] = y_te
        
        # Initial training
        self.scaler, X_tr_scaled = scale_fit(self.scaler, X_tr)
        self.model.fit(X_tr_scaled, y_tr)
        
        if self.verbose:
            print(f"\nInitial training: [{tr_start_idx}:{tr_end_idx}]")
            print(f"Training samples: {len(X_tr)}")
        
        current_idx = tr_end_idx + 1
        iteration = 0
        
        # Main prediction and retraining loop
        while current_idx < len(X):
            iteration += 1
            batch_start_idx = current_idx
            batch_end_idx = min(current_idx + self.batch_size, len(X)) - 1
            
            # Get batch
            X_batch = X.iloc[batch_start_idx:batch_end_idx+1, :]
            y_batch = y[batch_start_idx:batch_end_idx+1]
            X_batch_scaled = scale_transform(self.scaler, X_batch)
            
            indices = X_batch.index
            
            # Batch prediction
            y_pred_value = self.model.predict(X_batch_scaled)
            y_pred.extend(y_pred_value)
            
            # On last iteration: predict only, skip retraining
            if len(X_batch) != self.batch_size:
                break
            
            # Update training end index
            tr_end_idx = tr_end_idx + self.batch_size
            
            # Detect drift
            drift_result = self.detector.detect(indices=indices, batch_size=self.batch_size)
            drift_flag = drift_result['drift_flag']
            
            # Retrain if drift detected
            if drift_flag:
                drift_indices.append(batch_end_idx)
                
                # Cumulative: use all data from start to current point
                X_train = X.iloc[tr_start_idx:tr_end_idx+1, :]
                y_train = y[tr_start_idx:tr_end_idx+1]
                
                self.scaler, X_train_scaled = scale_fit(self.scaler, X_train)
                self.model.fit(X_train_scaled, y_train)
                
                if self.verbose:
                    print(f"\nIteration {iteration}: Drift detected at {batch_end_idx}")
                    print(f"  Retrained on [{tr_start_idx}:{tr_end_idx}]")
                    print(f"  Training samples: {len(X_train)}")
            
            elif self.verbose and iteration % 10 == 0:
                print(f"Iteration {iteration}: [{batch_start_idx}:{batch_end_idx}]")
            
            current_idx += self.batch_size
        
        # Store results
        pred_df['y_pred'] = y_pred
        pred_df['drift_flag'] = 0
        pred_df.loc[[idx for idx in drift_indices if idx in pred_df.index], 'drift_flag'] = 1
        
        if self.verbose:
            print(f"\ndrift 발생 지점: {drift_indices}")
            print(f"drift 발생 횟수: {len(drift_indices)}")
        
        # Calculate performance
        y_te_pred = pred_df['y_pred'].values
        y_te_true = pred_df['y_true'].values
        
        if self.measure is None:
            # Classification metrics
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
            
            perf_df = {
                'accuracy': float(np.round(accuracy_score(y_te_true, y_te_pred), 4)),
                'precision': float(np.round(precision_score(y_te_true, y_te_pred, average='macro', zero_division=0), 4)),
                'recall': float(np.round(recall_score(y_te_true, y_te_pred, average='macro', zero_division=0), 4)),
                'f1': float(np.round(f1_score(y_te_true, y_te_pred, average='macro', zero_division=0), 4))
            }
        else:
            # Regression metrics
            from sklearn.metrics import mean_absolute_percentage_error, mean_absolute_error, mean_squared_error, r2_score
            
            perf_df = {
                'mape': float(np.round(mean_absolute_percentage_error(y_te_true, y_te_pred) * 100, 4)),
                'mae': float(np.round(mean_absolute_error(y_te_true, y_te_pred), 4)),
                'rmse': float(np.round(np.sqrt(mean_squared_error(y_te_true, y_te_pred)), 4)),
                'r2': float(np.round(r2_score(y_te_true, y_te_pred), 4)),
                'ctq': float(np.round(hit_ratio(y_te_true, y_te_pred, np.std(y_tr)), 2))
            }
        
        if self.verbose:
            print("\nPerformance Metrics:")
            print(pd.DataFrame(perf_df, index=[0]))
            print("="*80)
        
        return pred_df['y_pred'], pred_df['drift_flag']
    
    def __repr__(self):
        return (f"CumulativeUpdate(period={self.period}, "
                f"batch_size={self.batch_size}, "
                f"index_type='{self.index_type}')")