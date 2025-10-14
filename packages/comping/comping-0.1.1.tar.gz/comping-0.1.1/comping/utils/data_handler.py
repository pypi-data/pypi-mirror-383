"""
Data handling utilities for preprocessing and splitting
"""
import numpy as np
import pandas as pd
from typing import Tuple, Optional, Any
from sklearn.preprocessing import StandardScaler, MinMaxScaler


def split_dataset(
    X: pd.DataFrame,
    y: pd.Series,
    start_idx: int,
    end_idx: int
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Split dataset into train and test sets.
    
    Args:
        X: Feature DataFrame
        y: Target Series
        start_idx: Training start index
        end_idx: Training end index (test starts from end_idx + 1)
    
    Returns:
        X_train, X_test, y_train, y_test
    """
    X_train = X.iloc[start_idx:end_idx+1, :]
    y_train = y[start_idx:end_idx+1]
    
    X_test = X.iloc[end_idx+1:, :]
    y_test = y[end_idx+1:]
    
    return X_train, X_test, y_train, y_test


def scale_fit(
    scaler: Optional[Any],
    X: pd.DataFrame
) -> Tuple[Any, np.ndarray]:
    """
    Fit scaler and transform data.
    
    Args:
        scaler: Scaler instance (if None, creates MinMaxScaler)
        X: Feature DataFrame
    
    Returns:
        Fitted scaler and scaled data
    """
    if scaler is None:
        scaler = MinMaxScaler()
    
    X_scaled = scaler.fit_transform(X)
    
    return scaler, X_scaled


def scale_transform(
    scaler: Any,
    X: pd.DataFrame
) -> np.ndarray:
    """
    Transform data using fitted scaler.
    
    Args:
        scaler: Fitted scaler instance
        X: Feature DataFrame
    
    Returns:
        Scaled data
    """
    return scaler.transform(X)


def hit_ratio(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    std_train: float,
    tolerance: float = 1.0
) -> float:
    """
    Calculate hit ratio (CTQ metric).
    
    Percentage of predictions within tolerance * std_train of true values.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        std_train: Standard deviation of training data
        tolerance: Tolerance multiplier
    
    Returns:
        Hit ratio (0-100)
    """
    threshold = tolerance * std_train
    within_tolerance = np.abs(y_true - y_pred) <= threshold
    return np.mean(within_tolerance) * 100