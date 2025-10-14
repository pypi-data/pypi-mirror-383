# cosmonet_xai.py (Fixed version with all issues resolved)
"""
Explainable AI (XAI) Module for CosmoNet
Provides transparency and interpretability for astronomical classification
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from typing import Dict, List, Tuple, Optional, Union
import os
import json
from pathlib import Path

# XAI libraries
import shap
import lime
import lime.lime_tabular

# Fix for scikit-learn version compatibility
try:
    # Try the newer import location first
    from sklearn.inspection import PartialDependenceDisplay
    plot_partial_dependence_available = True
    use_new_pdp = True
except ImportError:
    try:
        # Fall back to older import location
        from sklearn.inspection import plot_partial_dependence
        plot_partial_dependence_available = True
        use_new_pdp = False
    except ImportError:
        # If neither is available, we'll disable this feature
        plot_partial_dependence_available = False
        use_new_pdp = False
        print("Warning: plot_partial_dependence not available in this scikit-learn version")

# Always import partial_dependence function
from sklearn.inspection import partial_dependence
from sklearn.preprocessing import LabelEncoder
from sklearn.base import BaseEstimator, ClassifierMixin
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

warnings.filterwarnings('ignore')

class LightGBMWrapper(BaseEstimator, ClassifierMixin):
    """
    Wrapper for LightGBM Booster to make it compatible with scikit-learn API
    """
    def __init__(self, booster):
        self.booster = booster
        self.classes_ = None  # Will be set during fit
        self.n_features_in_ = None  # Will be set during fit
    
    def fit(self, X, y):
        """Fit method (not actually used, just for compatibility)"""
        # Store classes and feature count for compatibility
        self.classes_ = np.unique(y)
        self.n_features_in_ = X.shape[1]
        return self
    
    def predict(self, X):
        """Predict using the underlying LightGBM model"""
        if hasattr(self.booster, 'predict'):
            return self.booster.predict(X)
        else:
            # For older LightGBM versions
            return self.booster.predict(X)
    
    def predict_proba(self, X):
        """Predict probabilities using the underlying LightGBM model"""
        if hasattr(self.booster, 'predict'):
            return self.booster.predict(X)
        else:
            # For older LightGBM versions
            return self.booster.predict(X)
    
    def feature_importances_(self):
        """Get feature importances from the underlying LightGBM model"""
        return self.booster.feature_importance(importance_type='gain')
    
    def feature_name_(self):
        """Get feature names from the underlying LightGBM model"""
        return self.booster.feature_name()

class CosmoNetXAI:
    """
    XAI module for CosmoNet classifier
    Provides multiple explanation methods for transparency
    """
    
    def __init__(self, classifier, random_state=42):
        """
        Initialize XAI module
        
        Parameters:
        -----------
        classifier : CosmoNetClassifier
            Trained CosmoNet classifier
        random_state : int
            Random seed for reproducibility
        """
        self.classifier = classifier
        self.random_state = random_state
        np.random.seed(random_state)
        
        # Create output directory
        self.output_dir = Path('xai_results')
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.shap_explainer = None
        self.lime_explainer = None
        self.feature_names = None
        self.class_names = None
        
        # Results storage
        self.explanations = {}
        
        print("🔍 Initialized CosmoNet XAI Module")
    
    def setup(self, X_train, y_train=None):
        """
        Setup XAI components with training data
        
        Parameters:
        -----------
        X_train : pd.DataFrame
            Training features
        y_train : pd.Series, optional
            Training targets
        """
        print("🔧 Setting up XAI components...")
        
        # Store feature and class names
        self.feature_names = X_train.columns.tolist()
        
        if y_train is not None:
            # Get unique classes and map to names
            unique_classes = sorted(y_train.unique())
            self.class_names = [str(cls) for cls in unique_classes]
        else:
            # Use classifier's class definitions
            if hasattr(self.classifier, 'classes'):
                self.class_names = [str(cls) for cls in self.classifier.classes]
            else:
                self.class_names = [f"Class_{i}" for i in range(len(np.unique(y_train)))]
        
        # Initialize SHAP explainer
        print("   📊 Initializing SHAP explainer...")
        try:
            # Use TreeExplainer for LightGBM models
            if hasattr(self.classifier, 'models_galactic') and self.classifier.models_galactic:
                # Use the first galactic model as representative
                self.shap_explainer = shap.TreeExplainer(self.classifier.models_galactic[0])
            elif hasattr(self.classifier, 'models_extragalactic') and self.classifier.models_extragalactic:
                # Use the first extragalactic model as representative
                self.shap_explainer = shap.TreeExplainer(self.classifier.models_extragalactic[0])
            else:
                print("   ⚠️ No trained models found, using generic explainer")
                self.shap_explainer = None
        except Exception as e:
            print(f"   ⚠️ Error initializing SHAP explainer: {e}")
            self.shap_explainer = None
        
        # Initialize LIME explainer
        print("   📊 Initializing LIME explainer...")
        try:
            # Create a wrapper for the model to use with LIME
            if hasattr(self.classifier, 'models_galactic') and self.classifier.models_galactic:
                model = self.classifier.models_galactic[0]
                wrapped_model = LightGBMWrapper(model)
                
                # Fit the wrapper with dummy data
                dummy_X = X_train.head(1)
                dummy_y = pd.Series([0])  # Dummy target
                wrapped_model.fit(dummy_X, dummy_y)
                
                self.lime_explainer = lime.lime_tabular.LimeTabularExplainer(
                    X_train.values,
                    feature_names=self.feature_names,
                    class_names=self.class_names,
                    mode='classification',
                    random_state=self.random_state
                )
        except Exception as e:
            print(f"   ⚠️ Error initializing LIME explainer: {e}")
            self.lime_explainer = None
        
        print("✅ XAI components setup complete")
    
    def explain_global(self, X_test, y_test=None, model_type='galactic'):
        """
        Generate global explanations
        
        Parameters:
        -----------
        X_test : pd.DataFrame
            Test features
        y_test : pd.Series, optional
            Test targets
        model_type : str
            'galactic' or 'extragalactic' model to use
        """
        print(f"🌍 Generating global explanations for {model_type} model...")
        
        # Get appropriate model
        if model_type == 'galactic' and hasattr(self.classifier, 'models_galactic') and self.classifier.models_galactic:
            model = self.classifier.models_galactic[0]  # Use first model
        elif model_type == 'extragalactic' and hasattr(self.classifier, 'models_extragalactic') and self.classifier.models_extragalactic:
            model = self.classifier.models_extragalactic[0]  # Use first model
        else:
            print(f"   ⚠️ No {model_type} model available")
            return
        
        # 1. Feature Importance
        print("   📊 Calculating feature importance...")
        self._plot_feature_importance(model, model_type)
        
        # 2. SHAP Summary Plot
        if self.shap_explainer is not None:
            print("   📊 Calculating SHAP values...")
            try:
                # Calculate SHAP values for a subset of data
                sample_size = min(100, len(X_test))
                X_sample = X_test.sample(sample_size, random_state=self.random_state)
                
                shap_values = self.shap_explainer.shap_values(X_sample)
                
                # Handle multi-class output
                if isinstance(shap_values, list):
                    # Multi-class case
                    for i, class_name in enumerate(self.class_names):
                        plt.figure(figsize=(10, 8))
                        shap.summary_plot(shap_values[i], X_sample, 
                                         feature_names=self.feature_names,
                                         class_names=class_name,
                                         show=False)
                        plt.title(f'SHAP Summary for {class_name}')
                        plt.savefig(self.output_dir / f'shap_summary_{model_type}_{class_name}.png', 
                                   dpi=150, bbox_inches='tight')
                        plt.close()
                else:
                    # Binary case
                    plt.figure(figsize=(10, 8))
                    shap.summary_plot(shap_values, X_sample, 
                                     feature_names=self.feature_names,
                                     show=False)
                    plt.title(f'SHAP Summary for {model_type} model')
                    plt.savefig(self.output_dir / f'shap_summary_{model_type}.png', 
                               dpi=150, bbox_inches='tight')
                    plt.close()
                
                # Store SHAP values
                self.explanations[f'{model_type}_shap_values'] = shap_values
                self.explanations[f'{model_type}_shap_sample'] = X_sample
                
                print(f"   ✅ SHAP summary plots saved")
            except Exception as e:
                print(f"   ⚠️ Error calculating SHAP values: {e}")
        
        # 3. Partial Dependence Plots
        if plot_partial_dependence_available:
            print("   📊 Calculating partial dependence...")
            self._plot_partial_dependence(model, X_test, model_type)
        else:
            print("   ⚠️ Skipping partial dependence plots (not available in this scikit-learn version)")
        
        # 4. Permutation Importance
        print("   📊 Calculating permutation importance...")
        self._plot_permutation_importance(model, X_test, y_test, model_type)
        
        print(f"✅ Global explanations for {model_type} model complete")
    
    def explain_local(self, X_test, instance_idx=0, model_type='galactic'):
        """
        Generate local explanations for a specific instance
        
        Parameters:
        -----------
        X_test : pd.DataFrame
            Test features
        instance_idx : int
            Index of the instance to explain
        model_type : str
            'galactic' or 'extragalactic' model to use
        """
        print(f"🔍 Generating local explanations for instance {instance_idx} ({model_type} model)...")
        
        # Get appropriate model
        if model_type == 'galactic' and hasattr(self.classifier, 'models_galactic') and self.classifier.models_galactic:
            model = self.classifier.models_galactic[0]  # Use first model
        elif model_type == 'extragalactic' and hasattr(self.classifier, 'models_extragalactic') and self.classifier.models_extragalactic:
            model = self.classifier.models_extragalactic[0]  # Use first model
        else:
            print(f"   ⚠️ No {model_type} model available")
            return
        
        # Get the instance to explain
        if instance_idx >= len(X_test):
            print(f"   ⚠️ Instance index {instance_idx} out of range")
            return
        
        instance = X_test.iloc[instance_idx:instance_idx+1]
        
        # 1. SHAP Force Plot
        if self.shap_explainer is not None:
            print("   📊 Generating SHAP force plot...")
            try:
                shap_values = self.shap_explainer.shap_values(instance)
                
                # Handle multi-class output
                if isinstance(shap_values, list):
                    # Multi-class case - show for each class
                    for i, class_name in enumerate(self.class_names):
                        plt.figure(figsize=(12, 3))
                        # Fix for SHAP v0.20+ - base value should be first parameter
                        shap.force_plot(self.shap_explainer.expected_value[i], 
                                       shap_values[i], 
                                       instance,
                                       feature_names=self.feature_names,
                                       matplotlib=True, show=False)
                        plt.title(f'SHAP Force Plot for {class_name}')
                        plt.savefig(self.output_dir / f'shap_force_{model_type}_{instance_idx}_{class_name}.png', 
                                   dpi=150, bbox_inches='tight')
                        plt.close()
                else:
                    # Binary case
                    plt.figure(figsize=(12, 3))
                    # Fix for SHAP v0.20+ - base value should be first parameter
                    shap.force_plot(self.shap_explainer.expected_value, 
                                   shap_values, 
                                   instance,
                                   feature_names=self.feature_names,
                                   matplotlib=True, show=False)
                    plt.title(f'SHAP Force Plot for {model_type} model')
                    plt.savefig(self.output_dir / f'shap_force_{model_type}_{instance_idx}.png', 
                               dpi=150, bbox_inches='tight')
                    plt.close()
                
                print(f"   ✅ SHAP force plot saved")
            except Exception as e:
                print(f"   ⚠️ Error generating SHAP force plot: {e}")
        
        # 2. LIME Explanation
        if self.lime_explainer is not None:
            print("   📊 Generating LIME explanation...")
            try:
                # Create a wrapper for the model to use with LIME
                wrapped_model = LightGBMWrapper(model)
                
                # Fit the wrapper with dummy data
                dummy_X = X_test.head(1)
                dummy_y = pd.Series([0])  # Dummy target
                wrapped_model.fit(dummy_X, dummy_y)
                
                # Get prediction for the instance
                pred_proba = wrapped_model.predict_proba(instance)[0]
                pred_class = np.argmax(pred_proba)
                
                # Generate LIME explanation
                exp = self.lime_explainer.explain_instance(
                    instance.values[0],
                    wrapped_model.predict_proba,
                    num_features=10,
                    top_labels=1
                )
                
                # Save LIME explanation
                plt.figure(figsize=(10, 6))
                exp.save_to_file(str(self.output_dir / f'lime_{model_type}_{instance_idx}.html'))
                
                # Also create a matplotlib version
                plt.figure(figsize=(10, 6))
                exp.as_pyplot_figure(label=pred_class)
                plt.title(f'LIME Explanation for {self.class_names[pred_class]}')
                plt.savefig(self.output_dir / f'lime_{model_type}_{instance_idx}.png', 
                           dpi=150, bbox_inches='tight')
                plt.close()
                
                print(f"   ✅ LIME explanation saved")
            except Exception as e:
                print(f"   ⚠️ Error generating LIME explanation: {e}")
        
        # 3. Feature Contribution Bar Chart
        print("   📊 Generating feature contribution chart...")
        self._plot_feature_contributions(model, instance, model_type, instance_idx)
        
        print(f"✅ Local explanations for instance {instance_idx} complete")
    
    def explain_pinn_features(self, X_test, y_test=None):
        """
        Specifically analyze PINN feature contributions
        
        Parameters:
        -----------
        X_test : pd.DataFrame
            Test features
        y_test : pd.Series, optional
            Test targets
        """
        print("🔬 Analyzing PINN feature contributions...")
        
        # Identify PINN features
        pinn_features = [feat for feat in X_test.columns if 'pinn_' in feat]
        
        if not pinn_features:
            print("   ⚠️ No PINN features found in the dataset")
            return
        
        print(f"   📊 Found {len(pinn_features)} PINN features")
        
        # Get appropriate model
        if hasattr(self.classifier, 'models_galactic') and self.classifier.models_galactic:
            model = self.classifier.models_galactic[0]  # Use first model
            model_type = 'galactic'
        elif hasattr(self.classifier, 'models_extragalactic') and self.classifier.models_extragalactic:
            model = self.classifier.models_extragalactic[0]  # Use first model
            model_type = 'extragalactic'
        else:
            print("   ⚠️ No trained model available")
            return
        
        # 1. PINN Feature Importance
        print("   📊 Calculating PINN feature importance...")
        pinn_importance = self._get_feature_importance(model, X_test)
        pinn_importance = pinn_importance[pinn_importance['feature'].isin(pinn_features)]
        
        # Plot PINN feature importance
        plt.figure(figsize=(12, 8))
        sns.barplot(data=pinn_importance.head(20), x='importance', y='feature')
        plt.title(f'Top 20 PINN Feature Importance ({model_type} model)')
        plt.tight_layout()
        plt.savefig(self.output_dir / f'pinn_feature_importance_{model_type}.png', 
                   dpi=150, bbox_inches='tight')
        plt.close()
        
        # 2. PINN Feature Correlation
        print("   📊 Analyzing PINN feature correlations...")
        pinn_data = X_test[pinn_features]
        pinn_corr = pinn_data.corr()
        
        # Plot correlation heatmap
        plt.figure(figsize=(14, 12))
        mask = np.triu(np.ones_like(pinn_corr, dtype=bool))
        sns.heatmap(pinn_corr, mask=mask, cmap='coolwarm', center=0, 
                   square=True, linewidths=.5, cbar_kws={"shrink": .5})
        plt.title('PINN Feature Correlation Matrix')
        plt.tight_layout()
        plt.savefig(self.output_dir / 'pinn_feature_correlation.png', 
                   dpi=150, bbox_inches='tight')
        plt.close()
        
        # 3. PINN Feature SHAP Values
        if self.shap_explainer is not None:
            print("   📊 Calculating PINN feature SHAP values...")
            try:
                # Calculate SHAP values for a subset of data
                sample_size = min(100, len(X_test))
                X_sample = X_test.sample(sample_size, random_state=self.random_state)
                
                shap_values = self.shap_explainer.shap_values(X_sample)
                
                # Handle multi-class output
                if isinstance(shap_values, list):
                    # Multi-class case - use the first class
                    shap_values_class = shap_values[0]
                else:
                    # Binary case
                    shap_values_class = shap_values
                
                # Get SHAP values for PINN features only
                pinn_indices = [X_sample.columns.get_loc(feat) for feat in pinn_features]
                pinn_shap_values = shap_values_class[:, pinn_indices]
                pinn_shap_data = X_sample[pinn_features]
                
                # Create SHAP summary plot for PINN features
                plt.figure(figsize=(12, 8))
                shap.summary_plot(pinn_shap_values, pinn_shap_data, 
                                 feature_names=pinn_features,
                                 show=False)
                plt.title('SHAP Summary for PINN Features')
                plt.savefig(self.output_dir / 'pinn_shap_summary.png', 
                           dpi=150, bbox_inches='tight')
                plt.close()
                
                print(f"   ✅ PINN SHAP summary plot saved")
            except Exception as e:
                print(f"   ⚠️ Error calculating PINN SHAP values: {e}")
        
        # Store results
        self.explanations['pinn_importance'] = pinn_importance
        self.explanations['pinn_correlation'] = pinn_corr
        
        print("✅ PINN feature analysis complete")
    
    def generate_counterfactuals(self, X_test, instance_idx=0, target_class=None, model_type='galactic'):
        """
        Generate counterfactual explanations
        
        Parameters:
        -----------
        X_test : pd.DataFrame
            Test features
        instance_idx : int
            Index of the instance to explain
        target_class : int, optional
            Target class for counterfactual. If None, uses the highest probability class
        model_type : str
            'galactic' or 'extragalactic' model to use
        """
        print(f"🔄 Generating counterfactual explanations for instance {instance_idx} ({model_type} model)...")
        
        # Get appropriate model
        if model_type == 'galactic' and hasattr(self.classifier, 'models_galactic') and self.classifier.models_galactic:
            model = self.classifier.models_galactic[0]  # Use first model
        elif model_type == 'extragalactic' and hasattr(self.classifier, 'models_extragalactic') and self.classifier.models_extragalactic:
            model = self.classifier.models_extragalactic[0]  # Use first model
        else:
            print(f"   ⚠️ No {model_type} model available")
            return
        
        # Get the instance to explain
        if instance_idx >= len(X_test):
            print(f"   ⚠️ Instance index {instance_idx} out of range")
            return
        
        instance = X_test.iloc[instance_idx:instance_idx+1].copy()
        
        # Get original prediction
        original_pred = model.predict(instance)[0]
        original_class = np.argmax(original_pred)
        
        # If target_class is not specified, use the class with highest probability that's not the original class
        if target_class is None:
            sorted_indices = np.argsort(original_pred)[::-1]
            for idx in sorted_indices:
                if idx != original_class:
                    target_class = idx
                    break
        
        print(f"   📊 Original class: {self.class_names[original_class]} (prob: {original_pred[original_class]:.3f})")
        print(f"   📊 Target class: {self.class_names[target_class]} (prob: {original_pred[target_class]:.3f})")
        
        # Generate counterfactual using a simple approach
        # This is a simplified version - in practice, you might use more sophisticated methods
        counterfactual = instance.copy()
        
        # Get feature importance to guide the search
        feature_importance = self._get_feature_importance(model, X_test)
        
        # Sort features by importance
        sorted_features = feature_importance.sort_values('importance', ascending=False)['feature'].tolist()
        
        # Try to find minimal changes to flip the prediction
        max_iterations = 100
        learning_rate = 0.1
        found = False
        
        for iteration in range(max_iterations):
            # Get current prediction
            current_pred = model.predict(counterfactual)[0]
            current_class = np.argmax(current_pred)
            
            # Check if we've reached the target class
            if current_class == target_class:
                found = True
                break
            
            # Get gradient of prediction w.r.t. features (approximation)
            # This is a simplified approach - in practice, you'd use actual gradients
            for feat_name in sorted_features[:10]:  # Only modify top 10 features
                # Determine direction to change the feature
                # Increase if it helps the target class, decrease otherwise
                temp_inc = counterfactual.copy()
                temp_inc[feat_name] *= (1 + learning_rate)
                inc_pred = model.predict(temp_inc)[0][target_class]
                
                temp_dec = counterfactual.copy()
                temp_dec[feat_name] *= (1 - learning_rate)
                dec_pred = model.predict(temp_dec)[0][target_class]
                
                if inc_pred > dec_pred:
                    counterfactual[feat_name] *= (1 + learning_rate)
                else:
                    counterfactual[feat_name] *= (1 - learning_rate)
        
        if found:
            print(f"   ✅ Counterfactual found after {iteration+1} iterations")
            
            # Get final prediction
            final_pred = model.predict(counterfactual)[0]
            final_class = np.argmax(final_pred)
            
            print(f"   📊 Counterfactual class: {self.class_names[final_class]} (prob: {final_pred[final_class]:.3f})")
            
            # Calculate feature changes
            changes = pd.DataFrame({
                'feature': X_test.columns,
                'original': instance.values[0],
                'counterfactual': counterfactual.values[0],
                'change': counterfactual.values[0] - instance.values[0],
                'relative_change': (counterfactual.values[0] - instance.values[0]) / (instance.values[0] + 1e-8)
            })
            
            # Sort by absolute change
            changes['abs_change'] = changes['change'].abs()
            changes = changes.sort_values('abs_change', ascending=False)
            
            # Plot top changes
            plt.figure(figsize=(12, 8))
            top_changes = changes.head(10)
            sns.barplot(data=top_changes, x='change', y='feature')
            plt.title(f'Top 10 Feature Changes for Counterfactual (Original: {self.class_names[original_class]} → {self.class_names[final_class]})')
            plt.tight_layout()
            plt.savefig(self.output_dir / f'counterfactual_{model_type}_{instance_idx}.png', 
                       dpi=150, bbox_inches='tight')
            plt.close()
            
            # Store results
            self.explanations[f'{model_type}_counterfactual_{instance_idx}'] = {
                'original_instance': instance,
                'counterfactual': counterfactual,
                'original_class': original_class,
                'target_class': target_class,
                'final_class': final_class,
                'changes': changes
            }
        else:
            print(f"   ⚠️ Counterfactual not found after {max_iterations} iterations")
    
    def _get_feature_importance(self, model, X_test):
        """
        Get feature importance from model, handling different model types
        
        Parameters:
        -----------
        model : trained model
            The trained model (could be LightGBM Booster or scikit-learn model)
        X_test : pd.DataFrame
            Test features
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with feature names and importance values
        """
        try:
            # Check if it's a LightGBM Booster
            if hasattr(model, 'feature_importance'):
                # LightGBM Booster
                importance = model.feature_importance(importance_type='gain')
                feature_names = model.feature_name()
                
                # Create DataFrame
                feature_importance = pd.DataFrame({
                    'feature': feature_names,
                    'importance': importance
                }).sort_values('importance', ascending=False)
                
                # Ensure all features from X_test are included
                missing_features = set(X_test.columns) - set(feature_names)
                if missing_features:
                    for feat in missing_features:
                        feature_importance = pd.concat([
                            feature_importance,
                            pd.DataFrame({'feature': [feat], 'importance': [0]})
                        ])
                
                return feature_importance
            
            # Check if it's a scikit-learn model
            elif hasattr(model, 'feature_importances_'):
                # Scikit-learn model
                feature_importance = pd.DataFrame({
                    'feature': X_test.columns,
                    'importance': model.feature_importances_
                }).sort_values('importance', ascending=False)
                
                return feature_importance
            
            else:
                print("   ⚠️ Model doesn't support feature importance extraction")
                # Return a DataFrame with zero importance for all features
                return pd.DataFrame({
                    'feature': X_test.columns,
                    'importance': np.zeros(len(X_test.columns))
                })
                
        except Exception as e:
            print(f"   ⚠️ Error extracting feature importance: {e}")
            # Return a DataFrame with zero importance for all features
            return pd.DataFrame({
                'feature': X_test.columns,
                'importance': np.zeros(len(X_test.columns))
            })
    
    def _plot_feature_importance(self, model, model_type):
        """Plot feature importance"""
        # Get feature importance
        feature_importance = self._get_feature_importance(model, self.classifier.train_exact[self.classifier.feature_cols_exact])
        
        # Plot top features
        plt.figure(figsize=(12, 8))
        top_features = feature_importance.head(20)
        sns.barplot(data=top_features, x='importance', y='feature')
        plt.title(f'Top 20 Feature Importance ({model_type} model)')
        plt.tight_layout()
        plt.savefig(self.output_dir / f'feature_importance_{model_type}.png', 
                   dpi=150, bbox_inches='tight')
        plt.close()
        
        # Store results
        self.explanations[f'{model_type}_feature_importance'] = feature_importance
    
    def _plot_partial_dependence(self, model, X_test, model_type):
        """Plot partial dependence for top features"""
        # Get feature importance
        feature_importance = self._get_feature_importance(model, X_test)
        
        # Get top features
        top_features = feature_importance.head(6)['feature'].tolist()
        
        # Create a scikit-learn compatible wrapper for the LightGBM model
        wrapped_model = LightGBMWrapper(model)
        
        # Fit the wrapper (required for scikit-learn compatibility)
        # We'll use dummy data since the model is already trained
        dummy_X = X_test.head(1)
        dummy_y = pd.Series([0])  # Dummy target
        wrapped_model.fit(dummy_X, dummy_y)
        
        # Plot partial dependence using the appropriate method based on scikit-learn version
        if use_new_pdp:
            # Use newer PartialDependenceDisplay
            fig, ax = plt.subplots(figsize=(15, 10))
            PartialDependenceDisplay.from_estimator(
                wrapped_model, X_test, top_features,
                ax=ax, grid_resolution=20
            )
            fig.suptitle(f'Partial Dependence of Top Features ({model_type} model)')
            plt.tight_layout()
            plt.subplots_adjust(top=0.9)
            plt.savefig(self.output_dir / f'partial_dependence_{model_type}.png', 
                       dpi=150, bbox_inches='tight')
            plt.close()
        else:
            # Use older plot_partial_dependence function
            fig, ax = plt.subplots(figsize=(15, 10))
            plot_partial_dependence(
                wrapped_model, X_test, top_features,
                ax=ax, grid_resolution=20, 
                feature_names=self.feature_names
            )
            fig.suptitle(f'Partial Dependence of Top Features ({model_type} model)')
            plt.tight_layout()
            plt.subplots_adjust(top=0.9)
            plt.savefig(self.output_dir / f'partial_dependence_{model_type}.png', 
                       dpi=150, bbox_inches='tight')
            plt.close()
    
    def _plot_permutation_importance(self, model, X_test, y_test, model_type):
        """Plot permutation importance"""
        if y_test is None:
            print("   ⚠️ No test targets provided, skipping permutation importance")
            return
        
        try:
            from sklearn.inspection import permutation_importance
            
            # Create a scikit-learn compatible wrapper for the LightGBM model
            wrapped_model = LightGBMWrapper(model)
            
            # Fit the wrapper (required for scikit-learn compatibility)
            # We'll use dummy data since the model is already trained
            dummy_X = X_test.head(1)
            dummy_y = pd.Series([0])  # Dummy target
            wrapped_model.fit(dummy_X, dummy_y)
            
            # Convert y_test to integer labels if needed
            if hasattr(y_test, 'values'):
                y_test_values = y_test.values
            else:
                y_test_values = y_test
                
            # Ensure y_test is 1D array
            if len(y_test_values.shape) > 1:
                y_test_values = y_test_values.ravel()
            
            # Calculate permutation importance
            result = permutation_importance(
                wrapped_model, X_test, y_test_values, n_repeats=5, 
                random_state=self.random_state, n_jobs=-1
            )
            
            # Create DataFrame
            perm_importance = pd.DataFrame({
                'feature': X_test.columns,
                'importance': result.importances_mean,
                'std': result.importances_std
            }).sort_values('importance', ascending=False)
            
            # Plot top features
            plt.figure(figsize=(12, 8))
            top_features = perm_importance.head(20)
            sns.barplot(data=top_features, x='importance', y='feature')
            plt.title(f'Top 20 Permutation Importance ({model_type} model)')
            plt.tight_layout()
            plt.savefig(self.output_dir / f'permutation_importance_{model_type}.png', 
                       dpi=150, bbox_inches='tight')
            plt.close()
            
            # Store results
            self.explanations[f'{model_type}_permutation_importance'] = perm_importance
            
        except Exception as e:
            print(f"   ⚠️ Error calculating permutation importance: {e}")
    
    def _plot_feature_contributions(self, model, instance, model_type, instance_idx):
        """Plot feature contributions for a specific instance"""
        try:
            # Get prediction using the model's predict method
            pred = model.predict(instance)
            
            # Handle different output formats
            if isinstance(pred, np.ndarray) and len(pred.shape) == 2:
                # Multi-dimensional output (probabilities)
                pred_proba = pred[0]
                pred_class = np.argmax(pred_proba)
            else:
                # Single-dimensional output
                pred_proba = pred
                pred_class = np.argmax(pred_proba) if isinstance(pred_proba, np.ndarray) else pred_proba
            
            # Get base value (average prediction)
            try:
                # Try to get predictions for training data
                train_preds = model.predict(self.classifier.train_exact[self.classifier.feature_cols_exact].head(100))
                if isinstance(train_preds, np.ndarray) and len(train_preds.shape) == 2:
                    base_value = np.mean(train_preds, axis=0)[pred_class]
                else:
                    base_value = np.mean(train_preds)
            except:
                # Fallback to 0.5 if we can't calculate base value
                base_value = 0.5
            
            # Calculate feature contributions (simplified SHAP-like approach)
            contributions = []
            for feat_name in self.feature_names:
                # Create a copy of the instance with this feature set to its mean value
                temp_instance = instance.copy()
                temp_instance[feat_name] = self.classifier.train_exact[feat_name].mean()
                
                # Calculate the change in prediction
                temp_pred = model.predict(temp_instance)
                
                # Handle different output formats
                if isinstance(temp_pred, np.ndarray) and len(temp_pred.shape) == 2:
                    temp_pred_value = temp_pred[0][pred_class]
                else:
                    temp_pred_value = temp_pred[pred_class] if isinstance(temp_pred, np.ndarray) else temp_pred
                
                if isinstance(pred_proba, np.ndarray):
                    pred_value = pred_proba[pred_class]
                else:
                    pred_value = pred_proba
                
                contribution = pred_value - temp_pred_value
                contributions.append((feat_name, contribution))
            
            # Sort by absolute contribution
            contributions.sort(key=lambda x: abs(x[1]), reverse=True)
            
            # Create DataFrame
            contrib_df = pd.DataFrame(contributions, columns=['feature', 'contribution'])
            
            # Plot top contributions
            plt.figure(figsize=(12, 8))
            top_contrib = contrib_df.head(15)
            colors = ['red' if c < 0 else 'green' for c in top_contrib['contribution']]
            sns.barplot(data=top_contrib, x='contribution', y='feature', palette=colors)
            plt.title(f'Top 15 Feature Contributions for Instance {instance_idx} ({self.class_names[pred_class]})')
            plt.axvline(x=0, color='black', linestyle='--')
            plt.tight_layout()
            plt.savefig(self.output_dir / f'feature_contributions_{model_type}_{instance_idx}.png', 
                       dpi=150, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            print(f"   ⚠️ Error generating feature contributions: {e}")
    
    def generate_report(self):
        """Generate a comprehensive XAI report"""
        print("📄 Generating comprehensive XAI report...")
        
        # Create report structure
        report = {
            'summary': {
                'model_type': 'CosmoNet with PINN features',
                'feature_count': len(self.feature_names) if self.feature_names else 0,
                'class_count': len(self.class_names) if self.class_names else 0,
                'explanation_methods': ['SHAP', 'LIME', 'Feature Importance', 'Partial Dependence', 'Counterfactuals']
            },
            'global_explanations': {},
            'local_explanations': {},
            'pinn_analysis': {},
            'insights': []
        }
        
        # Add global explanations
        for key in self.explanations:
            if 'importance' in key and not 'counterfactual' in key:
                model_type = key.split('_')[0]
                if model_type in ['galactic', 'extragalactic']:
                    if f'{model_type}_explanations' not in report['global_explanations']:
                        report['global_explanations'][model_type] = {}
                    
                    # Convert DataFrame to dict for JSON serialization
                    if hasattr(self.explanations[key], 'to_dict'):
                        report['global_explanations'][model_type][key] = self.explanations[key].head(10).to_dict()
                    else:
                        report['global_explanations'][model_type][key] = str(self.explanations[key])
        
        # Add PINN analysis
        if 'pinn_importance' in self.explanations:
            report['pinn_analysis']['importance'] = self.explanations['pinn_importance'].head(10).to_dict()
            
            # Add insights about PINN features
            top_pinn = self.explanations['pinn_importance'].iloc[0]
            report['insights'].append(
                f"The most important PINN feature is '{top_pinn['feature']}' with importance {top_pinn['importance']:.3f}"
            )
        
        # Save report
        with open(self.output_dir / 'xai_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Create a summary visualization
        self._create_summary_visualization()
        
        print(f"✅ XAI report saved to {self.output_dir}")
        return report
    
    def _create_summary_visualization(self):
        """Create a summary visualization of XAI results"""
        # Create a multi-panel figure
        fig = plt.figure(figsize=(20, 15))
        
        # Panel 1: Feature Importance Comparison
        if 'galactic_feature_importance' in self.explanations and 'extragalactic_feature_importance' in self.explanations:
            ax1 = plt.subplot(2, 3, 1)
            
            galactic_importance = self.explanations['galactic_feature_importance'].head(10)
            extragalactic_importance = self.explanations['extragalactic_feature_importance'].head(10)
            
            # Get common top features
            common_features = set(galactic_importance['feature']).intersection(set(extragalactic_importance['feature']))
            
            if common_features:
                # Create comparison DataFrame
                comparison = pd.DataFrame({
                    'feature': list(common_features),
                    'galactic': [galactic_importance[galactic_importance['feature'] == f]['importance'].values[0] for f in common_features],
                    'extragalactic': [extragalactic_importance[extragalactic_importance['feature'] == f]['importance'].values[0] for f in common_features]
                })
                
                # Plot comparison
                comparison = comparison.sort_values('galactic', ascending=False)
                x = np.arange(len(comparison))
                width = 0.35
                
                ax1.bar(x - width/2, comparison['galactic'], width, label='Galactic')
                ax1.bar(x + width/2, comparison['extragalactic'], width, label='Extragalactic')
                ax1.set_xlabel('Features')
                ax1.set_ylabel('Importance')
                ax1.set_title('Feature Importance Comparison')
                ax1.set_xticks(x)
                ax1.set_xticklabels(comparison['feature'], rotation=45, ha='right')
                ax1.legend()
            else:
                ax1.text(0.5, 0.5, 'No common top features', ha='center', va='center', transform=ax1.transAxes)
                ax1.set_title('Feature Importance Comparison')
        
        # Panel 2: PINN Feature Importance
        if 'pinn_importance' in self.explanations:
            ax2 = plt.subplot(2, 3, 2)
            
            pinn_importance = self.explanations['pinn_importance'].head(10)
            ax2.barh(pinn_importance['feature'], pinn_importance['importance'])
            ax2.set_xlabel('Importance')
            ax2.set_title('Top 10 PINN Features')
            ax2.set_yticklabels(pinn_importance['feature'], fontsize=8)
        
        # Panel 3: PINN Feature Correlation
        if 'pinn_correlation' in self.explanations:
            ax3 = plt.subplot(2, 3, 3)
            
            pinn_corr = self.explanations['pinn_correlation']
            
            # Get top correlated features
            corr_matrix = pinn_corr.abs()
            top_corr_features = corr_matrix.sum().sort_values(ascending=False).head(10).index
            top_corr_matrix = pinn_corr.loc[top_corr_features, top_corr_features]
            
            im = ax3.imshow(top_corr_matrix, cmap='coolwarm', aspect='auto')
            ax3.set_xticks(np.arange(len(top_corr_features)))
            ax3.set_yticks(np.arange(len(top_corr_features)))
            ax3.set_xticklabels(top_corr_features, rotation=45, ha='right')
            ax3.set_yticklabels(top_corr_features)
            ax3.set_title('PINN Feature Correlation')
            
            # Add colorbar
            plt.colorbar(im, ax=ax3)
        
        # Panel 4: Model Performance Comparison
        ax4 = plt.subplot(2, 3, 4)
        
        # This would be populated with actual performance metrics
        # For now, we'll create a placeholder
        models = ['Galactic', 'Extragalactic']
        accuracy = [0.85, 0.82]  # Placeholder values
        log_loss = [0.45, 0.48]  # Placeholder values
        
        ax4_twin = ax4.twinx()
        ax4.bar(models, accuracy, color='blue', alpha=0.7, width=0.4, label='Accuracy')
        ax4_twin.bar(models, log_loss, color='red', alpha=0.7, width=0.4, label='Log Loss')
        ax4.set_ylabel('Accuracy')
        ax4_twin.set_ylabel('Log Loss')
        ax4.set_title('Model Performance')
        ax4.legend(loc='upper left')
        ax4_twin.legend(loc='upper right')
        
        # Panel 5: Class Distribution
        ax5 = plt.subplot(2, 3, 5)
        
        # This would be populated with actual class distribution
        # For now, we'll create a placeholder
        classes = ['Class 6', 'Class 15', 'Class 16', 'Class 42', 'Class 52', 'Class 53', 'Class 62', 'Class 64']
        counts = [1000, 800, 900, 600, 400, 300, 200, 100]  # Placeholder values
        
        ax5.bar(classes, counts)
        ax5.set_xlabel('Class')
        ax5.set_ylabel('Count')
        ax5.set_title('Class Distribution')
        ax5.tick_params(axis='x', rotation=45)
        
        # Panel 6: XAI Methods Summary
        ax6 = plt.subplot(2, 3, 6)
        ax6.axis('off')
        
        methods_text = """
        XAI Methods Used:
        
        1. SHAP (SHapley Additive exPlanations)
           - Global feature importance
           - Local instance explanations
           - Feature contribution analysis
        
        2. LIME (Local Interpretable Model-agnostic Explanations)
           - Local instance explanations
           - Feature contribution visualization
        
        3. Feature Importance
           - Model-based importance
           - Permutation importance
        
        4. Partial Dependence
           - Feature effect visualization
        
        5. Counterfactual Explanations
           - Minimal changes to alter predictions
        """
        
        ax6.text(0.05, 0.95, methods_text, transform=ax6.transAxes, 
                fontsize=10, verticalalignment='top', fontfamily='monospace')
        ax6.set_title('XAI Methods Summary')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'xai_summary.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        print("   ✅ Summary visualization saved")

# Integration with CosmoNet
def integrate_xai_with_cosmonet(classifier, X_train, y_train, X_test, y_test=None):
    """
    Integrate XAI with CosmoNet classifier
    
    Parameters:
    -----------
    classifier : CosmoNetClassifier
        Trained CosmoNet classifier
    X_train : pd.DataFrame
        Training features
    y_train : pd.Series
        Training targets
    X_test : pd.DataFrame
        Test features
    y_test : pd.Series, optional
        Test targets
    
    Returns:
    --------
    xai : CosmoNetXAI
        Initialized XAI module with explanations
    """
    # Initialize XAI module
    xai = CosmoNetXAI(classifier)
    
    # Setup XAI components
    xai.setup(X_train, y_train)
    
    # Generate global explanations
    xai.explain_global(X_test, y_test, model_type='galactic')
    xai.explain_global(X_test, y_test, model_type='extragalactic')
    
    # Generate local explanations for a few instances
    for i in range(min(3, len(X_test))):
        xai.explain_local(X_test, i, model_type='galactic')
        xai.explain_local(X_test, i, model_type='extragalactic')
    
    # Analyze PINN features
    xai.explain_pinn_features(X_test, y_test)
    
    # Generate counterfactuals
    for i in range(min(3, len(X_test))):
        xai.generate_counterfactuals(X_test, i, model_type='galactic')
        xai.generate_counterfactuals(X_test, i, model_type='extragalactic')
    
    # Generate report
    report = xai.generate_report()
    
    return xai, report