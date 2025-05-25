import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
import joblib

# 1. Load your dataset
df = pd.read_csv("real_india_city_routes.csv")  # Replace with your actual file

# 2. Define features and target
X = df[["From", "To", "Distance (KM)"]]
y = df["Time (Hours)"]

# 3. Preprocessing: One-hot encode categorical columns
categorical_features = ["From", "To"]

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
    ],
    remainder="passthrough"  # Keep numeric columns
)

# 4. Pipeline: Preprocessing + Model
model = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("regressor", LinearRegression())
])

# 5. Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 6. Train the model
model.fit(X_train, y_train)

# 7. Evaluate
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
print(f"Mean Absolute Error: {mae:.2f} hours")

# 8. Save the model
joblib.dump(model, "route_time_predictor.pkl")
print("Model saved as route_time_predictor.pkl")
