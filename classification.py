from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.tree import DecisionTreeClassifier

BASE_DIR = Path(__file__).parent
orders = pd.read_csv(BASE_DIR / "clean_orders.csv")

# Create the target: an order is high-value when it is at or above the median.
median_revenue = orders["revenue"].median()
orders["high_value"] = (orders["revenue"] >= median_revenue).astype(int)

features = ["quantity", "unit_price", "discount"]
X = orders[features]
y = orders["high_value"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

model = DecisionTreeClassifier(max_depth=3, random_state=42)
model.fit(X_train, y_train)
predictions = model.predict(X_test)

print("Median revenue:", median_revenue)
print("Actual labels:", y_test.to_list())
print("Predicted labels:", predictions.tolist())
print("Accuracy:", round(accuracy_score(y_test, predictions), 2))
print("\nDetailed report:")
print(classification_report(y_test, predictions, zero_division=0))

# Cross-validation repeats testing with different data splits.
cross_validation_scores = cross_val_score(model, X, y, cv=4, scoring="accuracy")
print("Cross-validation accuracy scores:", cross_validation_scores.round(2).tolist())
print("Average cross-validation accuracy:", round(cross_validation_scores.mean(), 2))
