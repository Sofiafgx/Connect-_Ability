"""
Neural Network Model for Exoplanet Detection
Advanced architecture with attention mechanisms and ensemble learning
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, callbacks
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os


class ExoplanetClassifier:
    """
    Neural network classifier for exoplanet detection
    Classifies transit signals as: confirmed exoplanet, planetary candidate, or false positive
    """
    
    def __init__(self, input_dim, model_name='exoplanet_classifier'):
        self.input_dim = input_dim
        self.model_name = model_name
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.history = None
        
    def build_model(self):
        """
        Build advanced neural network with attention mechanism
        """
        inputs = layers.Input(shape=(self.input_dim,), name='input')
        
        # First dense block with batch normalization
        x = layers.Dense(256, activation='relu', name='dense_1')(inputs)
        x = layers.BatchNormalization(name='bn_1')(x)
        x = layers.Dropout(0.3, name='dropout_1')(x)
        
        # Second dense block
        x = layers.Dense(128, activation='relu', name='dense_2')(x)
        x = layers.BatchNormalization(name='bn_2')(x)
        x = layers.Dropout(0.3, name='dropout_2')(x)
        
        # Third dense block
        x = layers.Dense(64, activation='relu', name='dense_3')(x)
        x = layers.BatchNormalization(name='bn_3')(x)
        x = layers.Dropout(0.2, name='dropout_3')(x)
        
        # Attention mechanism - learns to focus on important features
        attention = layers.Dense(64, activation='tanh', name='attention_tanh')(x)
        attention = layers.Dense(64, activation='softmax', name='attention_weights')(attention)
        x = layers.Multiply(name='attention_multiply')([x, attention])
        
        # Fourth dense block
        x = layers.Dense(32, activation='relu', name='dense_4')(x)
        x = layers.Dropout(0.2, name='dropout_4')(x)
        
        # Output layer - 3 classes (false positive, candidate, confirmed)
        outputs = layers.Dense(3, activation='softmax', name='output')(x)
        
        model = models.Model(inputs=inputs, outputs=outputs, name='exoplanet_classifier')
        
        # Compile with categorical crossentropy for multi-class classification
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.model = model
        print("\n" + "="*60)
        print("Model Architecture")
        print("="*60)
        self.model.summary()
        
        return model
    
    def train(self, X_train, y_train, X_val, y_val, epochs=100, batch_size=32):
        """
        Train the model with callbacks for early stopping and learning rate reduction
        """
        if self.model is None:
            self.build_model()
        
        # Handle class imbalance with SMOTE
        print("\nApplying SMOTE to balance classes...")
        smote = SMOTE(random_state=42)
        X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
        
        print(f"Original training set: {len(X_train)} samples")
        print(f"Balanced training set: {len(X_train_balanced)} samples")
        print(f"Class distribution after SMOTE:\n{pd.Series(y_train_balanced).value_counts().sort_index()}")
        
        # Callbacks
        early_stop = callbacks.EarlyStopping(
            monitor='val_loss',
            patience=15,
            restore_best_weights=True,
            verbose=1
        )
        
        reduce_lr = callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7,
            verbose=1
        )
        
        checkpoint = callbacks.ModelCheckpoint(
            f'models/{self.model_name}_best.h5',
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        )
        
        os.makedirs('models', exist_ok=True)
        
        # Train model
        print("\n" + "="*60)
        print("Training Neural Network")
        print("="*60)
        
        self.history = self.model.fit(
            X_train_balanced, y_train_balanced,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stop, reduce_lr, checkpoint],
            verbose=1
        )
        
        return self.history
    
    def evaluate(self, X_test, y_test):
        """
        Evaluate model performance on test set
        """
        print("\n" + "="*60)
        print("Model Evaluation")
        print("="*60)
        
        # Get predictions
        y_pred_proba = self.model.predict(X_test)
        y_pred = np.argmax(y_pred_proba, axis=1)
        
        # Calculate metrics
        test_loss, test_accuracy = self.model.evaluate(X_test, y_test, verbose=0)
        
        print(f"\nTest Loss: {test_loss:.4f}")
        print(f"Test Accuracy: {test_accuracy:.4f}")
        
        # Classification report
        label_names = ['False Positive', 'Candidate', 'Confirmed']
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=label_names))
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        print("\nConfusion Matrix:")
        print(cm)
        
        # Plot confusion matrix
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=label_names, yticklabels=label_names)
        plt.title('Confusion Matrix - Exoplanet Classification')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig('models/confusion_matrix.png', dpi=300, bbox_inches='tight')
        print("\nConfusion matrix saved to models/confusion_matrix.png")
        
        return {
            'accuracy': test_accuracy,
            'loss': test_loss,
            'predictions': y_pred,
            'probabilities': y_pred_proba
        }
    
    def plot_training_history(self):
        """
        Plot training history
        """
        if self.history is None:
            print("No training history available")
            return
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        
        # Accuracy plot
        axes[0].plot(self.history.history['accuracy'], label='Train')
        axes[0].plot(self.history.history['val_accuracy'], label='Validation')
        axes[0].set_title('Model Accuracy')
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Accuracy')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Loss plot
        axes[1].plot(self.history.history['loss'], label='Train')
        axes[1].plot(self.history.history['val_loss'], label='Validation')
        axes[1].set_title('Model Loss')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Loss')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        # Learning rate plot (if available in history)
        if 'lr' in self.history.history:
            axes[2].plot(self.history.history['lr'], label='Learning Rate')
            axes[2].set_title('Learning Rate')
            axes[2].set_xlabel('Epoch')
            axes[2].set_ylabel('Learning Rate')
            axes[2].set_yscale('log')
            axes[2].legend()
            axes[2].grid(True, alpha=0.3)
        else:
            axes[2].text(0.5, 0.5, 'Learning Rate\nNot Tracked', 
                        ha='center', va='center', transform=axes[2].transAxes)
        
        plt.tight_layout()
        plt.savefig('models/training_history.png', dpi=300, bbox_inches='tight')
        print("\nTraining history saved to models/training_history.png")
        
    def save_model(self, scaler, feature_names):
        """
        Save model, scaler, and feature names
        """
        os.makedirs('models', exist_ok=True)
        
        # Save Keras model
        self.model.save(f'models/{self.model_name}.h5')
        print(f"\nModel saved to models/{self.model_name}.h5")
        
        # Save scaler
        joblib.dump(scaler, f'models/{self.model_name}_scaler.pkl')
        print(f"Scaler saved to models/{self.model_name}_scaler.pkl")
        
        # Save feature names
        joblib.dump(feature_names, f'models/{self.model_name}_features.pkl')
        print(f"Feature names saved to models/{self.model_name}_features.pkl")
        
        self.scaler = scaler
        self.feature_names = feature_names
    
    def load_model(self):
        """
        Load saved model, scaler, and feature names
        """
        self.model = keras.models.load_model(f'models/{self.model_name}.h5')
        self.scaler = joblib.load(f'models/{self.model_name}_scaler.pkl')
        self.feature_names = joblib.load(f'models/{self.model_name}_features.pkl')
        print(f"\nModel loaded from models/{self.model_name}.h5")
        return self.model
    
    def predict(self, X, return_proba=False):
        """
        Make predictions on new data
        """
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        
        # Get predictions
        y_pred_proba = self.model.predict(X, verbose=0)
        y_pred = np.argmax(y_pred_proba, axis=1)
        
        if return_proba:
            return y_pred, y_pred_proba
        return y_pred
    
    def predict_single(self, features_dict):
        """
        Predict classification for a single observation
        
        Parameters:
        -----------
        features_dict : dict
            Dictionary containing feature values
            
        Returns:
        --------
        tuple : (prediction_label, probabilities)
        """
        if self.model is None or self.scaler is None or self.feature_names is None:
            self.load_model()
        
        # Create feature vector in correct order
        feature_vector = []
        for feature in self.feature_names:
            if feature in features_dict:
                feature_vector.append(features_dict[feature])
            else:
                # Use 0 for missing features (will be handled by scaler)
                feature_vector.append(0)
        
        # Reshape and scale
        X = np.array(feature_vector).reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        
        # Predict
        y_pred_proba = self.model.predict(X_scaled, verbose=0)[0]
        y_pred = np.argmax(y_pred_proba)
        
        label_names = ['False Positive', 'Planetary Candidate', 'Confirmed Exoplanet']
        
        return label_names[y_pred], {
            'false_positive': float(y_pred_proba[0]),
            'candidate': float(y_pred_proba[1]),
            'confirmed': float(y_pred_proba[2])
        }


if __name__ == "__main__":
    print("Exoplanet Classifier Module")
    print("Use train.py to train the model")
