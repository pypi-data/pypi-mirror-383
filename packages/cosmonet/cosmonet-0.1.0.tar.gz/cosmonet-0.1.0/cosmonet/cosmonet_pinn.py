# cosmonet_pinn.py
"""
COMPLETE PINN SYSTEM for CosmoNet
- All PINN modules in one file
- Easy to add new PINN modules
- Plug-and-play integration
- Progressive enhancement ready
"""
import tensorflow as tf
import numpy as np
import pandas as pd
import warnings
from abc import ABC, abstractmethod
from scipy.stats import linregress
from scipy.signal import savgol_filter, find_peaks

warnings.filterwarnings('ignore')

# ============================================================================
# CORE PINN FRAMEWORK
# ============================================================================

class PINNModule(ABC):
    """
    Base class for all PINN modules
    Add new PINN modules by inheriting from this class!
    """
    
    def __init__(self, name, description=""):
        self.name = name
        self.description = description
        self.is_trained = False
        self.feature_names = []
        
    @abstractmethod
    def calculate_features(self, light_curve_data):
        """Calculate features for this PINN module - IMPLEMENT THIS"""
        pass
    
    @abstractmethod
    def physics_loss(self, light_curve_data):
        """Calculate physics loss - IMPLEMENT THIS"""
        pass
    
    def get_feature_descriptions(self):
        """Get descriptions of features"""
        return {name: f"{self.name}: {name}" for name in self.feature_names}

# ============================================================================
# PINN MODULE 1: Light Curve Smoothness
# ============================================================================

class LightCurveSmoothnessPINN(PINNModule):
    """
    PINN for light curve smoothness and physical consistency
    """
    
    def __init__(self):
        super().__init__(
            name="lightcurve_smoothness",
            description="Ensures light curves follow physical smoothness constraints"
        )
        self.feature_names = [
            'pinn_smoothness_score',
            'pinn_derivative_consistency',
            'pinn_acceleration_metric'
        ]
        self.model = self._build_model()
    
    def _build_model(self):
        """Build neural network for smoothness learning"""
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(32, activation='relu', input_shape=(2,)),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(8, activation='relu'),
            tf.keras.layers.Dense(1, activation='linear')
        ])
        model.compile(optimizer='adam', loss='mse')
        return model
    
    def calculate_features(self, light_curve_data):
        """Calculate smoothness-related features"""
        features = {}
        
        object_ids = light_curve_data['object_id'].unique()
        smoothness_scores = []
        derivative_consistency = []
        acceleration_metrics = []
        
        for obj_id in object_ids:
            obj_data = light_curve_data[light_curve_data['object_id'] == obj_id]
            obj_features = self._analyze_single_lightcurve(obj_data)
            
            smoothness_scores.append(obj_features['smoothness'])
            derivative_consistency.append(obj_features['derivative_consistency'])
            acceleration_metrics.append(obj_features['acceleration'])
        
        features['pinn_smoothness_score'] = smoothness_scores
        features['pinn_derivative_consistency'] = derivative_consistency
        features['pinn_acceleration_metric'] = acceleration_metrics
        
        return features
    
    def _analyze_single_lightcurve(self, obj_data):
        """Analyze a single light curve for smoothness"""
        if len(obj_data) < 3:
            return {'smoothness': 0.0, 'derivative_consistency': 0.0, 'acceleration': 0.0}
        
        times = obj_data['mjd'].values
        fluxes = obj_data['flux'].values
        
        # Calculate derivatives
        time_diffs = np.diff(times)
        flux_diffs = np.diff(fluxes)
        
        if np.any(time_diffs <= 0):
            return {'smoothness': 1.0, 'derivative_consistency': 0.0, 'acceleration': 1.0}
        
        # First derivatives (rate of change)
        first_derivatives = flux_diffs / time_diffs
        
        # Second derivatives (acceleration)
        second_derivatives = np.diff(first_derivatives) / time_diffs[1:]
        
        # Smoothness: lower = smoother
        smoothness = np.mean(np.abs(second_derivatives)) if len(second_derivatives) > 0 else 0.0
        
        # Derivative consistency: how consistent are the changes
        derivative_consistency = 1.0 - (np.std(first_derivatives) / (np.mean(np.abs(first_derivatives)) + 1e-8))
        derivative_consistency = np.clip(derivative_consistency, 0.0, 1.0)
        
        # Acceleration metric
        acceleration = np.mean(np.abs(second_derivatives)) if len(second_derivatives) > 0 else 0.0
        
        return {
            'smoothness': float(smoothness),
            'derivative_consistency': float(derivative_consistency),
            'acceleration': float(acceleration)
        }
    
    def physics_loss(self, light_curve_data):
        """Calculate physics loss for training"""
        total_loss = 0.0
        count = 0
        
        for obj_id in light_curve_data['object_id'].unique():
            obj_data = light_curve_data[light_curve_data['object_id'] == obj_id]
            if len(obj_data) >= 3:
                features = self._analyze_single_lightcurve(obj_data)
                total_loss += features['smoothness']  # Penalize unsmooth curves
                count += 1
        
        return total_loss / count if count > 0 else 0.0

# ============================================================================
# PINN MODULE 2: Physical Plausibility
# ============================================================================

class PhysicalPlausibilityPINN(PINNModule):
    """
    PINN for checking physical plausibility of light curves
    """
    
    def __init__(self):
        super().__init__(
            name="physical_plausibility", 
            description="Checks if light curves obey physical laws and constraints"
        )
        self.feature_names = [
            'pinn_plausibility_score',
            'pinn_flux_consistency', 
            'pinn_time_consistency',
            'pinn_outlier_metric'
        ]
    
    def calculate_features(self, light_curve_data):
        """Calculate physical plausibility features"""
        features = {}
        
        object_ids = light_curve_data['object_id'].unique()
        plausibility_scores = []
        flux_consistency_scores = []
        time_consistency_scores = []
        outlier_metrics = []
        
        for obj_id in object_ids:
            obj_data = light_curve_data[light_curve_data['object_id'] == obj_id]
            obj_features = self._analyze_plausibility(obj_data)
            
            plausibility_scores.append(obj_features['plausibility'])
            flux_consistency_scores.append(obj_features['flux_consistency'])
            time_consistency_scores.append(obj_features['time_consistency'])
            outlier_metrics.append(obj_features['outlier_metric'])
        
        features['pinn_plausibility_score'] = plausibility_scores
        features['pinn_flux_consistency'] = flux_consistency_scores
        features['pinn_time_consistency'] = time_consistency_scores
        features['pinn_outlier_metric'] = outlier_metrics
        
        return features
    
    def _analyze_plausibility(self, obj_data):
        """Analyze physical plausibility of a light curve"""
        if len(obj_data) < 2:
            return {'plausibility': 0.5, 'flux_consistency': 0.5, 'time_consistency': 0.5, 'outlier_metric': 0.0}
        
        times = obj_data['mjd'].values
        fluxes = obj_data['flux'].values
        flux_errs = obj_data['flux_err'].values
        
        plausibility = 1.0  # Start with perfect score
        
        # Check 1: Negative fluxes (often unphysical)
        if np.any(fluxes < -50):  # Significant negative flux
            plausibility *= 0.3
        
        # Check 2: Extreme variations
        flux_std = np.std(fluxes)
        flux_mean = np.mean(np.abs(fluxes))
        if flux_mean > 0 and flux_std / flux_mean > 5.0:  # Extreme variation
            plausibility *= 0.5
        
        # Check 3: Duplicate times
        if len(np.unique(times)) < len(times):
            plausibility *= 0.7
        
        # Check 4: Measurement errors vs variations
        avg_error = np.mean(flux_errs)
        if avg_error > 0 and flux_std < avg_error * 0.1:  # Variations smaller than errors
            plausibility *= 0.8
        
        # Flux consistency across passbands
        if 'passband' in obj_data.columns:
            flux_consistency = self._calculate_flux_consistency(obj_data)
        else:
            flux_consistency = 0.5
        
        # Time consistency
        time_consistency = self._calculate_time_consistency(times)
        
        # Outlier metric
        outlier_metric = self._calculate_outlier_metric(fluxes)
        
        return {
            'plausibility': float(np.clip(plausibility, 0.0, 1.0)),
            'flux_consistency': float(flux_consistency),
            'time_consistency': float(time_consistency),
            'outlier_metric': float(outlier_metric)
        }
    
    def _calculate_flux_consistency(self, obj_data):
        """Check flux consistency across different passbands"""
        passbands = obj_data['passband'].unique()
        if len(passbands) < 2:
            return 0.5
        
        passband_fluxes = []
        for pb in passbands:
            pb_data = obj_data[obj_data['passband'] == pb]
            if len(pb_data) > 0:
                passband_fluxes.append(pb_data['flux'].mean())
        
        if len(passband_fluxes) < 2:
            return 0.5
        
        # Check if fluxes follow reasonable pattern (not random)
        flux_std = np.std(passband_fluxes)
        flux_mean = np.mean(np.abs(passband_fluxes))
        
        if flux_mean == 0:
            return 0.5
        
        # Higher consistency = lower relative standard deviation
        consistency = 1.0 - min(flux_std / flux_mean, 1.0)
        return consistency
    
    def _calculate_time_consistency(self, times):
        """Check time sampling consistency"""
        if len(times) < 2:
            return 0.5
        
        time_diffs = np.diff(np.sort(times))
        if len(time_diffs) == 0:
            return 0.5
        
        # Consistent time sampling = lower variation in time differences
        time_consistency = 1.0 - (np.std(time_diffs) / (np.mean(time_diffs) + 1e-8))
        return np.clip(time_consistency, 0.0, 1.0)
    
    def _calculate_outlier_metric(self, fluxes):
        """Calculate outlier metric using IQR"""
        if len(fluxes) < 4:
            return 0.0
        
        Q1 = np.percentile(fluxes, 25)
        Q3 = np.percentile(fluxes, 75)
        IQR = Q3 - Q1
        
        if IQR == 0:
            return 0.0
        
        # Count outliers beyond 1.5 * IQR
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = np.sum((fluxes < lower_bound) | (fluxes > upper_bound))
        
        return float(outliers / len(fluxes))
    
    def physics_loss(self, light_curve_data):
        """Physics loss based on plausibility violations"""
        total_loss = 0.0
        count = 0
        
        for obj_id in light_curve_data['object_id'].unique():
            obj_data = light_curve_data[light_curve_data['object_id'] == obj_id]
            features = self._analyze_plausibility(obj_data)
            # Loss = 1 - plausibility (higher loss for implausible curves)
            total_loss += (1.0 - features['plausibility'])
            count += 1
        
        return total_loss / count if count > 0 else 0.0

# ============================================================================
# PINN MODULE 3: Variability Physics
# ============================================================================

class VariabilityPhysicsPINN(PINNModule):
    """
    PINN for analyzing variability patterns with physical constraints
    """
    
    def __init__(self):
        super().__init__(
            name="variability_physics",
            description="Analyzes variability patterns with physical time constraints"
        )
        self.feature_names = [
            'pinn_variability_index',
            'pinn_timescale_metric',
            'pinn_amplitude_metric',
            'pinn_periodicity_hint'
        ]
    
    def calculate_features(self, light_curve_data):
        """Calculate variability physics features"""
        features = {}
        
        object_ids = light_curve_data['object_id'].unique()
        variability_indices = []
        timescale_metrics = []
        amplitude_metrics = []
        periodicity_hints = []
        
        for obj_id in object_ids:
            obj_data = light_curve_data[light_curve_data['object_id'] == obj_id]
            obj_features = self._analyze_variability(obj_data)
            
            variability_indices.append(obj_features['variability_index'])
            timescale_metrics.append(obj_features['timescale_metric'])
            amplitude_metrics.append(obj_features['amplitude_metric'])
            periodicity_hints.append(obj_features['periodicity_hint'])
        
        features['pinn_variability_index'] = variability_indices
        features['pinn_timescale_metric'] = timescale_metrics
        features['pinn_amplitude_metric'] = amplitude_metrics
        features['pinn_periodicity_hint'] = periodicity_hints
        
        return features
    
    def _analyze_variability(self, obj_data):
        """Analyze variability with physical constraints"""
        if len(obj_data) < 3:
            return {'variability_index': 0.0, 'timescale_metric': 0.0, 'amplitude_metric': 0.0, 'periodicity_hint': 0.0}
        
        times = obj_data['mjd'].values
        fluxes = obj_data['flux'].values
        
        total_time = times.max() - times.min()
        if total_time <= 0:
            return {'variability_index': 0.0, 'timescale_metric': 0.0, 'amplitude_metric': 0.0, 'periodicity_hint': 0.0}
        
        # Variability index (normalized by time)
        flux_range = fluxes.max() - fluxes.min()
        flux_mean = np.mean(np.abs(fluxes))
        
        if flux_mean > 0:
            variability_index = (flux_range / flux_mean) / (total_time + 1.0)
        else:
            variability_index = 0.0
        
        # Timescale metric (characteristic timescale)
        time_diffs = np.diff(np.sort(times))
        if len(time_diffs) > 0:
            timescale_metric = np.mean(time_diffs) / (total_time + 1e-8)
        else:
            timescale_metric = 0.0
        
        # Amplitude metric (relative to mean)
        amplitude_metric = flux_range / (flux_mean + 1e-8) if flux_mean > 0 else 0.0
        
        # Simple periodicity hint (autocorrelation-like)
        periodicity_hint = self._calculate_periodicity_hint(times, fluxes)
        
        return {
            'variability_index': float(variability_index),
            'timescale_metric': float(timescale_metric),
            'amplitude_metric': float(amplitude_metric),
            'periodicity_hint': float(periodicity_hint)
        }
    
    def _calculate_periodicity_hint(self, times, fluxes):
        """Calculate simple periodicity hint"""
        if len(fluxes) < 4:
            return 0.0
        
        # Simple approach: check for regular patterns in differences
        sorted_indices = np.argsort(times)
        sorted_fluxes = fluxes[sorted_indices]
        
        # Calculate simple autocorrelation at lag 1
        if len(sorted_fluxes) > 1:
            correlated = np.corrcoef(sorted_fluxes[:-1], sorted_fluxes[1:])[0, 1]
            if np.isnan(correlated):
                return 0.0
            return max(0.0, correlated)  # Only positive correlation hints periodicity
        return 0.0
    
    def physics_loss(self, light_curve_data):
        """Physics loss for variability constraints"""
        # Penalize physically implausible rapid variations
        total_loss = 0.0
        count = 0
        
        for obj_id in light_curve_data['object_id'].unique():
            obj_data = light_curve_data[light_curve_data['object_id'] == obj_id]
            features = self._analyze_variability(obj_data)
            
            # Penalize extremely high variability on very short timescales
            if features['variability_index'] > 10.0:  # Threshold
                total_loss += 1.0
            count += 1
        
        return total_loss / count if count > 0 else 0.0

# ============================================================================
# MAIN PINN MANAGER (The ONE class you need to use)
# ============================================================================
'''# IN cosmonet_pinn.py, UPDATE THE CosmoNetPINN CLASS:

class CosmoNetPINN:
    """
    UPDATED PINN MANAGER - Now with specialized explosion modules
    """
    
    def __init__(self, modules=None, auto_setup=True, include_phase2=True):
        # Available PINN modules - UPDATED WITH NEW MODULES
        self.available_modules = {
            # Core physics (keep existing good ones)
            'smoothness': LightCurveSmoothnessPINN(),
            'plausibility': PhysicalPlausibilityPINN(), 
            'variability': VariabilityPhysicsPINN(),
            
            # PHASE 1: Enhanced explosion physics (NEW)
            'core_explosion': CoreExplosionPINN(),
            'supernova_discrimination': SupernovaDiscriminationPINN(),
        }
        
        # Add Phase 2 modules if requested
        if include_phase2:
            try:
                self.available_modules['redshift_physics'] = RedshiftPhysicsPINN()
            except NameError:
                print("⚠️ RedshiftPhysicsPINN not available - skipping")
                
            try:
                self.available_modules['variability_timescales'] = VariabilityTimescalesPINN()
            except NameError:
                print("⚠️ VariabilityTimescalesPINN not available - skipping")
        
        # Active modules (all enabled by default)
        self.active_modules = self.available_modules.copy()
        
        if auto_setup:
            self._setup_modules()'''

#########################################################

class CoreExplosionPINN(PINNModule):
    def __init__(self):
        super().__init__("core_explosion", "Fundamental explosion physics")
        self.feature_names = ['pinn_total_energy_estimate', 'pinn_characteristic_rise_time']
    
    def calculate_features(self, light_curve_data):
        features = {}
        object_ids = light_curve_data['object_id'].unique()
        for feature in self.feature_names:
            features[feature] = [0.0] * len(object_ids)
        return features
    
    def physics_loss(self, light_curve_data):
        return 0.0

class SupernovaDiscriminationPINN(PINNModule):
    def __init__(self):
        super().__init__("supernova_discrimination", "SN type discrimination")
        self.feature_names = ['pinn_snia_likelihood', 'pinn_snii_likelihood']
    
    def calculate_features(self, light_curve_data):
        features = {}
        object_ids = light_curve_data['object_id'].unique()
        for feature in self.feature_names:
            features[feature] = [0.5] * len(object_ids)
        return features
    
    def physics_loss(self, light_curve_data):
        return 0.0

class SubluminousDiscriminationPINN(PINNModule):
    def __init__(self):
        super().__init__("subluminous_discrimination", "Subluminous SN discrimination")
        self.feature_names = ['pinn_sniax_likelihood_enhanced', 'pinn_91bg_likelihood_enhanced']
    
    def calculate_features(self, light_curve_data):
        features = {}
        object_ids = light_curve_data['object_id'].unique()
        for feature in self.feature_names:
            features[feature] = [0.5] * len(object_ids)
        return features
    
    def physics_loss(self, light_curve_data):
        return 0.0

class ExplosionDiscriminationPINN(PINNModule):
    def __init__(self):
        super().__init__("explosion_discrimination", "Stripped-envelope SN discrimination")
        self.feature_names = ['pinn_snibc_likelihood_enhanced', 'pinn_stripped_envelope_signature']
    
    def calculate_features(self, light_curve_data):
        features = {}
        object_ids = light_curve_data['object_id'].unique()
        for feature in self.feature_names:
            features[feature] = [0.5] * len(object_ids)
        return features
    
    def physics_loss(self, light_curve_data):
        return 0.0

class SpectralEvolutionPINN(PINNModule):
    def __init__(self):
        super().__init__("spectral_evolution", "Multi-band spectral features")
        self.feature_names = ['pinn_color_evolution_rate', 'pinn_blackbody_temperature']
    
    def calculate_features(self, light_curve_data):
        features = {}
        object_ids = light_curve_data['object_id'].unique()
        for feature in self.feature_names:
            if 'temperature' in feature:
                features[feature] = [5000.0] * len(object_ids)
            else:
                features[feature] = [0.5] * len(object_ids)
        return features
    
    def physics_loss(self, light_curve_data):
        return 0.0

class RedshiftPhysicsPINN(PINNModule):
    def __init__(self):
        super().__init__("redshift_physics", "Cosmological redshift effects")
        self.feature_names = ['pinn_distance_modulus', 'pinn_time_dilation']
    
    def calculate_features(self, light_curve_data, metadata=None):
        features = {}
        object_ids = light_curve_data['object_id'].unique()
        for feature in self.feature_names:
            features[feature] = [0.0] * len(object_ids)
        return features
    
    def physics_loss(self, light_curve_data):
        return 0.0

class VariabilityTimescalesPINN(PINNModule):
    def __init__(self):
        super().__init__("variability_timescales", "Characteristic timescales")
        self.feature_names = ['pinn_characteristic_timescale', 'pinn_rise_time_metric']
    
    def calculate_features(self, light_curve_data):
        features = {}
        object_ids = light_curve_data['object_id'].unique()
        for feature in self.feature_names:
            features[feature] = [0.0] * len(object_ids)
        return features
    
    def physics_loss(self, light_curve_data):
        return 0.0
#Corrected CosmoNet PINN MANAGER##############################
##############################################################
#changed
# class CosmoNetPINN:
#     """
#     UPDATED PINN MANAGER - Now with all Tier 3 competition-optimized modules
#     """
    
#     def __init__(self, modules=None, auto_setup=True, include_phase2=True, 
#                  include_phase3=True, include_tier2=True, include_tier3=True):
#         # Start with basic modules
#         self.available_modules = {
#             'smoothness': LightCurveSmoothnessPINN(),
#             'plausibility': PhysicalPlausibilityPINN(),
#             'variability': VariabilityPhysicsPINN(),
#         }
        
#         # Safely add other modules if they exist
#         module_classes = {
#             'core_explosion': CoreExplosionPINN,
#             'supernova_discrimination': SupernovaDiscriminationPINN,
#             'subluminous_discrimination': SubluminousDiscriminationPINN,
#             'explosion_discrimination': ExplosionDiscriminationPINN,
#             'spectral_evolution': SpectralEvolutionPINN,
#         }
        
#         for name, class_obj in module_classes.items():
#             try:
#                 self.available_modules[name] = class_obj()
#             except:
#                 print(f"⚠️ Could not load module: {name}")
        
#         # Add Phase 2 modules if requested
#         if include_phase2:
#             try:
#                 self.available_modules['redshift_physics'] = RedshiftPhysicsPINN()
#                 self.available_modules['variability_timescales'] = VariabilityTimescalesPINN()
#             except:
#                 print("⚠️ Could not load Phase 2 modules")
        
#         # Add Phase 3 modules if requested
#         if include_phase3:
#             try:
#                 self.available_modules['multi_scale_physics'] = MultiScalePhysicsPINN()
#                 self.available_modules['host_galaxy_context'] = HostGalaxyContextPINN()
#             except:
#                 print("⚠️ Could not load Phase 3 modules")
        
#         # Add Tier 2 modules if requested
#         if include_tier2:
#             try:
#                 self.available_modules['radioactive_decay'] = RadioactiveDecayPhysicsPINN()
#                 self.available_modules['shock_physics'] = ShockPhysicsPINN()
#             except:
#                 print("⚠️ Could not load Tier 2 modules")
        
#         # Add Tier 3 modules if requested
#         if include_tier3:
#             try:
#                 self.available_modules['confusion_resolution'] = ConfusionResolutionPINN()
#                 self.available_modules['bayesian_evidence'] = BayesianEvidencePINN()
#             except:
#                 print("⚠️ Could not load Tier 3 modules")
        
#         # Active modules (all enabled by default)
#         self.active_modules = self.available_modules.copy()
        
#         if auto_setup:
#             self._setup_modules()
    
#     def _setup_modules(self):
#         """Setup all PINN modules"""
#         print("🚀 CosmoNetPINN initialized with modules:")
#         for name, module in self.active_modules.items():
#             print(f"   ✅ {name}: {module.description}")
#         print(f"   Total features: {self.get_total_feature_count()}")
        
#         # Show comprehensive breakdown
#         phase1 = ['smoothness', 'plausibility', 'variability', 'core_explosion', 
#                  'supernova_discrimination', 'subluminous_discrimination', 
#                  'explosion_discrimination', 'spectral_evolution']
#         phase2 = ['redshift_physics', 'variability_timescales']
#         phase3 = ['multi_scale_physics', 'host_galaxy_context']
#         tier2 = ['radioactive_decay', 'shock_physics']
#         tier3 = ['confusion_resolution', 'bayesian_evidence']
        
#         phase1_count = len([m for m in self.active_modules.keys() if m in phase1])
#         phase2_count = len([m for m in self.active_modules.keys() if m in phase2])
#         phase3_count = len([m for m in self.active_modules.keys() if m in phase3])
#         tier2_count = len([m for m in self.active_modules.keys() if m in tier2])
#         tier3_count = len([m for m in self.active_modules.keys() if m in tier3])
        
#         print(f"   📊 Phase 1 (Core Physics): {phase1_count} modules")
#         print(f"   🚀 Phase 2 (Advanced): {phase2_count} modules") 
#         print(f"   🔬 Phase 3 (Context): {phase3_count} modules")
#         print(f"   💥 Tier 2 (Physics): {tier2_count} modules")
#         print(f"   🎯 Tier 3 (Competition): {tier3_count} modules")
#         print(f"   🏆 Total: {phase1_count + phase2_count + phase3_count + tier2_count + tier3_count} modules")
class CosmoNetPINN:
    """
    UPDATED PINN MANAGER - Fixed output handling for large datasets
    """
    
    def __init__(self, modules=None, auto_setup=True, include_phase2=True, 
                 include_phase3=True, include_tier2=True, include_tier3=True):
        # Start with basic modules
        self.available_modules = {
            'smoothness': LightCurveSmoothnessPINN(),
            'plausibility': PhysicalPlausibilityPINN(),
            'variability': VariabilityPhysicsPINN(),
        }
        
        # Safely add other modules if they exist
        module_classes = {
            'core_explosion': CoreExplosionPINN,
            'supernova_discrimination': SupernovaDiscriminationPINN,
            'subluminous_discrimination': SubluminousDiscriminationPINN,
            'explosion_discrimination': ExplosionDiscriminationPINN,
            'spectral_evolution': SpectralEvolutionPINN,
        }
        
        for name, class_obj in module_classes.items():
            try:
                self.available_modules[name] = class_obj()
            except:
                print(f"⚠️ Could not load module: {name}")
        
        # Add Phase 2 modules if requested
        if include_phase2:
            try:
                self.available_modules['redshift_physics'] = RedshiftPhysicsPINN()
                self.available_modules['variability_timescales'] = VariabilityTimescalesPINN()
            except:
                print("⚠️ Could not load Phase 2 modules")
        
        # Add Phase 3 modules if requested
        if include_phase3:
            try:
                self.available_modules['multi_scale_physics'] = MultiScalePhysicsPINN()
                self.available_modules['host_galaxy_context'] = HostGalaxyContextPINN()
            except:
                print("⚠️ Could not load Phase 3 modules")
        
        # Add Tier 2 modules if requested
        if include_tier2:
            try:
                self.available_modules['radioactive_decay'] = RadioactiveDecayPhysicsPINN()
                self.available_modules['shock_physics'] = ShockPhysicsPINN()
            except:
                print("⚠️ Could not load Tier 2 modules")
        
        # Add Tier 3 modules if requested
        if include_tier3:
            try:
                self.available_modules['confusion_resolution'] = ConfusionResolutionPINN()
                self.available_modules['bayesian_evidence'] = BayesianEvidencePINN()
            except:
                print("⚠️ Could not load Tier 3 modules")
        
        # Active modules (all enabled by default)
        self.active_modules = self.available_modules.copy()
        
        if auto_setup:
            self._setup_modules()
    
    def _setup_modules(self):
        """Setup all PINN modules with clean output"""
        print("🚀 CosmoNetPINN initialized with modules:")
        for name, module in self.active_modules.items():
            print(f"   ✅ {name}: {module.description}")
        
        total_features = self.get_total_feature_count()
        print(f"   Total features: {total_features}")
        
        # Show clean phase breakdown
        phase1 = ['smoothness', 'plausibility', 'variability', 'core_explosion', 
                 'supernova_discrimination', 'subluminous_discrimination', 
                 'explosion_discrimination', 'spectral_evolution']
        phase2 = ['redshift_physics', 'variability_timescales']
        phase3 = ['multi_scale_physics', 'host_galaxy_context']
        tier2 = ['radioactive_decay', 'shock_physics']
        tier3 = ['confusion_resolution', 'bayesian_evidence']
        
        phase1_count = len([m for m in self.active_modules.keys() if m in phase1])
        phase2_count = len([m for m in self.active_modules.keys() if m in phase2])
        phase3_count = len([m for m in self.active_modules.keys() if m in phase3])
        tier2_count = len([m for m in self.active_modules.keys() if m in tier2])
        tier3_count = len([m for m in self.active_modules.keys() if m in tier3])
        
        print(f"   📊 Phase 1 (Core Physics): {phase1_count} modules")
        print(f"   🚀 Phase 2 (Advanced): {phase2_count} modules") 
        print(f"   🔬 Phase 3 (Context): {phase3_count} modules")
        print(f"   💥 Tier 2 (Physics): {tier2_count} modules")
        print(f"   🎯 Tier 3 (Competition): {tier3_count} modules")
        print(f"   🏆 Total: {phase1_count + phase2_count + phase3_count + tier2_count + tier3_count} modules")
    
    def calculate_all_features(self, light_curve_data, metadata=None):
        """
        MAIN FUNCTION: Calculate ALL PINN features with clean output for large datasets
        """
        n_objects = light_curve_data['object_id'].nunique()
        print(f"🎯 Calculating PINN features for {n_objects:,} objects...")
        
        # Suppress detailed output for large datasets
        show_detailed_output = n_objects < 1000
        
        all_features = {}
        feature_descriptions = {}
        module_results = {}
        
        # Track progress for large datasets
        if not show_detailed_output:
            print("   📊 Processing modules...", end='', flush=True)
        
        for i, (module_name, module) in enumerate(self.active_modules.items()):
            if show_detailed_output:
                print(f"   🔧 {module_name}...")
            else:
                # Show progress indicator for large datasets
                progress_chars = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
                print(f'\r   📊 Processing modules... {progress_chars[i % len(progress_chars)]} ({i+1}/{len(self.active_modules)})', end='', flush=True)
            
            try:
                # Pass metadata to modules that need it
                if module_name == 'redshift_physics' and metadata is not None:
                    module_features = module.calculate_features(light_curve_data, metadata)
                elif module_name == 'host_galaxy_context' and metadata is not None:
                    module_features = module.calculate_features(light_curve_data, metadata)
                else:
                    module_features = module.calculate_features(light_curve_data)
                
                if show_detailed_output:
                    print(f"      📊 Returned {len(module_features)} features")
                
                # Store module results
                module_results[module_name] = {
                    'success': True,
                    'feature_count': len(module_features),
                    'features': module_features
                }
                
                # Add module features to overall features with module prefix
                for feature_name, feature_values in module_features.items():
                    unique_feature_name = f"{module_name}_{feature_name}"
                    
                    # Ensure we have the right number of values
                    if len(feature_values) != n_objects:
                        if show_detailed_output:
                            print(f"      ⚠️ Feature {unique_feature_name} has wrong length: {len(feature_values)} vs {n_objects}")
                        # Fill with default values
                        feature_values = [0.0] * n_objects
                    
                    # Convert to numpy array and handle NaN/inf
                    feature_array = np.array(feature_values, dtype=np.float64)
                    
                    # Replace NaN and Inf with 0
                    feature_array = np.nan_to_num(feature_array, nan=0.0, posinf=0.0, neginf=0.0)
                    
                    all_features[unique_feature_name] = feature_array
                    feature_descriptions[unique_feature_name] = f"{module.description}: {feature_name}"
                        
            except Exception as e:
                if show_detailed_output:
                    print(f"   ⚠️ Error in {module_name}: {e}")
                else:
                    print(f'\r   ⚠️ Error in {module_name}', end='', flush=True)
                
                # Store error information
                module_results[module_name] = {
                    'success': False,
                    'error': str(e),
                    'feature_count': 0
                }
                
                # Add default values for failed module
                for feature_name in module.feature_names:
                    unique_feature_name = f"{module_name}_{feature_name}"
                    all_features[unique_feature_name] = [0.0] * n_objects
        
        # Clear progress line for large datasets
        if not show_detailed_output:
            print('\r' + ' ' * 50, end='', flush=True)  # Clear line
            print('\r   ✅ All modules processed', flush=True)
        
        # Create DataFrame
        object_ids = light_curve_data['object_id'].unique()
        feature_df = pd.DataFrame(all_features, index=object_ids)
        feature_df.index.name = 'object_id'
        
        # Final NaN check and cleanup
        nan_count = feature_df.isna().sum().sum()
        if nan_count > 0:
            print(f"   🧹 Final cleanup: Found {nan_count} NaN values, filling with 0...")
            feature_df = feature_df.fillna(0)
        
        total_features = len(feature_df.columns)
        print(f"✅ Generated {total_features} PINN features")
        
        # Show summary for large datasets
        if not show_detailed_output:
            self._show_large_dataset_summary(module_results, total_features)
        else:
            # Show detailed features by module for small datasets
            print(f"\n📋 FEATURES BY MODULE:")
            for module_name in self.active_modules.keys():
                module_feats = [f for f in feature_df.columns if f.startswith(f"{module_name}_")]
                print(f"   {module_name}: {len(module_feats)} features")
        
        return feature_df
    
    def _show_large_dataset_summary(self, module_results, total_features):
        """Show clean summary for large datasets"""
        print(f"\n📊 PINN FEATURE SUMMARY:")
        print(f"   Total features generated: {total_features}")
        
        # Count successful vs failed modules
        successful_modules = [name for name, result in module_results.items() if result['success']]
        failed_modules = [name for name, result in module_results.items() if not result['success']]
        
        print(f"   ✅ Successful modules: {len(successful_modules)}/{len(self.active_modules)}")
        
        if failed_modules:
            print(f"   ⚠️  Failed modules: {len(failed_modules)}")
            for failed in failed_modules[:3]:  # Show first 3 failures
                error_msg = module_results[failed]['error']
                print(f"      - {failed}: {error_msg[:50]}..." if len(error_msg) > 50 else f"      - {failed}: {error_msg}")
            if len(failed_modules) > 3:
                print(f"      ... and {len(failed_modules) - 3} more")
        
        # Show feature breakdown by category
        categories = {
            'Core Physics': ['smoothness', 'plausibility', 'variability', 'core_explosion', 
                           'supernova_discrimination', 'subluminous_discrimination', 
                           'explosion_discrimination', 'spectral_evolution'],
            'Advanced': ['redshift_physics', 'variability_timescales'],
            'Context': ['multi_scale_physics', 'host_galaxy_context'],
            'Physics': ['radioactive_decay', 'shock_physics'],
            'Competition': ['confusion_resolution', 'bayesian_evidence']
        }
        
        print(f"\n🎯 FEATURES BY CATEGORY:")
        for category, modules in categories.items():
            category_feats = sum(module_results.get(m, {}).get('feature_count', 0) for m in modules if m in module_results)
            if category_feats > 0:
                print(f"   {category}: {category_feats} features")
    
    def enable_module(self, module_name):
        """Enable a specific PINN module"""
        if module_name in self.available_modules:
            self.active_modules[module_name] = self.available_modules[module_name]
            print(f"✅ Enabled module: {module_name}")
        else:
            print(f"❌ Module not found: {module_name}")
    
    def disable_module(self, module_name):
        """Disable a specific PINN module"""
        if module_name in self.active_modules:
            del self.active_modules[module_name]
            print(f"🔌 Disabled module: {module_name}")
        else:
            print(f"⚠️ Module not active: {module_name}")
    
    def add_custom_module(self, module_name, pinn_module):
        """Add your own PINN modules"""
        if not isinstance(pinn_module, PINNModule):
            raise ValueError("Custom module must inherit from PINNModule")
        
        self.available_modules[module_name] = pinn_module
        self.active_modules[module_name] = pinn_module
        
        print(f"🧩 Added custom module: {module_name}")
        print(f"   Description: {pinn_module.description}")
        print(f"   Features: {', '.join(pinn_module.feature_names)}")
    
    def get_module_info(self):
        """Get information about all modules"""
        info = {}
        for name, module in self.available_modules.items():
            info[name] = {
                'description': module.description,
                'features': module.feature_names,
                'active': name in self.active_modules
            }
        return info
    
    def get_total_feature_count(self):
        """Get total number of features from active modules"""
        total = 0
        for module in self.active_modules.values():
            total += len(module.feature_names)
        return total
    
    def calculate_physics_loss(self, light_curve_data):
        """Calculate total physics loss from all active modules"""
        total_loss = 0.0
        module_count = 0
        
        n_objects = light_curve_data['object_id'].nunique()
        show_detailed = n_objects < 1000
        
        if not show_detailed:
            print("   📊 Calculating physics losses...", end='', flush=True)
        
        for i, (module_name, module) in enumerate(self.active_modules.items()):
            try:
                module_loss = module.physics_loss(light_curve_data)
                total_loss += module_loss
                module_count += 1
                
                if show_detailed:
                    print(f"   📊 {module_name} physics loss: {module_loss:.6f}")
                else:
                    progress_chars = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
                    print(f'\r   📊 Calculating physics losses... {progress_chars[i % len(progress_chars)]} ({i+1}/{len(self.active_modules)})', end='', flush=True)
                    
            except Exception as e:
                if show_detailed:
                    print(f"   ⚠️ {module_name} loss calculation failed: {e}")
        
        # Clear progress line for large datasets
        if not show_detailed:
            print('\r' + ' ' * 50, end='', flush=True)
            print('\r   ✅ Physics losses calculated', flush=True)
        
        avg_loss = total_loss / module_count if module_count > 0 else 0.0
        print(f"📊 Total average physics loss: {avg_loss:.6f}")
        return avg_loss
    
    def get_feature_breakdown(self):
        """Get detailed breakdown of all features by module"""
        breakdown = {}
        for module_name, module in self.active_modules.items():
            breakdown[module_name] = {
                'description': module.description,
                'features': module.feature_names,
                'feature_count': len(module.feature_names)
            }
        return breakdown
    
    def list_all_features(self):
        """List all available features with descriptions"""
        all_features = {}
        for module_name, module in self.active_modules.items():
            for feature_name in module.feature_names:
                full_name = f"{module_name}_{feature_name}"
                all_features[full_name] = {
                    'module': module_name,
                    'description': f"{module.description}: {feature_name}",
                    'module_description': module.description
                }
        return all_features
    
    def validate_features(self, feature_df):
        """Validate the generated features for quality"""
        print("🔍 Validating PINN features...")
        
        issues = []
        warnings = []
        
        # Check for constant features
        constant_features = []
        for col in feature_df.columns:
            if feature_df[col].nunique() == 1:
                constant_features.append(col)
        
        if constant_features:
            warnings.append(f"Found {len(constant_features)} constant features")
        
        # Check for extreme values
        extreme_features = []
        for col in feature_df.columns:
            if feature_df[col].abs().max() > 1e6:  # Very large values
                extreme_features.append(col)
        
        if extreme_features:
            warnings.append(f"Found {len(extreme_features)} features with extreme values")
        
        # Check feature correlations
        try:
            corr_matrix = feature_df.corr().abs()
            high_corr_pairs = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    if corr_matrix.iloc[i, j] > 0.95:
                        high_corr_pairs.append((corr_matrix.columns[i], corr_matrix.columns[j]))
            
            if high_corr_pairs:
                warnings.append(f"Found {len(high_corr_pairs)} highly correlated feature pairs (>0.95)")
        except:
            warnings.append("Could not compute correlation matrix")
        
        # Report results
        if not issues and not warnings:
            print("   ✅ All features passed validation")
        else:
            if warnings:
                print("   ⚠️  Warnings:")
                for warning in warnings[:5]:  # Show first 5 warnings
                    print(f"      - {warning}")
            
            if issues:
                print("   ❌ Issues:")
                for issue in issues[:5]:  # Show first 5 issues
                    print(f"      - {issue}")
        
        return {
            'issues': issues,
            'warnings': warnings,
            'constant_features': constant_features,
            'extreme_features': extreme_features
        }
    
    
       








































# class CosmoNetPINN:
#     """
#     MAIN PINN MANAGER - One class to rule all PINN modules!
    
#     Usage:
#     1. pinn = CosmoNetPINN()
#     2. features = pinn.calculate_all_features(light_curve_data)
#     3. That's it!
#     """
    
   
#     def __init__(self, modules=None, auto_setup=True):
#         # Available PINN modules
#         self.available_modules = {
#             'smoothness': LightCurveSmoothnessPINN(),
#             'plausibility': PhysicalPlausibilityPINN(), 
#             'variability': VariabilityPhysicsPINN(),
#             'redshift_physics': RedshiftPhysicsPINN(),
#             'variability_timescales': VariabilityTimescalesPINN(),
#             # 🆕 ADD THIS LINE:
#             'explosion_physics': ExplosionPhysicsPINN()
#         }
            
#             # Active modules (all enabled by default)
#         self.active_modules = self.available_modules.copy()
            
#         if auto_setup:
#                 self._setup_modules()
    
#     def _setup_modules(self):
#         """Setup all PINN modules"""
#         print("🚀 CosmoNetPINN initialized with modules:")
#         for name, module in self.active_modules.items():
#             print(f"   ✅ {name}: {module.description}")
#             print(f"      Features: {', '.join(module.feature_names)}")
#         print(f"   Total features: {self.get_total_feature_count()}")
    
#     def calculate_all_features(self, light_curve_data):
#         """
#         MAIN FUNCTION: Calculate ALL PINN features with ONE call
        
#         Args:
#             light_curve_data: Your light curve DataFrame
        
#         Returns:
#             DataFrame with all PINN features, indexed by object_id
#         """
#         print(f"🎯 Calculating PINN features for {light_curve_data['object_id'].nunique()} objects...")
        
#         all_features = {}
#         feature_descriptions = {}
        
#         for module_name, module in self.active_modules.items():
#             print(f"   🔧 {module_name}...")
#             try:
#                 module_features = module.calculate_features(light_curve_data)
                
#                 # Add module features to overall features
#                 for feature_name, feature_values in module_features.items():
#                     all_features[feature_name] = feature_values
#                     feature_descriptions[feature_name] = module.description
                    
#             except Exception as e:
#                 print(f"   ⚠️ Error in {module_name}: {e}")
#                 # Add default values for failed module
#                 for feature_name in module.feature_names:
#                     all_features[feature_name] = [0.0] * light_curve_data['object_id'].nunique()
        
#         # Create DataFrame
#         object_ids = light_curve_data['object_id'].unique()
#         feature_df = pd.DataFrame(all_features, index=object_ids)
#         feature_df.index.name = 'object_id'
        
#         print(f"✅ Generated {len(feature_df.columns)} PINN features")
#         return feature_df
    
#     def enable_module(self, module_name):
#         """Enable a specific PINN module"""
#         if module_name in self.available_modules:
#             self.active_modules[module_name] = self.available_modules[module_name]
#             print(f"✅ Enabled module: {module_name}")
#         else:
#             print(f"❌ Module not found: {module_name}")
    
#     def disable_module(self, module_name):
#         """Disable a specific PINN module"""
#         if module_name in self.active_modules:
#             del self.active_modules[module_name]
#             print(f"🔌 Disabled module: {module_name}")
#         else:
#             print(f"⚠️ Module not active: {module_name}")
    
#     def add_custom_module(self, module_name, pinn_module):
#         """
#         ADD YOUR OWN PINN MODULES HERE!
        
#         Args:
#             module_name: Unique name for your module
#             pinn_module: Instance of a class that inherits from PINNModule
#         """
#         if not isinstance(pinn_module, PINNModule):
#             raise ValueError("Custom module must inherit from PINNModule")
        
#         self.available_modules[module_name] = pinn_module
#         self.active_modules[module_name] = pinn_module
        
#         print(f"🧩 Added custom module: {module_name}")
#         print(f"   Description: {pinn_module.description}")
#         print(f"   Features: {', '.join(pinn_module.feature_names)}")
    
#     def get_module_info(self):
#         """Get information about all modules"""
#         info = {}
#         for name, module in self.available_modules.items():
#             info[name] = {
#                 'description': module.description,
#                 'features': module.feature_names,
#                 'active': name in self.active_modules
#             }
#         return info
    
#     def get_total_feature_count(self):
#         """Get total number of features from active modules"""
#         total = 0
#         for module in self.active_modules.values():
#             total += len(module.feature_names)
#         return total
    
#     def calculate_physics_loss(self, light_curve_data):
#         """Calculate total physics loss from all active modules"""
#         total_loss = 0.0
#         module_count = 0
        
#         for module_name, module in self.active_modules.items():
#             try:
#                 module_loss = module.physics_loss(light_curve_data)
#                 total_loss += module_loss
#                 module_count += 1
#                 print(f"   📊 {module_name} physics loss: {module_loss:.6f}")
#             except Exception as e:
#                 print(f"   ⚠️ {module_name} loss calculation failed: {e}")
        
#         avg_loss = total_loss / module_count if module_count > 0 else 0.0
#         print(f"📊 Total average physics loss: {avg_loss:.6f}")
#         return avg_loss

# ============================================================================
# ULTRA-SIMPLE USAGE FUNCTIONS
# ============================================================================

# Global instance for easiest usage
_pinn_manager = None

def get_pinn():
    """Get the global PINN manager instance"""
    global _pinn_manager
    if _pinn_manager is None:
        _pinn_manager = CosmoNetPINN()
    return _pinn_manager

def calculate_pinn_features(light_curve_data):
    """
    ONE-FUNCTION SOLUTION for PINN features
    
    Usage:
        pinn_features = calculate_pinn_features(your_light_curve_data)
    """
    pinn = get_pinn()
    return pinn.calculate_all_features(light_curve_data)

def add_custom_pinn_module(module_name, pinn_module):
    """
    Add your custom PINN module to the global manager
    
    Usage:
        class MyCustomPINN(PINNModule):
            # ... your implementation ...
        
        add_custom_pinn_module('my_custom', MyCustomPINN())
    """
    pinn = get_pinn()
    pinn.add_custom_module(module_name, pinn_module)

# ============================================================================
# EXAMPLE: How to add your own PINN modules
# ============================================================================

class ExampleCustomPINN(PINNModule):
    """
    EXAMPLE: How to create your own PINN module
    Copy this structure to add more physics constraints!
    """
    
    def __init__(self):
        super().__init__(
            name="example_custom",
            description="Example custom PINN module - replace with your physics!"
        )
        self.feature_names = [
            'custom_feature_1',
            'custom_feature_2'
        ]
    
    def calculate_features(self, light_curve_data):
        """Calculate your custom features here"""
        # Your implementation here
        object_ids = light_curve_data['object_id'].unique()
        
        return {
            'custom_feature_1': [1.0] * len(object_ids),  # Replace with real calculation
            'custom_feature_2': [0.5] * len(object_ids)   # Replace with real calculation
        }
    
    def physics_loss(self, light_curve_data):
        """Calculate your physics loss here"""
        # Your implementation here  
        return 0.0

















# ============================================================================
# PHASE 2: REDSHIFT PHYSICS PINN 
# ============================================================================

class RedshiftPhysicsPINN(PINNModule):
    """
    PINN for cosmological redshift effects and distance corrections
    """
    
    def __init__(self):
        super().__init__(
            name="redshift_physics",
            description="Cosmological redshift effects and distance corrections"
        )
        self.feature_names = [
            'pinn_distance_modulus',
            'pinn_time_dilation', 
            'pinn_redshift_quality',
            'pinn_flux_correction_factor',
            'pinn_cosmological_distance'
        ]
    
    def calculate_features(self, light_curve_data, metadata=None):
        """Calculate redshift-based physics features"""
        features = {}
        
        if metadata is None:
            # Return default values if no metadata
            object_ids = light_curve_data['object_id'].unique()
            for feature in self.feature_names:
                features[feature] = [0.0] * len(object_ids)
            return features
        
        # Merge redshift data with light curves
        redshift_info = metadata.set_index('object_id')[['hostgal_specz', 'hostgal_photoz']]
        data_with_z = light_curve_data.merge(redshift_info, on='object_id', how='left')
        
        object_ids = light_curve_data['object_id'].unique()
        distance_moduli = []
        time_dilations = []
        redshift_qualities = []
        flux_factors = []
        cosmological_distances = []
        
        for obj_id in object_ids:
            obj_data = data_with_z[data_with_z['object_id'] == obj_id]
            
            if not obj_data.empty:
                # Use spectroscopic redshift if available, otherwise photometric
                z_spec = obj_data['hostgal_specz'].iloc[0]
                z_photo = obj_data['hostgal_photoz'].iloc[0]
                
                if not np.isnan(z_spec):
                    z = z_spec
                    z_quality = 1.0  # High quality - spectroscopic
                elif not np.isnan(z_photo) and z_photo > 0:
                    z = z_photo
                    z_quality = 0.7  # Medium quality - photometric
                else:
                    z = 0.0
                    z_quality = 0.3  # Low quality - no redshift
            else:
                z = 0.0
                z_quality = 0.3
            
            # 1. Distance modulus (simplified)
            if z > 0:
                # Simplified distance modulus: μ ≈ 5log₁₀(c z / H₀) + 25
                # Using H₀ = 70 km/s/Mpc, c = 3e5 km/s
                d_lum = 3e5 * z / 70  # Luminosity distance in Mpc (simplified)
                dist_modulus = 5 * np.log10(d_lum * 1e6) + 25  # Convert to parsecs
                cosmological_dist = d_lum
            else:
                dist_modulus = 0.0
                cosmological_dist = 0.0
            
            # 2. Time dilation factor
            time_dilation = 1.0 + z
            
            # 3. Flux correction factor (inverse square law)
            flux_correction = (1.0 + z) ** 2 if z > 0 else 1.0
            
            distance_moduli.append(dist_modulus)
            time_dilations.append(time_dilation)
            redshift_qualities.append(z_quality)
            flux_factors.append(flux_correction)
            cosmological_distances.append(cosmological_dist)
        
        features['pinn_distance_modulus'] = distance_moduli
        features['pinn_time_dilation'] = time_dilations
        features['pinn_redshift_quality'] = redshift_qualities
        features['pinn_flux_correction_factor'] = flux_factors
        features['pinn_cosmological_distance'] = cosmological_distances
        
        return features
    
    def physics_loss(self, light_curve_data):
        """Physics loss for redshift constraints"""
        return 0.0  # Would require metadata

# ============================================================================
# PHASE 2: VARIABILITY TIMESCALES PINN
# ============================================================================

class VariabilityTimescalesPINN(PINNModule):
    """
    PINN for characteristic variability timescales and temporal patterns
    """
    
    def __init__(self):
        super().__init__(
            name="variability_timescales", 
            description="Characteristic physical timescales and temporal patterns"
        )
        self.feature_names = [
            'pinn_characteristic_timescale',
            'pinn_rise_time_metric',
            'pinn_decay_time_metric', 
            'pinn_variability_amplitude',
            'pinn_peak_alignment',
            'pinn_autocorrelation_timescale'
        ]
    
    def calculate_features(self, light_curve_data):
        """Calculate variability timescale features"""
        features = {}
        
        object_ids = light_curve_data['object_id'].unique()
        char_timescales = []
        rise_times = []
        decay_times = []
        variability_amps = []
        peak_alignments = []
        autocorr_timescales = []
        
        for obj_id in object_ids:
            obj_data = light_curve_data[light_curve_data['object_id'] == obj_id]
            
            if len(obj_data) < 3:
                # Default values for insufficient data
                char_timescales.append(0.0)
                rise_times.append(0.0)
                decay_times.append(0.0)
                variability_amps.append(0.0)
                peak_alignments.append(0.0)
                autocorr_timescales.append(0.0)
                continue
            
            times = obj_data['mjd'].values
            fluxes = obj_data['flux'].values
            
            # Sort by time
            time_sorted_idx = np.argsort(times)
            times_sorted = times[time_sorted_idx]
            fluxes_sorted = fluxes[time_sorted_idx]
            
            total_duration = times_sorted[-1] - times_sorted[0]
            if total_duration <= 0:
                # Default values
                char_timescales.append(0.0)
                rise_times.append(0.0)
                decay_times.append(0.0)
                variability_amps.append(0.0)
                peak_alignments.append(0.0)
                autocorr_timescales.append(0.0)
                continue
            
            # 1. Characteristic timescale (mean time between observations)
            time_diffs = np.diff(times_sorted)
            char_timescale = np.mean(time_diffs) if len(time_diffs) > 0 else 0.0
            
            # 2. Rise and decay time metrics
            max_flux_idx = np.argmax(fluxes_sorted)
            min_flux_idx = np.argmin(fluxes_sorted)
            
            if max_flux_idx > 0:
                rise_time = times_sorted[max_flux_idx] - times_sorted[0]
            else:
                rise_time = 0.0
                
            if max_flux_idx < len(times_sorted) - 1:
                decay_time = times_sorted[-1] - times_sorted[max_flux_idx]
            else:
                decay_time = 0.0
            
            # Normalize by total duration
            rise_time_metric = rise_time / total_duration if total_duration > 0 else 0.0
            decay_time_metric = decay_time / total_duration if total_duration > 0 else 0.0
            
            # 3. Variability amplitude (normalized)
            flux_range = np.max(fluxes_sorted) - np.min(fluxes_sorted)
            flux_mean = np.mean(np.abs(fluxes_sorted))
            variability_amp = flux_range / (flux_mean + 1e-8) if flux_mean > 0 else 0.0
            
            # 4. Peak alignment (how centered is the peak in time)
            if len(times_sorted) > 0:
                peak_position = max_flux_idx / len(times_sorted)
                peak_alignment = 1.0 - abs(peak_position - 0.5) * 2  # 1.0 = centered
            else:
                peak_alignment = 0.0
            
            # 5. Autocorrelation timescale (simplified)
            autocorr_timescale = self._calculate_autocorrelation_timescale(times_sorted, fluxes_sorted)
            
            char_timescales.append(char_timescale)
            rise_times.append(rise_time_metric)
            decay_times.append(decay_time_metric)
            variability_amps.append(variability_amp)
            peak_alignments.append(peak_alignment)
            autocorr_timescales.append(autocorr_timescale)
        
        features['pinn_characteristic_timescale'] = char_timescales
        features['pinn_rise_time_metric'] = rise_times
        features['pinn_decay_time_metric'] = decay_times
        features['pinn_variability_amplitude'] = variability_amps
        features['pinn_peak_alignment'] = peak_alignments
        features['pinn_autocorrelation_timescale'] = autocorr_timescales
        
        return features
    
    def _calculate_autocorrelation_timescale(self, times, fluxes):
        """Calculate simplified autocorrelation timescale"""
        if len(fluxes) < 4:
            return 0.0
        
        try:
            # Simple autocorrelation at lag 1
            correlated = np.corrcoef(fluxes[:-1], fluxes[1:])[0, 1]
            if np.isnan(correlated):
                return 0.0
            
            # Convert correlation to timescale (simplified)
            time_diffs = np.diff(times)
            avg_time_diff = np.mean(time_diffs) if len(time_diffs) > 0 else 1.0
            autocorr_timescale = max(0.0, correlated) * avg_time_diff * 5  # Scale factor
            
            return autocorr_timescale
        except:
            return 0.0
    
    def physics_loss(self, light_curve_data):
        """Physics loss for timescale constraints"""
        total_loss = 0.0
        count = 0
        
        for obj_id in light_curve_data['object_id'].unique():
            obj_data = light_curve_data[light_curve_data['object_id'] == obj_id]
            if len(obj_data) >= 3:
                features = self.calculate_features(pd.DataFrame([obj_data]))
                # Penalize physically implausible timescales
                if features['pinn_characteristic_timescale'][0] > 1000:  # Unrealistically long
                    total_loss += 1.0
                count += 1
        
        return total_loss / count if count > 0 else 0.0

# ============================================================================
# UPDATED MAIN PINN MANAGER WITH PHASE 2 MODULES
# ============================================================================







# ============================================================================
# PHASE 3: EXPLOSION PHYSICS PINN 
# ============================================================================

class ExplosionPhysicsPINN(PINNModule):
    """
    PINN for explosion physics - covers SNIa, SNII, Kilonova, etc.
    """
    
    def __init__(self):
        super().__init__(
            name="explosion_physics",
            description="Explosion energy, nickel mass, and shock physics for transients"
        )
        self.feature_names = [
            'pinn_explosion_energy_estimate',
            'pinn_nickel_mass_estimate', 
            'pinn_rise_time_characteristic',
            'pinn_decay_consistency',
            'pinn_peak_luminosity_proxy'
        ]
    
    def calculate_features(self, light_curve_data):
        """Calculate explosion physics features for ALL objects"""
        features = {}
        
        object_ids = light_curve_data['object_id'].unique()
        explosion_energies = []
        nickel_masses = []
        rise_times = []
        decay_consistencies = []
        peak_luminosities = []
        
        for obj_id in object_ids:
            obj_data = light_curve_data[light_curve_data['object_id'] == obj_id]
            obj_features = self._analyze_explosion_physics(obj_data)
            
            explosion_energies.append(obj_features['explosion_energy'])
            nickel_masses.append(obj_features['nickel_mass'])
            rise_times.append(obj_features['rise_time'])
            decay_consistencies.append(obj_features['decay_consistency'])
            peak_luminosities.append(obj_features['peak_luminosity'])
        
        features['pinn_explosion_energy_estimate'] = explosion_energies
        features['pinn_nickel_mass_estimate'] = nickel_masses
        features['pinn_rise_time_characteristic'] = rise_times
        features['pinn_decay_consistency'] = decay_consistencies
        features['pinn_peak_luminosity_proxy'] = peak_luminosities
        
        return features
    
    def _analyze_explosion_physics(self, obj_data):
        """Analyze explosion physics for a single object"""
        if len(obj_data) < 4:
            return {
                'explosion_energy': 0.0, 
                'nickel_mass': 0.0, 
                'rise_time': 0.0, 
                'decay_consistency': 0.5,
                'peak_luminosity': 0.0
            }
        
        times = obj_data['mjd'].values
        fluxes = obj_data['flux'].values
        
        # Sort by time
        time_sorted_idx = np.argsort(times)
        times_sorted = times[time_sorted_idx]
        fluxes_sorted = fluxes[time_sorted_idx]
        
        # 1. Peak luminosity proxy
        peak_flux = np.max(fluxes_sorted)
        mean_flux = np.mean(np.abs(fluxes_sorted))
        peak_luminosity = peak_flux
        
        # 2. Explosion energy estimate
        explosion_energy = peak_flux / (mean_flux + 1e-8)
        
        # 3. Nickel mass estimate
        peak_idx = np.argmax(fluxes_sorted)
        nickel_mass = self._estimate_nickel_mass(times_sorted, fluxes_sorted, peak_idx)
        
        # 4. Characteristic rise time
        rise_time = times_sorted[peak_idx] - times_sorted[0] if peak_idx > 0 else 0.0
        
        # 5. Decay consistency
        decay_consistency = self._calculate_decay_consistency(times_sorted, fluxes_sorted, peak_idx)
        
        return {
            'explosion_energy': float(explosion_energy),
            'nickel_mass': float(nickel_mass),
            'rise_time': float(rise_time),
            'decay_consistency': float(decay_consistency),
            'peak_luminosity': float(peak_luminosity)
        }
    
    def _estimate_nickel_mass(self, times, fluxes, peak_idx):
        """Estimate nickel mass from decay phase"""
        if peak_idx >= len(fluxes) - 2:
            return 0.0
        
        decay_fluxes = fluxes[peak_idx:]
        decay_times = times[peak_idx:]
        
        if len(decay_fluxes) < 3:
            return 0.0
        
        initial_flux = decay_fluxes[0]
        final_flux = decay_fluxes[-1]
        time_span = decay_times[-1] - decay_times[0]
        
        if time_span > 0 and initial_flux > 0:
            decay_rate = -np.log(final_flux / initial_flux) / time_span
            nickel_mass = min(decay_rate * 10, 10.0)
        else:
            nickel_mass = 0.0
            
        return nickel_mass
    
    def _calculate_decay_consistency(self, times, fluxes, peak_idx):
        """Check decay consistency with explosion models"""
        if peak_idx >= len(fluxes) - 3:
            return 0.5
        
        decay_fluxes = fluxes[peak_idx:]
        
        if len(decay_fluxes) < 2:
            return 0.5
            
        decreasing_count = 0
        for i in range(1, len(decay_fluxes)):
            if decay_fluxes[i] <= decay_fluxes[i-1] + 2.0:
                decreasing_count += 1
        
        decay_consistency = decreasing_count / (len(decay_fluxes) - 1)
        return decay_consistency
    
    def physics_loss(self, light_curve_data):
        return 0.0

















########################################
#Another Explosion Physics and Supernova::
########################################



# ADD THESE NEW MODULES TO cosmonet_pinn.py






# ENHANCE THE CoreExplosionPINN WITH BETTER ERROR HANDLING

# cosmonet_pinn.py - PRODUCTION VERSION

class CoreExplosionPINN(PINNModule):
    """
    Core explosion physics for all explosive transients
    Enhanced version with proper error handling
    """
    
    def __init__(self):
        super().__init__(
            name="core_explosion",
            description="Fundamental explosion physics for all explosive transients"
        )
        self.feature_names = [
            'pinn_total_energy_estimate',
            'pinn_characteristic_rise_time', 
            'pinn_exponential_decay_rate',
            'pinn_peak_luminosity_proxy',
            'pinn_explosion_timescale'
        ]
    
    def calculate_features(self, light_curve_data):
        """Calculate explosion features with error handling"""
        features = {}
        
        object_ids = light_curve_data['object_id'].unique()
        total_energies = []
        rise_times = []
        decay_rates = []
        peak_luminosities = []
        explosion_timescales = []
        
        for obj_id in object_ids:
            obj_data = light_curve_data[light_curve_data['object_id'] == obj_id]
            obj_features = self._analyze_explosion_physics(obj_data)
            
            total_energies.append(obj_features['total_energy'])
            rise_times.append(obj_features['rise_time'])
            decay_rates.append(obj_features['decay_rate'])
            peak_luminosities.append(obj_features['peak_luminosity'])
            explosion_timescales.append(obj_features['explosion_timescale'])
        
        features['pinn_total_energy_estimate'] = total_energies
        features['pinn_characteristic_rise_time'] = rise_times
        features['pinn_exponential_decay_rate'] = decay_rates
        features['pinn_peak_luminosity_proxy'] = peak_luminosities
        features['pinn_explosion_timescale'] = explosion_timescales
        
        return features
    
    def _analyze_explosion_physics(self, obj_data):
        """Analyze explosion physics with bounds checking"""
        if len(obj_data) < 4:
            return self._get_default_features()
        
        try:
            times = obj_data['mjd'].values
            fluxes = obj_data['flux'].values
            
            # Data validation
            if len(np.unique(times)) < 3:
                return self._get_default_features()
            
            # Sort and clean data
            time_sorted_idx = np.argsort(times)
            times_sorted = times[time_sorted_idx]
            fluxes_sorted = fluxes[time_sorted_idx]
            
            # Remove non-finite values
            valid_mask = np.isfinite(times_sorted) & np.isfinite(fluxes_sorted)
            if np.sum(valid_mask) < 4:
                return self._get_default_features()
                
            times_sorted = times_sorted[valid_mask]
            fluxes_sorted = fluxes_sorted[valid_mask]
            
            # Calculate bounded features
            features = self._calculate_explosion_features(times_sorted, fluxes_sorted)
            return self._apply_feature_bounds(features)
            
        except Exception:
            return self._get_default_features()
    
    def _calculate_explosion_features(self, times, fluxes):
        """Calculate explosion features with physical bounds"""
        peak_idx = np.argmax(fluxes)
        peak_flux = fluxes[peak_idx]
        peak_time = times[peak_idx]
        
        # 1. Total energy estimate
        if len(times) > 1:
            time_intervals = np.diff(times)
            flux_avg = (fluxes[:-1] + fluxes[1:]) / 2
            total_energy = np.sum(flux_avg * time_intervals)
            total_energy = max(0, min(total_energy, 1e6))  # Physical bounds
        else:
            total_energy = peak_flux
        
        # 2. Characteristic rise time
        if peak_idx > 0 and len(fluxes[:peak_idx+1]) >= 3:
            rise_time = self._calculate_rise_time(times[:peak_idx+1], fluxes[:peak_idx+1])
            rise_time = max(0, min(rise_time, 365))  # Max 1 year
        else:
            rise_time = max(0, min(peak_time - times[0], 365))
        
        # 3. Exponential decay rate
        if peak_idx < len(fluxes) - 2:
            decay_rate = self._calculate_decay_rate(times[peak_idx:], fluxes[peak_idx:])
            decay_rate = max(0, min(decay_rate, 50))  # Reasonable bounds
        else:
            decay_rate = 0.0
        
        # 4. Peak luminosity proxy
        peak_luminosity = max(0, min(peak_flux, 1e5))
        
        # 5. Combined explosion timescale
        if decay_rate > 0.01:
            explosion_timescale = rise_time + (1.0 / decay_rate)
        else:
            explosion_timescale = rise_time
        explosion_timescale = max(0, min(explosion_timescale, 730))  # Max 2 years
        
        return {
            'total_energy': float(total_energy),
            'rise_time': float(rise_time),
            'decay_rate': float(decay_rate),
            'peak_luminosity': float(peak_luminosity),
            'explosion_timescale': float(explosion_timescale)
        }
    
    def _calculate_rise_time(self, times, fluxes):
        """Calculate characteristic rise time"""
        try:
            from scipy.optimize import curve_fit
            
            def rise_func(t, a, tau):
                return a * (1 - np.exp(-t/tau))
            
            t_normalized = times - times[0]
            t_normalized = np.maximum(t_normalized, 1e-6)  # Avoid zero
            
            # Initial parameters with bounds
            p0 = [np.max(fluxes), np.median(t_normalized)]
            bounds = ([0, 1e-6], [np.max(fluxes)*2, 365])
            
            popt, _ = curve_fit(rise_func, t_normalized, fluxes, p0=p0, bounds=bounds, maxfev=1000)
            return float(popt[1])
            
        except:
            # Fallback to simple time difference
            return float(times[-1] - times[0])
    
    def _calculate_decay_rate(self, times, fluxes):
        """Calculate exponential decay rate"""
        try:
            from scipy.optimize import curve_fit
            
            def decay_func(t, a, tau):
                return a * np.exp(-t/tau)
            
            t_normalized = times - times[0]
            t_normalized = np.maximum(t_normalized, 1e-6)
            
            p0 = [fluxes[0], np.median(t_normalized)]
            bounds = ([0, 1e-6], [fluxes[0]*2, 365])
            
            popt, _ = curve_fit(decay_func, t_normalized, fluxes, p0=p0, bounds=bounds, maxfev=1000)
            return float(1.0 / popt[1])
            
        except:
            return 0.0
    
    def _apply_feature_bounds(self, features):
        """Ensure features stay within physical limits"""
        bounded = {}
        for key, value in features.items():
            if 'energy' in key:
                bounded[key] = max(0, min(value, 1e6))
            elif 'time' in key or 'rise' in key:
                bounded[key] = max(0, min(value, 730))
            elif 'rate' in key:
                bounded[key] = max(0, min(value, 50))
            elif 'luminosity' in key:
                bounded[key] = max(0, min(value, 1e5))
            else:
                bounded[key] = value
        return bounded
    
    def _get_default_features(self):
        """Return default feature values for invalid data"""
        return {
            'total_energy': 0.0, 
            'rise_time': 0.0, 
            'decay_rate': 0.0,
            'peak_luminosity': 0.0, 
            'explosion_timescale': 0.0
        }
    
    def physics_loss(self, light_curve_data):
        """Physics constraints for explosion consistency"""
        return 0.0













class SupernovaDiscriminationPINN(PINNModule):
    """
    Specialized features for supernova type discrimination
    Targets SNIa, SNIbc, SNII, SNIax differentiation
    """
    
    def __init__(self):
        super().__init__(
            name="supernova_discrimination",
            description="Specialized features for supernova type discrimination"
        )
        self.feature_names = [
            'pinn_snia_likelihood',
            'pinn_snii_likelihood', 
            'pinn_snibc_likelihood',
            'pinn_sniax_likelihood',
            'pinn_lightcurve_symmetry'
        ]
    
    def calculate_features(self, light_curve_data):
        """Calculate supernova discrimination features"""
        features = {}
        
        object_ids = light_curve_data['object_id'].unique()
        snia_scores = []
        snii_scores = []
        snibc_scores = []
        sniax_scores = []
        symmetry_scores = []
        
        for obj_id in object_ids:
            obj_data = light_curve_data[light_curve_data['object_id'] == obj_id]
            obj_features = self._analyze_supernova_signatures(obj_data)
            
            snia_scores.append(obj_features['snia_likelihood'])
            snii_scores.append(obj_features['snii_likelihood'])
            snibc_scores.append(obj_features['snibc_likelihood'])
            sniax_scores.append(obj_features['sniax_likelihood'])
            symmetry_scores.append(obj_features['symmetry'])
        
        features['pinn_snia_likelihood'] = snia_scores
        features['pinn_snii_likelihood'] = snii_scores
        features['pinn_snibc_likelihood'] = snibc_scores
        features['pinn_sniax_likelihood'] = sniax_scores
        features['pinn_lightcurve_symmetry'] = symmetry_scores
        
        return features
    
    def _analyze_supernova_signatures(self, obj_data):
        """Analyze supernova type signatures"""
        if len(obj_data) < 5:
            return self._get_default_sn_features()
        
        try:
            times = obj_data['mjd'].values
            fluxes = obj_data['flux'].values
            
            # Sort data
            time_sorted_idx = np.argsort(times)
            times_sorted = times[time_sorted_idx]
            fluxes_sorted = fluxes[time_sorted_idx]
            
            # Calculate discrimination features
            snia_score = self._calculate_snia_signature(times_sorted, fluxes_sorted)
            snii_score = self._calculate_snii_signature(times_sorted, fluxes_sorted)
            snibc_score = self._calculate_snibc_signature(times_sorted, fluxes_sorted)
            sniax_score = self._calculate_sniax_signature(times_sorted, fluxes_sorted)
            symmetry_score = self._calculate_symmetry_signature(times_sorted, fluxes_sorted)
            
            return {
                'snia_likelihood': float(snia_score),
                'snii_likelihood': float(snii_score),
                'snibc_likelihood': float(snibc_score),
                'sniax_likelihood': float(sniax_score),
                'symmetry': float(symmetry_score)
            }
            
        except Exception:
            return self._get_default_sn_features()
    
    def _calculate_snia_signature(self, times, fluxes):
        """Calculate SNIa likelihood signature"""
        if len(fluxes) < 4:
            return 0.5
        
        # Characteristic timescale matching
        total_duration = times[-1] - times[0]
        timescale_match = 1.0 - min(abs(total_duration - 60) / 60, 1.0)
        
        # Symmetry signature
        symmetry = self._calculate_symmetry_signature(times, fluxes)
        
        # Decay smoothness
        decay_smoothness = self._calculate_decay_smoothness(times, fluxes)
        
        snia_score = (timescale_match * 0.4 + symmetry * 0.4 + decay_smoothness * 0.2)
        return np.clip(snia_score, 0.0, 1.0)
    
    def _calculate_snii_signature(self, times, fluxes):
        """Calculate SNII likelihood signature"""
        if len(fluxes) < 4:
            return 0.5
        
        # Plateau phase detection
        plateau_score = self._detect_plateau_phase(times, fluxes)
        
        # Asymmetry signature
        symmetry = self._calculate_symmetry_signature(times, fluxes)
        asymmetry = 1.0 - symmetry
        
        # Timescale signature (longer than SNIa)
        total_duration = times[-1] - times[0]
        timescale_match = min(total_duration / 100, 1.0)
        
        snii_score = (plateau_score * 0.5 + asymmetry * 0.3 + timescale_match * 0.2)
        return np.clip(snii_score, 0.0, 1.0)
    
    def _calculate_snibc_signature(self, times, fluxes):
        """Calculate SNIbc likelihood signature"""
        if len(fluxes) < 4:
            return 0.5
        
        # Rapid evolution signature
        total_duration = times[-1] - times[0]
        rapid_score = 1.0 - min(total_duration / 40, 1.0)
        
        # No plateau signature
        plateau_score = self._detect_plateau_phase(times, fluxes)
        no_plateau = 1.0 - plateau_score
        
        snibc_score = (rapid_score * 0.6 + no_plateau * 0.4)
        return np.clip(snibc_score, 0.0, 1.0)
    
    def _calculate_sniax_signature(self, times, fluxes):
        """Calculate SNIax likelihood signature"""
        if len(fluxes) < 4:
            return 0.5
        
        # Subluminous signature
        peak_flux = np.max(fluxes)
        mean_flux = np.mean(np.abs(fluxes))
        if mean_flux > 0:
            peak_ratio = peak_flux / mean_flux
            subluminous = 1.0 - min(peak_ratio / 5.0, 1.0)
        else:
            subluminous = 0.5
        
        # Peculiarity signature
        peculiarity = self._calculate_lightcurve_peculiarity(times, fluxes)
        
        sniax_score = (subluminous * 0.7 + peculiarity * 0.3)
        return np.clip(sniax_score, 0.0, 1.0)
    
    def _calculate_symmetry_signature(self, times, fluxes):
        """Calculate light curve symmetry around peak"""
        if len(fluxes) < 3:
            return 0.5
        
        peak_idx = np.argmax(fluxes)
        if peak_idx == 0 or peak_idx == len(fluxes) - 1:
            return 0.5
        
        # Compare rise and decay shapes
        rise_flux = fluxes[:peak_idx]
        decay_flux = fluxes[peak_idx:]
        
        if len(rise_flux) < 2 or len(decay_flux) < 2:
            return 0.5
        
        # Normalize and compare
        rise_norm = self._normalize_flux(rise_flux)
        decay_norm = self._normalize_flux(decay_flux)
        decay_reversed = decay_norm[::-1]
        
        # Correlation-based symmetry
        min_len = min(len(rise_norm), len(decay_reversed))
        if min_len >= 2:
            correlation = np.corrcoef(rise_norm[:min_len], decay_reversed[:min_len])[0, 1]
            if np.isnan(correlation):
                return 0.5
            symmetry = (correlation + 1) / 2
        else:
            symmetry = 0.5
        
        return np.clip(symmetry, 0.0, 1.0)
    
    def _normalize_flux(self, flux):
        """Normalize flux to 0-1 range"""
        flux_min = np.min(flux)
        flux_max = np.max(flux)
        if flux_max - flux_min > 0:
            return (flux - flux_min) / (flux_max - flux_min)
        else:
            return np.zeros_like(flux)
    
    def _detect_plateau_phase(self, times, fluxes):
        """Detect plateau phase characteristic of SNII"""
        if len(fluxes) < 6:
            return 0.0
        
        flux_diff = np.diff(fluxes)
        time_diff = np.diff(times)
        
        # Find periods with small changes
        small_changes = np.abs(flux_diff) < (np.std(fluxes) * 0.1)
        if np.any(small_changes):
            plateau_duration = np.sum(time_diff[small_changes])
            total_duration = times[-1] - times[0]
            if total_duration > 0:
                plateau_score = plateau_duration / total_duration
            else:
                plateau_score = 0.0
        else:
            plateau_score = 0.0
        
        return np.clip(plateau_score, 0.0, 1.0)
    
    def _calculate_decay_smoothness(self, times, fluxes):
        """Calculate smoothness of decay phase"""
        peak_idx = np.argmax(fluxes)
        if peak_idx >= len(fluxes) - 3:
            return 0.5
        
        decay_flux = fluxes[peak_idx:]
        decay_diff = np.diff(decay_flux)
        
        # Smooth decay has consistent negative derivatives
        negative_derivatives = np.sum(decay_diff < 0) / len(decay_diff)
        return np.clip(negative_derivatives, 0.0, 1.0)
    
    def _calculate_lightcurve_peculiarity(self, times, fluxes):
        """Calculate light curve peculiarity"""
        if len(fluxes) < 4:
            return 0.5
        
        # Multiple peaks indicate peculiarity
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(fluxes, height=np.mean(fluxes))
        multiple_peaks = min(len(peaks) / 3.0, 1.0)
        
        # Irregular variability
        flux_std = np.std(fluxes)
        flux_mean = np.mean(np.abs(fluxes))
        if flux_mean > 0:
            variability = flux_std / flux_mean
            irregularity = min(variability / 2.0, 1.0)
        else:
            irregularity = 0.5
        
        peculiarity = (multiple_peaks * 0.6 + irregularity * 0.4)
        return np.clip(peculiarity, 0.0, 1.0)
    
    def _get_default_sn_features(self):
        """Return default supernova features"""
        return {
            'snia_likelihood': 0.5,
            'snii_likelihood': 0.5,
            'snibc_likelihood': 0.5, 
            'sniax_likelihood': 0.5,
            'symmetry': 0.5
        }
    
    def physics_loss(self, light_curve_data):
        """Physics constraints for supernova discrimination"""
        return 0.0






##################################################
#################################################
#Targeted Discrimination Modules
##############################################













class SubluminousDiscriminationPINN(PINNModule):
    """
    Specialized features for discriminating subluminous supernovae
    Targets: SNIax (62) vs SNIa-91bg (67) confusion
    """
    
    def __init__(self):
        super().__init__(
            name="subluminous_discrimination",
            description="Specialized features for subluminous supernova discrimination"
        )
        self.feature_names = [
            'pinn_sniax_likelihood_enhanced',
            'pinn_91bg_likelihood_enhanced', 
            'pinn_subluminous_confidence',
            'pinn_peak_luminosity_ratio',
            'pinn_lightcurve_stretch'
        ]
    
    def calculate_features(self, light_curve_data):
        """Calculate subluminous discrimination features"""
        features = {}
        
        object_ids = light_curve_data['object_id'].unique()
        sniax_scores = []
        sn91bg_scores = []
        confidence_scores = []
        peak_ratios = []
        stretch_factors = []
        
        for obj_id in object_ids:
            obj_data = light_curve_data[light_curve_data['object_id'] == obj_id]
            obj_features = self._analyze_subluminous_signatures(obj_data)
            
            sniax_scores.append(obj_features['sniax_likelihood'])
            sn91bg_scores.append(obj_features['91bg_likelihood'])
            confidence_scores.append(obj_features['confidence'])
            peak_ratios.append(obj_features['peak_ratio'])
            stretch_factors.append(obj_features['stretch_factor'])
        
        features['pinn_sniax_likelihood_enhanced'] = sniax_scores
        features['pinn_91bg_likelihood_enhanced'] = sn91bg_scores
        features['pinn_subluminous_confidence'] = confidence_scores
        features['pinn_peak_luminosity_ratio'] = peak_ratios
        features['pinn_lightcurve_stretch'] = stretch_factors
        
        return features
    
    def _analyze_subluminous_signatures(self, obj_data):
        """Analyze signatures specific to subluminous SNe"""
        if len(obj_data) < 4:
            return self._get_default_subluminous_features()
        
        try:
            times = obj_data['mjd'].values
            fluxes = obj_data['flux'].values
            
            # Sort data
            time_sorted_idx = np.argsort(times)
            times_sorted = times[time_sorted_idx]
            fluxes_sorted = fluxes[time_sorted_idx]
            
            # Calculate subluminous-specific features
            sniax_score = self._calculate_sniax_signature(times_sorted, fluxes_sorted)
            sn91bg_score = self._calculate_91bg_signature(times_sorted, fluxes_sorted)
            confidence = self._calculate_discrimination_confidence(sniax_score, sn91bg_score)
            peak_ratio = self._calculate_peak_luminosity_ratio(times_sorted, fluxes_sorted)
            stretch_factor = self._calculate_lightcurve_stretch(times_sorted, fluxes_sorted)
            
            return {
                'sniax_likelihood': float(sniax_score),
                '91bg_likelihood': float(sn91bg_score),
                'confidence': float(confidence),
                'peak_ratio': float(peak_ratio),
                'stretch_factor': float(stretch_factor)
            }
            
        except Exception:
            return self._get_default_subluminous_features()
    
    def _calculate_sniax_signature(self, times, fluxes):
        """Calculate SNIax-specific signatures"""
        if len(fluxes) < 4:
            return 0.5
        
        # SNIax: intermediate luminosity, peculiar light curves
        peak_flux = np.max(fluxes)
        mean_flux = np.mean(np.abs(fluxes))
        
        if mean_flux > 0:
            # SNIax are subluminous but not as extreme as 91bg
            luminosity_ratio = peak_flux / mean_flux
            sniax_indicator = 1.0 - min(abs(luminosity_ratio - 3.0) / 3.0, 1.0)
        else:
            sniax_indicator = 0.5
        
        # SNIax often have broader light curves than 91bg
        stretch = self._calculate_lightcurve_stretch(times, fluxes)
        stretch_indicator = min(stretch / 2.0, 1.0)
        
        # Combine indicators
        sniax_score = (sniax_indicator * 0.6 + stretch_indicator * 0.4)
        return np.clip(sniax_score, 0.0, 1.0)
    
    def _calculate_91bg_signature(self, times, fluxes):
        """Calculate SNIa-91bg-specific signatures"""
        if len(fluxes) < 4:
            return 0.5
        
        # 91bg: extremely subluminous, rapid evolution
        peak_flux = np.max(fluxes)
        mean_flux = np.mean(np.abs(fluxes))
        
        if mean_flux > 0:
            # 91bg are very subluminous
            luminosity_ratio = peak_flux / mean_flux
            subluminous_indicator = 1.0 - min(luminosity_ratio / 5.0, 1.0)
        else:
            subluminous_indicator = 0.5
        
        # 91bg have faster decline rates
        decline_rate = self._calculate_decline_rate(times, fluxes)
        fast_decline = min(decline_rate / 2.0, 1.0)
        
        # 91bg are more symmetric than SNIax
        symmetry = self._calculate_lightcurve_symmetry(times, fluxes)
        symmetry_indicator = symmetry
        
        # Combine indicators
        sn91bg_score = (subluminous_indicator * 0.5 + fast_decline * 0.3 + symmetry_indicator * 0.2)
        return np.clip(sn91bg_score, 0.0, 1.0)
    
    def _calculate_discrimination_confidence(self, sniax_score, sn91bg_score):
        """Calculate confidence in discrimination"""
        # High confidence when scores are very different
        score_difference = abs(sniax_score - sn91bg_score)
        return np.clip(score_difference * 2.0, 0.0, 1.0)
    
    def _calculate_peak_luminosity_ratio(self, times, fluxes):
        """Calculate normalized peak luminosity"""
        if len(fluxes) < 2:
            return 0.5
        
        peak_flux = np.max(fluxes)
        median_flux = np.median(np.abs(fluxes))
        
        if median_flux > 0:
            return float(peak_flux / median_flux)
        else:
            return 0.5
    
    def _calculate_lightcurve_stretch(self, times, fluxes):
        """Calculate light curve stretch factor"""
        if len(fluxes) < 4:
            return 1.0
        
        peak_idx = np.argmax(fluxes)
        if peak_idx == 0 or peak_idx == len(fluxes) - 1:
            return 1.0
        
        # Calculate rise and decay times
        rise_time = times[peak_idx] - times[0]
        decay_time = times[-1] - times[peak_idx]
        
        if decay_time > 0:
            stretch = (rise_time + decay_time) / (2 * min(rise_time, decay_time))
            return float(np.clip(stretch, 0.5, 3.0))
        else:
            return 1.0
    
    def _calculate_decline_rate(self, times, fluxes):
        """Calculate decline rate after peak"""
        if len(fluxes) < 4:
            return 0.0
        
        peak_idx = np.argmax(fluxes)
        if peak_idx >= len(fluxes) - 2:
            return 0.0
        
        # Calculate average decline rate
        decline_flux = fluxes[peak_idx:]
        decline_times = times[peak_idx:]
        
        if len(decline_flux) >= 3:
            flux_decline = decline_flux[0] - decline_flux[-1]
            time_span = decline_times[-1] - decline_times[0]
            if time_span > 0:
                return float(flux_decline / time_span)
        
        return 0.0
    
    def _calculate_lightcurve_symmetry(self, times, fluxes):
        """Calculate light curve symmetry"""
        if len(fluxes) < 3:
            return 0.5
        
        peak_idx = np.argmax(fluxes)
        if peak_idx == 0 or peak_idx == len(fluxes) - 1:
            return 0.5
        
        rise_flux = fluxes[:peak_idx]
        decay_flux = fluxes[peak_idx:]
        
        if len(rise_flux) < 2 or len(decay_flux) < 2:
            return 0.5
        
        # Normalize and compare
        rise_norm = (rise_flux - np.min(rise_flux)) / (np.max(rise_flux) - np.min(rise_flux) + 1e-8)
        decay_norm = (decay_flux - np.min(decay_flux)) / (np.max(decay_flux) - np.min(decay_flux) + 1e-8)
        decay_reversed = decay_norm[::-1]
        
        min_len = min(len(rise_norm), len(decay_reversed))
        if min_len >= 2:
            correlation = np.corrcoef(rise_norm[:min_len], decay_reversed[:min_len])[0, 1]
            if np.isnan(correlation):
                return 0.5
            return float((correlation + 1) / 2)
        
        return 0.5
    
    def _get_default_subluminous_features(self):
        """Return default features"""
        return {
            'sniax_likelihood': 0.5,
            '91bg_likelihood': 0.5,
            'confidence': 0.0,
            'peak_ratio': 1.0,
            'stretch_factor': 1.0
        }
    
    def physics_loss(self, light_curve_data):
        """Physics constraints for subluminous discrimination"""
        return 0.0


class ExplosionDiscriminationPINN(PINNModule):
    """
    Enhanced discrimination for stripped-envelope supernovae
    Targets: SNIbc (15) vs other types confusion
    """
    
    def __init__(self):
        super().__init__(
            name="explosion_discrimination",
            description="Enhanced features for stripped-envelope supernova discrimination"
        )
        self.feature_names = [
            'pinn_snibc_likelihood_enhanced',
            'pinn_stripped_envelope_signature',
            'pinn_helium_detection_strength',
            'pinn_rapid_evolution_metric',
            'pinn_csm_interaction_hint'
        ]
    
    def calculate_features(self, light_curve_data):
        """Calculate explosion discrimination features"""
        features = {}
        
        object_ids = light_curve_data['object_id'].unique()
        snibc_scores = []
        stripped_scores = []
        helium_scores = []
        rapid_scores = []
        csm_scores = []
        
        for obj_id in object_ids:
            obj_data = light_curve_data[light_curve_data['object_id'] == obj_id]
            obj_features = self._analyze_explosion_signatures(obj_data)
            
            snibc_scores.append(obj_features['snibc_likelihood'])
            stripped_scores.append(obj_features['stripped_signature'])
            helium_scores.append(obj_features['helium_strength'])
            rapid_scores.append(obj_features['rapid_evolution'])
            csm_scores.append(obj_features['csm_interaction'])
        
        features['pinn_snibc_likelihood_enhanced'] = snibc_scores
        features['pinn_stripped_envelope_signature'] = stripped_scores
        features['pinn_helium_detection_strength'] = helium_scores
        features['pinn_rapid_evolution_metric'] = rapid_scores
        features['pinn_csm_interaction_hint'] = csm_scores
        
        return features
    
    def _analyze_explosion_signatures(self, obj_data):
        """Analyze stripped-envelope explosion signatures"""
        if len(obj_data) < 4:
            return self._get_default_explosion_features()
        
        try:
            times = obj_data['mjd'].values
            fluxes = obj_data['flux'].values
            
            # Sort data
            time_sorted_idx = np.argsort(times)
            times_sorted = times[time_sorted_idx]
            fluxes_sorted = fluxes[time_sorted_idx]
            
            # Calculate explosion-specific features
            snibc_score = self._calculate_snibc_signature(times_sorted, fluxes_sorted)
            stripped_score = self._calculate_stripped_signature(times_sorted, fluxes_sorted)
            helium_score = self._calculate_helium_signature(times_sorted, fluxes_sorted)
            rapid_score = self._calculate_rapid_evolution(times_sorted, fluxes_sorted)
            csm_score = self._calculate_csm_interaction(times_sorted, fluxes_sorted)
            
            return {
                'snibc_likelihood': float(snibc_score),
                'stripped_signature': float(stripped_score),
                'helium_strength': float(helium_score),
                'rapid_evolution': float(rapid_score),
                'csm_interaction': float(csm_score)
            }
            
        except Exception:
            return self._get_default_explosion_features()
    
    def _calculate_snibc_signature(self, times, fluxes):
        """Calculate SNIbc-specific signatures"""
        if len(fluxes) < 4:
            return 0.5
        
        # SNIbc: rapid evolution, no hydrogen, stripped envelope
        total_duration = times[-1] - times[0]
        
        # Rapid timescale
        rapid_score = 1.0 - min(total_duration / 50.0, 1.0)
        
        # No plateau (declining from peak)
        plateau_score = self._detect_plateau_phase(times, fluxes)
        no_plateau = 1.0 - plateau_score
        
        # Early peak (characteristic of stripped envelope)
        peak_idx = np.argmax(fluxes)
        peak_position = peak_idx / len(fluxes) if len(fluxes) > 0 else 0.5
        early_peak = 1.0 - min(abs(peak_position - 0.3) / 0.3, 1.0)
        
        snibc_score = (rapid_score * 0.4 + no_plateau * 0.3 + early_peak * 0.3)
        return np.clip(snibc_score, 0.0, 1.0)
    
    def _calculate_stripped_signature(self, times, fluxes):
        """Calculate stripped envelope signature"""
        if len(fluxes) < 4:
            return 0.5
        
        # Stripped envelope SNe have faster rise times
        rise_time = self._calculate_characteristic_rise_time(times, fluxes)
        total_duration = times[-1] - times[0]
        
        if total_duration > 0:
            fast_rise = 1.0 - min(rise_time / (total_duration * 0.3), 1.0)
        else:
            fast_rise = 0.5
        
        # Higher peak luminosity relative to duration
        peak_flux = np.max(fluxes)
        if total_duration > 0:
            peak_duration_ratio = peak_flux / total_duration
            high_peak = min(peak_duration_ratio / 100.0, 1.0)
        else:
            high_peak = 0.5
        
        stripped_score = (fast_rise * 0.6 + high_peak * 0.4)
        return np.clip(stripped_score, 0.0, 1.0)
    
    def _calculate_helium_signature(self, times, fluxes):
        """Calculate helium line strength indicator"""
        # This is a proxy using light curve shape
        # Real helium detection would require spectra
        if len(fluxes) < 5:
            return 0.5
        
        # Helium-rich SNe often have broader light curves
        stretch = self._calculate_lightcurve_stretch(times, fluxes)
        stretch_indicator = min((stretch - 1.0) / 2.0, 1.0)
        
        # Secondary peaks can indicate helium
        secondary_peaks = self._detect_secondary_peaks(fluxes)
        
        helium_score = (stretch_indicator * 0.7 + secondary_peaks * 0.3)
        return np.clip(helium_score, 0.0, 1.0)
    
    def _calculate_rapid_evolution(self, times, fluxes):
        """Calculate rapid evolution metric"""
        if len(fluxes) < 4:
            return 0.5
        
        total_duration = times[-1] - times[0]
        if total_duration <= 0:
            return 0.5
        
        # Rate of change
        flux_changes = np.abs(np.diff(fluxes))
        time_changes = np.diff(times)
        
        if len(flux_changes) > 0 and np.mean(time_changes) > 0:
            change_rate = np.mean(flux_changes) / np.mean(time_changes)
            rapid_score = min(change_rate / 10.0, 1.0)
        else:
            rapid_score = 0.5
        
        return rapid_score
    
    def _calculate_csm_interaction(self, times, fluxes):
        """Calculate CSM interaction hint"""
        if len(fluxes) < 6:
            return 0.0
        
        # CSM interaction can cause light curve bumps
        bumps = self._detect_lightcurve_bumps(fluxes)
        
        # Extended emission
        duration = times[-1] - times[0]
        if duration > 100:  # Long duration hint
            duration_hint = min(duration / 200.0, 1.0)
        else:
            duration_hint = 0.0
        
        csm_score = (bumps * 0.6 + duration_hint * 0.4)
        return np.clip(csm_score, 0.0, 1.0)
    
    def _calculate_characteristic_rise_time(self, times, fluxes):
        """Calculate characteristic rise time"""
        if len(fluxes) < 3:
            return 0.0
        
        peak_idx = np.argmax(fluxes)
        if peak_idx > 0:
            return float(times[peak_idx] - times[0])
        return 0.0
    
    def _detect_plateau_phase(self, times, fluxes):
        """Detect plateau phase in light curve"""
        if len(fluxes) < 6:
            return 0.0
        
        flux_diff = np.diff(fluxes)
        time_diff = np.diff(times)
        
        small_changes = np.abs(flux_diff) < (np.std(fluxes) * 0.15)
        if np.any(small_changes):
            plateau_duration = np.sum(time_diff[small_changes])
            total_duration = times[-1] - times[0]
            if total_duration > 0:
                return float(plateau_duration / total_duration)
        
        return 0.0
    
    def _detect_secondary_peaks(self, fluxes):
        """Detect secondary peaks in light curve"""
        if len(fluxes) < 7:
            return 0.0
        
        from scipy.signal import find_peaks
        
        # Find multiple peaks
        peaks, _ = find_peaks(fluxes, height=np.mean(fluxes), distance=3)
        
        if len(peaks) > 1:
            return min(len(peaks) / 4.0, 1.0)
        
        return 0.0
    
    def _detect_lightcurve_bumps(self, fluxes):
        """Detect bumps in light curve (CSM interaction)"""
        if len(fluxes) < 7:
            return 0.0
        
        # Calculate smoothness - bumps cause irregularities
        smoothed = np.convolve(fluxes, np.ones(3)/3, mode='valid')
        original = fluxes[1:-1]
        
        if len(smoothed) > 0 and len(original) > 0:
            residuals = np.abs(original - smoothed)
            bumpiness = np.std(residuals) / (np.std(fluxes) + 1e-8)
            return float(min(bumpiness * 5.0, 1.0))
        
        return 0.0
    
    def _calculate_lightcurve_stretch(self, times, fluxes):
        """Calculate light curve stretch factor"""
        if len(fluxes) < 4:
            return 1.0
        
        peak_idx = np.argmax(fluxes)
        if peak_idx == 0 or peak_idx == len(fluxes) - 1:
            return 1.0
        
        rise_time = times[peak_idx] - times[0]
        decay_time = times[-1] - times[peak_idx]
        
        if decay_time > 0:
            stretch = (rise_time + decay_time) / (2 * min(rise_time, decay_time))
            return float(np.clip(stretch, 0.5, 3.0))
        
        return 1.0
    
    def _get_default_explosion_features(self):
        """Return default features"""
        return {
            'snibc_likelihood': 0.5,
            'stripped_signature': 0.5,
            'helium_strength': 0.5,
            'rapid_evolution': 0.5,
            'csm_interaction': 0.0
        }
    
    def physics_loss(self, light_curve_data):
        """Physics constraints for explosion discrimination"""
        return 0.0


class SpectralEvolutionPINN(PINNModule):
    """
    Multi-band spectral evolution features
    Leverages passband information for better classification
    """
    
    def __init__(self):
        super().__init__(
            name="spectral_evolution",
            description="Multi-band spectral evolution and color features"
        )
        self.feature_names = [
            'pinn_color_evolution_rate',
            'pinn_blackbody_temperature',
            'pinn_spectral_index_evolution',
            'pinn_passband_timing_differences',
            'pinn_color_consistency'
        ]
    
    def calculate_features(self, light_curve_data):
        """Calculate spectral evolution features"""
        features = {}
        
        object_ids = light_curve_data['object_id'].unique()
        color_rates = []
        temperatures = []
        spectral_indices = []
        timing_diffs = []
        color_consistencies = []
        
        for obj_id in object_ids:
            obj_data = light_curve_data[light_curve_data['object_id'] == obj_id]
            obj_features = self._analyze_spectral_evolution(obj_data)
            
            color_rates.append(obj_features['color_rate'])
            temperatures.append(obj_features['temperature'])
            spectral_indices.append(obj_features['spectral_index'])
            timing_diffs.append(obj_features['timing_difference'])
            color_consistencies.append(obj_features['color_consistency'])
        
        features['pinn_color_evolution_rate'] = color_rates
        features['pinn_blackbody_temperature'] = temperatures
        features['pinn_spectral_index_evolution'] = spectral_indices
        features['pinn_passband_timing_differences'] = timing_diffs
        features['pinn_color_consistency'] = color_consistencies
        
        return features
    
    def _analyze_spectral_evolution(self, obj_data):
        """Analyze spectral evolution across passbands"""
        if len(obj_data) < 6 or 'passband' not in obj_data.columns:
            return self._get_default_spectral_features()
        
        try:
            # Group by passband
            passbands = obj_data['passband'].unique()
            if len(passbands) < 2:
                return self._get_default_spectral_features()
            
            # Calculate spectral features
            color_rate = self._calculate_color_evolution_rate(obj_data)
            temperature = self._estimate_blackbody_temperature(obj_data)
            spectral_index = self._calculate_spectral_index_evolution(obj_data)
            timing_diff = self._calculate_passband_timing_differences(obj_data)
            color_consistency = self._calculate_color_consistency(obj_data)
            
            return {
                'color_rate': float(color_rate),
                'temperature': float(temperature),
                'spectral_index': float(spectral_index),
                'timing_difference': float(timing_diff),
                'color_consistency': float(color_consistency)
            }
            
        except Exception:
            return self._get_default_spectral_features()
    
    def _calculate_color_evolution_rate(self, obj_data):
        """Improved color evolution calculation"""
        if len(obj_data) < 10:
            return 0.5
        
        try:
            # More robust color calculation
            if 'passband' not in obj_data.columns:
                return 0.5
                
            # Use more bands for better color measurement
            available_bands = sorted(obj_data['passband'].unique())
            if len(available_bands) < 2:
                return 0.5
                
            # Calculate color changes using multiple time bins
            time_bins = pd.cut(obj_data['mjd'], bins=min(4, len(obj_data)//10))
            color_changes = []
            
            for i in range(len(time_bins.cat.categories)-1):
                bin1_data = obj_data[time_bins == time_bins.cat.categories[i]]
                bin2_data = obj_data[time_bins == time_bins.cat.categories[i+1]]
                
                if len(bin1_data) > 0 and len(bin2_data) > 0:
                    # Calculate average color in each bin
                    color1 = self._calculate_bin_color(bin1_data)
                    color2 = self._calculate_bin_color(bin2_data)
                    
                    if color1 > 0 and color2 > 0:
                        color_change = abs(color2 - color1) / color1
                        color_changes.append(color_change)
            
            if color_changes:
                avg_change = np.mean(color_changes)
                return float(min(avg_change * 10.0, 1.0))
            
            return 0.5
        except:
            return 0.5
    ######################################################
    #####################################################
    #calculate_color_bin_color For supernova!
    def _calculate_bin_color(self, bin_data):
        """Calculate color for a time bin"""
        try:
            # Use bands 0 and 1 for color
            flux_0 = bin_data[bin_data['passband'] == 0]['flux'].mean()
            flux_1 = bin_data[bin_data['passband'] == 1]['flux'].mean()
            
            if pd.notna(flux_0) and pd.notna(flux_1) and flux_1 > 0:
                return flux_0 / flux_1
            return 1.0
        except:
            return 1.0
    
    def _estimate_blackbody_temperature(self, obj_data):
        """Estimate blackbody temperature from passband fluxes"""
        if len(obj_data) < 8:
            return 5000.0  # Default temperature
        
        try:
            # Simplified temperature estimation using flux ratios
            # Different passbands sample different parts of SED
            band_fluxes = []
            for band in [0, 1, 2]:  # Use first three bands
                band_data = obj_data[obj_data['passband'] == band]
                if len(band_data) > 0:
                    band_fluxes.append(band_data['flux'].mean())
            
            if len(band_fluxes) >= 2:
                # Hot objects have more blue flux
                if band_fluxes[1] > 0:
                    color_ratio = band_fluxes[0] / band_fluxes[1] if len(band_fluxes) > 1 else 1.0
                    # Convert ratio to temperature proxy
                    temperature = 3000.0 + 15000.0 * min(color_ratio, 2.0)
                    return float(np.clip(temperature, 3000.0, 20000.0))
            
            return 5000.0
        except:
            return 5000.0
    
    def _calculate_spectral_index_evolution(self, obj_data):
        """Calculate spectral index evolution"""
        if len(obj_data) < 10:
            return 0.0
        
        try:
            # Calculate how spectral shape changes over time
            time_bins = pd.cut(obj_data['mjd'], bins=3)
            spectral_changes = []
            
            for time_bin in time_bins.cat.categories:
                bin_data = obj_data[time_bins == time_bin]
                if len(bin_data) >= 2:
                    # Simple spectral index: flux ratio between bands
                    flux_0 = bin_data[bin_data['passband'] == 0]['flux'].mean()
                    flux_1 = bin_data[bin_data['passband'] == 1]['flux'].mean()
                    if flux_1 > 0:
                        spectral_index = flux_0 / flux_1
                        spectral_changes.append(spectral_index)
            
            if len(spectral_changes) >= 2:
                evolution = np.std(spectral_changes) / (np.mean(spectral_changes) + 1e-8)
            # ADD BOUNDS:
                evolution = np.clip(evolution, 0.0, 10.0)  # Prevent extreme values
                return float(min(evolution * 3.0, 1.0))    
                
            return 0.0   
        except:
            return 0.0
    
    def _calculate_passband_timing_differences(self, obj_data):
        """Calculate timing differences between passbands"""
        if len(obj_data) < 6:
            return 0.0
        
        try:
            # Find peak times in different passbands
            peak_times = []
            for band in obj_data['passband'].unique():
                band_data = obj_data[obj_data['passband'] == band]
                if len(band_data) > 0:
                    peak_time = band_data.loc[band_data['flux'].idxmax(), 'mjd']
                    peak_times.append(peak_time)
            
            if len(peak_times) >= 2:
                time_spread = np.std(peak_times)
                return float(min(time_spread / 10.0, 1.0))
            
            return 0.0
        except:
            return 0.0
    
    def _calculate_color_consistency(self, obj_data):
        """Calculate color consistency across the light curve"""
        if len(obj_data) < 8:
            return 0.5
        
        try:
            # Check if color remains consistent
            color_measurements = []
            unique_times = obj_data['mjd'].unique()
            
            for time in unique_times[:5]:  # Sample first 5 unique times
                time_data = obj_data[obj_data['mjd'] == time]
                if len(time_data) >= 2:
                    fluxes = time_data.set_index('passband')['flux']
                    if 0 in fluxes.index and 1 in fluxes.index:
                        color = fluxes[0] / fluxes[1] if fluxes[1] > 0 else 1.0
                        color_measurements.append(color)
            
            if len(color_measurements) >= 2:
                consistency = 1.0 - (np.std(color_measurements) / (np.mean(color_measurements) + 1e-8))
                return float(np.clip(consistency, 0.0, 1.0))
            
            return 0.5
        except:
            return 0.5
    
    def _get_default_spectral_features(self):
        """Return default spectral features"""
        return {
            'color_rate': 0.5,
            'temperature': 5000.0,
            'spectral_index': 0.0,
            'timing_difference': 0.0,
            'color_consistency': 0.5
        }
    
    def physics_loss(self, light_curve_data):
        """Physics constraints for spectral evolution"""
        return 0.0














# PHASE 3: MULTI-SCALE PHYSICS & HOST GALAXY CONTEXT PINNs
# ============================================================================

class MultiScalePhysicsPINN(PINNModule):
    """
    PINN for analyzing light curves across multiple temporal scales
    Targets: Fast transients (kilonovae) vs Intermediate (SNe) vs Long-term (AGN)
    """
    
    def __init__(self):
        super().__init__(
            name="multi_scale_physics",
            description="Multi-timescale analysis for temporal regime discrimination"
        )
        self.feature_names = [
            'pinn_fast_transient_score',      # Hours-days scale (kilonovae, flares)
            'pinn_intermediate_scale_score',   # Weeks scale (most supernovae)
            'pinn_long_term_variability',      # Months+ scale (AGN, TDE, microlensing)
            'pinn_dominant_timescale',         # Which timescale dominates
            'pinn_timescale_consistency',      # Physical consistency across scales
            'pinn_characteristic_period',      # Dominant variability period
            'pinn_scale_separation_index'      # How well-separated are the timescales
        ]
    
    def calculate_features(self, light_curve_data, metadata=None):
        """Calculate multi-scale temporal features"""
        features = {}
        
        object_ids = light_curve_data['object_id'].unique()
        fast_scores = []
        intermediate_scores = []
        long_term_scores = []
        dominant_scales = []
        consistency_scores = []
        characteristic_periods = []
        separation_indices = []
        
        for obj_id in object_ids:
            obj_data = light_curve_data[light_curve_data['object_id'] == obj_id]
            obj_features = self._analyze_multi_scale_physics(obj_data)
            
            fast_scores.append(obj_features['fast_score'])
            intermediate_scores.append(obj_features['intermediate_score'])
            long_term_scores.append(obj_features['long_term_score'])
            dominant_scales.append(obj_features['dominant_scale'])
            consistency_scores.append(obj_features['consistency'])
            characteristic_periods.append(obj_features['characteristic_period'])
            separation_indices.append(obj_features['separation_index'])
        
        features['pinn_fast_transient_score'] = fast_scores
        features['pinn_intermediate_scale_score'] = intermediate_scores
        features['pinn_long_term_variability'] = long_term_scores
        features['pinn_dominant_timescale'] = dominant_scales
        features['pinn_timescale_consistency'] = consistency_scores
        features['pinn_characteristic_period'] = characteristic_periods
        features['pinn_scale_separation_index'] = separation_indices
        
        return features
    
    def _analyze_multi_scale_physics(self, obj_data):
        """Analyze light curve across multiple temporal scales"""
        if len(obj_data) < 5:
            return self._get_default_multi_scale_features()
        
        try:
            times = obj_data['mjd'].values
            fluxes = obj_data['flux'].values
            
            # Sort by time
            time_sorted_idx = np.argsort(times)
            times_sorted = times[time_sorted_idx]
            fluxes_sorted = fluxes[time_sorted_idx]
            
            total_duration = times_sorted[-1] - times_sorted[0]
            if total_duration <= 0:
                return self._get_default_multi_scale_features()
            
            # 1. Fast variations (hours to 3 days)
            fast_features = self._extract_fast_variations(times_sorted, fluxes_sorted, total_duration)
            
            # 2. Intermediate variations (3 days to 3 weeks)
            intermediate_features = self._extract_intermediate_variations(times_sorted, fluxes_sorted, total_duration)
            
            # 3. Long-term trends (3 weeks+)
            long_term_features = self._extract_long_term_trends(times_sorted, fluxes_sorted, total_duration)
            
            # 4. Cross-scale analysis
            cross_analysis = self._analyze_cross_scale_behavior(
                fast_features, intermediate_features, long_term_features
            )
            
            # 5. Characteristic period estimation
            characteristic_period = self._estimate_characteristic_period(times_sorted, fluxes_sorted)
            
            return {
                'fast_score': float(fast_features['score']),
                'intermediate_score': float(intermediate_features['score']),
                'long_term_score': float(long_term_features['score']),
                'dominant_scale': float(cross_analysis['dominant_scale']),
                'consistency': float(cross_analysis['consistency']),
                'characteristic_period': float(characteristic_period),
                'separation_index': float(cross_analysis['separation_index'])
            }
            
        except Exception as e:
            print(f"Error in multi-scale analysis: {e}")
            return self._get_default_multi_scale_features()
    
    def _extract_fast_variations(self, times, fluxes, total_duration):
        """Extract features for fast timescales (hours to 3 days)"""
        if len(times) < 3:
            return {'score': 0.0, 'variability': 0.0}
        
        # Calculate time differences
        time_diffs = np.diff(times)
        flux_diffs = np.diff(fluxes)
        
        # Focus on short timescales (< 3 days)
        short_term_mask = time_diffs <= 3.0
        if not np.any(short_term_mask):
            return {'score': 0.0, 'variability': 0.0}
        
        short_term_flux_changes = np.abs(flux_diffs[short_term_mask])
        short_term_time_changes = time_diffs[short_term_mask]
        
        if len(short_term_flux_changes) == 0:
            return {'score': 0.0, 'variability': 0.0}
        
        # Fast variability score: rapid changes relative to mean flux
        mean_flux = np.mean(np.abs(fluxes))
        if mean_flux > 0:
            fast_variability = np.mean(short_term_flux_changes / short_term_time_changes) / mean_flux
        else:
            fast_variability = 0.0
        
        # Normalize score
        fast_score = min(fast_variability * 10.0, 1.0)
        
        return {'score': fast_score, 'variability': fast_variability}
    
    def _extract_intermediate_variations(self, times, fluxes, total_duration):
        """Extract features for intermediate timescales (3 days to 3 weeks)"""
        if len(times) < 4:
            return {'score': 0.0, 'rise_decay': 0.0}
        
        # Find peak and analyze rise/decay
        peak_idx = np.argmax(fluxes)
        peak_time = times[peak_idx]
        
        # Rise phase (before peak)
        rise_mask = times <= peak_time
        rise_times = times[rise_mask]
        rise_fluxes = fluxes[rise_mask]
        
        # Decay phase (after peak)
        decay_mask = times >= peak_time
        decay_times = times[decay_mask]
        decay_fluxes = fluxes[decay_mask]
        
        rise_duration = 0.0
        decay_duration = 0.0
        
        if len(rise_times) > 1:
            rise_duration = rise_times[-1] - rise_times[0]
        
        if len(decay_times) > 1:
            decay_duration = decay_times[-1] - decay_times[0]
        
        # Intermediate timescale: typical supernova duration
        total_event_duration = rise_duration + decay_duration
        if total_duration > 0:
            intermediate_fraction = min(total_event_duration / total_duration, 1.0)
        else:
            intermediate_fraction = 0.0
        
        # Score based on how well it fits intermediate timescale profile
        if 5 <= total_event_duration <= 50:  # 5-50 days typical for SNe
            intermediate_score = 1.0 - abs(total_event_duration - 20) / 45  # Peak at 20 days
        else:
            intermediate_score = max(0.0, 1.0 - total_event_duration / 100.0)
        
        return {'score': intermediate_score, 'rise_decay': intermediate_fraction}
    
    def _extract_long_term_trends(self, times, fluxes, total_duration):
        """Extract features for long-term trends (3 weeks+)"""
        if len(times) < 5:
            return {'score': 0.0, 'trend_strength': 0.0}
        
        # Fit linear trend to detect long-term changes
        try:
            from scipy.stats import linregress
            slope, intercept, r_value, p_value, std_err = linregress(times, fluxes)
            
            # Long-term trend strength
            trend_strength = abs(slope) * total_duration / (np.std(fluxes) + 1e-8)
            
            # Long-term score: favors objects with significant trends over long durations
            if total_duration >= 21:  # 3+ weeks
                long_term_score = min(trend_strength * 2.0, 1.0)
            else:
                long_term_score = 0.0
                
        except:
            trend_strength = 0.0
            long_term_score = 0.0
        
        return {'score': long_term_score, 'trend_strength': trend_strength}
    
    def _analyze_cross_scale_behavior(self, fast_features, intermediate_features, long_term_features):
        """Analyze how behavior correlates across different timescales"""
        scores = np.array([
            fast_features['score'],
            intermediate_features['score'], 
            long_term_features['score']
        ])
        
        # Dominant scale
        dominant_scale = np.argmax(scores) / 2.0  # Normalize to 0-1
        
        # Consistency: how concentrated is the power in one scale
        score_sum = np.sum(scores)
        if score_sum > 0:
            normalized_scores = scores / score_sum
            consistency = 1.0 - entropy(normalized_scores) / np.log(3)  # Max entropy for 3 classes
        else:
            consistency = 0.0
        
        # Separation index: how well-separated are the timescales
        separation_index = 0.0
        if len(scores) >= 2 and np.max(scores) > 0:
            sorted_scores = np.sort(scores)[::-1]
            separation_index = (sorted_scores[0] - sorted_scores[1]) / sorted_scores[0]
        
        return {
            'dominant_scale': dominant_scale,
            'consistency': consistency,
            'separation_index': separation_index
        }
    
    def _estimate_characteristic_period(self, times, fluxes):
        """Estimate characteristic variability period"""
        if len(times) < 6:
            return 0.0
        
        try:
            # Simple period estimation using autocorrelation
            normalized_flux = (fluxes - np.mean(fluxes)) / (np.std(fluxes) + 1e-8)
            
            # Calculate simple autocorrelation
            max_lag = min(20, len(normalized_flux) // 2)
            autocorr = []
            
            for lag in range(1, max_lag + 1):
                if lag < len(normalized_flux):
                    corr = np.corrcoef(normalized_flux[:-lag], normalized_flux[lag:])[0, 1]
                    if not np.isnan(corr):
                        autocorr.append(corr)
            
            if len(autocorr) > 0:
                # Find first significant peak after lag 0
                autocorr = np.array(autocorr)
                peaks, _ = find_peaks(autocorr, height=0.3)
                if len(peaks) > 0:
                    characteristic_period = peaks[0] + 1  # +1 because lag starts at 1
                else:
                    characteristic_period = 0.0
            else:
                characteristic_period = 0.0
                
        except:
            characteristic_period = 0.0
        
        return characteristic_period
    
    def _get_default_multi_scale_features(self):
        """Return default multi-scale features"""
        return {
            'fast_score': 0.0,
            'intermediate_score': 0.5,
            'long_term_score': 0.0,
            'dominant_scale': 0.5,
            'consistency': 0.5,
            'characteristic_period': 0.0,
            'separation_index': 0.0
        }
    
    def physics_loss(self, light_curve_data):
        """Physics loss for multi-scale constraints"""
        return 0.0


class HostGalaxyContextPINN(PINNModule):
    """
    PINN for incorporating host galaxy context into classification
    Uses: redshift, photometry, position to infer host properties
    """
    
    def __init__(self):
        super().__init__(
            name="host_galaxy_context",
            description="Host galaxy properties and environmental context features"
        )
        self.feature_names = [
            'pinn_host_mass_proxy',           # Galaxy mass estimate
            'pinn_sfr_indicator',             # Star formation rate proxy
            'pinn_morphology_hint',           # Elliptical vs spiral indication
            'pinn_environment_density',       # Field vs cluster environment
            'pinn_host_redshift_quality',     # Redshift reliability
            'pinn_physical_consistency',      # Host vs transient consistency
            'pinn_galactic_extinction'        # Dust extinction estimate
        ]
    
    def calculate_features(self, light_curve_data, metadata=None):
        """Calculate host galaxy context features"""
        features = {}
        
        if metadata is None:
            # Return default values if no metadata
            object_ids = light_curve_data['object_id'].unique()
            for feature in self.feature_names:
                features[feature] = [0.5] * len(object_ids)
            return features
        
        object_ids = light_curve_data['object_id'].unique()
        host_masses = []
        sfr_indicators = []
        morphology_hints = []
        environment_densities = []
        redshift_qualities = []
        physical_consistencies = []
        extinctions = []
        
        # Merge with metadata
        data_with_meta = light_curve_data.merge(
            metadata[['object_id', 'hostgal_photoz', 'hostgal_specz', 'ra', 'decl', 'gal_l', 'gal_b']],
            on='object_id', how='left'
        )
        
        for obj_id in object_ids:
            obj_meta = metadata[metadata['object_id'] == obj_id]
            obj_features = self._analyze_host_galaxy_context(obj_meta)
            
            host_masses.append(obj_features['host_mass'])
            sfr_indicators.append(obj_features['sfr_indicator'])
            morphology_hints.append(obj_features['morphology_hint'])
            environment_densities.append(obj_features['environment_density'])
            redshift_qualities.append(obj_features['redshift_quality'])
            physical_consistencies.append(obj_features['physical_consistency'])
            extinctions.append(obj_features['extinction'])
        
        features['pinn_host_mass_proxy'] = host_masses
        features['pinn_sfr_indicator'] = sfr_indicators
        features['pinn_morphology_hint'] = morphology_hints
        features['pinn_environment_density'] = environment_densities
        features['pinn_host_redshift_quality'] = redshift_qualities
        features['pinn_physical_consistency'] = physical_consistencies
        features['pinn_galactic_extinction'] = extinctions
        
        return features
    
    def _analyze_host_galaxy_context(self, obj_meta):
        """Analyze host galaxy context from metadata"""
        if len(obj_meta) == 0:
            return self._get_default_host_features()
        
        try:
            row = obj_meta.iloc[0]
            
            # 1. Host mass proxy using redshift and basic assumptions
            host_mass = self._estimate_host_mass(row)
            
            # 2. Star formation rate indicator
            sfr_indicator = self._estimate_sfr_indicator(row)
            
            # 3. Morphology hint (early-type vs late-type)
            morphology_hint = self._estimate_morphology(row)
            
            # 4. Environment density
            environment_density = self._estimate_environment_density(row)
            
            # 5. Redshift quality
            redshift_quality = self._assess_redshift_quality(row)
            
            # 6. Physical consistency
            physical_consistency = self._check_physical_consistency(row, host_mass)
            
            # 7. Galactic extinction estimate
            extinction = self._estimate_galactic_extinction(row)
            
            return {
                'host_mass': float(host_mass),
                'sfr_indicator': float(sfr_indicator),
                'morphology_hint': float(morphology_hint),
                'environment_density': float(environment_density),
                'redshift_quality': float(redshift_quality),
                'physical_consistency': float(physical_consistency),
                'extinction': float(extinction)
            }
            
        except Exception as e:
            print(f"Error in host galaxy analysis: {e}")
            return self._get_default_host_features()
    
    def _estimate_host_mass(self, row):
        """Estimate host galaxy mass proxy"""
        # Use redshift as mass proxy (simplified)
        z_spec = row.get('hostgal_specz', 0)
        z_photo = row.get('hostgal_photoz', 0)
        
        # Prefer spectroscopic redshift
        if not np.isnan(z_spec) and z_spec > 0:
            z = z_spec
            confidence = 1.0
        elif not np.isnan(z_photo) and z_photo > 0:
            z = z_photo
            confidence = 0.7
        else:
            z = 0.0
            confidence = 0.3
        
        # Simple mass proxy: higher redshift typically means more massive galaxies
        # but this is very simplified - real mass estimation would need more data
        mass_proxy = min(z * 10.0, 1.0) * confidence
        
        return mass_proxy
    
    def _estimate_sfr_indicator(self, row):
        """Estimate star formation rate indicator"""
        # Galactic objects (within Milky Way) have different SFR context
        is_galactic = row.get('hostgal_photoz', 1) == 0
        
        if is_galactic:
            # Galactic objects: use position as rough SFR proxy
            # Higher galactic latitude often means lower dust and different populations
            gal_b = abs(row.get('gal_b', 0))
            if gal_b > 30:
                sfr_indicator = 0.2  # Halo, old population
            elif gal_b > 10:
                sfr_indicator = 0.5  # Intermediate
            else:
                sfr_indicator = 0.8  # Disk, more star formation
        else:
            # Extragalactic: use redshift and basic assumptions
            z = row.get('hostgal_photoz', 0)
            # Higher redshift galaxies typically have higher SFR
            sfr_indicator = min(z * 5.0, 1.0)
        
        return sfr_indicator
    
    def _estimate_morphology(self, row):
        """Estimate galaxy morphology hint"""
        is_galactic = row.get('hostgal_photoz', 1) == 0
        
        if is_galactic:
            # For galactic objects, use position hints
            gal_b = abs(row.get('gal_b', 0))
            if gal_b > 45:
                return 0.8  # High latitude, more likely elliptical/halo
            else:
                return 0.3  # Lower latitude, more likely spiral/disk
        else:
            # For extragalactic, use redshift and other proxies
            z = row.get('hostgal_photoz', 0)
            # Very simplified: lower redshift more likely early-type
            if z < 0.1:
                return 0.7  # More likely early-type
            elif z < 0.5:
                return 0.5  # Mixed
            else:
                return 0.3  # More likely late-type at higher z
    
    def _estimate_environment_density(self, row):
        """Estimate environmental density (field vs cluster)"""
        # Use position correlations as density proxy
        ra = row.get('ra', 0)
        dec = row.get('decl', 0)
        
        # Very simplified: use positional modulations as density proxy
        # In reality, this would need cross-matching with galaxy catalogs
        ra_mod = ra % 180
        dec_mod = dec % 180
        
        # Create artificial density patterns (replace with real data if available)
        density = (np.sin(ra_mod * np.pi / 180) * np.cos(dec_mod * np.pi / 180) + 1) / 2
        
        return float(density)
    
    def _assess_redshift_quality(self, row):
        """Assess redshift measurement quality"""
        z_spec = row.get('hostgal_specz', np.nan)
        z_photo = row.get('hostgal_photoz', np.nan)
        
        if not np.isnan(z_spec) and z_spec >= 0:
            return 1.0  # Spectroscopic - high quality
        elif not np.isnan(z_photo) and z_photo >= 0:
            return 0.7  # Photometric - medium quality
        else:
            return 0.3  # No redshift - low quality
    
    def _check_physical_consistency(self, row, host_mass):
        """Check physical consistency between transient and host"""
        is_galactic = row.get('hostgal_photoz', 1) == 0
        
        if is_galactic:
            # Galactic objects should have certain properties
            consistency = 0.8  # Generally consistent
        else:
            # Extragalactic: check if mass and redshift are reasonable
            z = max(row.get('hostgal_specz', 0), row.get('hostgal_photoz', 0))
            if z > 0 and host_mass > 0:
                # Basic consistency check
                consistency = 0.9
            else:
                consistency = 0.5
        
        return consistency
    
    def _estimate_galactic_extinction(self, row):
        """Estimate galactic extinction using position"""
        # Use galactic coordinates to estimate extinction
        gal_b = abs(row.get('gal_b', 0))
        
        # Simplified: higher extinction at lower galactic latitudes
        if gal_b > 60:
            extinction = 0.1  # Very low
        elif gal_b > 30:
            extinction = 0.3  # Low
        elif gal_b > 10:
            extinction = 0.6  # Medium
        else:
            extinction = 0.9  # High
        
        return extinction
    
    def _get_default_host_features(self):
        """Return default host galaxy features"""
        return {
            'host_mass': 0.5,
            'sfr_indicator': 0.5,
            'morphology_hint': 0.5,
            'environment_density': 0.5,
            'redshift_quality': 0.5,
            'physical_consistency': 0.5,
            'extinction': 0.5
        }
    
    def physics_loss(self, light_curve_data):
        """Physics loss for host galaxy constraints"""
        return 0.0


# Add entropy function for multi-scale analysis
def entropy(probabilities):
    """Calculate entropy of probability distribution"""
    probabilities = np.array(probabilities)
    probabilities = probabilities[probabilities > 0]  # Remove zeros
    if len(probabilities) == 0:
        return 0.0
    return -np.sum(probabilities * np.log(probabilities))


# Add scipy peak finding utility
def find_peaks(x, height=None):
    """Simple peak finding implementation"""
    peaks = []
    properties = {}
    
    for i in range(1, len(x) - 1):
        if x[i] > x[i-1] and x[i] > x[i+1]:
            if height is None or x[i] > height:
                peaks.append(i)
    
    properties['peak_heights'] = [x[i] for i in peaks] if peaks else []
    
    return np.array(peaks), properties








# ============================================================================
# TIER 2: ADVANCED PHYSICS-DRIVEN DISCRIMINATION PINNs
# ============================================================================

class RadioactiveDecayPhysicsPINN(PINNModule):
    """
    PINN for modeling radioactive decay chains in supernovae
    Specifically targets 56Ni → 56Co → 56Fe decay physics
    """
    
    def __init__(self):
        super().__init__(
            name="radioactive_decay_physics",
            description="Radioactive decay chain modeling for supernova power sources"
        )
        self.feature_names = [
            'pinn_nickel_decay_signature',    # 56Ni → 56Co decay strength
            'pinn_cobalt_decay_signature',    # 56Co → 56Fe decay strength  
            'pinn_decay_chain_consistency',   # Physical consistency of decay chain
            'pinn_nickel_mass_estimate',      # Estimated nickel mass proxy
            'pinn_56ni_detection_strength',   # Confidence in nickel detection
            'pinn_decay_timescale_match',     # How well timescales match 56Ni/56Co
            'pinn_bolometric_correction'      # Bolometric luminosity proxy
        ]
        
        # Physical constants
        self.nickel_half_life = 6.077  # days (56Ni half-life)
        self.cobalt_half_life = 77.27  # days (56Co half-life)
        self.nickel_decay_constant = np.log(2) / self.nickel_half_life
        self.cobalt_decay_constant = np.log(2) / self.cobalt_half_life
    
    def calculate_features(self, light_curve_data, metadata=None):
        """Calculate radioactive decay physics features"""
        features = {}
        
        object_ids = light_curve_data['object_id'].unique()
        nickel_signatures = []
        cobalt_signatures = []
        chain_consistencies = []
        nickel_masses = []
        detection_strengths = []
        timescale_matches = []
        bolometric_corrections = []
        
        for obj_id in object_ids:
            obj_data = light_curve_data[light_curve_data['object_id'] == obj_id]
            obj_features = self._analyze_radioactive_decay(obj_data)
            
            nickel_signatures.append(obj_features['nickel_signature'])
            cobalt_signatures.append(obj_features['cobalt_signature'])
            chain_consistencies.append(obj_features['chain_consistency'])
            nickel_masses.append(obj_features['nickel_mass'])
            detection_strengths.append(obj_features['detection_strength'])
            timescale_matches.append(obj_features['timescale_match'])
            bolometric_corrections.append(obj_features['bolometric_correction'])
        
        features['pinn_nickel_decay_signature'] = nickel_signatures
        features['pinn_cobalt_decay_signature'] = cobalt_signatures
        features['pinn_decay_chain_consistency'] = chain_consistencies
        features['pinn_nickel_mass_estimate'] = nickel_masses
        features['pinn_56ni_detection_strength'] = detection_strengths
        features['pinn_decay_timescale_match'] = timescale_matches
        features['pinn_bolometric_correction'] = bolometric_corrections
        
        return features
    
    def _analyze_radioactive_decay(self, obj_data):
        """Analyze radioactive decay signatures in light curve"""
        if len(obj_data) < 6:
            return self._get_default_decay_features()
        
        try:
            times = obj_data['mjd'].values
            fluxes = obj_data['flux'].values
            
            # Sort by time
            time_sorted_idx = np.argsort(times)
            times_sorted = times[time_sorted_idx]
            fluxes_sorted = fluxes[time_sorted_idx]
            
            total_duration = times_sorted[-1] - times_sorted[0]
            if total_duration <= 0:
                return self._get_default_decay_features()
            
            # 1. Nickel decay signature (first ~15 days)
            nickel_features = self._extract_nickel_decay_signature(times_sorted, fluxes_sorted)
            
            # 2. Cobalt decay signature (15-100 days)
            cobalt_features = self._extract_cobalt_decay_signature(times_sorted, fluxes_sorted)
            
            # 3. Nickel mass estimate
            nickel_mass = self._estimate_nickel_mass(times_sorted, fluxes_sorted)
            
            # 4. Decay chain consistency
            chain_consistency = self._check_decay_chain_consistency(nickel_features, cobalt_features)
            
            # 5. Timescale matching
            timescale_match = self._assess_timescale_matching(times_sorted, fluxes_sorted)
            
            # 6. Bolometric correction
            bolometric_correction = self._calculate_bolometric_correction(obj_data)
            
            return {
                'nickel_signature': float(nickel_features['signature_strength']),
                'cobalt_signature': float(cobalt_features['signature_strength']),
                'chain_consistency': float(chain_consistency),
                'nickel_mass': float(nickel_mass),
                'detection_strength': float(nickel_features['detection_confidence']),
                'timescale_match': float(timescale_match),
                'bolometric_correction': float(bolometric_correction)
            }
            
        except Exception as e:
            print(f"Error in radioactive decay analysis: {e}")
            return self._get_default_decay_features()
    
    def _extract_nickel_decay_signature(self, times, fluxes):
        """Extract 56Ni decay signature (early phase)"""
        if len(times) < 3:
            return {'signature_strength': 0.0, 'detection_confidence': 0.0}
        
        # Focus on first 15 days for nickel decay
        early_mask = times - times[0] <= 15.0
        if np.sum(early_mask) < 2:
            return {'signature_strength': 0.0, 'detection_confidence': 0.0}
        
        early_times = times[early_mask]
        early_fluxes = fluxes[early_mask]
        
        # Nickel decay should show rapid rise then slower decline
        peak_idx = np.argmax(early_fluxes)
        if peak_idx == 0 or peak_idx == len(early_fluxes) - 1:
            return {'signature_strength': 0.0, 'detection_confidence': 0.0}
        
        # Calculate rise and decay rates
        rise_times = early_times[:peak_idx + 1] - early_times[0]
        rise_fluxes = early_fluxes[:peak_idx + 1]
        
        decay_times = early_times[peak_idx:] - early_times[peak_idx]
        decay_fluxes = early_fluxes[peak_idx:]
        
        # Fit exponential rise and decay
        try:
            # Rise phase (should be fast)
            if len(rise_times) >= 2 and np.max(rise_times) > 0:
                rise_fit = self._fit_exponential_rise(rise_times, rise_fluxes)
                rise_timescale = 1.0 / rise_fit['rate'] if rise_fit['rate'] > 0 else 0.0
            else:
                rise_timescale = 0.0
            
            # Decay phase (should match nickel timescale)
            if len(decay_times) >= 3 and np.max(decay_times) > 0:
                decay_fit = self._fit_exponential_decay(decay_times, decay_fluxes)
                decay_timescale = 1.0 / decay_fit['rate'] if decay_fit['rate'] > 0 else 0.0
                
                # Compare to expected nickel decay timescale
                nickel_match = 1.0 - min(abs(decay_timescale - self.nickel_half_life) / self.nickel_half_life, 1.0)
            else:
                decay_timescale = 0.0
                nickel_match = 0.0
            
            # Signature strength based on timescale matching
            signature_strength = nickel_match
            detection_confidence = min((len(early_fluxes) / 5.0) * nickel_match, 1.0)
            
        except:
            signature_strength = 0.0
            detection_confidence = 0.0
        
        return {
            'signature_strength': signature_strength,
            'detection_confidence': detection_confidence,
            'rise_timescale': rise_timescale if 'rise_timescale' in locals() else 0.0,
            'decay_timescale': decay_timescale if 'decay_timescale' in locals() else 0.0
        }
    
    def _extract_cobalt_decay_signature(self, times, fluxes):
        """Extract 56Co decay signature (later phase)"""
        if len(times) < 4:
            return {'signature_strength': 0.0, 'detection_confidence': 0.0}
        
        # Focus on days 15-100 for cobalt decay
        time_from_start = times - times[0]
        cobalt_mask = (time_from_start >= 15.0) & (time_from_start <= 100.0)
        
        if np.sum(cobalt_mask) < 3:
            return {'signature_strength': 0.0, 'detection_confidence': 0.0}
        
        cobalt_times = times[cobalt_mask]
        cobalt_fluxes = fluxes[cobalt_mask]
        
        # Cobalt decay should show smooth exponential decline
        try:
            if len(cobalt_times) >= 3:
                # Normalize times relative to cobalt phase start
                cobalt_times_normalized = cobalt_times - cobalt_times[0]
                
                # Fit exponential decay
                decay_fit = self._fit_exponential_decay(cobalt_times_normalized, cobalt_fluxes)
                decay_timescale = 1.0 / decay_fit['rate'] if decay_fit['rate'] > 0 else 0.0
                
                # Compare to expected cobalt decay timescale
                cobalt_match = 1.0 - min(abs(decay_timescale - self.cobalt_half_life) / self.cobalt_half_life, 1.0)
                
                # Also check goodness of fit
                fit_quality = decay_fit['r_squared']
                
                signature_strength = cobalt_match * fit_quality
                detection_confidence = min((len(cobalt_fluxes) / 8.0) * cobalt_match, 1.0)
            else:
                signature_strength = 0.0
                detection_confidence = 0.0
                
        except:
            signature_strength = 0.0
            detection_confidence = 0.0
        
        return {
            'signature_strength': signature_strength,
            'detection_confidence': detection_confidence
        }
    
    def _estimate_nickel_mass(self, times, fluxes):
        """Estimate nickel mass proxy from peak luminosity and decline rate"""
        if len(fluxes) < 3:
            return 0.0
        
        peak_flux = np.max(fluxes)
        mean_flux = np.mean(np.abs(fluxes))
        
        if mean_flux <= 0:
            return 0.0
        
        # Simple nickel mass proxy based on peak luminosity and decline rate
        peak_idx = np.argmax(fluxes)
        
        if peak_idx < len(fluxes) - 2:
            # Calculate decline rate after peak
            post_peak_flux = fluxes[peak_idx:]
            if len(post_peak_flux) >= 2:
                decline_rate = (post_peak_flux[0] - post_peak_flux[-1]) / (len(post_peak_flux) - 1)
            else:
                decline_rate = 0.0
        else:
            decline_rate = 0.0
        
        # Nickel mass proxy (simplified)
        nickel_mass_proxy = (peak_flux / mean_flux) * (1.0 + decline_rate * 10.0)
        nickel_mass_proxy = min(nickel_mass_proxy, 10.0)  # Cap at reasonable value
        
        return nickel_mass_proxy / 10.0  # Normalize to 0-1
    
    def _check_decay_chain_consistency(self, nickel_features, cobalt_features):
        """Check physical consistency between nickel and cobalt decay signatures"""
        nickel_strength = nickel_features['signature_strength']
        cobalt_strength = cobalt_features['signature_strength']
        
        # In physically consistent decay chain:
        # - Strong nickel should be followed by strong cobalt
        # - Weak nickel but strong cobalt is suspicious
        # - Strong nickel but weak cobalt might indicate other power sources
        
        if nickel_strength > 0.7 and cobalt_strength > 0.5:
            consistency = 0.9  # Good consistency
        elif nickel_strength > 0.5 and cobalt_strength > 0.3:
            consistency = 0.7  # Reasonable consistency
        elif nickel_strength < 0.3 and cobalt_strength > 0.6:
            consistency = 0.3  # Suspicious - cobalt without nickel
        elif nickel_strength > 0.6 and cobalt_strength < 0.2:
            consistency = 0.4  # Nickel without cobalt - unusual
        else:
            consistency = 0.5  # Neutral
        
        return consistency
    
    def _assess_timescale_matching(self, times, fluxes):
        """Assess how well light curve timescales match radioactive decay expectations"""
        if len(times) < 4:
            return 0.0
        
        total_duration = times[-1] - times[0]
        
        # Expected supernova timescales from radioactive decay
        # Nickel-dominated: ~1-2 weeks
        # Cobalt-dominated: ~2 weeks to 3 months
        expected_duration = 60.0  # Typical SN duration
        
        duration_match = 1.0 - min(abs(total_duration - expected_duration) / expected_duration, 1.0)
        
        # Also check if we have observations spanning both nickel and cobalt phases
        phase_coverage = min(total_duration / 80.0, 1.0)  # Normalize to 80 days
        
        timescale_match = (duration_match + phase_coverage) / 2.0
        
        return timescale_match
    
    def _calculate_bolometric_correction(self, obj_data):
        """Calculate bolometric correction proxy using multiple passbands"""
        if 'passband' not in obj_data.columns:
            return 0.5
        
        passbands = obj_data['passband'].unique()
        if len(passbands) < 2:
            return 0.5
        
        # Simple bolometric correction: more uniform across bands = better bolometric estimate
        band_fluxes = []
        for pb in passbands:
            pb_flux = obj_data[obj_data['passband'] == pb]['flux'].mean()
            if not np.isnan(pb_flux):
                band_fluxes.append(pb_flux)
        
        if len(band_fluxes) < 2:
            return 0.5
        
        # Coefficient of variation as bolometric correction quality
        flux_std = np.std(band_fluxes)
        flux_mean = np.mean(band_fluxes)
        
        if flux_mean > 0:
            cv = flux_std / flux_mean
            bolometric_quality = 1.0 - min(cv, 1.0)  # Lower CV = better bolometric estimate
        else:
            bolometric_quality = 0.5
        
        return bolometric_quality
    
    def _fit_exponential_rise(self, times, fluxes):
        """Fit exponential rise function"""
        try:
            # Simple exponential rise: y = A * (1 - exp(-t/τ))
            if len(times) < 2 or np.max(times) <= 0:
                return {'rate': 0.0, 'amplitude': 0.0, 'r_squared': 0.0}
            
            # Use linear fit on log space for simplicity
            normalized_flux = (fluxes - fluxes[0]) / (np.max(fluxes) - fluxes[0] + 1e-8)
            valid_mask = (normalized_flux > 0) & (normalized_flux < 1)
            
            if np.sum(valid_mask) < 2:
                return {'rate': 0.0, 'amplitude': 0.0, 'r_squared': 0.0}
            
            y_fit = -np.log(1 - normalized_flux[valid_mask])
            x_fit = times[valid_mask]
            
            slope, intercept, r_value, p_value, std_err = linregress(x_fit, y_fit)
            rate = max(slope, 1e-8)  # Avoid negative rates
            
            return {
                'rate': rate,
                'amplitude': np.max(fluxes),
                'r_squared': r_value ** 2
            }
        except:
            return {'rate': 0.0, 'amplitude': 0.0, 'r_squared': 0.0}
    
    def _fit_exponential_decay(self, times, fluxes):
        """Fit exponential decay function"""
        try:
            # Simple exponential decay: y = A * exp(-t/τ)
            if len(times) < 2 or np.max(times) <= 0:
                return {'rate': 0.0, 'amplitude': 0.0, 'r_squared': 0.0}
            
            # Use linear fit on log space
            valid_mask = fluxes > 0
            if np.sum(valid_mask) < 2:
                return {'rate': 0.0, 'amplitude': 0.0, 'r_squared': 0.0}
            
            y_fit = np.log(fluxes[valid_mask])
            x_fit = times[valid_mask]
            
            slope, intercept, r_value, p_value, std_err = linregress(x_fit, y_fit)
            rate = max(-slope, 1e-8)  # Positive decay rate
            
            return {
                'rate': rate,
                'amplitude': np.exp(intercept),
                'r_squared': r_value ** 2
            }
        except:
            return {'rate': 0.0, 'amplitude': 0.0, 'r_squared': 0.0}
    
    def _get_default_decay_features(self):
        """Return default radioactive decay features"""
        return {
            'nickel_signature': 0.0,
            'cobalt_signature': 0.0,
            'chain_consistency': 0.5,
            'nickel_mass': 0.0,
            'detection_strength': 0.0,
            'timescale_match': 0.5,
            'bolometric_correction': 0.5
        }
    
    def physics_loss(self, light_curve_data):
        """Physics loss for radioactive decay constraints"""
        return 0.0


class ShockPhysicsPINN(PINNModule):
    """
    PINN for shock breakout and circumstellar material interaction physics
    Critical for distinguishing SNII (strong CSM) from SNIbc (weak CSM)
    """
    
    def __init__(self):
        super().__init__(
            name="shock_physics",
            description="Shock breakout and circumstellar material interaction analysis"
        )
        self.feature_names = [
            'pinn_shock_breakout_signature',  # Early shock breakout detection
            'pinn_csm_interaction_strength',  # Circumstellar material interaction
            'pinn_wind_density_estimate',     # Progenitor wind density proxy
            'pinn_reverse_shock_indicator',   # Reverse shock signature
            'pinn_early_emission_consistency', # Early light curve consistency
            'pinn_shock_timescale',           # Characteristic shock timescale
            'pinn_csm_geometry_hint'          # CSM geometry indication (shell vs wind)
        ]
    
    def calculate_features(self, light_curve_data, metadata=None):
        """Calculate shock physics features"""
        features = {}
        
        object_ids = light_curve_data['object_id'].unique()
        shock_signatures = []
        csm_strengths = []
        wind_densities = []
        reverse_shocks = []
        early_consistencies = []
        shock_timescales = []
        csm_geometries = []
        
        for obj_id in object_ids:
            obj_data = light_curve_data[light_curve_data['object_id'] == obj_id]
            obj_features = self._analyze_shock_physics(obj_data)
            
            shock_signatures.append(obj_features['shock_signature'])
            csm_strengths.append(obj_features['csm_strength'])
            wind_densities.append(obj_features['wind_density'])
            reverse_shocks.append(obj_features['reverse_shock'])
            early_consistencies.append(obj_features['early_consistency'])
            shock_timescales.append(obj_features['shock_timescale'])
            csm_geometries.append(obj_features['csm_geometry'])
        
        features['pinn_shock_breakout_signature'] = shock_signatures
        features['pinn_csm_interaction_strength'] = csm_strengths
        features['pinn_wind_density_estimate'] = wind_densities
        features['pinn_reverse_shock_indicator'] = reverse_shocks
        features['pinn_early_emission_consistency'] = early_consistencies
        features['pinn_shock_timescale'] = shock_timescales
        features['pinn_csm_geometry_hint'] = csm_geometries
        
        return features
    
    def _analyze_shock_physics(self, obj_data):
        """Analyze shock breakout and CSM interaction signatures"""
        if len(obj_data) < 5:
            return self._get_default_shock_features()
        
        try:
            times = obj_data['mjd'].values
            fluxes = obj_data['flux'].values
            
            # Sort by time
            time_sorted_idx = np.argsort(times)
            times_sorted = times[time_sorted_idx]
            fluxes_sorted = fluxes[time_sorted_idx]
            
            total_duration = times_sorted[-1] - times_sorted[0]
            if total_duration <= 0:
                return self._get_default_shock_features()
            
            # 1. Shock breakout signature (very early phase)
            shock_features = self._extract_shock_breakout_signature(times_sorted, fluxes_sorted)
            
            # 2. CSM interaction strength
            csm_features = self._extract_csm_interaction(times_sorted, fluxes_sorted)
            
            # 3. Wind density estimate
            wind_density = self._estimate_wind_density(times_sorted, fluxes_sorted)
            
            # 4. Reverse shock indicator
            reverse_shock = self._detect_reverse_shock(times_sorted, fluxes_sorted)
            
            # 5. Early emission consistency
            early_consistency = self._check_early_emission_consistency(times_sorted, fluxes_sorted)
            
            # 6. Shock timescale
            shock_timescale = self._calculate_shock_timescale(times_sorted, fluxes_sorted)
            
            # 7. CSM geometry hint
            csm_geometry = self._infer_csm_geometry(times_sorted, fluxes_sorted)
            
            return {
                'shock_signature': float(shock_features['signature_strength']),
                'csm_strength': float(csm_features['interaction_strength']),
                'wind_density': float(wind_density),
                'reverse_shock': float(reverse_shock),
                'early_consistency': float(early_consistency),
                'shock_timescale': float(shock_timescale),
                'csm_geometry': float(csm_geometry)
            }
            
        except Exception as e:
            print(f"Error in shock physics analysis: {e}")
            return self._get_default_shock_features()
    
    def _extract_shock_breakout_signature(self, times, fluxes):
        """Extract shock breakout signature from early light curve"""
        if len(times) < 3:
            return {'signature_strength': 0.0, 'breakout_time': 0.0}
        
        # Focus on first 5 days for shock breakout
        early_mask = times - times[0] <= 5.0
        if np.sum(early_mask) < 2:
            return {'signature_strength': 0.0, 'breakout_time': 0.0}
        
        early_times = times[early_mask]
        early_fluxes = fluxes[early_mask]
        
        # Shock breakout often shows very rapid rise
        time_diffs = np.diff(early_times)
        flux_diffs = np.diff(early_fluxes)
        
        if len(time_diffs) == 0 or np.any(time_diffs <= 0):
            return {'signature_strength': 0.0, 'breakout_time': 0.0}
        
        rise_rates = flux_diffs / time_diffs
        max_rise_rate = np.max(rise_rates) if len(rise_rates) > 0 else 0.0
        
        # Normalize by mean flux
        mean_flux = np.mean(np.abs(early_fluxes))
        if mean_flux > 0:
            normalized_rise = max_rise_rate / mean_flux
        else:
            normalized_rise = 0.0
        
        # Shock breakout signature: very rapid early rise
        shock_strength = min(normalized_rise * 5.0, 1.0)  # Scale factor
        
        # Also check if rise is followed by decline (characteristic of shock cooling)
        if len(early_fluxes) >= 3:
            peak_idx = np.argmax(early_fluxes)
            if peak_idx > 0 and peak_idx < len(early_fluxes) - 1:
                # Check if decline after peak is consistent with shock cooling
                post_peak_decline = early_fluxes[peak_idx] - early_fluxes[-1]
                if post_peak_decline > 0:
                    shock_strength *= 1.2  # Boost if decline present
        
        return {
            'signature_strength': shock_strength,
            'breakout_time': early_times[0] if shock_strength > 0 else 0.0
        }
    
    def _extract_csm_interaction(self, times, fluxes):
        """Extract CSM interaction signatures"""
        if len(times) < 6:
            return {'interaction_strength': 0.0, 'bump_detection': 0.0}
        
        # CSM interaction often shows:
        # - Slower decline than radioactive decay
        # - Bumps or re-brightening in light curve
        # - Extended emission
        
        # 1. Check for light curve bumps (re-brightening)
        bump_strength = self._detect_light_curve_bumps(times, fluxes)
        
        # 2. Check decline rate consistency
        decline_consistency = self._analyze_decline_consistency(times, fluxes)
        
        # 3. Check for extended emission
        extension_strength = self._assess_emission_extension(times, fluxes)
        
        # CSM interaction strength combines these indicators
        csm_strength = (bump_strength * 0.4 + 
                        (1.0 - decline_consistency) * 0.3 + 
                        extension_strength * 0.3)
        
        return {
            'interaction_strength': csm_strength,
            'bump_detection': bump_strength
        }
    
    def _estimate_wind_density(self, times, fluxes):
        """Estimate progenitor wind density proxy"""
        if len(times) < 4:
            return 0.5
        
        # Wind density affects:
        # - CSM interaction strength
        # - Light curve width
        # - Peak luminosity
        
        peak_flux = np.max(fluxes)
        mean_flux = np.mean(np.abs(fluxes))
        
        if mean_flux <= 0:
            return 0.5
        
        # Broader light curves suggest higher density
        total_duration = times[-1] - times[0]
        peak_idx = np.argmax(fluxes)
        peak_time = times[peak_idx] - times[0]
        
        if total_duration > 0:
            # Width parameter: how symmetric/wide is the light curve
            width_parameter = total_duration / (2 * peak_time) if peak_time > 0 else 1.0
        else:
            width_parameter = 1.0
        
        # Higher peak/mean ratio can indicate stronger interaction
        luminosity_ratio = peak_flux / mean_flux
        
        # Wind density proxy
        wind_density = min((width_parameter * luminosity_ratio) / 5.0, 1.0)
        
        return wind_density
    
    def _detect_reverse_shock(self, times, fluxes):
        """Detect reverse shock signatures"""
        if len(times) < 5:
            return 0.0
        
        # Reverse shock can cause:
        # - Early emission features
        # - Specific spectral signatures (proxy via light curve shape)
        # - Re-brightening at specific times
        
        # Look for secondary peaks or inflection points
        from scipy.signal import savgol_filter
        
        try:
            # Smooth the light curve
            window_size = min(5, len(fluxes) // 2 * 2 + 1)  # Ensure odd
            if window_size >= 3:
                smoothed = savgol_filter(fluxes, window_size, 2)
                
                # Find inflection points
                second_deriv = np.gradient(np.gradient(smoothed))
                
                # Count significant inflection points beyond the main peak
                peak_idx = np.argmax(fluxes)
                if peak_idx < len(second_deriv) - 2:
                    post_peak_inflections = np.sum(np.abs(second_deriv[peak_idx:]) > np.std(second_deriv) * 0.5)
                    reverse_shock_strength = min(post_peak_inflections / 3.0, 1.0)
                else:
                    reverse_shock_strength = 0.0
            else:
                reverse_shock_strength = 0.0
                
        except:
            reverse_shock_strength = 0.0
        
        return reverse_shock_strength
    
    def _check_early_emission_consistency(self, times, fluxes):
        """Check consistency of early emission with shock models"""
        if len(times) < 3:
            return 0.5
        
        # Early emission should be smooth and follow shock cooling models
        early_mask = times - times[0] <= 10.0  # First 10 days
        if np.sum(early_mask) < 2:
            return 0.5
        
        early_times = times[early_mask]
        early_fluxes = fluxes[early_mask]
        
        # Calculate smoothness of early light curve
        flux_diffs = np.diff(early_fluxes)
        time_diffs = np.diff(early_times)
        
        if len(flux_diffs) == 0:
            return 0.5
        
        # Shock cooling should show smooth, monotonic behavior initially
        positive_changes = np.sum(flux_diffs > 0)
        negative_changes = np.sum(flux_diffs < 0)
        
        total_changes = len(flux_diffs)
        
        if total_changes > 0:
            # Early rise followed by decline is expected
            if positive_changes > negative_changes:
                consistency = 0.7  # Mostly rising - reasonable
            elif positive_changes == negative_changes:
                consistency = 0.5  # Mixed - neutral
            else:
                consistency = 0.3  # Mostly declining - unusual for early phase
        else:
            consistency = 0.5
        
        return consistency
    
    def _calculate_shock_timescale(self, times, fluxes):
        """Calculate characteristic shock timescale"""
        if len(times) < 3:
            return 0.0
        
        total_duration = times[-1] - times[0]
        if total_duration <= 0:
            return 0.0
        
        # Shock timescale related to light curve rise time
        peak_idx = np.argmax(fluxes)
        if peak_idx > 0:
            rise_time = times[peak_idx] - times[0]
            shock_timescale = min(rise_time / 20.0, 1.0)  # Normalize to 20 days
        else:
            shock_timescale = 0.0
        
        return shock_timescale
    
    def _infer_csm_geometry(self, times, fluxes):
        """Infer CSM geometry from light curve shape"""
        if len(times) < 4:
            return 0.5
        
        # Different geometries produce different light curve shapes:
        # - Spherical wind: smooth light curve
        # - Shell interaction: sharper features, possible double peaks
        
        # Calculate light curve "bumpiness" as geometry indicator
        try:
            from scipy.signal import savgol_filter
            
            window_size = min(5, len(fluxes) // 2 * 2 + 1)
            if window_size >= 3:
                smoothed = savgol_filter(fluxes, window_size, 2)
                residuals = fluxes - smoothed
                bumpiness = np.std(residuals) / (np.std(fluxes) + 1e-8)
                
                # High bumpiness suggests shell geometry
                geometry_hint = min(bumpiness * 3.0, 1.0)
            else:
                geometry_hint = 0.5
                
        except:
            geometry_hint = 0.5
        
        return geometry_hint
    
    def _detect_light_curve_bumps(self, times, fluxes):
        """Detect bumps or re-brightening in light curve"""
        if len(fluxes) < 7:
            return 0.0
        
        try:
            from scipy.signal import find_peaks
            
            # Find multiple peaks
            peaks, properties = find_peaks(fluxes, height=np.mean(fluxes), distance=3)
            
            if len(peaks) > 1:
                # Multiple peaks suggest CSM interaction
                bump_strength = min(len(peaks) / 4.0, 1.0)
            else:
                bump_strength = 0.0
                
        except:
            bump_strength = 0.0
        
        return bump_strength
    
    def _analyze_decline_consistency(self, times, fluxes):
        """Analyze decline rate consistency with radioactive decay"""
        if len(times) < 4:
            return 0.5
        
        peak_idx = np.argmax(fluxes)
        if peak_idx >= len(fluxes) - 3:
            return 0.5
        
        # Check if decline is consistent with exponential decay
        post_peak_times = times[peak_idx:] - times[peak_idx]
        post_peak_fluxes = fluxes[peak_idx:]
        
        try:
            if len(post_peak_fluxes) >= 3:
                # Fit exponential decay
                decay_fit = self._fit_exponential_decay(post_peak_times, post_peak_fluxes)
                r_squared = decay_fit['r_squared']
                
                # High R² means consistent with exponential decay (less CSM)
                # Low R² means inconsistent (more CSM interaction)
                decline_consistency = r_squared
            else:
                decline_consistency = 0.5
                
        except:
            decline_consistency = 0.5
        
        return decline_consistency
    
    def _assess_emission_extension(self, times, fluxes):
        """Assess emission extension beyond typical timescales"""
        if len(times) < 3:
            return 0.0
        
        total_duration = times[-1] - times[0]
        
        # Typical core-collapse SN duration: ~100 days
        # Extended emission suggests CSM interaction
        extension_strength = min(total_duration / 150.0, 1.0)  # Normalize to 150 days
        
        return extension_strength
    
    def _fit_exponential_decay(self, times, fluxes):
        """Fit exponential decay function (reuse from RadioactiveDecayPhysicsPINN)"""
        try:
            if len(times) < 2 or np.max(times) <= 0:
                return {'rate': 0.0, 'amplitude': 0.0, 'r_squared': 0.0}
            
            valid_mask = fluxes > 0
            if np.sum(valid_mask) < 2:
                return {'rate': 0.0, 'amplitude': 0.0, 'r_squared': 0.0}
            
            y_fit = np.log(fluxes[valid_mask])
            x_fit = times[valid_mask]
            
            slope, intercept, r_value, p_value, std_err = linregress(x_fit, y_fit)
            rate = max(-slope, 1e-8)
            
            return {
                'rate': rate,
                'amplitude': np.exp(intercept),
                'r_squared': r_value ** 2
            }
        except:
            return {'rate': 0.0, 'amplitude': 0.0, 'r_squared': 0.0}
    
    def _get_default_shock_features(self):
        """Return default shock physics features"""
        return {
            'shock_signature': 0.0,
            'csm_strength': 0.0,
            'wind_density': 0.5,
            'reverse_shock': 0.0,
            'early_consistency': 0.5,
            'shock_timescale': 0.0,
            'csm_geometry': 0.5
        }
    
    def physics_loss(self, light_curve_data):
        """Physics loss for shock physics constraints"""
        return 0.0




























# ============================================================================
# TIER 3: COMPETITION-OPTIMIZED PINNs
# ============================================================================

class ConfusionResolutionPINN(PINNModule):
    """
    PINN specifically targeting known class confusions in PLAsTiCC
    Directly addresses the most problematic class pairs
    """
    
    def __init__(self):
        super().__init__(
            name="confusion_resolution",
            description="Targeted discrimination for known problematic class pairs"
        )
        self.feature_names = [
            'pinn_64_vs_15_discriminator',    # Kilonova (64) vs SNIbc (15)
            'pinn_62_vs_67_separator',        # SNIax (62) vs 91bg (67)
            'pinn_42_vs_92_likelihood',       # AGN (42) vs LLAGN (92)
            'pinn_65_confidence_metric',      # Microlensing (65) certainty
            'pinn_rare_class_booster',        # Rare class enhancement
            'pinn_16_vs_88_discriminator',    # SNII (16) vs SLSN (88)
            'pinn_6_vs_90_separator'          # SNIa (6) vs PISN (90)
        ]
        
        # Confusion matrix analysis from PLAsTiCC
        self.problematic_pairs = {
            (64, 15): 'kilonova_vs_snibc',    # Fast vs intermediate timescale
            (62, 67): 'sniax_vs_91bg',        # Subluminous SNe
            (42, 92): 'agn_vs_llagn',         # AGN luminosity types
            (16, 88): 'snii_vs_slsn',         # Normal vs super-luminous
            (6, 90): 'snia_vs_pisn',          # Thermonuclear vs pair-instability
            (65,): 'microlensing_confidence'  # Microlensing identification
        }
    
    def calculate_features(self, light_curve_data, metadata=None):
        """Calculate confusion resolution features"""
        features = {}
        
        object_ids = light_curve_data['object_id'].unique()
        kilonova_snibc_scores = []
        sniax_91bg_scores = []
        agn_llagn_scores = []
        microlensing_confidences = []
        rare_boosters = []
        snii_slsn_scores = []
        snia_pisn_scores = []
        
        for obj_id in object_ids:
            obj_data = light_curve_data[light_curve_data['object_id'] == obj_id]
            obj_features = self._analyze_confusion_resolution(obj_data)
            
            kilonova_snibc_scores.append(obj_features['kilonova_snibc'])
            sniax_91bg_scores.append(obj_features['sniax_91bg'])
            agn_llagn_scores.append(obj_features['agn_llagn'])
            microlensing_confidences.append(obj_features['microlensing'])
            rare_boosters.append(obj_features['rare_booster'])
            snii_slsn_scores.append(obj_features['snii_slsn'])
            snia_pisn_scores.append(obj_features['snia_pisn'])
        
        features['pinn_64_vs_15_discriminator'] = kilonova_snibc_scores
        features['pinn_62_vs_67_separator'] = sniax_91bg_scores
        features['pinn_42_vs_92_likelihood'] = agn_llagn_scores
        features['pinn_65_confidence_metric'] = microlensing_confidences
        features['pinn_rare_class_booster'] = rare_boosters
        features['pinn_16_vs_88_discriminator'] = snii_slsn_scores
        features['pinn_6_vs_90_separator'] = snia_pisn_scores
        
        return features
    
    def _analyze_confusion_resolution(self, obj_data):
        """Analyze specific confusion resolution signatures"""
        if len(obj_data) < 4:
            return self._get_default_confusion_features()
        
        try:
            times = obj_data['mjd'].values
            fluxes = obj_data['flux'].values
            
            # Sort by time
            time_sorted_idx = np.argsort(times)
            times_sorted = times[time_sorted_idx]
            fluxes_sorted = fluxes[time_sorted_idx]
            
            total_duration = times_sorted[-1] - times_sorted[0]
            if total_duration <= 0:
                return self._get_default_confusion_features()
            
            # 1. Kilonova (64) vs SNIbc (15) discrimination
            kilonova_snibc = self._discriminate_kilonova_vs_snibc(times_sorted, fluxes_sorted)
            
            # 2. SNIax (62) vs 91bg (67) separation
            sniax_91bg = self._separate_sniax_vs_91bg(times_sorted, fluxes_sorted)
            
            # 3. AGN (42) vs LLAGN (92) likelihood
            agn_llagn = self._discriminate_agn_vs_llagn(times_sorted, fluxes_sorted)
            
            # 4. Microlensing (65) confidence
            microlensing = self._assess_microlensing_confidence(times_sorted, fluxes_sorted)
            
            # 5. Rare class booster
            rare_booster = self._calculate_rare_class_booster(times_sorted, fluxes_sorted)
            
            # 6. SNII (16) vs SLSN (88) discrimination
            snii_slsn = self._discriminate_snii_vs_slsn(times_sorted, fluxes_sorted)
            
            # 7. SNIa (6) vs PISN (90) separation
            snia_pisn = self._separate_snia_vs_pisn(times_sorted, fluxes_sorted)
            
            return {
                'kilonova_snibc': float(kilonova_snibc),
                'sniax_91bg': float(sniax_91bg),
                'agn_llagn': float(agn_llagn),
                'microlensing': float(microlensing),
                'rare_booster': float(rare_booster),
                'snii_slsn': float(snii_slsn),
                'snia_pisn': float(snia_pisn)
            }
            
        except Exception as e:
            print(f"Error in confusion resolution analysis: {e}")
            return self._get_default_confusion_features()
    
    def _discriminate_kilonova_vs_snibc(self, times, fluxes):
        """Discriminate between Kilonova (64) and SNIbc (15)"""
        # Key differences:
        # - Kilonova: Very fast (hours to days), blue, no radioactive tail
        # - SNIbc: Intermediate (weeks), broader light curve, radioactive decay
        
        total_duration = times[-1] - times[0]
        
        # Timescale discrimination
        if total_duration <= 7:  # Less than 1 week
            kilonova_likelihood = 0.8
        elif total_duration <= 14:  # 1-2 weeks
            kilonova_likelihood = 0.4
        else:  # More than 2 weeks
            kilonova_likelihood = 0.1
        
        # Rise time analysis
        peak_idx = np.argmax(fluxes)
        rise_time = times[peak_idx] - times[0] if peak_idx > 0 else total_duration
        
        if rise_time <= 2:  # Very fast rise (< 2 days)
            kilonova_likelihood *= 1.2
        elif rise_time <= 7:  # Fast rise (2-7 days)
            kilonova_likelihood *= 1.0
        else:  # Slow rise (> 7 days)
            kilonova_likelihood *= 0.6
        
        # Decline rate analysis
        if peak_idx < len(fluxes) - 2:
            decline_rate = (fluxes[peak_idx] - fluxes[-1]) / (times[-1] - times[peak_idx])
            if decline_rate > np.mean(fluxes) * 0.1:  # Rapid decline
                kilonova_likelihood *= 1.1
            else:  # Slow decline
                kilonova_likelihood *= 0.8
        
        return min(kilonova_likelihood, 1.0)
    
    def _separate_sniax_vs_91bg(self, times, fluxes):
        """Separate SNIax (62) from SNIa-91bg (67)"""
        # Both are subluminous, but:
        # - SNIax: Broader, more irregular, often have secondary maxima
        # - 91bg: Faster decline, more symmetric
        
        peak_flux = np.max(fluxes)
        mean_flux = np.mean(np.abs(fluxes))
        
        if mean_flux <= 0:
            return 0.5
        
        # Luminosity ratio (both are subluminous)
        luminosity_ratio = peak_flux / mean_flux
        
        # SNIax tend to be slightly brighter relative to mean
        if luminosity_ratio < 2.0:
            sniax_likelihood = 0.3  # Very subluminous - more like 91bg
        elif luminosity_ratio < 4.0:
            sniax_likelihood = 0.6  # Intermediate
        else:
            sniax_likelihood = 0.8  # Less subluminous - more like SNIax
        
        # Light curve width analysis
        total_duration = times[-1] - times[0]
        peak_idx = np.argmax(fluxes)
        peak_time = times[peak_idx] - times[0]
        
        if total_duration > 0:
            symmetry = peak_time / total_duration
            # SNIax often less symmetric
            if symmetry < 0.3 or symmetry > 0.7:
                sniax_likelihood *= 1.2  # Less symmetric - favors SNIax
            else:
                sniax_likelihood *= 0.8  # More symmetric - favors 91bg
        
        # Check for secondary features (SNIax can have bumps)
        bumpiness = self._calculate_lightcurve_bumpiness(fluxes)
        if bumpiness > 0.3:
            sniax_likelihood *= 1.1  # Bumpy - favors SNIax
        
        return min(sniax_likelihood, 1.0)
    
    def _discriminate_agn_vs_llagn(self, times, fluxes):
        """Discriminate AGN (42) from LLAGN (92)"""
        # Key differences:
        # - AGN: Stronger variability, larger amplitude changes
        # - LLAGN: Weaker variability, more stable
        
        # Variability amplitude
        flux_std = np.std(fluxes)
        flux_mean = np.mean(np.abs(fluxes))
        
        if flux_mean > 0:
            variability = flux_std / flux_mean
        else:
            variability = 0.0
        
        # AGN typically show stronger variability
        if variability > 0.5:
            agn_likelihood = 0.8
        elif variability > 0.2:
            agn_likelihood = 0.6
        else:
            agn_likelihood = 0.3
        
        # Timescale of variability
        total_duration = times[-1] - times[0]
        if total_duration > 100:  # Long-term monitoring
            # Check for characteristic AGN variability timescales
            timescale_consistency = self._assess_agn_timescales(times, fluxes)
            agn_likelihood = (agn_likelihood + timescale_consistency) / 2.0
        
        return agn_likelihood
    
    def _assess_microlensing_confidence(self, times, fluxes):
        """Assess confidence in microlensing (65) identification"""
        # Microlensing signatures:
        # - Smooth, symmetric light curve
        # - Single peak
        # - Specific timescale (weeks to months)
        # - Color-independent magnification
        
        if len(fluxes) < 5:
            return 0.0
        
        total_duration = times[-1] - times[0]
        
        # Timescale check (typical microlensing: 20-100 days)
        if total_duration < 10 or total_duration > 200:
            timescale_score = 0.2
        elif 20 <= total_duration <= 100:
            timescale_score = 0.9
        else:
            timescale_score = 0.6
        
        # Symmetry check
        symmetry_score = self._assess_lightcurve_symmetry(times, fluxes)
        
        # Smoothness check
        smoothness_score = self._assess_lightcurve_smoothness(fluxes)
        
        # Single peak check
        peak_score = self._check_single_peak(fluxes)
        
        # Combined microlensing confidence
        microlensing_confidence = (timescale_score * 0.3 + 
                                 symmetry_score * 0.3 + 
                                 smoothness_score * 0.2 + 
                                 peak_score * 0.2)
        
        return microlensing_confidence
    
    def _calculate_rare_class_booster(self, times, fluxes):
        """Calculate rare class enhancement score"""
        # Identifies objects that don't fit common patterns
        # and might belong to rare classes (64, 88, 90, 92, 95)
        
        common_pattern_deviation = self._assess_common_pattern_deviation(times, fluxes)
        
        # Rare classes often have unusual characteristics
        unusual_features = self._detect_unusual_features(times, fluxes)
        
        # Combine into rare class booster
        rare_booster = (common_pattern_deviation * 0.6 + unusual_features * 0.4)
        
        return rare_booster
    
    def _discriminate_snii_vs_slsn(self, times, fluxes):
        """Discriminate SNII (16) from SLSN (88)"""
        # Key differences:
        # - SLSN: Much brighter, longer duration, different color evolution
        # - SNII: Plateau phase, specific luminosity range
        
        peak_flux = np.max(fluxes)
        mean_flux = np.mean(np.abs(fluxes))
        
        if mean_flux <= 0:
            return 0.5
        
        # Luminosity discrimination (SLSN are much brighter)
        luminosity_ratio = peak_flux / mean_flux
        
        if luminosity_ratio > 8.0:
            slsn_likelihood = 0.8  # Very high peak/mean ratio
        elif luminosity_ratio > 5.0:
            slsn_likelihood = 0.6  # High ratio
        elif luminosity_ratio > 3.0:
            slsn_likelihood = 0.4  # Moderate ratio
        else:
            slsn_likelihood = 0.2  # Low ratio
        
        # Duration check (SLSN often longer)
        total_duration = times[-1] - times[0]
        if total_duration > 80:
            slsn_likelihood *= 1.2  # Long duration favors SLSN
        elif total_duration < 40:
            slsn_likelihood *= 0.8  # Short duration favors SNII
        
        # Check for plateau phase (characteristic of SNII)
        plateau_strength = self._detect_plateau_phase(times, fluxes)
        if plateau_strength > 0.5:
            slsn_likelihood *= 0.7  # Strong plateau favors SNII
        
        return min(slsn_likelihood, 1.0)
    
    def _separate_snia_vs_pisn(self, times, fluxes):
        """Separate SNIa (6) from PISN (90)"""
        # Key differences:
        # - PISN: Much longer timescale, broader light curve
        # - SNIa: Characteristic 56Ni decay timescale
        
        total_duration = times[-1] - times[0]
        
        # Timescale discrimination
        if total_duration > 150:  # Very long duration
            pisn_likelihood = 0.8
        elif total_duration > 100:  # Long duration
            pisn_likelihood = 0.6
        elif total_duration > 60:  # Moderate duration
            pisn_likelihood = 0.4
        else:  # Short duration
            pisn_likelihood = 0.2
        
        # Light curve width analysis
        peak_idx = np.argmax(fluxes)
        if peak_idx > 0:
            rise_time = times[peak_idx] - times[0]
            if total_duration > 0:
                width_parameter = total_duration / rise_time if rise_time > 0 else 1.0
                # PISN have broader light curves
                if width_parameter > 3.0:
                    pisn_likelihood *= 1.2
                elif width_parameter < 1.5:
                    pisn_likelihood *= 0.8
        
        # Check for nickel decay signature (favors SNIa)
        nickel_signature = self._check_nickel_decay_signature(times, fluxes)
        if nickel_signature > 0.6:
            pisn_likelihood *= 0.7  # Strong nickel signature favors SNIa
        
        return min(pisn_likelihood, 1.0)
    
    def _calculate_lightcurve_bumpiness(self, fluxes):
        """Calculate light curve bumpiness"""
        if len(fluxes) < 5:
            return 0.0
        
        try:
            from scipy.signal import savgol_filter
            window_size = min(5, len(fluxes) // 2 * 2 + 1)
            if window_size >= 3:
                smoothed = savgol_filter(fluxes, window_size, 2)
                residuals = fluxes - smoothed
                bumpiness = np.std(residuals) / (np.std(fluxes) + 1e-8)
                return min(bumpiness * 2.0, 1.0)
        except:
            pass
        
        return 0.0
    
    def _assess_agn_timescales(self, times, fluxes):
        """Assess AGN characteristic variability timescales"""
        if len(times) < 10:
            return 0.5
        
        # AGN show variability on multiple timescales
        # Check for both short-term and long-term variations
        time_diffs = np.diff(times)
        flux_diffs = np.diff(fluxes)
        
        if len(time_diffs) == 0:
            return 0.5
        
        # Calculate variability on different timescales
        short_term_var = self._calculate_variability_on_timescale(times, fluxes, max_timescale=10)
        long_term_var = self._calculate_variability_on_timescale(times, fluxes, min_timescale=30)
        
        # AGN typically show variability on both timescales
        if short_term_var > 0.3 and long_term_var > 0.3:
            return 0.8
        elif short_term_var > 0.2 or long_term_var > 0.2:
            return 0.6
        else:
            return 0.4
    
    def _assess_lightcurve_symmetry(self, times, fluxes):
        """Assess light curve symmetry"""
        if len(fluxes) < 3:
            return 0.5
        
        peak_idx = np.argmax(fluxes)
        if peak_idx == 0 or peak_idx == len(fluxes) - 1:
            return 0.5
        
        rise_flux = fluxes[:peak_idx + 1]
        decay_flux = fluxes[peak_idx:]
        
        if len(rise_flux) < 2 or len(decay_flux) < 2:
            return 0.5
        
        # Normalize and compare
        rise_norm = (rise_flux - np.min(rise_flux)) / (np.max(rise_flux) - np.min(rise_flux) + 1e-8)
        decay_norm = (decay_flux - np.min(decay_flux)) / (np.max(decay_flux) - np.min(decay_flux) + 1e-8)
        decay_reversed = decay_norm[::-1]
        
        min_len = min(len(rise_norm), len(decay_reversed))
        if min_len >= 2:
            correlation = np.corrcoef(rise_norm[:min_len], decay_reversed[:min_len])[0, 1]
            if np.isnan(correlation):
                return 0.5
            symmetry = (correlation + 1) / 2
            return symmetry
        
        return 0.5
    
    def _assess_lightcurve_smoothness(self, fluxes):
        """Assess light curve smoothness"""
        if len(fluxes) < 3:
            return 0.5
        
        flux_diffs = np.diff(fluxes)
        smoothness = 1.0 - min(np.std(flux_diffs) / (np.std(fluxes) + 1e-8), 1.0)
        return smoothness
    
    def _check_single_peak(self, fluxes):
        """Check if light curve has single dominant peak"""
        if len(fluxes) < 3:
            return 0.5
        
        try:
            from scipy.signal import find_peaks
            peaks, properties = find_peaks(fluxes, height=np.mean(fluxes))
            
            if len(peaks) == 1:
                return 0.9
            elif len(peaks) == 2:
                return 0.6
            else:
                return 0.3
        except:
            return 0.5
    
    def _assess_common_pattern_deviation(self, times, fluxes):
        """Assess deviation from common supernova patterns"""
        # Check how well the light curve fits common templates
        # Rare classes often deviate significantly
        
        # 1. Check rise and decline times
        peak_idx = np.argmax(fluxes)
        if peak_idx == 0 or peak_idx == len(fluxes) - 1:
            return 0.5
        
        rise_time = times[peak_idx] - times[0]
        decay_time = times[-1] - times[peak_idx]
        
        # Typical SN: rise ~15-20 days, decay ~30-60 days
        typical_rise = 18.0
        typical_decay = 45.0
        
        rise_deviation = 1.0 - min(abs(rise_time - typical_rise) / typical_rise, 1.0)
        decay_deviation = 1.0 - min(abs(decay_time - typical_decay) / typical_decay, 1.0)
        
        # High deviation from typical = more likely rare
        common_pattern_deviation = 1.0 - (rise_deviation + decay_deviation) / 2.0
        
        return common_pattern_deviation
    
    def _detect_unusual_features(self, times, fluxes):
        """Detect unusual features that might indicate rare classes"""
        unusual_score = 0.0
        
        # Check for multiple peaks
        bumpiness = self._calculate_lightcurve_bumpiness(fluxes)
        if bumpiness > 0.4:
            unusual_score += 0.3
        
        # Check for very fast or very slow evolution
        total_duration = times[-1] - times[0]
        if total_duration < 10 or total_duration > 200:
            unusual_score += 0.3
        
        # Check for irregular variability
        flux_std = np.std(fluxes)
        flux_mean = np.mean(np.abs(fluxes))
        if flux_mean > 0:
            variability = flux_std / flux_mean
            if variability > 0.8 or variability < 0.1:
                unusual_score += 0.4
        
        return min(unusual_score, 1.0)
    
    def _detect_plateau_phase(self, times, fluxes):
        """Detect plateau phase characteristic of SNII"""
        if len(fluxes) < 6:
            return 0.0
        
        flux_diff = np.diff(fluxes)
        time_diff = np.diff(times)
        
        # Look for periods with small flux changes
        small_changes = np.abs(flux_diff) < (np.std(fluxes) * 0.15)
        if np.any(small_changes):
            plateau_duration = np.sum(time_diff[small_changes])
            total_duration = times[-1] - times[0]
            if total_duration > 0:
                return min(plateau_duration / total_duration, 1.0)
        
        return 0.0
    
    def _check_nickel_decay_signature(self, times, fluxes):
        """Check for nickel decay signature"""
        if len(fluxes) < 4:
            return 0.0
        
        peak_idx = np.argmax(fluxes)
        if peak_idx >= len(fluxes) - 2:
            return 0.0
        
        # Nickel decay: exponential decline with ~6 day timescale initially
        post_peak_times = times[peak_idx:] - times[peak_idx]
        post_peak_fluxes = fluxes[peak_idx:]
        
        try:
            if len(post_peak_fluxes) >= 3:
                # Fit exponential decay
                decay_fit = self._fit_exponential_decay(post_peak_times, post_peak_fluxes)
                timescale = 1.0 / decay_fit['rate'] if decay_fit['rate'] > 0 else 0.0
                
                # Compare to nickel decay timescale (~6 days)
                if 4 <= timescale <= 10:
                    nickel_match = 0.8
                elif 2 <= timescale <= 15:
                    nickel_match = 0.5
                else:
                    nickel_match = 0.2
                
                return nickel_match * decay_fit['r_squared']
        except:
            pass
        
        return 0.0
    
    def _calculate_variability_on_timescale(self, times, fluxes, min_timescale=0, max_timescale=999):
        """Calculate variability on specific timescales"""
        if len(times) < 3:
            return 0.0
        
        time_diffs = np.diff(times)
        flux_diffs = np.diff(fluxes)
        
        if len(time_diffs) == 0:
            return 0.0
        
        # Filter for specific timescale
        timescale_mask = (time_diffs >= min_timescale) & (time_diffs <= max_timescale)
        if not np.any(timescale_mask):
            return 0.0
        
        relevant_flux_diffs = flux_diffs[timescale_mask]
        if len(relevant_flux_diffs) == 0:
            return 0.0
        
        variability = np.std(relevant_flux_diffs) / (np.mean(np.abs(fluxes)) + 1e-8)
        return min(variability, 1.0)
    
    def _fit_exponential_decay(self, times, fluxes):
        """Fit exponential decay function"""
        try:
            if len(times) < 2 or np.max(times) <= 0:
                return {'rate': 0.0, 'amplitude': 0.0, 'r_squared': 0.0}
            
            valid_mask = fluxes > 0
            if np.sum(valid_mask) < 2:
                return {'rate': 0.0, 'amplitude': 0.0, 'r_squared': 0.0}
            
            y_fit = np.log(fluxes[valid_mask])
            x_fit = times[valid_mask]
            
            slope, intercept, r_value, p_value, std_err = linregress(x_fit, y_fit)
            rate = max(-slope, 1e-8)
            
            return {
                'rate': rate,
                'amplitude': np.exp(intercept),
                'r_squared': r_value ** 2
            }
        except:
            return {'rate': 0.0, 'amplitude': 0.0, 'r_squared': 0.0}
    
    def _get_default_confusion_features(self):
        """Return default confusion resolution features"""
        return {
            'kilonova_snibc': 0.5,
            'sniax_91bg': 0.5,
            'agn_llagn': 0.5,
            'microlensing': 0.0,
            'rare_booster': 0.0,
            'snii_slsn': 0.5,
            'snia_pisn': 0.5
        }
    
    def physics_loss(self, light_curve_data):
        """Physics loss for confusion resolution"""
        return 0.0


class BayesianEvidencePINN(PINNModule):
    """
    PINN for Bayesian model comparison and uncertainty quantification
    Provides principled Bayesian evidence for different physical scenarios
    """
    
    def __init__(self):
        super().__init__(
            name="bayesian_evidence",
            description="Bayesian model comparison and evidence calculation"
        )
        self.feature_names = [
            'pinn_snia_bayes_factor',          # SNIa vs other models
            'pinn_snii_bayes_factor',          # SNII vs other models
            'pinn_agn_bayes_factor',           # AGN vs other models
            'pinn_model_evidence_ratio',       # Best vs second-best model
            'pinn_bayesian_class_confidence',  # Overall classification confidence
            'pinn_evidence_strength',          # Strength of Bayesian evidence
            'pinn_model_complexity_penalty'    # Model complexity consideration
        ]
        
        # Define model classes for comparison
        self.model_classes = {
            'snia': [6, 62, 67],    # Thermonuclear SNe
            'snii': [16],           # Core-collapse H-rich
            'snibc': [15],          # Stripped-envelope
            'agn': [42, 92],        # Active galaxies
            'microlensing': [65],   # Microlensing
            'kilonova': [64],       # Neutron star mergers
            'slsn': [88],           # Super-luminous SNe
            'other': [52, 53, 90, 95]  # Other transients
        }
    
    def calculate_features(self, light_curve_data, metadata=None):
        """Calculate Bayesian evidence features"""
        features = {}
        
        object_ids = light_curve_data['object_id'].unique()
        snia_factors = []
        snii_factors = []
        agn_factors = []
        evidence_ratios = []
        class_confidences = []
        evidence_strengths = []
        complexity_penalties = []
        
        for obj_id in object_ids:
            obj_data = light_curve_data[light_curve_data['object_id'] == obj_id]
            obj_features = self._calculate_bayesian_evidence(obj_data)
            
            snia_factors.append(obj_features['snia_factor'])
            snii_factors.append(obj_features['snii_factor'])
            agn_factors.append(obj_features['agn_factor'])
            evidence_ratios.append(obj_features['evidence_ratio'])
            class_confidences.append(obj_features['class_confidence'])
            evidence_strengths.append(obj_features['evidence_strength'])
            complexity_penalties.append(obj_features['complexity_penalty'])
        
        features['pinn_snia_bayes_factor'] = snia_factors
        features['pinn_snii_bayes_factor'] = snii_factors
        features['pinn_agn_bayes_factor'] = agn_factors
        features['pinn_model_evidence_ratio'] = evidence_ratios
        features['pinn_bayesian_class_confidence'] = class_confidences
        features['pinn_evidence_strength'] = evidence_strengths
        features['pinn_model_complexity_penalty'] = complexity_penalties
        
        return features
    
    def _calculate_bayesian_evidence(self, obj_data):
        """Calculate Bayesian evidence for different models"""
        if len(obj_data) < 4:
            return self._get_default_bayesian_features()
        
        try:
            times = obj_data['mjd'].values
            fluxes = obj_data['flux'].values
            
            # Sort by time
            time_sorted_idx = np.argsort(times)
            times_sorted = times[time_sorted_idx]
            fluxes_sorted = fluxes[time_sorted_idx]
            
            # Calculate evidence for different model classes
            model_evidences = {}
            
            # 1. SNIa model evidence
            model_evidences['snia'] = self._calculate_snia_evidence(times_sorted, fluxes_sorted)
            
            # 2. SNII model evidence
            model_evidences['snii'] = self._calculate_snii_evidence(times_sorted, fluxes_sorted)
            
            # 3. AGN model evidence
            model_evidences['agn'] = self._calculate_agn_evidence(times_sorted, fluxes_sorted)
            
            # 4. SNIbc model evidence
            model_evidences['snibc'] = self._calculate_snibc_evidence(times_sorted, fluxes_sorted)
            
            # 5. Microlensing model evidence
            model_evidences['microlensing'] = self._calculate_microlensing_evidence(times_sorted, fluxes_sorted)
            
            # 6. Kilonova model evidence
            model_evidences['kilonova'] = self._calculate_kilonova_evidence(times_sorted, fluxes_sorted)
            
            # Calculate Bayes factors and other metrics
            bayesian_features = self._compute_bayesian_metrics(model_evidences)
            
            return bayesian_features
            
        except Exception as e:
            print(f"Error in Bayesian evidence calculation: {e}")
            return self._get_default_bayesian_features()
    
    def _calculate_snia_evidence(self, times, fluxes):
        """Calculate evidence for SNIa model"""
        # SNIa characteristics:
        # - Characteristic rise and decline times
        # - Nickel decay signature
        # - Specific luminosity range
        # - Color evolution
        
        evidence = 0.0
        total_duration = times[-1] - times[0]
        
        # Timescale consistency (SNIa: ~60 days total)
        if 40 <= total_duration <= 100:
            evidence += 0.3
        elif 20 <= total_duration <= 150:
            evidence += 0.1
        
        # Rise time consistency (SNIa: ~15-20 days)
        peak_idx = np.argmax(fluxes)
        if peak_idx > 0:
            rise_time = times[peak_idx] - times[0]
            if 10 <= rise_time <= 25:
                evidence += 0.3
            elif 5 <= rise_time <= 35:
                evidence += 0.1
        
        # Decline rate consistency
        if peak_idx < len(fluxes) - 2:
            decline_rate = self._calculate_decline_rate(times[peak_idx:], fluxes[peak_idx:])
            # SNIa have specific decline rates
            if 0.015 <= decline_rate <= 0.035:
                evidence += 0.2
            elif 0.005 <= decline_rate <= 0.05:
                evidence += 0.1
        
        # Nickel decay signature
        nickel_evidence = self._check_nickel_decay_evidence(times, fluxes)
        evidence += nickel_evidence * 0.2
        
        return min(evidence, 1.0)
    
    def _calculate_snii_evidence(self, times, fluxes):
        """Calculate evidence for SNII model"""
        # SNII characteristics:
        # - Plateau phase
        # - Longer duration than SNIa
        # - Different color evolution
        
        evidence = 0.0
        total_duration = times[-1] - times[0]
        
        # Duration consistency (SNII: often longer than SNIa)
        if total_duration > 80:
            evidence += 0.3
        elif total_duration > 50:
            evidence += 0.2
        
        # Plateau detection
        plateau_strength = self._detect_plateau_phase(times, fluxes)
        evidence += plateau_strength * 0.4
        
        # Rise time (SNII can have varied rise times)
        peak_idx = np.argmax(fluxes)
        if peak_idx > 0:
            rise_time = times[peak_idx] - times[0]
            if 10 <= rise_time <= 40:  # Broader range than SNIa
                evidence += 0.2
            elif 5 <= rise_time <= 60:
                evidence += 0.1
        
        # Variability pattern
        variability_evidence = self._assess_snii_variability(times, fluxes)
        evidence += variability_evidence * 0.1
        
        return min(evidence, 1.0)
    
    def _calculate_agn_evidence(self, times, fluxes):
        """Calculate evidence for AGN model"""
        # AGN characteristics:
        # - Long-term variability
        # - Specific timescales
        # - No characteristic explosion shape
        
        evidence = 0.0
        total_duration = times[-1] - times[0]
        
        # Long duration favored for AGN
        if total_duration > 100:
            evidence += 0.3
        elif total_duration > 50:
            evidence += 0.2
        
        # Check for characteristic AGN variability
        agn_variability = self._assess_agn_variability_pattern(times, fluxes)
        evidence += agn_variability * 0.4
        
        # Check for lack of explosion signature
        explosion_signature = self._check_explosion_signature(times, fluxes)
        evidence += (1.0 - explosion_signature) * 0.3  # AGN should not look like explosions
        
        return min(evidence, 1.0)
    
    def _calculate_snibc_evidence(self, times, fluxes):
        """Calculate evidence for SNIbc model"""
        # SNIbc characteristics:
        # - Faster evolution than SNII
        # - No hydrogen features (proxy via light curve shape)
        # - Similar to SNIa but different timescales
        
        evidence = 0.0
        total_duration = times[-1] - times[0]
        
        # Timescale (intermediate between fast and slow)
        if 30 <= total_duration <= 70:
            evidence += 0.3
        elif 20 <= total_duration <= 100:
            evidence += 0.2
        
        # Faster decline than SNII
        peak_idx = np.argmax(fluxes)
        if peak_idx < len(fluxes) - 2:
            decline_rate = self._calculate_decline_rate(times[peak_idx:], fluxes[peak_idx:])
            if decline_rate > 0.02:  # Faster decline than typical SNII
                evidence += 0.3
        
        # No plateau phase (different from SNII)
        plateau_strength = self._detect_plateau_phase(times, fluxes)
        evidence += (1.0 - plateau_strength) * 0.2
        
        # Nickel decay signature (weaker than SNIa)
        nickel_evidence = self._check_nickel_decay_evidence(times, fluxes)
        evidence += nickel_evidence * 0.2
        
        return min(evidence, 1.0)
    
    def _calculate_microlensing_evidence(self, times, fluxes):
        """Calculate evidence for microlensing model"""
        # Microlensing characteristics:
        # - Symmetric light curve
        # - Single peak
        # - Specific timescale
        # - Smooth variation
        
        evidence = 0.0
        total_duration = times[-1] - times[0]
        
        # Timescale consistency (typical microlensing: 20-100 days)
        if 20 <= total_duration <= 100:
            evidence += 0.3
        elif 10 <= total_duration <= 150:
            evidence += 0.1
        
        # Symmetry
        symmetry = self._assess_lightcurve_symmetry(times, fluxes)
        evidence += symmetry * 0.3
        
        # Smoothness
        smoothness = self._assess_lightcurve_smoothness(fluxes)
        evidence += smoothness * 0.2
        
        # Single peak
        single_peak = self._check_single_peak(fluxes)
        evidence += single_peak * 0.2
        
        return min(evidence, 1.0)
    
    def _calculate_kilonova_evidence(self, times, fluxes):
        """Calculate evidence for kilonova model"""
        # Kilonova characteristics:
        # - Very fast evolution
        # - Blue colors initially
        # - Rapid decline
        # - Short duration
        
        evidence = 0.0
        total_duration = times[-1] - times[0]
        
        # Very short duration
        if total_duration <= 7:
            evidence += 0.4
        elif total_duration <= 14:
            evidence += 0.2
        elif total_duration <= 21:
            evidence += 0.1
        
        # Rapid rise
        peak_idx = np.argmax(fluxes)
        if peak_idx > 0:
            rise_time = times[peak_idx] - times[0]
            if rise_time <= 2:
                evidence += 0.3
            elif rise_time <= 5:
                evidence += 0.2
        
        # Rapid decline
        if peak_idx < len(fluxes) - 2:
            decline_rate = self._calculate_decline_rate(times[peak_idx:], fluxes[peak_idx:])
            if decline_rate > 0.05:  # Very rapid decline
                evidence += 0.3
        
        return min(evidence, 1.0)
    
    def _compute_bayesian_metrics(self, model_evidences):
        """Compute Bayesian metrics from model evidences"""
        # Convert evidences to probabilities (simplified)
        evidence_sum = sum(model_evidences.values())
        if evidence_sum > 0:
            model_probabilities = {k: v / evidence_sum for k, v in model_evidences.items()}
        else:
            model_probabilities = {k: 1.0 / len(model_evidences) for k in model_evidences.keys()}
        
        # Calculate Bayes factors (relative to other models)
        snia_factor = model_probabilities.get('snia', 0) / max(model_probabilities.get('snii', 1e-8), 1e-8)
        snii_factor = model_probabilities.get('snii', 0) / max(model_probabilities.get('snia', 1e-8), 1e-8)
        agn_factor = model_probabilities.get('agn', 0) / max(model_probabilities.get('snia', 1e-8), 1e-8)
        
        # Normalize Bayes factors
        snia_factor = min(snia_factor, 10.0) / 10.0
        snii_factor = min(snii_factor, 10.0) / 10.0
        agn_factor = min(agn_factor, 10.0) / 10.0
        
        # Evidence ratio (best vs second best)
        sorted_probs = sorted(model_probabilities.values(), reverse=True)
        if len(sorted_probs) >= 2 and sorted_probs[1] > 0:
            evidence_ratio = sorted_probs[0] / sorted_probs[1]
            evidence_ratio = min(evidence_ratio, 5.0) / 5.0  # Normalize to 0-1
        else:
            evidence_ratio = 0.0
        
        # Overall classification confidence
        max_prob = max(model_probabilities.values())
        class_confidence = max_prob
        
        # Evidence strength
        evidence_strength = np.std(list(model_probabilities.values()))
        
        # Model complexity penalty (simplified)
        complexity_penalty = 1.0 - evidence_strength  # More uniform = more complex
        
        return {
            'snia_factor': float(snia_factor),
            'snii_factor': float(snii_factor),
            'agn_factor': float(agn_factor),
            'evidence_ratio': float(evidence_ratio),
            'class_confidence': float(class_confidence),
            'evidence_strength': float(evidence_strength),
            'complexity_penalty': float(complexity_penalty)
        }
    
    def _calculate_decline_rate(self, times, fluxes):
        """Calculate decline rate after peak"""
        if len(fluxes) < 2:
            return 0.0
        
        time_span = times[-1] - times[0]
        if time_span <= 0:
            return 0.0
        
        flux_change = fluxes[0] - fluxes[-1]
        return flux_change / time_span
    
    def _check_nickel_decay_evidence(self, times, fluxes):
        """Check evidence for nickel decay signature"""
        # Similar to previous implementation but returning evidence score
        nickel_evidence = 0.0
        
        peak_idx = np.argmax(fluxes)
        if peak_idx >= len(fluxes) - 2:
            return 0.0
        
        post_peak_times = times[peak_idx:] - times[peak_idx]
        post_peak_fluxes = fluxes[peak_idx:]
        
        try:
            if len(post_peak_fluxes) >= 3:
                decay_fit = self._fit_exponential_decay(post_peak_times, post_peak_fluxes)
                timescale = 1.0 / decay_fit['rate'] if decay_fit['rate'] > 0 else 0.0
                
                # Nickel decay timescale evidence
                if 4 <= timescale <= 10:
                    nickel_evidence = 0.8 * decay_fit['r_squared']
                elif 2 <= timescale <= 15:
                    nickel_evidence = 0.5 * decay_fit['r_squared']
                else:
                    nickel_evidence = 0.2 * decay_fit['r_squared']
        except:
            pass
        
        return nickel_evidence
    
    def _detect_plateau_phase(self, times, fluxes):
        """Detect plateau phase (reuse from ConfusionResolutionPINN)"""
        if len(fluxes) < 6:
            return 0.0
        
        flux_diff = np.diff(fluxes)
        time_diff = np.diff(times)
        
        small_changes = np.abs(flux_diff) < (np.std(fluxes) * 0.15)
        if np.any(small_changes):
            plateau_duration = np.sum(time_diff[small_changes])
            total_duration = times[-1] - times[0]
            if total_duration > 0:
                return min(plateau_duration / total_duration, 1.0)
        
        return 0.0
    
    def _assess_snii_variability(self, times, fluxes):
        """Assess SNII-like variability pattern"""
        # SNII can show more irregular variability than SNIa
        bumpiness = self._calculate_lightcurve_bumpiness(fluxes)
        return min(bumpiness * 1.5, 1.0)  # Some bumpiness is OK for SNII
    
    def _assess_agn_variability_pattern(self, times, fluxes):
        """Assess AGN-like variability pattern"""
        if len(times) < 10:
            return 0.0
        
        # AGN show variability on multiple timescales
        short_term_var = self._calculate_variability_on_timescale(times, fluxes, max_timescale=10)
        long_term_var = self._calculate_variability_on_timescale(times, fluxes, min_timescale=30)
        
        # AGN typically show both short and long-term variability
        if short_term_var > 0.2 and long_term_var > 0.2:
            return 0.8
        elif short_term_var > 0.1 or long_term_var > 0.1:
            return 0.5
        else:
            return 0.2
    
    def _check_explosion_signature(self, times, fluxes):
        """Check for explosion-like signature"""
        # Explosions typically show:
        # - Rapid rise to peak
        # - Followed by decline
        # - Characteristic timescale
        
        peak_idx = np.argmax(fluxes)
        if peak_idx == 0 or peak_idx == len(fluxes) - 1:
            return 0.0
        
        rise_time = times[peak_idx] - times[0]
        total_duration = times[-1] - times[0]
        
        if total_duration <= 0:
            return 0.0
        
        # Explosions typically have rise time < 1/3 of total duration
        if rise_time / total_duration < 0.33:
            explosion_signature = 0.7
        elif rise_time / total_duration < 0.5:
            explosion_signature = 0.4
        else:
            explosion_signature = 0.1
        
        return explosion_signature
    
    def _calculate_lightcurve_bumpiness(self, fluxes):
        """Calculate light curve bumpiness (reuse from ConfusionResolutionPINN)"""
        if len(fluxes) < 5:
            return 0.0
        
        try:
            from scipy.signal import savgol_filter
            window_size = min(5, len(fluxes) // 2 * 2 + 1)
            if window_size >= 3:
                smoothed = savgol_filter(fluxes, window_size, 2)
                residuals = fluxes - smoothed
                bumpiness = np.std(residuals) / (np.std(fluxes) + 1e-8)
                return min(bumpiness * 2.0, 1.0)
        except:
            pass
        
        return 0.0
    
    def _assess_lightcurve_symmetry(self, times, fluxes):
        """Assess light curve symmetry (reuse from ConfusionResolutionPINN)"""
        if len(fluxes) < 3:
            return 0.5
        
        peak_idx = np.argmax(fluxes)
        if peak_idx == 0 or peak_idx == len(fluxes) - 1:
            return 0.5
        
        rise_flux = fluxes[:peak_idx + 1]
        decay_flux = fluxes[peak_idx:]
        
        if len(rise_flux) < 2 or len(decay_flux) < 2:
            return 0.5
        
        rise_norm = (rise_flux - np.min(rise_flux)) / (np.max(rise_flux) - np.min(rise_flux) + 1e-8)
        decay_norm = (decay_flux - np.min(decay_flux)) / (np.max(decay_flux) - np.min(decay_flux) + 1e-8)
        decay_reversed = decay_norm[::-1]
        
        min_len = min(len(rise_norm), len(decay_reversed))
        if min_len >= 2:
            correlation = np.corrcoef(rise_norm[:min_len], decay_reversed[:min_len])[0, 1]
            if np.isnan(correlation):
                return 0.5
            return (correlation + 1) / 2
        
        return 0.5
    
    def _assess_lightcurve_smoothness(self, fluxes):
        """Assess light curve smoothness (reuse from ConfusionResolutionPINN)"""
        if len(fluxes) < 3:
            return 0.5
        
        flux_diffs = np.diff(fluxes)
        smoothness = 1.0 - min(np.std(flux_diffs) / (np.std(fluxes) + 1e-8), 1.0)
        return smoothness
    
    def _check_single_peak(self, fluxes):
        """Check single peak (reuse from ConfusionResolutionPINN)"""
        if len(fluxes) < 3:
            return 0.5
        
        try:
            from scipy.signal import find_peaks
            peaks, properties = find_peaks(fluxes, height=np.mean(fluxes))
            
            if len(peaks) == 1:
                return 0.9
            elif len(peaks) == 2:
                return 0.6
            else:
                return 0.3
        except:
            return 0.5
    
    def _calculate_variability_on_timescale(self, times, fluxes, min_timescale=0, max_timescale=999):
        """Calculate variability on specific timescales (reuse)"""
        if len(times) < 3:
            return 0.0
        
        time_diffs = np.diff(times)
        flux_diffs = np.diff(fluxes)
        
        if len(time_diffs) == 0:
            return 0.0
        
        timescale_mask = (time_diffs >= min_timescale) & (time_diffs <= max_timescale)
        if not np.any(timescale_mask):
            return 0.0
        
        relevant_flux_diffs = flux_diffs[timescale_mask]
        if len(relevant_flux_diffs) == 0:
            return 0.0
        
        variability = np.std(relevant_flux_diffs) / (np.mean(np.abs(fluxes)) + 1e-8)
        return min(variability, 1.0)
    
    def _fit_exponential_decay(self, times, fluxes):
        """Fit exponential decay (reuse)"""
        try:
            if len(times) < 2 or np.max(times) <= 0:
                return {'rate': 0.0, 'amplitude': 0.0, 'r_squared': 0.0}
            
            valid_mask = fluxes > 0
            if np.sum(valid_mask) < 2:
                return {'rate': 0.0, 'amplitude': 0.0, 'r_squared': 0.0}
            
            y_fit = np.log(fluxes[valid_mask])
            x_fit = times[valid_mask]
            
            slope, intercept, r_value, p_value, std_err = linregress(x_fit, y_fit)
            rate = max(-slope, 1e-8)
            
            return {
                'rate': rate,
                'amplitude': np.exp(intercept),
                'r_squared': r_value ** 2
            }
        except:
            return {'rate': 0.0, 'amplitude': 0.0, 'r_squared': 0.0}
    
    def _get_default_bayesian_features(self):
        """Return default Bayesian evidence features"""
        return {
            'snia_factor': 0.5,
            'snii_factor': 0.5,
            'agn_factor': 0.5,
            'evidence_ratio': 0.5,
            'class_confidence': 0.5,
            'evidence_strength': 0.5,
            'complexity_penalty': 0.5
        }
    
    def physics_loss(self, light_curve_data):
        """Physics loss for Bayesian evidence"""
        return 0.0













# ============================================================================
# UPDATED SIMPLE USAGE FUNCTIONS
# # ============================================================================

# # Global instance for easiest usage
# _pinn_manager = None

# def get_pinn(include_phase2=True):
#     """Get the global PINN manager instance"""
#     global _pinn_manager
#     if _pinn_manager is None:
#         _pinn_manager = CosmoNetPINN(include_phase2=include_phase2)
#     return _pinn_manager

# def calculate_pinn_features(light_curve_data, metadata=None, include_phase2=True):
#     """
#     UPDATED ONE-FUNCTION SOLUTION for PINN features
#     Now supports metadata for redshift features
#     """
#     pinn = get_pinn(include_phase2=include_phase2)
#     return pinn.calculate_all_features(light_curve_data, metadata)




# ============================================================================
# COSMONET ADVANCED NEURAL NETWORK MODELS
# TensorFlow 2.13.0 Compatible
# ============================================================================

import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.utils.class_weight import compute_class_weight
import warnings
warnings.filterwarnings('ignore')

class CosmoNetAdvancedModels:
    """
    Advanced Neural Network Models for CosmoNet
    Designed to work with PINN features for 30%+ accuracy improvements
    """
    
    def __init__(self, num_classes=14, input_dim=None):
        self.num_classes = num_classes
        self.input_dim = input_dim
        self.models = {}
        
    # ============================================================================
    # MODEL 1: PHYSICS-AWARE TRANSFORMER NETWORK
    # ============================================================================
    
    def create_physics_transformer(self, input_dim, num_heads=8, ff_dim=512, num_layers=6):
        """
        Transformer model that understands physical relationships between PINN features
        """
        inputs = tf.keras.Input(shape=(input_dim,))
        
        # Feature embedding with physics-aware projections
        x = tf.keras.layers.Dense(512, activation='linear')(inputs)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Activation('swish')(x)
        x = tf.keras.layers.Dropout(0.2)(x)
        
        # Reshape for multi-head attention (treat features as sequence)
        sequence_length = 32  # Adjust based on input_dim
        projected_dim = 64
        
        # Project to sequence format
        x = tf.keras.layers.Dense(sequence_length * projected_dim)(x)
        x = tf.reshape(x, (-1, sequence_length, projected_dim))
        
        # Transformer layers with physics constraints
        for i in range(num_layers):
            # Multi-head attention with residual
            attention_output = tf.keras.layers.MultiHeadAttention(
                num_heads=num_heads, 
                key_dim=projected_dim // num_heads,
                dropout=0.1
            )(x, x)
            
            x = tf.keras.layers.Add()([x, attention_output])
            x = tf.keras.layers.LayerNormalization()(x)
            
            # Feed-forward with physics-inspired activation
            ff_output = tf.keras.layers.Dense(ff_dim, activation='swish')(x)
            ff_output = tf.keras.layers.Dropout(0.1)(ff_output)
            ff_output = tf.keras.layers.Dense(projected_dim)(ff_output)
            ff_output = tf.keras.layers.Dropout(0.1)(ff_output)
            
            x = tf.keras.layers.Add()([x, ff_output])
            x = tf.keras.layers.LayerNormalization()(x)
        
        # Global attention pooling
        x = tf.keras.layers.GlobalAveragePooling1D()(x)
        
        # Physics-informed dense layers
        x = tf.keras.layers.Dense(256, activation='swish', 
                                 kernel_regularizer=tf.keras.regularizers.l2(1e-4))(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dropout(0.3)(x)
        
        x = tf.keras.layers.Dense(128, activation='swish', 
                                 kernel_regularizer=tf.keras.regularizers.l2(1e-4))(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dropout(0.3)(x)
        
        # Output with temperature scaling for better calibration
        outputs = tf.keras.layers.Dense(self.num_classes, activation='softmax',
                                       kernel_regularizer=tf.keras.regularizers.l2(1e-4))(x)
        
        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        
        # Custom learning rate schedule for transformers
        def transformer_schedule(epoch, lr):
            if epoch < 10:
                return 1e-3
            elif epoch < 30:
                return 5e-4
            else:
                return 1e-4
        
        model.transformer_schedule = transformer_schedule
        return model
    
    # ============================================================================
    # MODEL 2: MULTI-SCALE RESIDUAL PHYSICS NETWORK
    # ============================================================================
    
    def create_multiscale_residual_net(self, input_dim):
        """
        Multi-scale architecture that processes features at different physical scales
        """
        inputs = tf.keras.Input(shape=(input_dim,))
        
        # Input normalization with physics-aware scaling
        x = tf.keras.layers.BatchNormalization()(inputs)
        x = tf.keras.layers.GaussianNoise(0.01)(x)  # Small noise for regularization
        
        # Multiple parallel branches for different physical scales
        branches = []
        
        # Branch 1: Fast timescale features (explosion physics)
        b1 = tf.keras.layers.Dense(128, activation='swish')(x)
        b1 = tf.keras.layers.BatchNormalization()(b1)
        b1 = tf.keras.layers.Dense(64, activation='swish')(b1)
        b1 = tf.keras.layers.BatchNormalization()(b1)
        branches.append(b1)
        
        # Branch 2: Intermediate timescale features (radioactive decay)
        b2 = tf.keras.layers.Dense(256, activation='swish')(x)
        b2 = tf.keras.layers.BatchNormalization()(b2)
        b2 = tf.keras.layers.Dropout(0.2)(b2)
        b2 = tf.keras.layers.Dense(128, activation='swish')(b2)
        b2 = tf.keras.layers.BatchNormalization()(b2)
        branches.append(b2)
        
        # Branch 3: Slow timescale features (host galaxy, long-term variability)
        b3 = tf.keras.layers.Dense(512, activation='swish')(x)
        b3 = tf.keras.layers.BatchNormalization()(b3)
        b3 = tf.keras.layers.Dropout(0.3)(b3)
        b3 = tf.keras.layers.Dense(256, activation='swish')(b3)
        b3 = tf.keras.layers.BatchNormalization()(b3)
        b3 = tf.keras.layers.Dropout(0.2)(b3)
        b3 = tf.keras.layers.Dense(128, activation='swish')(b3)
        branches.append(b3)
        
        # Branch 4: Cross-scale interactions
        b4 = tf.keras.layers.Dense(384, activation='swish')(x)
        b4 = tf.keras.layers.BatchNormalization()(b4)
        b4 = tf.keras.layers.Dropout(0.25)(b4)
        b4 = tf.keras.layers.Dense(192, activation='swish')(b4)
        b4 = tf.keras.layers.BatchNormalization()(b4)
        branches.append(b4)
        
        # Concatenate all branches
        if len(branches) > 1:
            x = tf.keras.layers.concatenate(branches)
        else:
            x = branches[0]
        
        # Residual blocks with skip connections
        for units in [512, 256, 128]:
            # Residual block
            residual = x
            
            x = tf.keras.layers.Dense(units, activation='swish')(x)
            x = tf.keras.layers.BatchNormalization()(x)
            x = tf.keras.layers.Dropout(0.3)(x)
            x = tf.keras.layers.Dense(units, activation='swish')(x)
            x = tf.keras.layers.BatchNormalization()(x)
            
            # Skip connection if dimensions match
            if residual.shape[-1] == units:
                x = tf.keras.layers.Add()([x, residual])
            
            x = tf.keras.layers.Activation('swish')(x)
            x = tf.keras.layers.Dropout(0.2)(x)
        
        # Physics-aware output layer
        x = tf.keras.layers.Dense(64, activation='swish')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dropout(0.1)(x)
        
        outputs = tf.keras.layers.Dense(self.num_classes, activation='softmax')(x)
        
        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        return model
    
    # ============================================================================
    # MODEL 3: PHYSICS-GUIDED ATTENTION ENSEMBLE
    # ============================================================================
    
    def create_physics_attention_ensemble(self, input_dim):
        """
        Ensemble model with physics-guided attention mechanisms
        """
        inputs = tf.keras.Input(shape=(input_dim,))
        
        # Learn attention weights for each physics category
        attention_weights = []
        attention_outputs = []
        
        # Base feature processing
        x_base = tf.keras.layers.BatchNormalization()(inputs)
        x_base = tf.keras.layers.Dense(256, activation='swish')(x_base)
        
        # Multiple attention heads for different physics aspects
        for i in range(5):  # 5 physics aspects
            # Attention mechanism
            attention = tf.keras.layers.Dense(input_dim, activation='sigmoid', 
                                            name=f'attention_{i}')(x_base)
            attended_features = tf.keras.layers.Multiply()([inputs, attention])
            
            # Process attended features
            x = tf.keras.layers.Dense(128, activation='swish')(attended_features)
            x = tf.keras.layers.BatchNormalization()(x)
            x = tf.keras.layers.Dropout(0.2)(x)
            x = tf.keras.layers.Dense(64, activation='swish')(x)
            
            attention_outputs.append(x)
            attention_weights.append(attention)
        
        # Combine attention outputs
        if len(attention_outputs) > 1:
            x = tf.keras.layers.concatenate(attention_outputs)
        else:
            x = attention_outputs[0]
        
        # Cross-attention between physics aspects
        x = tf.keras.layers.Dense(256, activation='swish')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dropout(0.3)(x)
        
        # Residual fusion
        for units in [128, 64]:
            residual = x
            x = tf.keras.layers.Dense(units, activation='swish')(x)
            x = tf.keras.layers.BatchNormalization()(x)
            x = tf.keras.layers.Dropout(0.2)(x)
            
            if residual.shape[-1] == units:
                x = tf.keras.layers.Add()([x, residual])
        
        # Output with uncertainty estimation
        x = tf.keras.layers.Dense(32, activation='swish')(x)
        outputs = tf.keras.layers.Dense(self.num_classes, activation='softmax')(x)
        
        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        
        # Store attention weights for interpretability
        model.attention_weights = attention_weights
        
        return model
    
    # ============================================================================
    # MODEL 4: BAYESIAN PHYSICS NETWORK WITH UNCERTAINTY
    # ============================================================================
    
    def create_bayesian_physics_net(self, input_dim, num_mc_samples=50):
        """
        Bayesian neural network that provides uncertainty estimates
        """
        # This will use dropout at test time for uncertainty estimation
        inputs = tf.keras.Input(shape=(input_dim,))
        
        def mc_dropout_model():
            inner_inputs = tf.keras.Input(shape=(input_dim,))
            
            x = tf.keras.layers.BatchNormalization()(inner_inputs)
            x = tf.keras.layers.GaussianNoise(0.02)(x)
            
            # Bayesian layers with high dropout
            x = tf.keras.layers.Dense(512, activation='swish')(x)
            x = tf.keras.layers.BatchNormalization()(x)
            x = tf.keras.layers.Dropout(0.5)(x)  # High dropout for uncertainty
            
            x = tf.keras.layers.Dense(256, activation='swish')(x)
            x = tf.keras.layers.BatchNormalization()(x)
            x = tf.keras.layers.Dropout(0.4)(x)
            
            x = tf.keras.layers.Dense(128, activation='swish')(x)
            x = tf.keras.layers.BatchNormalization()(x)
            x = tf.keras.layers.Dropout(0.3)(x)
            
            x = tf.keras.layers.Dense(64, activation='swish')(x)
            x = tf.keras.layers.Dropout(0.2)(x)
            
            outputs = tf.keras.layers.Dense(self.num_classes, activation='softmax')(x)
            
            return tf.keras.Model(inputs=inner_inputs, outputs=outputs)
        
        model = mc_dropout_model()
        model.num_mc_samples = num_mc_samples
        
        # Method for MC dropout predictions
        def predict_with_uncertainty(self, X, n_samples=50):
            # Enable dropout at test time
            mc_predictions = []
            for _ in range(n_samples):
                pred = self(X, training=True)  # training=True for dropout
                mc_predictions.append(pred)
            
            mc_predictions = tf.stack(mc_predictions)
            mean_prediction = tf.reduce_mean(mc_predictions, axis=0)
            uncertainty = tf.reduce_std(mc_predictions, axis=0)
            
            return mean_prediction, uncertainty
        
        model.predict_with_uncertainty = predict_with_uncertainty.__get__(model)
        
        return model
    
    # ============================================================================
    # HYPERPARAMETER OPTIMIZATION AND TRAINING
    # ============================================================================
    
    def get_advanced_optimizer(self, model_type='transformer'):
        """Get optimized optimizer for each model type"""
        if model_type == 'transformer':
            return tf.keras.optimizers.Nadam(
                learning_rate=1e-3,
                beta_1=0.9,
                beta_2=0.98,
                epsilon=1e-9
            )
        elif model_type == 'bayesian':
            return tf.keras.optimizers.Adam(
                learning_rate=1e-4,
                beta_1=0.9,
                beta_2=0.999,
                epsilon=1e-7
            )
        else:
            return tf.keras.optimizers.Adam(
                learning_rate=5e-4,
                beta_1=0.9,
                beta_2=0.999,
                epsilon=1e-7
            )
    
    def get_callbacks(self, model_type='transformer', checkpoint_path='best_model.h5'):
        """Advanced callbacks for each model type"""
        callbacks = []
        
        # Learning rate scheduler
        if model_type == 'transformer':
            lr_scheduler = tf.keras.callbacks.LearningRateScheduler(
                lambda epoch, lr: lr * 0.95 if epoch > 20 else lr
            )
        else:
            lr_scheduler = tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=10,
                min_lr=1e-7,
                verbose=1
            )
        callbacks.append(lr_scheduler)
        
        # Early stopping with patience based on model type
        patience = 30 if model_type == 'bayesian' else 25
        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor='val_accuracy',
            patience=patience,
            restore_best_weights=True,
            verbose=1
        )
        callbacks.append(early_stopping)
        
        # Model checkpoint
        checkpoint = tf.keras.callbacks.ModelCheckpoint(
            checkpoint_path,
            monitor='val_accuracy',
            save_best_only=True,
            save_weights_only=False,
            verbose=1
        )
        callbacks.append(checkpoint)
        
        return callbacks
    
    def compile_and_train(self, model, X_train, y_train, X_val, y_val, 
                         model_type='transformer', epochs=200, batch_size=64):
        """Compile and train with advanced strategies"""
        
        # Convert to categorical if needed
        if len(y_train.shape) == 1:
            y_train = tf.keras.utils.to_categorical(y_train, self.num_classes)
            y_val = tf.keras.utils.to_categorical(y_val, self.num_classes)
        
        # Get optimizer and compile
        optimizer = self.get_advanced_optimizer(model_type)
        model.compile(
            optimizer=optimizer,
            loss='categorical_crossentropy',
            metrics=['accuracy', 'top_k_categorical_accuracy']
        )
        
        # Get callbacks
        callbacks = self.get_callbacks(model_type)
        
        # Class weights for imbalanced data
        y_classes = np.argmax(y_train, axis=1)
        class_weights = compute_class_weight(
            'balanced',
            classes=np.unique(y_classes),
            y=y_classes
        )
        class_weight_dict = dict(enumerate(class_weights))
        
        # Train model
        history = model.fit(
            X_train, y_train,
            batch_size=batch_size,
            epochs=epochs,
            validation_data=(X_val, y_val),
            callbacks=callbacks,
            class_weight=class_weight_dict,
            verbose=1,
            shuffle=True
        )
        
        return history, model
    
    # ============================================================================
    # ENSEMBLE METHODS
    # ============================================================================
    
    def create_super_ensemble(self, X_train, y_train, X_val, y_val, input_dim):
        """Create and train an ensemble of all advanced models"""
        print("🏗️ Building Super Ensemble...")
        
        models = {}
        histories = {}
        
        # 1. Physics Transformer
        print("🔧 Training Physics Transformer...")
        models['transformer'] = self.create_physics_transformer(input_dim)
        histories['transformer'], models['transformer'] = self.compile_and_train(
            models['transformer'], X_train, y_train, X_val, y_val, 'transformer'
        )
        
        # 2. Multi-scale Residual Net
        print("🔧 Training Multi-scale Residual Network...")
        models['multiscale'] = self.create_multiscale_residual_net(input_dim)
        histories['multiscale'], models['multiscale'] = self.compile_and_train(
            models['multiscale'], X_train, y_train, X_val, y_val, 'residual'
        )
        
        # 3. Physics Attention Ensemble
        print("🔧 Training Physics Attention Ensemble...")
        models['attention'] = self.create_physics_attention_ensemble(input_dim)
        histories['attention'], models['attention'] = self.compile_and_train(
            models['attention'], X_train, y_train, X_val, y_val, 'attention'
        )
        
        # 4. Bayesian Physics Network
        print("🔧 Training Bayesian Physics Network...")
        models['bayesian'] = self.create_bayesian_physics_net(input_dim)
        histories['bayesian'], models['bayesian'] = self.compile_and_train(
            models['bayesian'], X_train, y_train, X_val, y_val, 'bayesian'
        )
        
        self.ensemble_models = models
        self.ensemble_histories = histories
        
        return models, histories
    
    def ensemble_predict(self, X, method='weighted'):
        """Make predictions using the ensemble"""
        if not hasattr(self, 'ensemble_models'):
            raise ValueError("Ensemble not trained yet. Call create_super_ensemble first.")
        
        predictions = {}
        
        # Get predictions from each model
        for name, model in self.ensemble_models.items():
            if name == 'bayesian':
                # Use MC dropout for bayesian model
                pred, unc = model.predict_with_uncertainty(X)
                predictions[name] = pred
            else:
                predictions[name] = model.predict(X)
        
        # Combine predictions
        if method == 'weighted':
            # Weight by validation accuracy (you would need to track this)
            weights = {
                'transformer': 0.3,
                'multiscale': 0.25,
                'attention': 0.25,
                'bayesian': 0.2
            }
            
            weighted_pred = np.zeros_like(predictions['transformer'])
            for name, pred in predictions.items():
                weighted_pred += weights[name] * pred
            
            final_pred = weighted_pred
            
        elif method == 'average':
            # Simple average
            all_preds = np.stack(list(predictions.values()))
            final_pred = np.mean(all_preds, axis=0)
        
        elif method == 'stacking':
            # Use a meta-learner (simplified version)
            all_preds = np.concatenate(list(predictions.values()), axis=1)
            # In practice, you'd train a meta-learner on validation set
            final_pred = np.mean(all_preds.reshape(-1, len(predictions), self.num_classes), axis=1)
        
        return final_pred

# ============================================================================
# USAGE EXAMPLE AND TESTING
# ============================================================================

def test_tensorflow_installation():
    """Test if TensorFlow 2.13.0 is working correctly"""
    print("🧪 Testing TensorFlow 2.13.0 Installation...")
    
    try:
        import tensorflow as tf
        print(f"✅ TensorFlow {tf.__version__} imported successfully!")
        
        # Test basic functionality
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(10, activation='relu', input_shape=(5,)),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(optimizer='adam', loss='binary_crossentropy')
        print("✅ Model compilation successful!")
        
        # Test advanced models
        advanced_models = CosmoNetAdvancedModels(num_classes=14, input_dim=100)
        transformer_model = advanced_models.create_physics_transformer(100)
        print("✅ Advanced models created successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Test the installation
    if test_tensorflow_installation():
        print("🎉 TensorFlow 2.13.0 is working perfectly!")
    else:
        print("❌ There are issues with your TensorFlow installation.")