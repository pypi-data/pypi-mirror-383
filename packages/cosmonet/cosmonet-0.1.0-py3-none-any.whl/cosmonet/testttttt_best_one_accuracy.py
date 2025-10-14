#!/usr/bin/env python3
"""
Complete CosmoNet PINN Accuracy Checker
Imports and uses ALL existing PINN modules for detailed evaluation
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from typing import Dict, List, Optional, Tuple
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import (accuracy_score, log_loss, classification_report, 
                           confusion_matrix, precision_recall_fscore_support,
                           roc_auc_score, roc_curve)
from sklearn.preprocessing import label_binarize
import lightgbm as lgb
import gc
import os

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8')

# Import your existing modules
try:
    from cosmonet_classifier import CosmoNetClassifier
    from cosmonet_pinn import CosmoNetPINN
    print("✅ Successfully imported CosmoNet modules")
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("Make sure cosmonet_classifier.py and cosmonet_pinn.py are in the same directory")
    exit(1)

# ============================================================================
# COMPLETE ACCURACY CHECKER
# ============================================================================

class CosmoNetCompleteAccuracyChecker:
    """Complete accuracy checker using ALL existing PINN modules"""
    
    def __init__(self, random_state=42, n_folds=5):
        self.random_state = random_state
        np.random.seed(random_state)
        self.n_folds = n_folds
        
        # Initialize components
        self.classifier = CosmoNetClassifier(random_state=random_state)
        self.pinn = CosmoNetPINN(
            include_phase2=True,
            include_phase3=True, 
            include_tier2=True,
            include_tier3=True
        )
        
        # Results storage
        self.results = {}
        self.feature_importance = None
        self.pinn_feature_importance = None
        
        # Create output directory
        os.makedirs('accuracy_report', exist_ok=True)
        
        print("🚀 Initialized Complete CosmoNet Accuracy Checker")
        print(f"   PINN Modules: {len(self.pinn.active_modules)} active")
        print(f"   Cross-validation: {n_folds} folds")
    
    def load_data(self, meta_path: str, lc_path: str):
        """Load training data"""
        print("\n📁 Loading data...")
        
        try:
            self.classifier.load_data(meta_path, lc_path)
            print(f"✅ Loaded {self.classifier.train_meta.shape[0]:,} objects")
            print(f"✅ Loaded {self.classifier.train_lc.shape[0]:,} observations")
            return True
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def run_complete_analysis(self, test_size=0.2):
        """Run complete analysis with all PINN features"""
        print("\n" + "="*60)
        print("🎯 RUNNING COMPLETE COSMONET ANALYSIS")
        print("="*60)
        
        # Step 1: Explore data
        print("\n📊 Step 1: Data Exploration")
        self.classifier.explore_data()
        
        # Step 2: Define classes
        print("\n🏷️ Step 2: Class Definitions")
        self.classifier.define_classes()
        
        # Step 3: Calculate ALL features (including PINN)
        print("\n🔧 Step 3: Feature Engineering with ALL PINN")
        self.classifier.engineer_features()
        
        # Step 4: Detailed feature analysis
        print("\n🔬 Step 4: PINN Feature Analysis")
        self._analyze_pinn_features()
        
        # Step 5: Train models with cross-validation
        print("\n🚀 Step 5: Model Training with Cross-Validation")
        self._train_with_cv()
        
        # Step 6: Hold-out test evaluation
        print("\n📈 Step 6: Hold-out Test Evaluation")
        self._holdout_evaluation(test_size)
        
        # Step 7: Comprehensive analysis
        print("\n📊 Step 7: Comprehensive Analysis")
        self._comprehensive_analysis()
        
        # Step 8: Generate report
        print("\n📄 Step 8: Generating Report")
        self._generate_report()
        
        return self.results
    
    def _analyze_pinn_features(self):
        """Analyze PINN features in detail"""
        print("   🔍 Analyzing PINN feature breakdown...")
        
        # Get feature breakdown
        feature_breakdown = self.pinn.get_feature_breakdown()
        
        print(f"\n   📋 PINN MODULES ACTIVE ({len(feature_breakdown)}):")
        total_features = 0
        for module_name, info in feature_breakdown.items():
            print(f"      • {module_name}: {info['feature_count']} features")
            print(f"        {info['description']}")
            total_features += info['feature_count']
        
        print(f"\n   🎯 Total PINN Features: {total_features}")
        
        # Get all feature names
        all_features = self.pinn.list_all_features()
        pinn_feature_names = list(all_features.keys())
        
        # Check which PINN features are in the classifier
        classifier_features = self.classifier.feature_cols_exact
        active_pinn_features = [f for f in pinn_feature_names if f in classifier_features]
        
        print(f"   ✅ Active PINN Features in Classifier: {len(active_pinn_features)}")
        
        # Store for later
        self.active_pinn_features = active_pinn_features
        self.feature_breakdown = feature_breakdown
    
    def _train_with_cv(self):
        """Train models with stratified cross-validation"""
        print(f"   🔄 Training with {self.n_folds}-fold cross-validation...")
        
        # Prepare data
        data = self.classifier.train_exact.copy()
        X = data[self.classifier.feature_cols_exact]
        y = data['target_mapped']
        
        # Initialize CV
        skf = StratifiedKFold(n_splits=self.n_folds, shuffle=True, random_state=self.random_state)
        
        cv_scores = []
        cv_models = []
        fold_results = []
        
        for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
            print(f"      Fold {fold + 1}/{self.n_folds}...")
            
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            
            # Train model
            model = lgb.LGBMClassifier(
                objective='multiclass',
                num_class=len(self.classifier.classes),
                random_state=self.random_state,
                n_estimators=200,
                learning_rate=0.05,
                num_leaves=31,
                feature_fraction=0.9,
                bagging_fraction=0.8,
                bagging_freq=5,
                verbose=-1
            )
            
            model.fit(X_train, y_train,
                     eval_set=[(X_val, y_val)],
                     eval_metric='multi_logloss',
                     callbacks=[lgb.early_stopping(50), lgb.log_evaluation(0)])
            
            # Predict
            y_pred_proba = model.predict_proba(X_val)
            y_pred = np.argmax(y_pred_proba, axis=1)
            
            # Calculate metrics
            accuracy = accuracy_score(y_val, y_pred)
            logloss = log_loss(y_val, y_pred_proba)
            
            cv_scores.append({
                'fold': fold + 1,
                'accuracy': accuracy,
                'log_loss': logloss,
                'n_train': len(X_train),
                'n_val': len(X_val)
            })
            
            cv_models.append(model)
            
            # Per-class metrics
            precision, recall, f1, _ = precision_recall_fscore_support(
                y_val, y_pred, average=None, zero_division=0
            )
            
            fold_results.append({
                'fold': fold + 1,
                'precision': precision,
                'recall': recall,
                'f1': f1
            })
            
            print(f"         Accuracy: {accuracy:.4f}, Log Loss: {logloss:.4f}")
        
        # Aggregate CV results
        cv_df = pd.DataFrame(cv_scores)
        
        self.results['cross_validation'] = {
            'scores': cv_df,
            'mean_accuracy': cv_df['accuracy'].mean(),
            'std_accuracy': cv_df['accuracy'].std(),
            'mean_log_loss': cv_df['log_loss'].mean(),
            'std_log_loss': cv_df['log_loss'].std(),
            'models': cv_models,
            'fold_results': fold_results
        }
        
        print(f"\n   📊 Cross-Validation Results:")
        print(f"      Accuracy: {cv_df['accuracy'].mean():.4f} ± {cv_df['accuracy'].std():.4f}")
        print(f"      Log Loss: {cv_df['log_loss'].mean():.4f} ± {cv_df['log_loss'].std():.4f}")
        
        # Store best model
        best_idx = cv_df['log_loss'].idxmin()
        self.best_cv_model = cv_models[best_idx]
        print(f"      Best model: Fold {best_idx + 1} (Log Loss: {cv_df.loc[best_idx, 'log_loss']:.4f})")
    
    def _holdout_evaluation(self, test_size=0.2):
        """Evaluate on hold-out test set"""
        print(f"   🎯 Hold-out Evaluation (test_size={test_size})...")
        
        # Prepare data
        data = self.classifier.train_exact.copy()
        X = data[self.classifier.feature_cols_exact]
        y = data['target_mapped']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state,
            stratify=y
        )
        
        # Train final model
        final_model = lgb.LGBMClassifier(
            objective='multiclass',
            num_class=len(self.classifier.classes),
            random_state=self.random_state,
            n_estimators=300,
            learning_rate=0.05,
            num_leaves=31,
            feature_fraction=0.9,
            bagging_fraction=0.8,
            bagging_freq=5,
            verbose=-1
        )
        
        final_model.fit(X_train, y_train,
                       eval_set=[(X_test, y_test)],
                       eval_metric='multi_logloss',
                       callbacks=[lgb.early_stopping(50), lgb.log_evaluation(0)])
        
        # Predictions
        y_pred_proba = final_model.predict_proba(X_test)
        y_pred = np.argmax(y_pred_proba, axis=1)
        
        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        logloss = log_loss(y_test, y_pred_proba)
        
        # Detailed classification report
        class_names = [str(c) for c in self.classifier.classes]
        report = classification_report(y_test, y_pred, 
                                     target_names=class_names,
                                     output_dict=True,
                                     zero_division=0)
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': final_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # PINN feature importance
        pinn_importance = feature_importance[
            feature_importance['feature'].str.contains('pinn_')
        ].copy()
        
        self.results['holdout'] = {
            'accuracy': accuracy,
            'log_loss': logloss,
            'classification_report': report,
            'confusion_matrix': cm,
            'feature_importance': feature_importance,
            'pinn_importance': pinn_importance,
            'model': final_model,
            'y_true': y_test,
            'y_pred': y_pred,
            'y_pred_proba': y_pred_proba,
            'class_names': class_names
        }
        
        self.feature_importance = feature_importance
        self.pinn_feature_importance = pinn_importance
        
        print(f"      Hold-out Accuracy: {accuracy:.4f}")
        print(f"      Hold-out Log Loss: {logloss:.4f}")
        print(f"      Top PINN Feature: {pinn_importance.iloc[0]['feature'] if len(pinn_importance) > 0 else 'None'}")
    
    def _comprehensive_analysis(self):
        """Perform comprehensive analysis"""
        print("   📊 Performing comprehensive analysis...")
        
        # 1. Class-wise performance
        self._analyze_class_performance()
        
        # 2. PINN vs Traditional features
        self._compare_pinn_vs_traditional()
        
        # 3. Feature correlation analysis
        self._feature_correlation_analysis()
        
        # 4. Error analysis
        self._error_analysis()
        
        # 5. Reliability analysis
        self._reliability_analysis()
    
    def _analyze_class_performance(self):
        """Analyze performance per class"""
        print("      📈 Class-wise performance analysis...")
        
        holdout = self.results['holdout']
        report = holdout['classification_report']
        
        # Extract per-class metrics
        class_metrics = []
        for class_name in holdout['class_names']:
            if class_name in report:
                metrics = report[class_name]
                class_metrics.append({
                    'class': class_name,
                    'precision': metrics['precision'],
                    'recall': metrics['recall'],
                    'f1-score': metrics['f1-score'],
                    'support': metrics['support']
                })
        
        class_df = pd.DataFrame(class_metrics)
        
        # Plot class performance
        plt.figure(figsize=(12, 6))
        
        plt.subplot(1, 2, 1)
        sns.barplot(data=class_df, x='class', y='f1-score')
        plt.title('F1-Score by Class')
        plt.xticks(rotation=45)
        
        plt.subplot(1, 2, 2)
        sns.barplot(data=class_df, x='class', y='support')
        plt.title('Support by Class')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig('accuracy_report/class_performance.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        self.results['class_performance'] = class_df
        
        print(f"         Best performing class: {class_df.loc[class_df['f1-score'].idxmax(), 'class']}")
        print(f"         Worst performing class: {class_df.loc[class_df['f1-score'].idxmin(), 'class']}")
    
    def _compare_pinn_vs_traditional(self):
        """Compare PINN vs Traditional feature importance"""
        print("      🔬 PINN vs Traditional feature comparison...")
        
        all_importance = self.feature_importance
        pinn_importance = self.pinn_feature_importance
        traditional_importance = all_importance[
            ~all_importance['feature'].str.contains('pinn_')
        ].copy()
        
        # Summary statistics
        pinn_summary = {
            'count': len(pinn_importance),
            'total_importance': pinn_importance['importance'].sum(),
            'mean_importance': pinn_importance['importance'].mean(),
            'max_importance': pinn_importance['importance'].max()
        }
        
        traditional_summary = {
            'count': len(traditional_importance),
            'total_importance': traditional_importance['importance'].sum(),
            'mean_importance': traditional_importance['importance'].mean(),
            'max_importance': traditional_importance['importance'].max()
        }
        
        # Plot comparison
        plt.figure(figsize=(15, 5))
        
        plt.subplot(1, 3, 1)
        categories = ['PINN', 'Traditional']
        counts = [pinn_summary['count'], traditional_summary['count']]
        plt.bar(categories, counts, color=['#2E86AB', '#A23B72'])
        plt.title('Feature Count Comparison')
        plt.ylabel('Number of Features')
        
        plt.subplot(1, 3, 2)
        total_importance = [pinn_summary['total_importance'], traditional_summary['total_importance']]
        plt.bar(categories, total_importance, color=['#2E86AB', '#A23B72'])
        plt.title('Total Importance Comparison')
        plt.ylabel('Total Importance')
        
        plt.subplot(1, 3, 3)
        mean_importance = [pinn_summary['mean_importance'], traditional_summary['mean_importance']]
        plt.bar(categories, mean_importance, color=['#2E86AB', '#A23B72'])
        plt.title('Mean Importance Comparison')
        plt.ylabel('Mean Importance')
        
        plt.tight_layout()
        plt.savefig('accuracy_report/pinn_vs_traditional.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        self.results['pinn_vs_traditional'] = {
            'pinn_summary': pinn_summary,
            'traditional_summary': traditional_summary,
            'pinn_importance': pinn_importance,
            'traditional_importance': traditional_importance
        }
        
        print(f"         PINN Features: {pinn_summary['count']} features, {pinn_summary['total_importance']:.1f} total importance")
        print(f"         Traditional: {traditional_summary['count']} features, {traditional_summary['total_importance']:.1f} total importance")
    
    def _feature_correlation_analysis(self):
        """Analyze feature correlations"""
        print("      📊 Feature correlation analysis...")
        
        # Get top features for correlation analysis
        top_features = self.feature_importance.head(20)['feature'].tolist()
        
        # Prepare data
        data = self.classifier.train_exact.copy()
        correlation_matrix = data[top_features].corr()
        
        # Plot heatmap
        plt.figure(figsize=(12, 10))
        sns.heatmap(correlation_matrix, annot=False, cmap='coolwarm', center=0)
        plt.title('Top 20 Features Correlation Matrix')
        plt.tight_layout()
        plt.savefig('accuracy_report/feature_correlation.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        # Find highly correlated pairs
        high_corr_pairs = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_val = correlation_matrix.iloc[i, j]
                if abs(corr_val) > 0.8:
                    high_corr_pairs.append({
                        'feature1': correlation_matrix.columns[i],
                        'feature2': correlation_matrix.columns[j],
                        'correlation': corr_val
                    })
        
        self.results['correlation_analysis'] = {
            'correlation_matrix': correlation_matrix,
            'high_corr_pairs': high_corr_pairs
        }
        
        print(f"         Found {len(high_corr_pairs)} highly correlated feature pairs (|r| > 0.8)")
    
    def _error_analysis(self):
        """Analyze prediction errors"""
        print("      ❌ Error analysis...")
        
        holdout = self.results['holdout']
        y_true = holdout['y_true']
        y_pred = holdout['y_pred']
        y_pred_proba = holdout['y_pred_proba']
        
        # Find misclassified samples
        misclassified = y_true != y_pred
        misclassified_indices = np.where(misclassified)[0]
        
        # Analyze confidence of wrong predictions
        wrong_confidences = np.max(y_pred_proba[misclassified], axis=1)
        right_confidences = np.max(y_pred_proba[~misclassified], axis=1)
        
        # Plot confidence distributions
        plt.figure(figsize=(10, 4))
        
        plt.subplot(1, 2, 1)
        plt.hist(wrong_confidences, bins=20, alpha=0.7, label='Wrong', color='red')
        plt.hist(right_confidences, bins=20, alpha=0.7, label='Correct', color='green')
        plt.xlabel('Prediction Confidence')
        plt.ylabel('Count')
        plt.title('Confidence Distribution')
        plt.legend()
        
        plt.subplot(1, 2, 2)
        class_errors = {}
        for true_class in np.unique(y_true):
            class_mask = y_true == true_class
            class_misclassified = misclassified & class_mask
            error_rate = np.sum(class_misclassified) / np.sum(class_mask)
            class_errors[true_class] = error_rate
        
        plt.bar(class_errors.keys(), class_errors.values())
        plt.xlabel('True Class')
        plt.ylabel('Error Rate')
        plt.title('Error Rate by Class')
        
        plt.tight_layout()
        plt.savefig('accuracy_report/error_analysis.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        self.results['error_analysis'] = {
            'misclassified_count': len(misclassified_indices),
            'misclassified_rate': len(misclassified_indices) / len(y_true),
            'mean_wrong_confidence': np.mean(wrong_confidences),
            'mean_right_confidence': np.mean(right_confidences),
            'class_errors': class_errors
        }
        
        print(f"         Misclassified: {len(misclassified_indices)}/{len(y_true)} ({len(misclassified_indices)/len(y_true):.2%})")
        print(f"         Mean confidence (wrong): {np.mean(wrong_confidences):.3f}")
        print(f"         Mean confidence (right): {np.mean(right_confidences):.3f}")
    
    def _reliability_analysis(self):
        """Analyze prediction reliability/calibration"""
        print("      🎯 Reliability analysis...")
        
        holdout = self.results['holdout']
        y_true = holdout['y_true']
        y_pred_proba = holdout['y_pred_proba']
        
        # Calculate Expected Calibration Error (ECE)
        n_bins = 10
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        bin_lowers = bin_boundaries[:-1]
        bin_uppers = bin_boundaries[1:]
        
        ece = 0
        for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
            # Find samples in this bin
            in_bin = (np.max(y_pred_proba, axis=1) > bin_lower) & (np.max(y_pred_proba, axis=1) <= bin_upper)
            
            if np.sum(in_bin) > 0:
                accuracy_in_bin = np.mean(y_true[in_bin] == np.argmax(y_pred_proba[in_bin], axis=1))
                avg_confidence_in_bin = np.mean(np.max(y_pred_proba[in_bin], axis=1))
                
                ece += np.abs(accuracy_in_bin - avg_confidence_in_bin) * np.sum(in_bin) / len(y_true)
        
        # Plot reliability diagram
        plt.figure(figsize=(8, 6))
        
        # Perfect calibration line
        plt.plot([0, 1], [0, 1], 'k--', label='Perfect Calibration')
        
        # Actual calibration
        confidences = np.max(y_pred_proba, axis=1)
        accuracies = (y_true == np.argmax(y_pred_proba, axis=1)).astype(float)
        
        # Bin the data
        bin_indices = np.digitize(confidences, bin_boundaries) - 1
        bin_accuracies = []
        bin_confidences = []
        
        for i in range(n_bins):
            mask = bin_indices == i
            if np.sum(mask) > 0:
                bin_accuracies.append(np.mean(accuracies[mask]))
                bin_confidences.append(np.mean(confidences[mask]))
            else:
                bin_accuracies.append(0)
                bin_confidences.append((bin_lowers[i] + bin_uppers[i]) / 2)
        
        plt.plot(bin_confidences, bin_accuracies, 'bo-', label='Model')
        plt.xlabel('Confidence')
        plt.ylabel('Accuracy')
        plt.title('Reliability Diagram')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('accuracy_report/reliability_diagram.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        self.results['reliability_analysis'] = {
            'expected_calibration_error': ece,
            'bin_accuracies': bin_accuracies,
            'bin_confidences': bin_confidences
        }
        
        print(f"         Expected Calibration Error: {ece:.4f}")
    
    def _generate_report(self):
        """Generate comprehensive report"""
        print("   📄 Generating comprehensive report...")
        
        # Create summary
        summary = {
            'dataset_info': {
                'n_objects': len(self.classifier.train_meta),
                'n_observations': len(self.classifier.train_lc),
                'n_classes': len(self.classifier.classes),
                'classes': self.classifier.classes.tolist()
            },
            'feature_info': {
                'total_features': len(self.classifier.feature_cols_exact),
                'pinn_features': len(self.active_pinn_features),
                'traditional_features': len(self.classifier.feature_cols_exact) - len(self.active_pinn_features)
            },
            'performance': {
                'cv_accuracy_mean': self.results['cross_validation']['mean_accuracy'],
                'cv_accuracy_std': self.results['cross_validation']['std_accuracy'],
                'cv_log_loss_mean': self.results['cross_validation']['mean_log_loss'],
                'cv_log_loss_std': self.results['cross_validation']['std_log_loss'],
                'holdout_accuracy': self.results['holdout']['accuracy'],
                'holdout_log_loss': self.results['holdout']['log_loss']
            },
            'pinn_analysis': self.results['pinn_vs_traditional'],
            'error_analysis': self.results['error_analysis'],
            'reliability': self.results['reliability_analysis']
        }
        
        # Save summary as JSON
        import json
        with open('accuracy_report/summary.json', 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        # Save detailed results
        self.results['summary'] = summary
        
        # Print final summary
        print("\n" + "="*60)
        print("🎉 COMPLETE ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"\n📊 Dataset:")
        print(f"   Objects: {summary['dataset_info']['n_objects']:,}")
        print(f"   Observations: {summary['dataset_info']['n_observations']:,}")
        print(f"   Classes: {summary['dataset_info']['n_classes']}")
        
        print(f"\n🔬 Features:")
        print(f"   Total: {summary['feature_info']['total_features']}")
        print(f"   PINN: {summary['feature_info']['pinn_features']}")
        print(f"   Traditional: {summary['feature_info']['traditional_features']}")
        
        print(f"\n🎯 Performance:")
        print(f"   CV Accuracy: {summary['performance']['cv_accuracy_mean']:.4f} ± {summary['performance']['cv_accuracy_std']:.4f}")
        print(f"   CV Log Loss: {summary['performance']['cv_log_loss_mean']:.4f} ± {summary['performance']['cv_log_loss_std']:.4f}")
        print(f"   Hold-out Accuracy: {summary['performance']['holdout_accuracy']:.4f}")
        print(f"   Hold-out Log Loss: {summary['performance']['holdout_log_loss']:.4f}")
        
        print(f"\n🔥 Top 5 Features:")
        for _, row in self.feature_importance.head(5).iterrows():
            print(f"   {row['feature']}: {row['importance']:.1f}")
        
        print(f"\n🔬 Top 3 PINN Features:")
        if len(self.pinn_feature_importance) > 0:
            for _, row in self.pinn_feature_importance.head(3).iterrows():
                print(f"   {row['feature']}: {row['importance']:.1f}")
        else:
            print("   No PINN features found in top importance")
        
        print(f"\n📁 Report saved to: accuracy_report/")
        print("="*60)
        
        return summary

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main function to run complete accuracy check"""
    print("🌌 COSMONET COMPLETE PINN ACCURACY CHECKER")
    print("="*60)
    
    # Initialize checker
    checker = CosmoNetCompleteAccuracyChecker(random_state=42, n_folds=5)
    
    # Load data
    if not checker.load_data(r'E:\Cosmonet\plasticc\training_set_metadata.csv', r'E:\Cosmonet\plasticc\training_set.csv'):
        print("\n❌ Failed to load data. Please check file paths.")
        return
    
    # Run complete analysis
    try:
        results = checker.run_complete_analysis(test_size=0.2)
        print("\n✅ Complete analysis finished successfully!")
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()