import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import OneHotEncoder

# Load file
csv_file_path = "../files/all_apts_big.csv"
df = pd.read_csv(csv_file_path)

# Prepare data
# 1) drop not relevant or dependent columns
cols_not_relevant = ['hash', 'name', 'url', 'postal_code','street', 'neighborhood', 'city', 'description', 'utilities_price',
                     'moving_in_price', 'energy label', 'latitude', 'longitude', 'nearest_metro', 'nearest_s_station',
                     'sharing friendly', 'pets allowed', 'senior friendly', 'only students', 'dishwasher',
                     'washing maching', 'charging stand', 'dryer']
df.drop(columns=cols_not_relevant, inplace=True)

# 2) replace strings Jeg/Nej by 1/0
# Replace different strings with the same statement
df.replace({
    "Ja": 1,
    "Nej": 0,
    "Ikke angivet": 1,
    "Stuen": 0,
    "-": 0,
    "Kælder": 0},  # None
    inplace=True
)
# 3) Categorize columns
encoder = OneHotEncoder(sparse_output=False)
type_encoded = encoder.fit_transform(df[['type']])
type_encoded_df = pd.DataFrame(type_encoded, columns=encoder.get_feature_names_out(['type']))
df = pd.concat([df.drop('type', axis=1), type_encoded_df], axis=1)

# 4) Clean specific data
# found_rows = df[df.map(lambda x: isinstance(x, str) and 'Kælder' in x)]

# Price is what we want to predict
# Split between attributes (X) and objective (y)
X = df.drop(columns='price', axis=1)
y = df['price']

# Split data into training and testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize model
modelo_rf = RandomForestRegressor(n_estimators=100, random_state=42)

# Train the model
modelo_rf.fit(X_train, y_train)

# Predict results with the test dataset
y_predicted = modelo_rf.predict(X_test)

# Compute metrics for the validation
mse_rf = mean_squared_error(y_test, y_predicted)
r2_rf = r2_score(y_test, y_predicted)

print("Random Forest:")
print("Error cuadrático medio (MSE):", mse_rf)
print("Coeficiente de determinación (R^2):", r2_rf)




import matplotlib.pyplot as plt

# Graficar valores reales versus predicciones
plt.scatter(y_test, y_predicted)
plt.xlabel('Valores reales')
plt.ylabel('Predicciones')
plt.title('Valores reales vs. Predicciones')
plt.show()


# Obtener la importancia de las características del modelo
importancias = modelo_rf.feature_importances_

# Crear un DataFrame para visualizar las importancias de las características
importancias_df = pd.DataFrame({'Característica': X.columns, 'Importancia': importancias})
importancias_df = importancias_df.sort_values(by='Importancia', ascending=False)

# Graficar la importancia de las características
plt.bar(importancias_df['Característica'], importancias_df['Importancia'])
plt.xlabel('Característica')
plt.ylabel('Importancia')
plt.title('Importancia de las características')
plt.xticks(rotation=90)  # Rotar etiquetas del eje x para mayor legibilidad
plt.show()


print("end")





