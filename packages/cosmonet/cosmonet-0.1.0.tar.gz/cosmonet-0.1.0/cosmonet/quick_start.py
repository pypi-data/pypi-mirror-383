from cosmonet import CosmoNetClassifier

# Initialize the classifier
classifier = CosmoNetClassifier(random_state=42)

# Load your data
classifier.load_data('metadata.csv', 'light_curves.csv')

# Define astronomical classes
classifier.define_classes()

# Engineer features
classifier.engineer_features()

# Train models
classifier.train_models(n_folds=5)

# Evaluate performance
results = classifier.evaluate_models()
print(f"Accuracy: {results['accuracy']:.3f}")