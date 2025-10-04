"""
Exoplanet Detection ML Model
Advanced ensemble model for exoplanet classification and property prediction
"""

import numpy as np
import pandas as pd
import pickle
import warnings
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
import joblib

warnings.filterwarnings('ignore')

class ExoplanetModel:
    """
    Ensemble ML model for exoplanet detection and classification
    """
    
    def __init__(self):
        self.classifier = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = []
        self.feature_importance = None
        
    def prepare_features(self, df):
        """
        Prepare feature set for training/prediction
        """
        # Define feature columns (input features + engineered features)
        feature_cols = [
            # Input features
            'orbital_period',
            'transit_depth',
            'transit_duration',
            'stellar_radius',
            'stellar_mass',
            'stellar_temp',
            'snr',
            'stellar_magnitude',
            
            # Engineered features
            'impact_parameter',
            'semi_major_axis',
            'planet_radius',
            'planet_temp',
            'insolation_flux',
            'transit_probability',
            'snr_metric',
            'log_orbital_period',
            'log_transit_depth',
            'stellar_density',
            'potentially_habitable'
        ]
        
        # Use only available columns
        available_features = [col for col in feature_cols if col in df.columns]
        self.feature_names = available_features
        
        # Extract features
        X = df[available_features].copy()
        
        # Handle missing values
        # For critical features, fill with median
        for col in available_features:
            if X[col].isna().any():
                median_val = X[col].median()
                if np.isnan(median_val):
                    median_val = 0
                X[col].fillna(median_val, inplace=True)
        
        # Replace inf values
        X.replace([np.inf, -np.inf], 0, inplace=True)
        
        return X
    
    def build_ensemble_model(self, fast_mode=False):
        """
        Build advanced ensemble classifier
        Combines multiple algorithms for robust predictions
        """
        if fast_mode:
            # Faster training with fewer estimators
            n_rf = 100
            n_xgb = 100
            n_gb = 50
            mlp_iters = 200
        else:
            n_rf = 300
            n_xgb = 300
            n_gb = 200
            mlp_iters = 500
        
        # Random Forest - excellent for feature importance
        rf = RandomForestClassifier(
            n_estimators=n_rf,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            max_features='sqrt',
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        )
        
        # XGBoost - powerful gradient boosting
        xgb = XGBClassifier(
            n_estimators=n_xgb,
            max_depth=10,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=1,
            random_state=42,
            n_jobs=-1,
            eval_metric='mlogloss'
        )
        
        # Gradient Boosting
        gb = GradientBoostingClassifier(
            n_estimators=n_gb,
            max_depth=8,
            learning_rate=0.1,
            min_samples_split=5,
            subsample=0.8,
            random_state=42
        )
        
        # Neural Network
        mlp = MLPClassifier(
            hidden_layer_sizes=(128, 64, 32),
            activation='relu',
            solver='adam',
            alpha=0.001,
            batch_size=32,
            learning_rate='adaptive',
            max_iter=mlp_iters,
            random_state=42,
            early_stopping=True,
            validation_fraction=0.1
        )
        
        # Voting classifier - combines all models
        ensemble = VotingClassifier(
            estimators=[
                ('rf', rf),
                ('xgb', xgb),
                ('gb', gb),
                ('mlp', mlp)
            ],
            voting='soft',  # Use probability predictions
            n_jobs=-1
        )
        
        return ensemble
    
    def train(self, df, test_size=0.2, validate=True, fast_mode=False):
        """
        Train the ensemble model
        """
        print("=" * 60)
        print("Training Exoplanet Detection Model")
        print("=" * 60)
        
        # Prepare features and labels
        X = self.prepare_features(df)
        y = df['disposition'].values
        
        print(f"\nFeatures used: {len(self.feature_names)}")
        print(f"Training samples: {len(X)}")
        print(f"\nClass distribution:")
        print(pd.Series(y).value_counts())
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=test_size, random_state=42, stratify=y_encoded
        )
        
        # Scale features
        print("\nScaling features...")
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Build and train model
        print("\nBuilding ensemble model...")
        self.classifier = self.build_ensemble_model(fast_mode=fast_mode)
        
        print("Training model (this may take a few minutes)...")
        self.classifier.fit(X_train_scaled, y_train)
        
        # Evaluate on test set
        print("\n" + "=" * 60)
        print("Model Evaluation")
        print("=" * 60)
        
        y_pred = self.classifier.predict(X_test_scaled)
        
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        print(f"\nTest Accuracy: {accuracy:.4f}")
        print(f"F1 Score: {f1:.4f}")
        
        print("\nClassification Report:")
        print(classification_report(
            y_test, y_pred,
            target_names=self.label_encoder.classes_
        ))
        
        print("\nConfusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(cm)
        
        # Cross-validation
        if validate:
            print("\nPerforming cross-validation...")
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            cv_scores = cross_val_score(
                self.classifier, X_train_scaled, y_train,
                cv=cv, scoring='accuracy', n_jobs=-1
            )
            print(f"CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        
        # Feature importance (from Random Forest component)
        try:
            rf_model = self.classifier.named_estimators_['rf']
            self.feature_importance = pd.DataFrame({
                'feature': self.feature_names,
                'importance': rf_model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            print("\nTop 10 Most Important Features:")
            print(self.feature_importance.head(10).to_string(index=False))
        except Exception as e:
            print(f"Could not extract feature importance: {e}")
        
        print("\n" + "=" * 60)
        print("Training Complete!")
        print("=" * 60)
        
        return {
            'accuracy': accuracy,
            'f1_score': f1,
            'classification_report': classification_report(
                y_test, y_pred, target_names=self.label_encoder.classes_, output_dict=True
            )
        }
    
    def predict(self, input_data):
        """
        Predict exoplanet classification and properties
        
        Args:
            input_data: dict or DataFrame with required features
        
        Returns:
            dict with classification and predicted properties
        """
        if self.classifier is None:
            raise ValueError("Model not trained. Please train or load a model first.")
        
        # Convert to DataFrame if dict
        if isinstance(input_data, dict):
            input_df = pd.DataFrame([input_data])
        else:
            input_df = input_data.copy()
        
        # Ensure all required features are present
        for feature in self.feature_names:
            if feature not in input_df.columns:
                input_df[feature] = 0  # Will be calculated if possible
        
        # Extract features in correct order
        X = input_df[self.feature_names].values
        
        # Replace any NaN or inf
        X = np.nan_to_num(X, nan=0, posinf=0, neginf=0)
        
        # Scale
        X_scaled = self.scaler.transform(X)
        
        # Predict
        prediction = self.classifier.predict(X_scaled)
        probabilities = self.classifier.predict_proba(X_scaled)
        
        # Decode label
        predicted_class = self.label_encoder.inverse_transform(prediction)[0]
        
        # Get confidence scores
        prob_dict = {}
        for idx, class_name in enumerate(self.label_encoder.classes_):
            prob_dict[class_name] = probabilities[0][idx]
        
        # Get predicted exoplanet properties
        result = {
            'classification': predicted_class,
            'confidence': max(probabilities[0]),
            'probabilities': prob_dict,
        }
        
        # Add exoplanet properties if it's a confirmed planet or candidate
        if predicted_class in ['CONFIRMED', 'CANDIDATE']:
            result['planet_radius'] = input_df['planet_radius'].values[0] if 'planet_radius' in input_df.columns else None
            result['planet_temp'] = input_df['planet_temp'].values[0] if 'planet_temp' in input_df.columns else None
            result['semi_major_axis'] = input_df['semi_major_axis'].values[0] if 'semi_major_axis' in input_df.columns else None
            result['impact_parameter'] = input_df['impact_parameter'].values[0] if 'impact_parameter' in input_df.columns else None
            result['potentially_habitable'] = input_df['potentially_habitable'].values[0] if 'potentially_habitable' in input_df.columns else None
        
        return result
    
    def save_model(self, filepath='exoplanet_model.pkl'):
        """Save trained model to disk"""
        model_data = {
            'classifier': self.classifier,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_names': self.feature_names,
            'feature_importance': self.feature_importance
        }
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath='exoplanet_model.pkl'):
        """Load trained model from disk"""
        model_data = joblib.load(filepath)
        self.classifier = model_data['classifier']
        self.scaler = model_data['scaler']
        self.label_encoder = model_data['label_encoder']
        self.feature_names = model_data['feature_names']
        self.feature_importance = model_data.get('feature_importance')
        print(f"Model loaded from {filepath}")

if __name__ == "__main__":
    print("Exoplanet ML Model Module")
    print("Use exoplanet_trainer.py to train the model")
