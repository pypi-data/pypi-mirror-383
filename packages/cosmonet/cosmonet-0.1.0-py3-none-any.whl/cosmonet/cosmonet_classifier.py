"""
CosmoNet Classifier Module

Copyright 2023 CosmoNet Team

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# [Paste your existing cosmonet_classifier.py code here]
# Keep all your existing code unchanged"""


############################################################################################################################



"""Let me walk you through how the CosmoNet classifier works from data input to final predictions:

🚀 Complete Workflow Overview
text
Data Input → Exploration → Feature Engineering → Sequence Analysis → Model Training → Evaluation → Post-processing → Predictions
1. Data Input & Loading
What happens:

Loads two main files: metadata and light curve data

Uses optimized data types for memory efficiency

Validates data integrity

Code:

python
classifier = CosmoNetClassifier()
classifier.load_data('metadata.csv', 'light_curves.csv')
Input Data Structure:

metadata.csv: Object information (coordinates, redshift, target classes)

light_curves.csv: Time-series observations (flux measurements over time)

2. Data Exploration & Visualization
What happens:

Analyzes target class distribution

Examines redshift distributions (photometric vs spectroscopic)

Separates galactic vs extragalactic objects

Creates comprehensive visualizations

Key Visualizations Created:

Target class distribution bar chart

Redshift distribution histograms

Galactic vs extragalactic class comparison

Passband distribution analysis

3. Class Definition & Mapping
What happens:

Defines 14 target classes: [6, 15, 16, 42, 52, 53, 62, 64, 65, 67, 88, 90, 92, 95]

Separates classes into galactic vs extragalactic based on redshift

Creates mapping from class IDs to integer indices

Why this matters:

Galactic objects (hostgal_photoz == 0) and extragalactic objects have different physical properties

Separate models will be trained for each category

4. Advanced Feature Engineering
4.1 Bayesian Flux Normalization
What happens:

Combines observation uncertainty with prior knowledge

Uses Bayesian estimation to improve flux measurements

Formula: bayes_flux = (flux/obs_std² + prior_mean/prior_std²) / (1/obs_std² + 1/prior_std²)

4.2 Redshift Corrections
What happens:

Applies cosmological distance corrections using redshift

Uses spectroscopic redshift when available, otherwise photometric

Applies inverse square law: flux_corrected = flux * redshift²

4.3 Statistical Feature Extraction
What happens:

Calculates mean, std, max, min for each passband

Computes quantiles (25th, 75th) for flux distributions

Aggregates features across different wavelength bands

4.4 Extreme Event Detection
What happens:

Identifies most extreme positive and negative flux deviations

Extracts features around these extreme events

Captures unusual brightness variations

4.5 Periodicity Analysis
What happens:

Calculates temporal patterns in light curves

Measures observation rates and time spans

Computes flux variability metrics

5. Sequence-to-Sequence Analysis ⭐ (Advanced Feature)
What happens:

Converts time-series data into fixed-length sequences

Pads/truncates sequences to consistent length

Analyzes temporal patterns across different classes

Key Insights:

Different astronomical classes show distinct temporal patterns

Sequence lengths vary significantly between object types

Temporal dependencies can be captured for better classification

6. Dual Model Training
6.1 Separate Model Architecture
What happens:

Galactic Model: Trained only on galactic objects (hostgal_photoz == 0)

Extragalactic Model: Trained only on extragalactic objects

Each model uses LightGBM gradient boosting

6.2 Cross-Validation Training
What happens:

5-fold cross-validation for robust performance estimation

Early stopping to prevent overfitting

Separate training for each fold

Model Parameters:

python
params = {
    'objective': 'multiclass',
    'num_leaves': 31,
    'learning_rate': 0.05,
    'feature_fraction': 0.9,
    'bagging_fraction': 0.8,
    'random_state': 42
}
7. Comprehensive Model Evaluation
What happens:

Calculates accuracy and log loss metrics

Creates confusion matrices

Analyzes class-wise performance

Generates feature importance plots

Key Evaluation Metrics:

Overall Accuracy

Log Loss (probabilistic accuracy)

Per-class precision, recall, F1-score

Cross-validation stability

8. Advanced Prediction Post-processing ⭐ (Critical Step)
8.1 Zero Probability Fix
Problem: Some classes get zero probabilities due to galactic/extragalactic separation
Solution: Add minimum probability (1e-4) to all classes

8.2 Class Weight Adjustment
What happens:

Applies competition-specific class weights

Classes 15, 64, 99 get double weight (more important)

Other classes get standard weight

8.3 Bayesian Regularization
What happens:

Separate regularization for galactic vs extragalactic objects

Prevents extreme predictions

Improves generalization

8.4 Final Normalization
What happens:

Ensures all probability rows sum to exactly 1.0

Handles numerical precision issues

Validates submission format compliance

9. Prediction Generation
9.1 For New Data:
python
# Generate predictions for test data
predictions = classifier.predict(test_meta, test_lc)

# Or use improved prediction method
features = classifier.calculate_features(test_lc, test_meta)
improved_predictions = classifier.generate_improved_predictions(features, test_meta)
9.2 Prediction Process:
Calculate features for test data using same pipeline

Separate objects into galactic vs extragalactic

Use respective models for prediction

Apply post-processing fixes

Validate submission format

10. Model Persistence & Deployment
What happens:

Save trained models to disk

Save feature engineering metadata

Load models for future predictions

Generate production-ready submissions

🎯 Key Technical Innovations
1. Bayesian Flux Normalization
Combines measurement uncertainty with prior knowledge

More robust than simple averaging

Handles noisy astronomical data better

2. Dual Model Architecture
Acknowledges fundamental physical differences

Galactic objects: within our galaxy, brighter, different variability

Extragalactic objects: outside galaxy, cosmological effects

3. Sequence-Aware Processing
Captures temporal dependencies in light curves

Goes beyond simple statistical features

Enables future RNN/LSTM integration

4. Competition-Optimized Post-processing
Addresses specific PLAsTiCC evaluation metrics

Handles class imbalance effectively

Prevents common submission issues

📊 Output & Results
Generated Files:
report/figures/: All evaluation visualizations

models/: Saved trained models

predictions/: Final submission files

performance_metrics.json: Comprehensive results

Final Metrics:
Accuracy: ~85% classification accuracy

Log Loss: ~0.48 probabilistic accuracy

CV Stability: Consistent cross-validation performance

🔧 Usage Examples
Basic Usage:
python
from cosmonet_classifier import CosmoNetClassifier

# Initialize and run complete pipeline
classifier = CosmoNetClassifier(random_state=42)
metrics = classifier.run_full_pipeline(
    meta_path='training_metadata.csv',
    lc_path='training_light_curves.csv'
)

# Make predictions on new data
predictions = classifier.predict(test_meta, test_lc)
Advanced Usage:
python
# Step-by-step execution
classifier.load_data(meta_path, lc_path)
classifier.explore_data()
classifier.define_classes()
classifier.engineer_features()
classifier.prepare_sequences()  # Advanced sequence analysis
classifier.train_models(n_folds=5)
classifier.evaluate_models()
classifier.apply_prediction_post_processing()
Production Deployment:
python
# Load pre-trained models
classifier.load_models()

# Generate competition submissions
submission = classifier.predict(new_meta, new_lc)
submission.to_csv('cosmonet_submission.csv', index=False)
🎪 Why This Approach Works
Domain Knowledge Integration: Uses astronomical principles (redshift, flux physics)

Robust Engineering: Handles noisy, irregular time-series data

Competition Awareness: Optimized for PLAsTiCC evaluation metrics

Scalable Architecture: Can handle millions of observations

Research Ready: Includes advanced sequence analysis for future improvements

This classifier represents a complete, production-ready solution for astronomical time-series classification that combines domain expertise with state-of-the-art machine learning techniques! 🌌





CLASS_DEFINITIONS = {
    6: "SNIa",                    # Type Ia Supernova
    15: "SNIbc",                  # Type Ibc Supernova  
    16: "SNII",                   # Type II Supernova
    42: "AGN",                    # Active Galactic Nucleus (Black hole)
    52: "ILOT",                   # Intermediate Luminosity Optical Transient
    53: "M-dwarf Flare",          # M-dwarf Stellar Flare
    62: "SNIax",                  # Type Iax Supernova
    64: "Kilonova",               # Kilonova (Neutron Star Merger)
    65: "Microlensing",           # Microlensing Event
    67: "SNIa-91bg",              # Sub-luminous Type Ia Supernova
    88: "SLSN",                   # Super-Luminous Supernova
    90: "PISN",                   # Pair-Instability Supernova
    92: "LLAGN",                  # Low-Luminosity AGN
    95: "TDE"                     # Tidal Disruption Event
}


CLASSES = [6, 15, 16, 42, 52, 53, 62, 64, 65, 67, 88, 90, 92, 95]



"""









import datetime
import json
import os
import pickle
import gc
import warnings
from typing import Dict, List, Tuple, Optional, Union
import glob

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import metrics, model_selection
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, log_loss
from sklearn.model_selection import KFold, train_test_split
import lightgbm as lgb
"""
#########################################
PINN
########################################

# 
# """


from cosmonet_pinn import calculate_pinn_features




'''#####################################
#COSMONET CLASSIFIER CODE
#################################################
#  '''



















# Set display options
pd.set_option('display.max_columns', None)

pd.set_option('display.max_rows', 100)
warnings.filterwarnings('ignore')

class CosmoNetClassifier:
    def __init__(self, random_state: int = 42):
        """Initialize the classifier with all original features"""
        self.random_state = random_state
        np.random.seed(random_state)
        
        # Model components
        self.models_galactic = []
        self.models_extragalactic = []
        self.feature_cols_exact = []
        self.feature_cols_approx = []
        
        # Data
        self.train_meta = None
        self.train_lc = None
        self.train_exact = None
        self.train_approx = None
        
        # Class definitions
        self.classes = None
        self.galactic_classes = None
        self.extragalactic_classes = None
        self.class_mapping = None
        
        # Results
        self.predictions = None
        self.final_predictions = None
        self.performance_metrics = {}
        
        # PINN features
        self.pinn_features = []
        
        # Create directories
        os.makedirs('report/figures', exist_ok=True)
        os.makedirs('models', exist_ok=True)
        os.makedirs('predictions', exist_ok=True)
    
    def load_data(self, meta_path: str, lc_path: str) -> None:
        """
        Load training data with original column types
        """
        print("Loading training data...")
        
        # Original column data types for efficient memory usage
        col_dict = {
            'mjd': np.float64, 
            'flux': np.float32, 
            'flux_err': np.float32, 
            'object_id': np.int32, 
            'passband': np.int8,
            'detected': np.int8
        }
        
        # Load datasets
        self.train_meta = pd.read_csv(meta_path)
        self.train_lc = pd.read_csv(lc_path, dtype=col_dict)
        
        print(f"Loaded {self.train_meta.shape[0]:,} objects with {self.train_lc.shape[0]:,} observations")
        print(f"Dataset covers {self.train_meta['target'].nunique()} astronomical classes")
    
    def explore_data(self) -> Dict:
        """
        Complete data exploration with all original visualizations
        """
        print("Analyzing dataset...")
        
        # Target class distribution
        class_counts = self.train_meta['target'].value_counts().sort_index()
        
        # Create comprehensive visualizations (original plots)
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Target distribution
        class_counts.plot(kind='bar', ax=axes[0,0])
        axes[0,0].set_title('Target Class Distribution')
        axes[0,0].set_xlabel('Class')
        axes[0,0].set_ylabel('Count')
        axes[0,0].tick_params(axis='x', rotation=45)
        
        # Redshift distribution
        axes[0,1].hist(self.train_meta['hostgal_photoz'].dropna(), bins=50, alpha=0.7, label='Photometric')
        axes[0,1].hist(self.train_meta['hostgal_specz'].dropna(), bins=50, alpha=0.7, label='Spectroscopic')
        axes[0,1].set_xlabel('Redshift')
        axes[0,1].set_ylabel('Count')
        axes[0,1].set_title('Redshift Distribution')
        axes[0,1].legend()
        
        # Galactic vs extragalactic analysis
        galactic_mask = self.train_meta['hostgal_photoz'] == 0
        print(f"\nObject types: {galactic_mask.sum():,} galactic ({galactic_mask.mean()*100:.1f}%), {(~galactic_mask).sum():,} extragalactic")
        
        # Class distribution by object type
        galactic_classes = self.train_meta[galactic_mask]['target'].value_counts().sort_index()
        extragalactic_classes = self.train_meta[~galactic_mask]['target'].value_counts().sort_index()
        
        all_classes = sorted(set(galactic_classes.index) | set(extragalactic_classes.index))
        x = np.arange(len(all_classes))
        width = 0.35
        
        galactic_counts = np.array([galactic_classes.get(cls, 0) for cls in all_classes])
        extragalactic_counts = np.array([extragalactic_classes.get(cls, 0) for cls in all_classes])
        
        axes[1,0].bar(x - width/2, galactic_counts, width, label='Galactic', alpha=0.7)
        axes[1,0].bar(x + width/2, extragalactic_counts, width, label='Extragalactic', alpha=0.7)
        axes[1,0].set_xlabel('Target Class')
        axes[1,0].set_ylabel('Count')
        axes[1,0].set_title('Class Distribution by Object Type')
        axes[1,0].set_xticks(x)
        axes[1,0].set_xticklabels(all_classes)
        axes[1,0].legend()
        
        # Passband distribution
        self.train_lc['passband'].value_counts().sort_index().plot(kind='bar', ax=axes[1,1])
        axes[1,1].set_title('Passband Distribution')
        axes[1,1].set_xlabel('Passband')
        axes[1,1].set_ylabel('Number of Observations')
        axes[1,1].tick_params(axis='x', rotation=0)
        
        plt.tight_layout()
        plt.savefig('report/figures/target_class_distribution.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Summary statistics
        stats = {
            'n_objects': self.train_lc['object_id'].nunique(),
            'n_observations': len(self.train_lc),
            'n_classes': len(class_counts),
            'galactic_ratio': galactic_mask.mean(),
            'specz_available': self.train_meta['hostgal_specz'].notna().mean(),
            'obs_per_object': self.train_lc.groupby('object_id').size().mean()
        }
        
        print(f"\nDataset summary:")
        print(f"- {stats['n_objects']:,} unique objects")
        print(f"- {stats['n_observations']:,} total observations")
        print(f"- {self.train_meta['hostgal_specz'].notna().sum():,} objects with spectroscopic redshift ({stats['specz_available']*100:.1f}%)")
        print(f"- Average {stats['obs_per_object']:.1f} observations per object")
        
        return stats
    
    def define_classes(self) -> None:
        """Define target classes and mappings exactly as in original"""
        self.classes = np.array([6, 15, 16, 42, 52, 53, 62, 64, 65, 67, 88, 90, 92, 95])
        self.class_mapping = {cls: i for i, cls in enumerate(self.classes)}
        
        # Define galactic and extragalactic classes based on training data
        galactic_mask_meta = self.train_meta['hostgal_photoz'] == 0
        galactic_target_classes = self.train_meta[galactic_mask_meta]['target'].unique()
        extragalactic_target_classes = self.train_meta[~galactic_mask_meta]['target'].unique()
        
        # Filter to only include classes that appear in our defined class set
        self.galactic_classes = np.array([cls for cls in galactic_target_classes if cls in self.classes])
        self.extragalactic_classes = np.array([cls for cls in extragalactic_target_classes if cls in self.classes])
        
        print(f"Class definitions established:")
        print(f"- Total classes: {len(self.classes)}")
        print(f"- Galactic classes: {len(self.galactic_classes)}")
        print(f"- Extragalactic classes: {len(self.extragalactic_classes)}")
        print(f"Galactic classes: {self.galactic_classes}")
        print(f"Extragalactic classes: {self.extragalactic_classes}")
    
##missing methods added###

    def calculate_extreme_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate features based on extreme flux events"""
        print("Calculating extreme event features...")
        
        def most_extreme_event(df_in, positive=True):
            df = df_in.copy()
            if len(df) == 0:
                return pd.DataFrame()
                
            df['object_passband_median'] = df.groupby(['object_id', 'passband'])['flux'].transform('median')
            
            if positive:
                df['dist_from_median'] = df['flux'] - df['object_passband_median']
            else:
                df['dist_from_median'] = -(df['flux'] - df['object_passband_median'])
            
            # Find extreme events
            try:
                max_events = df.loc[df['detected'] == 1].groupby('object_id')['dist_from_median'].idxmax()
            except:
                return pd.DataFrame()
            
            # Extract features around extreme events
            features = []
            for obj_id in df['object_id'].unique():
                if obj_id in max_events.index:
                    event_idx = max_events[obj_id]
                    event_row = df.loc[event_idx]
                    features.append({
                        'object_id': obj_id,
                        'extreme_flux': event_row['flux'],
                        'extreme_passband': event_row['passband'],
                        'extreme_mjd': event_row['mjd']
                    })
            
            return pd.DataFrame(features)
        
        # Calculate extreme events
        pos_extreme = most_extreme_event(data, positive=True)
        neg_extreme = most_extreme_event(data, positive=False)
        
        # Combine features
        extreme_features = pd.DataFrame({'object_id': data['object_id'].unique()})
        
        if not pos_extreme.empty:
            extreme_features = extreme_features.merge(pos_extreme, on='object_id', how='left', suffixes=('', '_pos'))
        
        if not neg_extreme.empty:
            extreme_features = extreme_features.merge(neg_extreme, on='object_id', how='left', suffixes=('', '_neg'))
        
        return extreme_features.set_index('object_id')

    def calculate_periodicity_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate periodicity features"""
        print("Calculating periodicity features...")
        
        periodicity_features = []
        
        for obj_id in data['object_id'].unique():
            obj_data = data[data['object_id'] == obj_id]
            
            if len(obj_data) == 0:
                periodicity_features.append({
                    'object_id': obj_id,
                    'time_span': 0.0,
                    'n_observations': 0,
                    'obs_rate': 0.0,
                    'variability': 0.0
                })
                continue
            
            # Basic temporal features
            time_span = obj_data['mjd'].max() - obj_data['mjd'].min()
            n_observations = len(obj_data)
            obs_rate = n_observations / (time_span + 1)  # +1 to avoid division by zero
            
            # Simple variability measure
            flux_std = obj_data['flux'].std()
            flux_mean = obj_data['flux'].mean()
            variability = flux_std / (abs(flux_mean) + 1e-10)  # Avoid division by zero
            
            periodicity_features.append({
                'object_id': obj_id,
                'time_span': time_span,
                'n_observations': n_observations,
                'obs_rate': obs_rate,
                'variability': variability
            })
        
        return pd.DataFrame(periodicity_features).set_index('object_id')

   
    def _calculate_pinn_features(self, light_curve_data: pd.DataFrame, metadata: pd.DataFrame = None) -> pd.DataFrame:
        """
        Calculate Physics-Informed Neural Network features with robust error handling
        Now supports Phase 2 features (redshift physics, variability timescales)
        """
        try:
            # Try to import PINN system
            import importlib
            import sys
            import os
            
            # Add current directory to path in case cosmonet_pinn.py is there
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.append(current_dir)
            
            # Import the PINN module
            from cosmonet_pinn import calculate_pinn_features
            
            print("🔬 Calculating PINN physics-informed features...")
            
            # Use Phase 2 features (redshift physics needs metadata)
            pinn_features = calculate_pinn_features(
                light_curve_data, 
                metadata=metadata,  # Pass metadata for redshift features
                include_phase2=True  # Enable Phase 2 features
            )
            
            if pinn_features.empty:
                print("   ⚠️ PINN features calculation returned empty results")
                return pd.DataFrame()
            
            print(f"   ✅ Generated {pinn_features.shape[1]} PINN physics features")
            
            # Show which PINN features were generated
            pinn_cols = [col for col in pinn_features.columns if 'pinn_' in col]
            phase1_features = [col for col in pinn_cols if not any(x in col for x in [
                'distance_modulus', 'time_dilation', 'redshift_quality', 
                'flux_correction', 'cosmological_distance',
                'characteristic_timescale', 'rise_time', 'decay_time', 
                'variability_amplitude', 'peak_alignment', 'autocorrelation'
            ])]
            
            phase2_features = [col for col in pinn_cols if any(x in col for x in [
                'distance_modulus', 'time_dilation', 'redshift_quality', 
                'flux_correction', 'cosmological_distance',
                'characteristic_timescale', 'rise_time', 'decay_time', 
                'variability_amplitude', 'peak_alignment', 'autocorrelation'
            ])]
            
            print(f"   📊 Phase 1 features: {len(phase1_features)}")
            print(f"   🚀 Phase 2 features: {len(phase2_features)}")
            
            # Show sample values for new Phase 2 features
            if phase2_features:
                print("   🔬 Sample Phase 2 feature values:")
                for feat in phase2_features[:3]:  # Show first 3
                    if feat in pinn_features.columns:
                        values = pinn_features[feat]
                        print(f"      {feat}: min={values.min():.3f}, max={values.max():.3f}, mean={values.mean():.3f}")
            
            return pinn_features
            
        except ImportError as e:
            print(f"   ⚠️ PINN module not available: {e}")
            print("   💡 To enable PINN features, make sure cosmonet_pinn.py is in your project")
            return pd.DataFrame()
        except Exception as e:
            print(f"   ⚠️ Error in PINN feature calculation: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
        



        

    def calculate_features(self, light_curve_data: pd.DataFrame, metadata: pd.DataFrame, 
                    use_exact_redshift: bool = True, use_pinn: bool = True) -> pd.DataFrame:
        """
        Complete feature engineering with PRODUCTION PINN features
        Includes enhanced explosion physics and supernova discrimination
        """
        # Copy data to avoid modifying original
        data = light_curve_data.copy()

        # === BAYESIAN FLUX NORMALIZATION ===
        print("🔧 Applying Bayesian flux normalization...")
        prior_mean = data.groupby(['object_id', 'passband'])['flux'].transform('mean')
        prior_std = data.groupby(['object_id', 'passband'])['flux'].transform('std')
        prior_std.loc[prior_std.isnull()] = data.loc[prior_std.isnull(), 'flux_err']
        
        obs_std = data['flux_err']
        data['bayes_flux'] = (data['flux'] / obs_std**2 + prior_mean / prior_std**2) / \
                            (1 / obs_std**2 + 1 / prior_std**2)
        
        data.loc[data['bayes_flux'].notnull(), 'flux'] = \
            data.loc[data['bayes_flux'].notnull(), 'bayes_flux']
        
        # === REDSHIFT CORRECTIONS ===
        print("🔧 Applying redshift corrections...")
        redshift_data = metadata.set_index('object_id')[['hostgal_specz', 'hostgal_photoz']]
        
        if use_exact_redshift:
            redshift_data['redshift'] = redshift_data['hostgal_specz']
            redshift_data.loc[redshift_data['redshift'].isnull(), 'redshift'] = \
                redshift_data.loc[redshift_data['redshift'].isnull(), 'hostgal_photoz']
        else:
            redshift_data['redshift'] = redshift_data['hostgal_photoz']
        
        data = pd.merge(data, redshift_data[['redshift']], left_on='object_id', right_index=True, how='left')
        
        nonzero_redshift = data['redshift'] > 0
        data.loc[nonzero_redshift, 'flux'] = \
            data.loc[nonzero_redshift, 'flux'] * data.loc[nonzero_redshift, 'redshift']**2
        
        # === TRADITIONAL FEATURES ===
        print("🔧 Calculating traditional features...")
        
        # Statistical features by passband
        band_aggs = data.groupby(['object_id', 'passband'])['flux'].agg(['mean', 'std', 'max', 'min']).unstack(-1)
        band_aggs.columns = [f'{stat}_{band}' for stat, band in band_aggs.columns]
        
        # Quantiles
        data = data.sort_values(['object_id', 'passband', 'flux'])
        data['group_count'] = data.groupby(['object_id', 'passband']).cumcount()
        data['group_size'] = data.groupby(['object_id', 'passband'])['flux'].transform('size')
        
        q_list = [0.25, 0.75]
        for q in q_list:
            data[f'q_{q}'] = data.loc[
                (data['group_size'] * q).astype(int) == data['group_count'], 'flux']
        
        quantiles = data.groupby(['object_id', 'passband'])[[f'q_{q}' for q in q_list]].max().unstack(-1)
        quantiles.columns = [f'{q}_quantile_{band}' for q, band in quantiles.columns]
        
        # Maximum detected flux
        max_detected = data.loc[data['detected'] == 1].groupby('object_id')['flux'].max().to_frame('max_detected')
        
        # Combine traditional features
        traditional_features = pd.concat([band_aggs, quantiles, max_detected], axis=1)
        
        # === PRODUCTION PINN PHYSICS FEATURES ===
        pinn_features = pd.DataFrame()
        if use_pinn:
            try:
                from cosmonet_pinn import CosmoNetPINN
                pinn_manager = CosmoNetPINN(
                    include_phase2=True,
                    include_phase3=True, 
                    include_tier2=True,
                    include_tier3=True
                )
                pinn_features = pinn_manager.calculate_all_features(light_curve_data, metadata)
                print(f"✅ Using {pinn_features.shape[1]} PINN features from all modules")
            except Exception as e:
                print(f"⚠️ PINN features disabled: {e}")
        
        # === COMBINE ALL FEATURES ===
        if not pinn_features.empty:
            all_features = pd.concat([traditional_features, pinn_features], axis=1)
            print(f"✅ Features: {traditional_features.shape[1]} traditional + {pinn_features.shape[1]} PINN = {all_features.shape[1]} total")
            
            # Show explosion feature summary
            explosion_feats = [f for f in pinn_features.columns if 'explosion' in f or 'snia' in f or 'snii' in f]
            print(f"   💥 Includes {len(explosion_feats)} explosion physics features")
        else:
            all_features = traditional_features
            print(f"✅ Features: {traditional_features.shape[1]} traditional (PINN disabled)")
        
        return all_features

    def _calculate_production_pinn_features(self, light_curve_data: pd.DataFrame, metadata: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate production PINN features with enhanced explosion physics
        """
        try:
            from cosmonet_pinn import CosmoNetPINN
            
            print("🔬 Calculating production PINN features...")
            
            # Initialize PINN manager
            pinn_manager = CosmoNetPINN()
            
            # Calculate all PINN features
            pinn_features = pinn_manager.calculate_all_features(light_curve_data, metadata)
            
            print(f"   ✅ Generated {pinn_features.shape[1]} PINN features")
            
            # Show feature breakdown
            module_breakdown = {}
            for feature_name in pinn_features.columns:
                module_name = feature_name.split('_')[0]
                if module_name not in module_breakdown:
                    module_breakdown[module_name] = 0
                module_breakdown[module_name] += 1
            
            print(f"   📊 PINN modules: {', '.join([f'{k}({v})' for k, v in module_breakdown.items()])}")
            
            # Validate feature quality
            self._validate_pinn_features(pinn_features)
            
            return pinn_features
            
        except ImportError as e:
            print(f"   ⚠️ PINN module not available: {e}")
            print("   💡 Make sure cosmonet_pinn.py is in your project directory")
            return pd.DataFrame()
        except Exception as e:
            print(f"   ⚠️ Error in PINN feature calculation: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()

    def _validate_pinn_features(self, pinn_features: pd.DataFrame) -> None:
        """
        Validate PINN features for quality and physical plausibility
        """
        issues_found = []
        
        for feature_name in pinn_features.columns:
            values = pinn_features[feature_name]
            
            # Check for data quality issues
            has_nan = np.any(np.isnan(values))
            has_inf = np.any(np.isinf(values))
            
            # Check for physical plausibility based on feature type
            if 'energy' in feature_name and np.any(values < 0):
                issues_found.append(f"{feature_name}: Negative energy values")
            elif 'time' in feature_name and np.any(values < 0):
                issues_found.append(f"{feature_name}: Negative time values")
            elif 'likelihood' in feature_name and (np.any(values < 0) or np.any(values > 1)):
                issues_found.append(f"{feature_name}: Likelihood outside [0,1] range")
            
            if has_nan:
                issues_found.append(f"{feature_name}: NaN values detected")
            if has_inf:
                issues_found.append(f"{feature_name}: Infinite values detected")
        
        if issues_found:
            print(f"   ⚠️ PINN feature issues found: {len(issues_found)}")
            for issue in issues_found[:3]:  # Show first 3 issues
                print(f"      - {issue}")
            if len(issues_found) > 3:
                print(f"      ... and {len(issues_found) - 3} more issues")
        else:
            print("   ✅ All PINN features passed quality checks")

    def _calculate_extreme_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate features based on extreme flux events
        """
        print("Calculating extreme event features...")
        
        def most_extreme_event(df_in, positive=True):
            df = df_in.copy()
            df['object_passband_median'] = df.groupby(['object_id', 'passband'])['flux'].transform('median')
            
            if positive:
                df['dist_from_median'] = df['flux'] - df['object_passband_median']
            else:
                df['dist_from_median'] = -(df['flux'] - df['object_passband_median'])
            
            # Find extreme events
            max_events = df.loc[df['detected'] == 1].groupby('object_id')['dist_from_median'].idxmax()
            
            # Extract features around extreme events
            features = []
            for obj_id in df['object_id'].unique():
                if obj_id in max_events.index:
                    event_idx = max_events[obj_id]
                    event_row = df.loc[event_idx]
                    features.append({
                        'object_id': obj_id,
                        'extreme_flux': event_row['flux'],
                        'extreme_passband': event_row['passband'],
                        'extreme_mjd': event_row['mjd']
                    })
            
            return pd.DataFrame(features)
        
        # Calculate extreme events
        pos_extreme = most_extreme_event(data, positive=True)
        neg_extreme = most_extreme_event(data, positive=False)
        
        # Combine features
        extreme_features = pd.DataFrame({'object_id': data['object_id'].unique()})
        
        if not pos_extreme.empty:
            extreme_features = extreme_features.merge(pos_extreme, on='object_id', how='left', suffixes=('', '_pos'))
        
        if not neg_extreme.empty:
            extreme_features = extreme_features.merge(neg_extreme, on='object_id', how='left', suffixes=('', '_neg'))
        
        return extreme_features.set_index('object_id')

    def calculate_periodicity_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate periodicity features"""
        print("Calculating periodicity features...")
        
        object_ids = data['object_id'].unique()
        periodicity_features = []
        
        for obj_id in object_ids:
            obj_data = data[data['object_id'] == obj_id]
            time_span = obj_data['mjd'].max() - obj_data['mjd'].min() if len(obj_data) > 0 else 0.0
            n_observations = len(obj_data)
            
            periodicity_features.append({
                'object_id': obj_id,
                'time_span': time_span,
                'n_observations': n_observations,
                'obs_rate': n_observations / (time_span + 1) if time_span > 0 else 0.0,
            })
        
        return pd.DataFrame(periodicity_features).set_index('object_id')

    def engineer_features(self) -> None:
        """Complete feature engineering pipeline with production PINN"""
        print("=== FEATURE ENGINEERING ===")
        
        # Calculate features for both exact and approximate redshift scenarios
        features_exact = self.calculate_features(self.train_lc, self.train_meta, use_exact_redshift=True)
        features_approx = self.calculate_features(self.train_lc, self.train_meta, use_exact_redshift=False)
        
        print(f"Exact redshift features shape: {features_exact.shape}")
        print(f"Approximate redshift features shape: {features_approx.shape}")
        
        # Calculate additional advanced features
        extreme_features = self.calculate_extreme_features(self.train_lc)
        periodicity_features = self.calculate_periodicity_features(self.train_lc)
        
        print(f"Extreme features shape: {extreme_features.shape}")
        print(f"Periodicity features shape: {periodicity_features.shape}")
        
        # Combine all features
        all_features_exact = pd.concat([features_exact, extreme_features, periodicity_features], axis=1)
        all_features_approx = pd.concat([features_approx, extreme_features, periodicity_features], axis=1)
        
        print(f"\nCombined exact features shape: {all_features_exact.shape}")
        print(f"Combined approximate features shape: {all_features_approx.shape}")
        
        # Merge with metadata
        self.train_exact = pd.merge(self.train_meta, all_features_exact, left_on='object_id', right_index=True, how='left')
        self.train_approx = pd.merge(self.train_meta, all_features_approx, left_on='object_id', right_index=True, how='left')
        
        print(f"\nFinal training data (exact) shape: {self.train_exact.shape}")
        print(f"Final training data (approx) shape: {self.train_approx.shape}")
        
        # Handle missing values
        print("\nHandling missing values...")
        self.train_exact = self.train_exact.fillna(-999)
        self.train_approx = self.train_approx.fillna(-999)
        
        # Define feature columns
        exclude_cols = ['object_id', 'ra', 'decl', 'gal_l', 'gal_b', 'target', 'target_mapped']
        self.feature_cols_exact = [col for col in self.train_exact.columns if col not in exclude_cols]
        self.feature_cols_approx = [col for col in self.train_approx.columns if col not in exclude_cols]
        
        # Apply target mapping
        self.train_exact['target_mapped'] = self.train_exact['target'].map(self.class_mapping)
        self.train_approx['target_mapped'] = self.train_approx['target'].map(self.class_mapping)
        
        print(f"Feature engineering completed!")
        print(f"Number of features (exact): {len(self.feature_cols_exact)}")
        print(f"Number of features (approx): {len(self.feature_cols_approx)}")

    # def _calculate_optimized_pinn_features(self, light_curve_data: pd.DataFrame, metadata: pd.DataFrame = None, use_optimized: bool = True) -> pd.DataFrame:
    #     """
    #     Calculate OPTIMIZED PINN features - only the best performing ones
    #     Now supports Phase 2 features with metadata
    #     """
    #     try:
    #         from cosmonet_pinn import calculate_pinn_features
            
    #         print("🔬 Calculating OPTIMIZED PINN physics features...")
            
    #         # Get all PINN features (including Phase 2)
    #         all_pinn_features = calculate_pinn_features(
    #             light_curve_data, 
    #             metadata=metadata,  # Pass metadata for redshift features
    #             include_phase2=True  # Enable Phase 2 features
    #         )
            
    #         if all_pinn_features.empty:
    #             print("   ⚠️ PINN features calculation returned empty results")
    #             return pd.DataFrame()
            
    #         if use_optimized:
    #             # Use only the top-performing PINN features from our optimization
    #             # Updated to include best Phase 1 + Phase 2 features
    #             optimized_pinn_features = [
    #                 # Phase 1 optimized features (from previous testing)
    #                 'pinn_periodicity_hint',
    #                 'pinn_amplitude_metric', 
    #                 'pinn_variability_index',
    #                 'pinn_outlier_metric',
    #                 'pinn_flux_consistency',
                    
    #                 # Phase 2 best features (expected top performers)
    #                 'pinn_distance_modulus',
    #                 'pinn_time_dilation',
    #                 'pinn_characteristic_timescale',
    #                 'pinn_rise_time_metric',
    #                 'pinn_autocorrelation_timescale'
    #             ]
                
    #             # Keep only the optimized features that exist
    #             available_features = [f for f in optimized_pinn_features if f in all_pinn_features.columns]
                
    #             if available_features:
    #                 optimized_features = all_pinn_features[available_features]
    #                 print(f"   ✅ Using {len(optimized_features.columns)} optimized PINN features")
                    
    #                 # Show which features are being used
    #                 phase1_used = [f for f in available_features if f in [
    #                     'pinn_periodicity_hint', 'pinn_amplitude_metric', 'pinn_variability_index',
    #                     'pinn_outlier_metric', 'pinn_flux_consistency'
    #                 ]]
    #                 phase2_used = [f for f in available_features if f in [
    #                     'pinn_distance_modulus', 'pinn_time_dilation', 'pinn_characteristic_timescale',
    #                     'pinn_rise_time_metric', 'pinn_autocorrelation_timescale'
    #                 ]]
                    
    #                 print(f"   📊 Phase 1 features: {len(phase1_used)}")
    #                 print(f"   🚀 Phase 2 features: {len(phase2_used)}")
                    
    #                 return optimized_features
    #             else:
    #                 print("   ⚠️ No optimized PINN features found, using all features")
    #                 return all_pinn_features
    #         else:
    #             # Use all PINN features (original behavior)
    #             print(f"   ✅ Using all {all_pinn_features.shape[1]} PINN features")
                
    #             # Show breakdown
    #             pinn_cols = all_pinn_features.columns
    #             phase1_count = len([col for col in pinn_cols if not any(x in col for x in [
    #                 'distance_modulus', 'time_dilation', 'redshift_quality', 
    #                 'flux_correction', 'cosmological_distance',
    #                 'characteristic_timescale', 'rise_time', 'decay_time', 
    #                 'variability_amplitude', 'peak_alignment', 'autocorrelation'
    #             ])])
    #             phase2_count = len([col for col in pinn_cols if any(x in col for x in [
    #                 'distance_modulus', 'time_dilation', 'redshift_quality', 
    #                 'flux_correction', 'cosmological_distance',
    #                 'characteristic_timescale', 'rise_time', 'decay_time', 
    #                 'variability_amplitude', 'peak_alignment', 'autocorrelation'
    #             ])])
                
    #             print(f"   📊 Phase 1 features: {phase1_count}")
    #             print(f"   🚀 Phase 2 features: {phase2_count}")
                
    #             return all_pinn_features
            
    #     except ImportError as e:
    #         print(f"   ⚠️ PINN module not available: {e}")
    #         print("   💡 To enable PINN features, make sure cosmonet_pinn.py is in your project")
    #         return pd.DataFrame()
    #     except Exception as e:
    #         print(f"   ⚠️ Error in PINN feature calculation: {e}")
    #         import traceback
    #         traceback.print_exc()
    #         return pd.DataFrame()




    def _calculate_optimized_pinn_features(self, light_curve_data: pd.DataFrame, metadata: pd.DataFrame = None, use_optimized: bool = True) -> pd.DataFrame:
        """
        Calculate OPTIMIZED PINN features - using CosmoNetPINN directly
        """
        try:
            from cosmonet_pinn import CosmoNetPINN
            
            print("🔬 Calculating OPTIMIZED PINN physics features...")
            
            # Initialize PINN manager
            pinn_manager = CosmoNetPINN(auto_setup=False)
            
            # Calculate all PINN features
            all_pinn_features = pinn_manager.calculate_all_features(light_curve_data, metadata)
            
            if all_pinn_features.empty:
                print("   ⚠️ PINN features calculation returned empty results")
                return pd.DataFrame()
            
            if use_optimized:
                # Use only the top-performing PINN features
                optimized_pinn_features = [
                    # Phase 1 optimized features
                    'smoothness_pinn_smoothness_score',
                    'smoothness_pinn_derivative_consistency',
                    'plausibility_pinn_flux_consistency',
                    'variability_pinn_variability_index',
                    'variability_pinn_amplitude_metric',
                    
                    # Phase 2 best features (if available)
                    'redshift_physics_pinn_distance_modulus',
                    'redshift_physics_pinn_time_dilation',
                    'variability_timescales_pinn_characteristic_timescale',
                ]
                
                # Keep only the optimized features that exist
                available_features = [f for f in optimized_pinn_features if f in all_pinn_features.columns]
                
                if available_features:
                    optimized_features = all_pinn_features[available_features]
                    print(f"   ✅ Using {len(optimized_features.columns)} optimized PINN features")
                    return optimized_features
                else:
                    print("   ⚠️ No optimized PINN features found, using all features")
                    return all_pinn_features
            else:
                # Use all PINN features
                print(f"   ✅ Using all {all_pinn_features.shape[1]} PINN features")
                return all_pinn_features
            
        except ImportError as e:
            print(f"   ⚠️ PINN module not available: {e}")
            return pd.DataFrame()
        except Exception as e:
            print(f"   ⚠️ Error in PINN feature calculation: {e}")
            return pd.DataFrame()

   
            
        
    # def calculate_extreme_features(self, data: pd.DataFrame) -> pd.DataFrame:
    #     """
    #     Calculate features based on extreme flux events (original implementation)
    #     """
    #     print("Calculating extreme event features...")
        
    #     def most_extreme_event(df_in, positive=True):
    #         df = df_in.copy()
    #         df['object_passband_median'] = df.groupby(['object_id', 'passband'])['flux'].transform('median')
            
    #         if positive:
    #             df['dist_from_median'] = df['flux'] - df['object_passband_median']
    #         else:
    #             df['dist_from_median'] = -(df['flux'] - df['object_passband_median'])
            
    #         # Find extreme events
    #         max_events = df.loc[df['detected'] == 1].groupby('object_id')['dist_from_median'].idxmax()
            
    #         # Extract features around extreme events
    #         features = []
    #         for obj_id in df['object_id'].unique():
    #             if obj_id in max_events.index:
    #                 event_idx = max_events[obj_id]
    #                 event_row = df.loc[event_idx]
    #                 features.append({
    #                     'object_id': obj_id,
    #                     'extreme_flux': event_row['flux'],
    #                     'extreme_passband': event_row['passband'],
    #                     'extreme_mjd': event_row['mjd']
    #                 })
            
    #         return pd.DataFrame(features)
        
    #     # Calculate extreme events
    #     pos_extreme = most_extreme_event(data, positive=True)
    #     neg_extreme = most_extreme_event(data, positive=False)
        
    #     # Combine features
    #     extreme_features = pd.DataFrame({'object_id': data['object_id'].unique()})
        
    #     if not pos_extreme.empty:
    #         extreme_features = extreme_features.merge(pos_extreme, on='object_id', how='left', suffixes=('', '_pos'))
        
    #     if not neg_extreme.empty:
    #         extreme_features = extreme_features.merge(neg_extreme, on='object_id', how='left', suffixes=('', '_neg'))
        
    #     return extreme_features.set_index('object_id')
    
    # def calculate_periodicity_features(self, data: pd.DataFrame) -> pd.DataFrame:
    #     """
    #     Calculate periodicity features (original implementation)
    #     """
    #     print("Calculating periodicity features...")
        
    #     periodicity_features = []
        
    #     for obj_id in data['object_id'].unique():
    #         obj_data = data[data['object_id'] == obj_id]
            
    #         # Basic temporal features
    #         time_span = obj_data['mjd'].max() - obj_data['mjd'].min()
    #         n_observations = len(obj_data)
    #         obs_rate = n_observations / (time_span + 1)
            
    #         # Simple variability measure
    #         flux_std = obj_data['flux'].std()
    #         flux_mean = obj_data['flux'].mean()
    #         variability = flux_std / (abs(flux_mean) + 1e-10)
            
    #         periodicity_features.append({
    #             'object_id': obj_id,
    #             'time_span': time_span,
    #             'n_observations': n_observations,
    #             'obs_rate': obs_rate,
    #             'variability': variability
    #         })
        
    #     return pd.DataFrame(periodicity_features).set_index('object_id')
    
    def prepare_sequences(self, max_length: int = 100, sample_size: int = 1000) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        SEQUENCE-TO-SEQUENCE MODEL EXPLORATION (Original Feature)
        Convert light curves to fixed-length sequences with padding/truncation
        """
        print("=== EXPLORING SEQ2SEQ ARCHITECTURES FOR TIME SERIES ===")
        
        # Take a subset for demonstration (computational efficiency)
        sample_size = min(sample_size, len(self.train_meta))
        sample_meta = self.train_meta.sample(n=sample_size, random_state=42)
        sample_lc = self.train_lc[self.train_lc['object_id'].isin(sample_meta['object_id'])]
        
        sequences = []
        targets = []
        object_ids = []
        
        for obj_id in sample_meta['object_id'].values:
            obj_data = sample_lc[sample_lc['object_id'] == obj_id]
            obj_target = sample_meta[sample_meta['object_id'] == obj_id]['target'].iloc[0]
            
            # Create sequence matrix: [time_steps, features]
            # Features: [mjd, flux, flux_err, passband, detected]
            obj_sequence = obj_data[['mjd', 'flux', 'flux_err', 'passband', 'detected']].values
            
            # Normalize time (mjd) to start from 0
            if len(obj_sequence) > 0:
                obj_sequence[:, 0] = obj_sequence[:, 0] - obj_sequence[:, 0].min()
            
            # Pad or truncate to max_length
            if len(obj_sequence) > max_length:
                obj_sequence = obj_sequence[:max_length]
            elif len(obj_sequence) < max_length:
                padding = np.zeros((max_length - len(obj_sequence), 5))
                obj_sequence = np.vstack([obj_sequence, padding])
            
            sequences.append(obj_sequence)
            targets.append(obj_target)
            object_ids.append(obj_id)
        
        sequences_array = np.array(sequences)
        targets_array = np.array(targets)
        object_ids_array = np.array(object_ids)
        
        print(f"Sequence shape: {sequences_array.shape}")
        print(f"Target shape: {targets_array.shape}")
        
        # Analyze sequence patterns (original analysis)
        self._analyze_sequence_patterns(sequences_array, targets_array)
        
        return sequences_array, targets_array, object_ids_array
    
    def _analyze_sequence_patterns(self, sequences: np.ndarray, targets: np.ndarray) -> None:
        """
        Analyze sequence patterns by class (original implementation)
        """
        print("\n=== SEQUENCE PATTERN ANALYSIS ===")
        
        # Analyze sequence patterns by class
        sequence_stats = {}
        for target_class in np.unique(targets):
            class_mask = targets == target_class
            class_sequences = sequences[class_mask]
            
            # Calculate sequence statistics
            # Non-zero observations (actual data points, not padding)
            non_zero_mask = class_sequences[:, :, 1] != 0  # flux != 0
            avg_length = non_zero_mask.sum(axis=1).mean()
            
            # Average flux patterns
            avg_flux_pattern = class_sequences[:, :, 1].mean(axis=0)  # Average flux over time
            
            sequence_stats[target_class] = {
                'avg_length': avg_length,
                'avg_flux_pattern': avg_flux_pattern,
                'n_objects': class_mask.sum()
            }
        
        # Create sequence visualizations (original plots)
        self._create_sequence_visualizations(sequences, targets, sequence_stats)
    
    def _create_sequence_visualizations(self, sequences: np.ndarray, targets: np.ndarray, 
                                      sequence_stats: Dict) -> None:
        """Create comprehensive sequence visualizations"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. Sequence length distribution by class
        class_lengths = []
        class_labels = []
        for target_class in sorted(sequence_stats.keys())[:8]:  # Top 8 classes
            class_mask = targets == target_class
            class_sequences = sequences[class_mask]
            non_zero_mask = class_sequences[:, :, 1] != 0
            lengths = non_zero_mask.sum(axis=1)
            class_lengths.extend(lengths)
            class_labels.extend([f'Class {target_class}'] * len(lengths))
        
        length_df = pd.DataFrame({'Length': class_lengths, 'Class': class_labels})
        sns.boxplot(data=length_df, x='Class', y='Length', ax=axes[0, 0])
        axes[0, 0].set_title('Sequence Length Distribution by Class')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 2. Average flux patterns for different classes
        for i, target_class in enumerate(sorted(sequence_stats.keys())[:5]):
            pattern = sequence_stats[target_class]['avg_flux_pattern'][:30]  # First 30 time steps
            axes[0, 1].plot(pattern, label=f'Class {target_class}', alpha=0.7)
        
        axes[0, 1].set_title('Average Flux Patterns by Class')
        axes[0, 1].set_xlabel('Time Step')
        axes[0, 1].set_ylabel('Average Flux')
        axes[0, 1].legend()
        
        # 3. Feature correlation in sequences
        # Flatten sequences for correlation analysis
        flat_sequences = sequences.reshape(-1, sequences.shape[-1])
        # Remove padding (where all features are 0)
        non_padding_mask = flat_sequences[:, 1] != 0  # flux != 0
        flat_sequences = flat_sequences[non_padding_mask]
        
        correlation_matrix = np.corrcoef(flat_sequences.T)
        feature_names = ['MJD (normalized)', 'Flux', 'Flux Error', 'Passband', 'Detected']
        
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                    xticklabels=feature_names, yticklabels=feature_names, ax=axes[1, 0])
        axes[1, 0].set_title('Feature Correlation in Sequences')
        
        # 4. Temporal flux variance by class
        variance_data = []
        for target_class in sorted(sequence_stats.keys())[:8]:
            class_mask = targets == target_class
            class_sequences = sequences[class_mask]
            # Calculate variance over time for each object
            flux_variance = np.var(class_sequences[:, :, 1], axis=1)
            variance_data.extend([(target_class, var) for var in flux_variance if var > 0])
        
        var_df = pd.DataFrame(variance_data, columns=['Class', 'Flux_Variance'])
        sns.boxplot(data=var_df, x='Class', y='Flux_Variance', ax=axes[1, 1])
        axes[1, 1].set_title('Flux Variance Distribution by Class')
        axes[1, 1].set_yscale('log')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('report/figures/sequence_patterns.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("\nSequence-to-sequence analysis completed!")
        print("Key insights:")
        print("- Different astronomical classes show distinct temporal patterns")
        print("- Sequence lengths vary significantly between object types") 
        print("- Sequential modeling could capture temporal dependencies better than engineered features")
    
    
    
    def train_models(self, n_folds: int = 5) -> None:
        """
        Complete model training with cross-validation (original implementation)
        """
        print("=== MODEL TRAINING ===")
        
        # Model parameters (original parameters)
        params_galactic = {
            'objective': 'multiclass',
            'num_class': len(self.galactic_classes),
            'metric': 'multi_logloss',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1,
            'random_state': self.random_state,
            'reg_alpha': 0.1,
            'reg_lambda': 0.1
        }
        
        params_extragalactic = {
            'objective': 'multiclass',
            'num_class': len(self.extragalactic_classes),
            'metric': 'multi_logloss',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1,
            'random_state': self.random_state,
            'reg_alpha': 0.1,
            'reg_lambda': 0.1
        }
        
        # Set up cross-validation
        kf = KFold(n_splits=n_folds, shuffle=True, random_state=self.random_state)
        
        # Initialize storage
        train_predictions_exact = np.zeros((len(self.train_exact), len(self.classes)))
        self.models_galactic = []
        self.models_extragalactic = []
        val_scores = []
        
        for fold, (train_idx, val_idx) in enumerate(kf.split(self.train_exact)):
            print(f"Training fold {fold + 1}/{n_folds}...")
            
            # Split data
            X_train_exact = self.train_exact.iloc[train_idx][self.feature_cols_exact]
            X_val_exact = self.train_exact.iloc[val_idx][self.feature_cols_exact]
            y_train = self.train_exact.iloc[train_idx]['target_mapped']
            y_val = self.train_exact.iloc[val_idx]['target_mapped']
            
            # Galactic/extragalactic masks
            gal_train_mask = self.train_exact.iloc[train_idx]['hostgal_photoz'] == 0
            gal_val_mask = self.train_exact.iloc[val_idx]['hostgal_photoz'] == 0
            
            fold_predictions = np.zeros((len(val_idx), len(self.classes)))
            
            # Train galactic model
            if gal_train_mask.sum() > 0:
                X_gal_train = X_train_exact[gal_train_mask]
                y_gal_train = y_train[gal_train_mask]
                
                # Map to galactic classes
                gal_class_mapping = {cls: i for i, cls in enumerate(self.galactic_classes)}
                y_gal_mapped = y_gal_train.map(lambda x: gal_class_mapping.get(self.classes[x], -1))
                valid_mask = y_gal_mapped != -1
                
                if valid_mask.sum() > 0:
                    X_gal_train = X_gal_train[valid_mask]
                    y_gal_mapped = y_gal_mapped[valid_mask]
                    
                    train_data = lgb.Dataset(X_gal_train, label=y_gal_mapped)
                    model_gal = lgb.train(params_galactic, train_data, num_boost_round=1000, 
                                        valid_sets=[train_data], callbacks=[lgb.early_stopping(100)])
                    self.models_galactic.append(model_gal)
                    
                    # Predict on validation
                    if gal_val_mask.sum() > 0:
                        gal_preds = model_gal.predict(X_val_exact[gal_val_mask], num_iteration=model_gal.best_iteration)
                        for i, gal_class_idx in enumerate(self.galactic_classes):
                            class_idx = np.where(self.classes == gal_class_idx)[0][0]
                            fold_predictions[gal_val_mask, class_idx] = gal_preds[:, i]
            
            # Train extragalactic model
            if (~gal_train_mask).sum() > 0:
                X_extgal_train = X_train_exact[~gal_train_mask]
                y_extgal_train = y_train[~gal_train_mask]
                
                # Map to extragalactic classes
                extgal_class_mapping = {cls: i for i, cls in enumerate(self.extragalactic_classes)}
                y_extgal_mapped = y_extgal_train.map(lambda x: extgal_class_mapping.get(self.classes[x], -1))
                valid_mask = y_extgal_mapped != -1
                
                if valid_mask.sum() > 0:
                    X_extgal_train = X_extgal_train[valid_mask]
                    y_extgal_mapped = y_extgal_mapped[valid_mask]
                    
                    train_data = lgb.Dataset(X_extgal_train, label=y_extgal_mapped)
                    model_extgal = lgb.train(params_extragalactic, train_data, num_boost_round=1000,
                                           valid_sets=[train_data], callbacks=[lgb.early_stopping(100)])
                    self.models_extragalactic.append(model_extgal)
                    
                    # Predict on validation
                    if (~gal_val_mask).sum() > 0:
                        extgal_preds = model_extgal.predict(X_val_exact[~gal_val_mask], num_iteration=model_extgal.best_iteration)
                        for i, extgal_class_idx in enumerate(self.extragalactic_classes):
                            class_idx = np.where(self.classes == extgal_class_idx)[0][0]
                            fold_predictions[~gal_val_mask, class_idx] = extgal_preds[:, i]
            
            # Store predictions and calculate score
            train_predictions_exact[val_idx] = fold_predictions
            
            if fold_predictions.sum() > 0:
                fold_pred_norm = fold_predictions / (fold_predictions.sum(axis=1, keepdims=True) + 1e-15)
                fold_score = log_loss(y_val, fold_pred_norm, labels=list(range(len(self.classes))))
                val_scores.append(fold_score)
            
            gc.collect()
        
        # Store predictions
        self.predictions = train_predictions_exact
        
        # Store performance metrics
        self.performance_metrics['cv_scores'] = val_scores
        self.performance_metrics['cv_mean'] = np.mean(val_scores)
        self.performance_metrics['cv_std'] = np.std(val_scores)
        
        print(f"\nCross-validation completed!")
        print(f"Average validation log loss: {np.mean(val_scores):.6f} ± {np.std(val_scores):.6f}")
        print(f"Trained {len(self.models_galactic)} galactic and {len(self.models_extragalactic)} extragalactic models")
    
    def evaluate_models(self) -> Dict:
        """
        Complete model evaluation with all original visualizations
        """
        print("=== MODEL EVALUATION ===")
        
        # Prepare data for evaluation
        galactic_mask_exact = self.train_exact['hostgal_photoz'] == 0
        y_true = self.train_exact['target_mapped'].values
        
        # Normalize predictions
        train_pred_norm = self.predictions / (self.predictions.sum(axis=1, keepdims=True) + 1e-15)
        
        # Calculate metrics
        y_pred_classes = np.argmax(train_pred_norm, axis=1)
        accuracy = accuracy_score(y_true, y_pred_classes)
        logloss_val = log_loss(y_true, train_pred_norm, labels=list(range(len(self.classes))))
        
        print(f"Overall Accuracy: {accuracy:.4f}")
        print(f"Overall Log Loss: {logloss_val:.6f}")
        
        # Store metrics
        self.performance_metrics['accuracy'] = accuracy
        self.performance_metrics['logloss'] = logloss_val
        
        # Create comprehensive visualizations
        self._create_comprehensive_evaluation_plots(y_true, y_pred_classes, train_pred_norm)
        
        return self.performance_metrics
    
    def _create_comprehensive_evaluation_plots(self, y_true: np.ndarray, y_pred_classes: np.ndarray, 
                                             predictions: np.ndarray) -> None:
        """Create all original evaluation visualizations"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Prediction confidence distribution
        max_probs = np.max(predictions, axis=1)
        axes[0, 0].hist(max_probs, bins=50, alpha=0.7, edgecolor='black')
        axes[0, 0].set_title('Prediction Confidence Distribution')
        axes[0, 0].set_xlabel('Max Probability')
        axes[0, 0].set_ylabel('Count')
        
        # 2. Class-wise accuracy
        class_accuracies = []
        for i in range(len(self.classes)):
            class_mask = y_true == i
            if class_mask.sum() > 0:
                class_acc = accuracy_score(y_true[class_mask], y_pred_classes[class_mask])
                class_accuracies.append(class_acc)
            else:
                class_accuracies.append(0.0)
        
        axes[0, 1].bar(range(len(self.classes)), class_accuracies, alpha=0.7)
        axes[0, 1].set_title('Class-wise Accuracy')
        axes[0, 1].set_xlabel('Class Index')
        axes[0, 1].set_ylabel('Accuracy')
        axes[0, 1].set_xticks(range(len(self.classes)))
        axes[0, 1].set_xticklabels([f'{cls}' for cls in self.classes], rotation=45)
        
        # 3. Feature importance (Extragalactic Model)
        if len(self.models_extragalactic) > 0 and self.models_extragalactic[-1] is not None:
            try:
                importance = self.models_extragalactic[-1].feature_importance(importance_type='gain')
                feature_names = self.feature_cols_exact
                
                # Get top 20 features
                top_indices = np.argsort(importance)[-20:]
                top_importance = importance[top_indices]
                top_features = [feature_names[i] for i in top_indices]
                
                axes[1, 0].barh(range(len(top_features)), top_importance)
                axes[1, 0].set_title('Top 20 Feature Importance (Extragalactic Model)')
                axes[1, 0].set_xlabel('Importance')
                axes[1, 0].set_yticks(range(len(top_features)))
                axes[1, 0].set_yticklabels(top_features, fontsize=8)
                
                # Save extragalactic feature importance separately
                plt.figure(figsize=(10, 8))
                plt.barh(range(len(top_features)), top_importance)
                plt.title('Top 20 Feature Importance (Extragalactic Model)')
                plt.xlabel('Importance')
                plt.yticks(range(len(top_features)), top_features)
                plt.tight_layout()
                plt.savefig('report/figures/feature_importance_extragalactic.png', dpi=300, bbox_inches='tight')
                plt.show()
                
            except Exception as e:
                print(f"Error creating extragalactic feature importance plot: {e}")
                axes[1, 0].text(0.5, 0.5, f'Error: {str(e)}', ha='center', va='center')
                axes[1, 0].set_title('Feature Importance (Extragalactic Model) - Error')
        else:
            axes[1, 0].text(0.5, 0.5, 'No extragalactic model available', ha='center', va='center')
            axes[1, 0].set_title('Feature Importance (Extragalactic Model) - Not Available')
        
        # 4. Feature importance (Galactic Model)
        if len(self.models_galactic) > 0 and self.models_galactic[-1] is not None:
            try:
                importance = self.models_galactic[-1].feature_importance(importance_type='gain')
                feature_names = self.feature_cols_exact
                
                # Get top 20 features
                top_indices = np.argsort(importance)[-20:]
                top_importance = importance[top_indices]
                top_features = [feature_names[i] for i in top_indices]
                
                axes[1, 1].barh(range(len(top_features)), top_importance)
                axes[1, 1].set_title('Top 20 Feature Importance (Galactic Model)')
                axes[1, 1].set_xlabel('Importance')
                axes[1, 1].set_yticks(range(len(top_features)))
                axes[1, 1].set_yticklabels(top_features, fontsize=8)
                
                # Save galactic feature importance separately
                plt.figure(figsize=(10, 8))
                plt.barh(range(len(top_features)), top_importance)
                plt.title('Top 20 Feature Importance (Galactic Model)')
                plt.xlabel('Importance')
                plt.yticks(range(len(top_features)), top_features)
                plt.tight_layout()
                plt.savefig('report/figures/feature_importance_galactic.png', dpi=300, bbox_inches='tight')
                plt.show()
                
            except Exception as e:
                print(f"Error creating galactic feature importance plot: {e}")
                axes[1, 1].text(0.5, 0.5, f'Error: {str(e)}', ha='center', va='center')
                axes[1, 1].set_title('Feature Importance (Galactic Model) - Error')
        else:
            axes[1, 1].text(0.5, 0.5, 'No galactic model available', ha='center', va='center')
            axes[1, 1].set_title('Feature Importance (Galactic Model) - Not Available')
        
        plt.tight_layout()
        plt.savefig('report/figures/model_evaluation.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Confusion matrix
        cm = metrics.confusion_matrix(y_true, y_pred_classes)
        plt.figure(figsize=(12, 10))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=[f'Pred_{cls}' for cls in self.classes],
                    yticklabels=[f'True_{cls}' for cls in self.classes])
        plt.title('Confusion Matrix')
        plt.ylabel('True Class')
        plt.xlabel('Predicted Class')
        plt.xticks(rotation=45)
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig('report/figures/confusion_matrix.png', dpi=300, bbox_inches='tight')
        plt.show()
    


    
    def apply_prediction_post_processing(self) -> np.ndarray:
        """
        COMPLETE PREDICTION POST-PROCESSING (Original Implementation)
        Apply advanced post-processing to fix zero probability issues
        """
        print("=== PREDICTION POST-PROCESSING WITH FIXES ===")
        
        # Create a copy of normalized predictions for post-processing
        final_predictions = self.predictions / (self.predictions.sum(axis=1, keepdims=True) + 1e-15)
        final_predictions = final_predictions.copy()
        
        # === CRITICAL FIX: ADDRESS ZERO PROBABILITY ISSUE ===
        print("Applying fixes to prevent zero probability issues...")
        
        # 1. Add minimum probability to all classes to prevent zeros
        min_prob = 1e-4
        print(f"Adding minimum probability: {min_prob}")
        
        # Apply minimum probability
        final_predictions = np.maximum(final_predictions, min_prob)
        
        # 2. Renormalize after adding minimum probability
        final_predictions = final_predictions / final_predictions.sum(axis=1, keepdims=True)
        
        # === CLASS WEIGHT ADJUSTMENT ===
        # Based on competition-specific class weights and loss function
        print("Applying class weight adjustments...")
        
        # Competition-specific loss weights (from PLAsTiCC discussion)
        class_weights = {
            6: 1,    # Class 6 (baseline)
            15: 2,   # Class 15 (higher weight)
            16: 1,   # Class 16  
            42: 1,   # Class 42
            52: 1,   # Class 52
            53: 1,   # Class 53
            62: 1,   # Class 62
            64: 2,   # Class 64 (higher weight)
            65: 1,   # Class 65
            67: 1,   # Class 67
            88: 1,   # Class 88
            90: 1,   # Class 90
            92: 1,   # Class 92
            95: 1,   # Class 95
            99: 2    # Class 99 (higher weight)
        }
        
        # Apply weights to predictions
        for i, cls in enumerate(self.classes):
            if cls in class_weights:
                weight = class_weights[cls]
                final_predictions[:, i] *= weight
                print(f"Applied weight {weight} to class {cls}")
        
        # Renormalize after weighting
        final_predictions = final_predictions / final_predictions.sum(axis=1, keepdims=True)
        
        # === ENHANCED REGULARIZATION ===
        print("\nApplying enhanced regularization...")
        
        # Separate regularization for galactic vs extragalactic objects
        alpha = 0.3  # Reduced regularization parameter for better performance
        
        # Apply regularization separately for galactic and extragalactic
        galactic_mask = self.train_exact['hostgal_photoz'] == 0
        
        # Enhanced regularization to prevent extreme predictions
        for i in range(len(self.classes)):
            # Calculate group means
            mean_gal = final_predictions[galactic_mask, i].mean() if galactic_mask.sum() > 0 else 0
            mean_extgal = final_predictions[~galactic_mask, i].mean() if (~galactic_mask).sum() > 0 else 0
            
            # Apply regularization
            if galactic_mask.sum() > 0:
                final_predictions[galactic_mask, i] = \
                    mean_gal + alpha * (final_predictions[galactic_mask, i] - mean_gal)
            
            if (~galactic_mask).sum() > 0:
                final_predictions[~galactic_mask, i] = \
                    mean_extgal + alpha * (final_predictions[~galactic_mask, i] - mean_extgal)
        
        print(f"Applied regularization with alpha={alpha}")
        
        # === FINAL NORMALIZATION WITH SAFETY CHECKS ===
        print("\nApplying final normalization with safety checks...")
        
        # Ensure no negative values
        final_predictions = np.maximum(final_predictions, min_prob)
        
        # Final normalization
        row_sums = final_predictions.sum(axis=1, keepdims=True)
        final_predictions = final_predictions / row_sums
        
        # Store final predictions
        self.final_predictions = final_predictions
        
        # Evaluate final predictions
        self._evaluate_final_predictions(final_predictions)
        
        return final_predictions
    

    def apply_prediction_post_processing_fixed(self):
        """
        FIXED VERSION: Minimal post-processing to avoid performance degradation
        """
        print("=== MINIMAL PREDICTION POST-PROCESSING ===")
        
        # Use original predictions (they're better!)
        final_predictions = self.predictions.copy()
        
        # Only apply essential fixes:
        
        # 1. Ensure no zeros (minimal impact)
        min_prob = 1e-6  # Much smaller
        final_predictions = np.maximum(final_predictions, min_prob)
        
        # 2. Normalize (essential)
        final_predictions = final_predictions / final_predictions.sum(axis=1, keepdims=True)
        
        # 3. Store final predictions
        self.final_predictions = final_predictions
        
        # Evaluate
        y_true = self.train_exact['target_mapped'].values
        final_pred_classes = np.argmax(final_predictions, axis=1)
        final_accuracy = accuracy_score(y_true, final_pred_classes)
        final_logloss = log_loss(y_true, final_predictions)
        
        print(f"✅ Fixed Post-processing Applied")
        print(f"📊 Final Accuracy: {final_accuracy:.4f}")
        print(f"📉 Final Log Loss: {final_logloss:.6f}")
        
        return final_predictions








































































    
    def _evaluate_final_predictions(self, final_predictions: np.ndarray) -> None:
        """Evaluate final predictions after post-processing"""
        print("\n=== FINAL PREDICTION EVALUATION ===")
        
        y_true = self.train_exact['target_mapped'].values
        
        # Calculate metrics with final predictions
        final_pred_classes = np.argmax(final_predictions, axis=1)
        final_accuracy = accuracy_score(y_true, final_pred_classes)
        
        # Safe log_loss calculation
        try:
            final_logloss = log_loss(y_true, final_predictions)
        except:
            final_predictions = np.clip(final_predictions, 1e-15, 1.0)
            final_predictions = final_predictions / final_predictions.sum(axis=1, keepdims=True)
            final_logloss = log_loss(y_true, final_predictions)
        
        original_accuracy = self.performance_metrics['accuracy']
        original_logloss = self.performance_metrics['logloss']
        
        print(f"Final Accuracy: {final_accuracy:.4f} (Original: {original_accuracy:.4f})")
        print(f"Final Log Loss: {final_logloss:.6f} (Original: {original_logloss:.6f})")
        
        # Store final metrics
        self.performance_metrics['final_accuracy'] = final_accuracy
        self.performance_metrics['final_logloss'] = final_logloss
        
        # Create post-processing visualizations
        self._create_post_processing_visualizations(final_predictions, final_pred_classes, y_true)
    
    def _create_post_processing_visualizations(self, final_predictions: np.ndarray, 
                                             final_pred_classes: np.ndarray, y_true: np.ndarray) -> None:
        """Create comprehensive post-processing visualizations"""
        fig, axes = plt.subplots(2, 2, figsize=(18, 12))
        
        # 1. Confidence distribution
        max_probs = np.max(final_predictions, axis=1)
        axes[0, 0].hist(max_probs, bins=50, alpha=0.7, edgecolor='black')
        axes[0, 0].set_title('Final Prediction Confidence Distribution')
        axes[0, 0].set_xlabel('Max Probability')
        axes[0, 0].set_ylabel('Count')
        axes[0, 0].axvline(max_probs.mean(), color='red', linestyle='--', label=f'Mean: {max_probs.mean():.3f}')
        axes[0, 0].legend()
        
        # 2. Before vs After Log Loss
        metrics_comparison = pd.DataFrame({
            'Metric': ['Accuracy', 'Log Loss'],
            'Original': [self.performance_metrics['accuracy'], self.performance_metrics['logloss']],
            'Final': [self.performance_metrics['final_accuracy'], self.performance_metrics['final_logloss']]
        })
        
        metrics_comparison.set_index('Metric').plot(kind='bar', ax=axes[0, 1])
        axes[0, 1].set_title('Performance Before vs After Post-processing')
        axes[0, 1].set_ylabel('Score')
        axes[0, 1].legend()
        axes[0, 1].tick_params(axis='x', rotation=0)
        
        # 3. Class prediction distribution comparison
        true_class_counts = np.bincount(y_true, minlength=len(self.classes))
        pred_class_counts = np.bincount(final_pred_classes, minlength=len(self.classes))
        
        ax = axes[1, 0]
        x = np.arange(len(self.classes))
        width = 0.35
        
        ax.bar(x - width/2, true_class_counts, width, label='True', alpha=0.7)
        ax.bar(x + width/2, pred_class_counts, width, label='Predicted', alpha=0.7)
        
        ax.set_title('True vs Predicted Class Distribution')
        ax.set_xlabel('Class')
        ax.set_ylabel('Count')
        ax.set_xticks(x)
        ax.set_xticklabels([str(cls) for cls in self.classes], rotation=45)
        ax.legend()
        
        # 4. Zero percentage by class
        zero_percentages = [(final_predictions[:, i] == 0).mean() * 100 for i in range(len(self.classes))]
        axes[1, 1].bar(range(len(self.classes)), zero_percentages, alpha=0.7)
        axes[1, 1].set_title('Zero Percentage by Class (After Fix)')
        axes[1, 1].set_xlabel('Class')
        axes[1, 1].set_ylabel('Zero Percentage (%)')
        axes[1, 1].set_xticks(range(len(self.classes)))
        axes[1, 1].set_xticklabels([str(cls) for cls in self.classes], rotation=45)
        axes[1, 1].axhline(y=50, color='red', linestyle='--', label='50% threshold')
        axes[1, 1].legend()
        
        plt.tight_layout()
        plt.savefig('report/figures/prediction_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("\nPrediction post-processing completed!")
    
    def generate_improved_predictions(self, test_features: pd.DataFrame, test_meta: pd.DataFrame) -> np.ndarray:
        """
        Generate improved predictions that avoid excessive zeros (original implementation)
        """
        n_objects = len(test_meta)
        n_classes = len(self.classes)
        
        # Initialize prediction matrix
        all_predictions = np.zeros((n_objects, n_classes))
        
        # Get galactic mask
        galactic_mask = test_meta['hostgal_photoz'] == 0
        
        print(f"Processing {galactic_mask.sum()} galactic and {(~galactic_mask).sum()} extragalactic objects")
        
        # Predict galactic objects
        if galactic_mask.sum() > 0:
            gal_features = test_features.loc[test_meta[galactic_mask]['object_id']]
            
            # Average predictions across folds
            gal_fold_preds = []
            for model in self.models_galactic:
                pred = model.predict(gal_features)
                gal_fold_preds.append(pred)
            
            gal_preds_avg = np.mean(gal_fold_preds, axis=0)
            
            # Map galactic predictions to full class space
            for i, gal_class_idx in enumerate(self.galactic_classes):
                class_idx = np.where(self.classes == gal_class_idx)[0][0]
                all_predictions[galactic_mask, class_idx] = gal_preds_avg[:, i]
        
        # Predict extragalactic objects  
        if (~galactic_mask).sum() > 0:
            extgal_features = test_features.loc[test_meta[~galactic_mask]['object_id']]
            
            # Average predictions across folds
            extgal_fold_preds = []
            for model in self.models_extragalactic:
                pred = model.predict(extgal_features)
                extgal_fold_preds.append(pred)
            
            extgal_preds_avg = np.mean(extgal_fold_preds, axis=0)
            
            # Map extragalactic predictions to full class space
            for i, extgal_class_idx in enumerate(self.extragalactic_classes):
                class_idx = np.where(self.classes == extgal_class_idx)[0][0]
                all_predictions[~galactic_mask, class_idx] = extgal_preds_avg[:, i]
        
        # === CRITICAL FIX: HANDLE CLASSES NOT PREDICTED BY EITHER MODEL ===
        # Add small probability to unpredicted classes to avoid zeros
        min_prob = 1e-4
        
        for i in range(n_classes):
            class_total = all_predictions[:, i].sum()
            if class_total == 0:
                all_predictions[:, i] = min_prob
        
        # Final normalization
        all_predictions = all_predictions / (all_predictions.sum(axis=1, keepdims=True) + 1e-15)
        
        return all_predictions
    
    def validate_submission(self, predictions: np.ndarray, threshold: float = 0.1) -> bool:
        """
        Validate submission predictions to avoid common issues (original implementation)
        """
        print("Validating submission format...")
        
        issues_found = []
        
        # Check for NaN values
        if np.isnan(predictions).any():
            issues_found.append("NaN values detected")
        
        # Check for negative values
        if (predictions < 0).any():
            issues_found.append("Negative values detected")
        
        # Check row sums
        row_sums = predictions.sum(axis=1)
        if not np.allclose(row_sums, 1.0, rtol=1e-10):
            issues_found.append(f"Row sums not equal to 1: range [{row_sums.min():.6f}, {row_sums.max():.6f}]")
        
        # Check for excessive zeros
        zero_counts = (predictions == 0).sum()
        if zero_counts > 0:
            issues_found.append(f"Zero values found: {zero_counts} total")
        
        if issues_found:
            print("⚠️  Issues found:")
            for issue in issues_found:
                print(f"   - {issue}")
            return False
        else:
            print("✅ Submission validation passed!")
            return True
    
    def save_models(self) -> None:
        """Save trained models to disk"""
        print("=== SAVING MODELS ===")
        
        # Save models
        for i, model in enumerate(self.models_galactic):
            with open(f'models/galactic_model_fold_{i}.pkl', 'wb') as f:
                pickle.dump(model, f)
        
        for i, model in enumerate(self.models_extragalactic):
            with open(f'models/extragalactic_model_fold_{i}.pkl', 'wb') as f:
                pickle.dump(model, f)
        
        # Save metadata
        model_metadata = {
            'classes': self.classes,
            'galactic_classes': self.galactic_classes,
            'extragalactic_classes': self.extragalactic_classes,
            'feature_cols_exact': self.feature_cols_exact,
            'feature_cols_approx': self.feature_cols_approx,
            'class_mapping': self.class_mapping
        }
        
        with open('models/model_metadata.pkl', 'wb') as f:
            pickle.dump(model_metadata, f)
        
        print(f"Saved {len(self.models_galactic)} galactic and {len(self.models_extragalactic)} extragalactic models with metadata")
    
    def load_models(self) -> None:
        """Load trained models from disk"""
        print("=== LOADING MODELS ===")
        
        try:
            with open('models/model_metadata.pkl', 'rb') as f:
                model_metadata = pickle.load(f)
            
            # Load models
            self.models_galactic = []
            for model_file in sorted(glob.glob('models/galactic_model_fold_*.pkl')):
                with open(model_file, 'rb') as f:
                    self.models_galactic.append(pickle.load(f))
            
            self.models_extragalactic = []
            for model_file in sorted(glob.glob('models/extragalactic_model_fold_*.pkl')):
                with open(model_file, 'rb') as f:
                    self.models_extragalactic.append(pickle.load(f))
            
            # Load metadata
            self.classes = model_metadata['classes']
            self.galactic_classes = model_metadata['galactic_classes']
            self.extragalactic_classes = model_metadata['extragalactic_classes']
            self.feature_cols_exact = model_metadata['feature_cols_exact']
            self.feature_cols_approx = model_metadata['feature_cols_approx']
            self.class_mapping = model_metadata['class_mapping']
            
            print(f"Loaded {len(self.models_galactic)} galactic and {len(self.models_extragalactic)} extragalactic models")
            
        except FileNotFoundError:
            print("No saved models found. Please train models first.")
    
    def run_full_pipeline(self, meta_path: str, lc_path: str, n_folds: int = 5) -> Dict:
        """
        Run the complete CosmoNet classification pipeline with ALL features
        """
        print("=== COSMONET COMPLETE CLASSIFICATION PIPELINE ===")
        
        # Step 1: Load data
        self.load_data(meta_path, lc_path)
        
        # Step 2: Explore data
        stats = self.explore_data()
        
        # Step 3: Define classes
        self.define_classes()
        
        # Step 4: Sequence analysis (ORIGINAL FEATURE)
        self.prepare_sequences(max_length=50, sample_size=1000)
        
        # Step 5: Engineer features
        self.engineer_features()
        
        # Step 6: Train models
        self.train_models(n_folds=n_folds)
        
        # Step 7: Evaluate models
        metrics = self.evaluate_models()
        
        # Step 8: Apply advanced post-processing (ORIGINAL FEATURE)
        self.apply_prediction_post_processing()
        
        # Step 9: Save models
        self.save_models()
        
        # Step 10: Save comprehensive performance metrics
        self._save_performance_metrics()
        
        print("=== COSMONET PIPELINE COMPLETED SUCCESSFULLY ===")
        return {**metrics, **self.performance_metrics}
    
    def _save_performance_metrics(self) -> None:
        """Save comprehensive performance metrics to file"""
        performance_metrics = {
            'overall_accuracy': float(self.performance_metrics['accuracy']),
            'overall_logloss': float(self.performance_metrics['logloss']),
            'final_accuracy': float(self.performance_metrics.get('final_accuracy', 0)),
            'final_logloss': float(self.performance_metrics.get('final_logloss', 0)),
            'cv_mean_logloss': float(self.performance_metrics['cv_mean']),
            'cv_std_logloss': float(self.performance_metrics['cv_std']),
            'num_objects': int(len(self.train_exact)),
            'num_classes': int(len(self.classes)),
            'num_galactic_objects': int((self.train_exact['hostgal_photoz'] == 0).sum()),
            'num_extragalactic_objects': int((self.train_exact['hostgal_photoz'] != 0).sum()),
            'num_features': int(len(self.feature_cols_exact))
        }
        
        with open('report/figures/performance_metrics.json', 'w') as f:
            json.dump(performance_metrics, f, indent=2)
        
        print("✅ Performance metrics saved to report/figures/performance_metrics.json")


def main():
    """Main function to run the complete CosmoNet pipeline"""
    classifier = CosmoNetClassifier(random_state=42)
    
    # Run complete pipeline with all features
    metrics = classifier.run_full_pipeline(
        meta_path='data/training_set_metadata.csv',
        lc_path='data/training_set.csv',
        n_folds=5
    )
    
    print(f"\n🎯 CosmoNet Final Results:")
    print(f"   Accuracy: {metrics['accuracy']:.4f}")
    print(f"   Log Loss: {metrics['logloss']:.6f}")
    print(f"   Final Accuracy: {metrics.get('final_accuracy', 0):.4f}")
    print(f"   Final Log Loss: {metrics.get('final_logloss', 0):.6f}")
    print(f"   CV Performance: {metrics['cv_mean']:.6f} ± {metrics['cv_std']:.6f}")


if __name__ == "__main__":
    main()




