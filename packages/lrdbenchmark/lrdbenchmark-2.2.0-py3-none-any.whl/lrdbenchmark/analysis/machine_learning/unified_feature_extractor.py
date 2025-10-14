"""
Unified Feature Extractor for ML Models

This module provides a unified feature extraction pipeline for ML models
matching pre-trained model expectations. Extracts 76 features for Random Forest,
with subset selection for other models.
"""

import numpy as np
from scipy import stats
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class UnifiedFeatureExtractor:
    """
    Unified feature extraction for ML models matching pre-trained model expectations.
    Extracts 76 features for Random Forest, with subset selection for other models.
    """
    
    @staticmethod
    def extract_features_76(data: np.ndarray) -> np.ndarray:
        """Extract comprehensive 76-feature set for LRD analysis."""
        features = []
        
        # 1. Basic Statistical Features (10 features)
        features.extend([
            np.mean(data),              # 0
            np.std(data),               # 1
            np.var(data),               # 2
            np.min(data),               # 3
            np.max(data),               # 4
            np.median(data),            # 5
            np.percentile(data, 25),    # 6
            np.percentile(data, 75),    # 7
            stats.skew(data),           # 8
            stats.kurtosis(data)        # 9
        ])
        
        # 2. Autocorrelation Features (7 lags: 1,2,5,10,20,50,100) - 7 features
        for lag in [1, 2, 5, 10, 20, 50, 100]:
            if len(data) > lag:
                autocorr = np.corrcoef(data[:-lag], data[lag:])[0, 1]
                features.append(autocorr if not np.isnan(autocorr) else 0.0)
            else:
                features.append(0.0)
        
        # 3. Multi-scale Variance of Increments (5 scales × 4 metrics) - 20 features
        scales = [1, 2, 4, 8, 16]
        for scale in scales:
            if len(data) > scale:
                increments = data[scale:] - data[:-scale]
                features.extend([
                    np.var(increments),
                    np.mean(np.abs(increments)),
                    np.std(increments),
                    np.max(increments) - np.min(increments)
                ])
            else:
                features.extend([0.0, 0.0, 0.0, 0.0])
        
        # 4. Spectral Features - 10 features
        try:
            fft = np.fft.fft(data)
            power_spectrum = np.abs(fft) ** 2
            freqs = np.fft.fftfreq(len(data))
            positive_freqs = freqs > 0
            
            # Power in frequency bands
            n = len(power_spectrum)
            features.extend([
                np.sum(power_spectrum[:n//4]) / np.sum(power_spectrum),  # Low freq
                np.sum(power_spectrum[n//4:n//2]) / np.sum(power_spectrum),  # Mid freq
                np.sum(power_spectrum[n//2:3*n//4]) / np.sum(power_spectrum),  # High freq
            ])
            
            # Spectral slope (power-law exponent)
            if np.sum(positive_freqs) > 1:
                log_freqs = np.log(freqs[positive_freqs] + 1e-10)
                log_power = np.log(power_spectrum[positive_freqs] + 1e-10)
                slope = np.polyfit(log_freqs, log_power, 1)[0]
                features.append(slope)
            else:
                features.append(0.0)
            
            # Spectral centroid and spread
            spectral_centroid = np.sum(freqs[positive_freqs] * power_spectrum[positive_freqs]) / np.sum(power_spectrum[positive_freqs])
            spectral_spread = np.sqrt(np.sum(((freqs[positive_freqs] - spectral_centroid)**2) * power_spectrum[positive_freqs]) / np.sum(power_spectrum[positive_freqs]))
            features.extend([spectral_centroid, spectral_spread])
            
            # Spectral entropy
            ps_norm = power_spectrum[positive_freqs] / np.sum(power_spectrum[positive_freqs])
            spectral_entropy = -np.sum(ps_norm * np.log(ps_norm + 1e-10))
            features.append(spectral_entropy)
            
            # Dominant frequency and its power
            dom_freq_idx = np.argmax(power_spectrum[positive_freqs])
            features.extend([
                freqs[positive_freqs][dom_freq_idx],
                power_spectrum[positive_freqs][dom_freq_idx] / np.sum(power_spectrum)
            ])
            
            # Spectral rolloff (95% power)
            cumsum_power = np.cumsum(power_spectrum[positive_freqs])
            rolloff_idx = np.where(cumsum_power >= 0.95 * cumsum_power[-1])[0]
            rolloff_freq = freqs[positive_freqs][rolloff_idx[0]] if len(rolloff_idx) > 0 else 0.0
            features.append(rolloff_freq)
            
        except:
            features.extend([0.0] * 10)
        
        # 5. DFA-inspired Features - 8 features
        try:
            # Detrended fluctuation at multiple scales
            for scale in [4, 8, 16, 32]:
                if len(data) > scale:
                    n_segments = len(data) // scale
                    fluctuations = []
                    for i in range(n_segments):
                        segment = data[i*scale:(i+1)*scale]
                        x = np.arange(len(segment))
                        trend = np.polyfit(x, segment, 1)
                        detrended = segment - (trend[0] * x + trend[1])
                        fluctuations.append(np.std(detrended))
                    features.append(np.mean(fluctuations))
                else:
                    features.append(0.0)
                    
            # Overall detrending metrics
            x = np.arange(len(data))
            trend = np.polyfit(x, data, 1)
            detrended = data - (trend[0] * x + trend[1])
            features.extend([
                np.std(detrended),
                np.mean(np.abs(detrended)),
                trend[0],  # Linear trend slope
                np.corrcoef(x, data)[0,1]  # Trend correlation
            ])
        except:
            features.extend([0.0] * 8)
        
        # 6. Wavelet-inspired Features - 6 features
        try:
            # Multi-resolution variance
            for level in [1, 2, 3]:
                if len(data) >= 2**level:
                    # Simple Haar-like decomposition
                    n = len(data) // (2**level)
                    downsampled = data[::2**level][:n]
                    features.append(np.var(downsampled))
                else:
                    features.append(0.0)
            
            # Approximate wavelet coefficients statistics
            if len(data) >= 4:
                haar_approx = (data[::2] + data[1::2]) / 2
                haar_detail = (data[::2] - data[1::2]) / 2
                features.extend([
                    np.var(haar_approx),
                    np.var(haar_detail),
                    np.mean(np.abs(haar_detail))
                ])
            else:
                features.extend([0.0, 0.0, 0.0])
        except:
            features.extend([0.0] * 6)
        
        # 7. Higher-order Statistics - 8 features
        try:
            # Moments and quantiles
            features.extend([
                np.percentile(data, 10),
                np.percentile(data, 90),
                np.percentile(data, 95) - np.percentile(data, 5),  # Inter-quantile range
                np.mean(np.abs(data - np.mean(data))),  # Mean absolute deviation
            ])
            
            # Non-linear features
            diff1 = np.diff(data)
            if len(diff1) > 0:
                features.extend([
                    np.var(diff1),
                    np.mean(np.abs(diff1)),
                    stats.skew(diff1),
                    stats.kurtosis(diff1)
                ])
            else:
                features.extend([0.0, 0.0, 0.0, 0.0])
        except:
            features.extend([0.0] * 8)
        
        # 8. Range-based Features - 7 features
        try:
            # R/S inspired features at multiple scales
            for n_segments in [2, 4, 8]:
                if len(data) >= n_segments:
                    segment_size = len(data) // n_segments
                    rs_values = []
                    for i in range(n_segments):
                        segment = data[i*segment_size:(i+1)*segment_size]
                        mean_centered = segment - np.mean(segment)
                        cumsum = np.cumsum(mean_centered)
                        R = np.max(cumsum) - np.min(cumsum)
                        S = np.std(segment)
                        rs_values.append(R / (S + 1e-10))
                    features.append(np.mean(rs_values))
                else:
                    features.append(0.0)
            
            # Overall R/S statistic
            mean_centered = data - np.mean(data)
            cumsum = np.cumsum(mean_centered)
            R = np.max(cumsum) - np.min(cumsum)
            S = np.std(data)
            features.append(R / (S + 1e-10))
            
            # Range statistics
            features.extend([
                np.max(data) - np.min(data),
                (np.max(data) - np.min(data)) / (np.std(data) + 1e-10),
                np.mean(np.abs(np.diff(data)))
            ])
        except:
            features.extend([0.0] * 7)
        
        return np.array(features[:76])  # Ensure exactly 76 features
    
    @staticmethod
    def extract_features_29(data: np.ndarray) -> np.ndarray:
        """Extract first 29 features for SVR model."""
        features_76 = UnifiedFeatureExtractor.extract_features_76(data)
        return features_76[:29]
    
    @staticmethod
    def extract_features_54(data: np.ndarray) -> np.ndarray:
        """Extract first 54 features for Gradient Boosting model."""
        features_76 = UnifiedFeatureExtractor.extract_features_76(data)
        return features_76[:54]
    
    @staticmethod
    def get_feature_names() -> List[str]:
        """Return descriptive names for all 76 features."""
        names = []
        names.extend(['mean', 'std', 'var', 'min', 'max', 'median', 'q25', 'q75', 'skew', 'kurt'])
        names.extend([f'acf_lag{lag}' for lag in [1,2,5,10,20,50,100]])
        for scale in [1,2,4,8,16]:
            names.extend([f'incr_var_s{scale}', f'incr_mae_s{scale}', f'incr_std_s{scale}', f'incr_range_s{scale}'])
        names.extend(['psd_low', 'psd_mid', 'psd_high', 'spectral_slope', 'spectral_centroid', 
                     'spectral_spread', 'spectral_entropy', 'dom_freq', 'dom_power', 'spectral_rolloff'])
        names.extend([f'dfa_scale{s}' for s in [4,8,16,32]] + ['detrend_std', 'detrend_mae', 'trend_slope', 'trend_corr'])
        names.extend([f'wavelet_var_l{l}' for l in [1,2,3]] + ['haar_approx_var', 'haar_detail_var', 'haar_detail_mae'])
        names.extend(['q10', 'q90', 'iqr', 'mad', 'diff_var', 'diff_mae', 'diff_skew', 'diff_kurt'])
        names.extend([f'rs_seg{n}' for n in [2,4,8]] + ['rs_total', 'range', 'norm_range', 'mean_abs_diff'])
        return names[:76]
    
    @staticmethod
    def get_feature_names_29() -> List[str]:
        """Return descriptive names for first 29 features."""
        return UnifiedFeatureExtractor.get_feature_names()[:29]
    
    @staticmethod
    def get_feature_names_54() -> List[str]:
        """Return descriptive names for first 54 features."""
        return UnifiedFeatureExtractor.get_feature_names()[:54]
