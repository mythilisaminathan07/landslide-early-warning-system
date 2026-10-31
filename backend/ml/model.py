import joblib
import os

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "landslide_random_forest_model.pkl"
)

model = joblib.load(MODEL_PATH)

print("Landslide Random Forest model loaded successfully!")