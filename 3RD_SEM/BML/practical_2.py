import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
from sklearn.model_selection import train_test_split 
from sklearn.tree import DecisionTreeRegressor 
from sklearn.metrics import mean_squared_error, r2_score 
df = pd.read_csv('path_to_your_regression_dataset.csv') 
print(df.head()) 
X = df[['city', 'aqi', 'feature3']]  # Replace with relevant feature names 
y = df['target']  # Replace with your target variable 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42) 
dt_regressor = DecisionTreeRegressor(random_state=42) 
dt_regressor.fit(X_train, y_train) 
y_pred = dt_regressor.predict(X_test) 
mse = mean_squared_error(y_test, y_pred) 
r2 = r2_score(y_test, y_pred) 
print('Mean Squared Error:', mse) 
print('R^2 Score:', r2) 
plt.scatter(y_test, y_pred) 
plt.xlabel('Actual Values') 
plt.ylabel('Predicted Values') 
plt.title('Decision Tree Regression: Actual vs Predicted') 
plt.plot([y.min(), y.max()], [y.min(), y.max()], color='red') 
plt.show()