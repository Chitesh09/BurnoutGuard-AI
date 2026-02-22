import pandas as pd
import matplotlib.pyplot as plt
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

# =========================
# 1. Load Dataset
# =========================

data = pd.read_csv("dataset/burnout_data.csv")

# =========================
# 2. Define Features & Target
# =========================

X = data[[
    "Sleep_Hours",
    "Screen_Time",
    "Study_Hours",
    "Attendance",
    "Stress_Level"
]]

y = data["Burnout_Level"]

# =========================
# 3. Train-Test Split
# =========================

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =========================
# 4. Train Model
# =========================

model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# =========================
# 5. Predictions
# =========================

predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("\n========== MODEL PERFORMANCE ==========")
print("Model Accuracy:", round(accuracy, 2))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, predictions))

# =========================
# 6. Feature Importance
# =========================

importances = model.feature_importances_
feature_names = X.columns

feature_importance_df = pd.DataFrame({
    "Feature": feature_names,
    "Importance": importances
}).sort_values(by="Importance", ascending=False)

print("\n========== FEATURE IMPORTANCE ==========")
print(feature_importance_df)

# =========================
# 7. Save Model BEFORE Graph
# =========================

os.makedirs("model", exist_ok=True)
joblib.dump(model, "model/burnout_model.pkl")

print("\nModel saved successfully in model/burnout_model.pkl")

# =========================
# 8. Plot Graph
# =========================

plt.figure(figsize=(8, 5))
plt.bar(feature_importance_df["Feature"], feature_importance_df["Importance"])
plt.xticks(rotation=45)
plt.title("Feature Importance in Burnout Prediction")
plt.xlabel("Features")
plt.ylabel("Importance Score")
plt.tight_layout()
plt.show()
