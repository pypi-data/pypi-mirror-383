# Grouped Time Series Cross-Validation

This repository provides tools for classifying and predicting event-based time series data using pipelines, parameter tuning, cross-validation, and model evaluation. By automating the trial-and-error tasks in model selection, these tools help developers save significant time. Leveraging Scikit-learn's robust tools, this approach enhances model performance even in data-constrained environments.

**Model training is performed using cross-validation, where predictions are made on independent data for each date, with the remaining dates used as training data.**


## 1. Pipelines Definition
We define pipelines for three classification models: Gaussian Naive Bayes, Decision Tree, and Logistic Regression. However, you can easily swap these for other classifiers such as Support Vector Machines, Neural Networks, XGBoost, or Random Forests. Each pipeline includes the following steps:

1. **Scaling:** Standardization of features.
2. **Feature Selection:** Selecting the top features.
3. **Model** 

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression

pipelines = [
    Pipeline([
        ('scaler', StandardScaler()),
        ('selector', SelectKBest()),
        ('model', GaussianNB())
    ]),
    Pipeline([
        ('scaler', StandardScaler()),
        ('selector', SelectKBest()),
        ('model', DecisionTreeClassifier())
    ]),
    Pipeline([
        ('scaler', StandardScaler()),
        ('selector', SelectKBest()),
        ('model', LogisticRegression())
    ])
]
```

## 2. Parameter Grids
Each pipeline requires a corresponding parameter grid to define the hyperparameters for tuning. Below are the grids for the Gaussian Naive Bayes, Decision Tree, and Logistic Regression models.

```python

from sklearn.feature_selection import mutual_info_classif
param_grids = [
    # GaussianNB
    {
        'selector__k': [3, 5, 'all'],
        'selector__score_func': [mutual_info_classif],
        'model__var_smoothing': [1e-9, 1e-8, 1e-7, 1e-6]
    },
    
    # DecisionTreeClassifier
    {
        'selector__k': [3, 5, 'all'],
        'selector__score_func': [mutual_info_classif],
        'model__criterion': ['gini', 'entropy'],
        'model__splitter': ['best', 'random'],
        'model__max_depth': [None, 10, 20, 30],
        'model__min_samples_split': [2, 5, 10],
        'model__min_samples_leaf': [1, 2, 4],
        'model__random_state': [0, 12, 22, 42]
    },
    
    # LogisticRegression
    {
        'selector__k': [3, 5, 'all'],
        'selector__score_func': [mutual_info_classif],
        'model__penalty': ['l1', 'l2', 'elasticnet', 'none'],
        'model__C': [0.1, 1.0, 10.0],
        'model__solver': ['lbfgs', 'liblinear', 'saga'],
        'model__max_iter': [100, 200, 500],
        'model__random_state': [0, 12, 22, 42]
    }
]
```

## 3. Load the Dataset
Load the dataset from a CSV file and ensure the 'DateTime' column is converted to a datetime object. 

```python
import pandas as pd

data = pd.read_csv('model_data.csv')
data['DateTime'] = pd.to_datetime(data['DateTime'])
```

## 4. Classification
Perform classification using the grouped time series cross-validation with the defined pipelines and parameter grids. The `GroupedTimeSerieCV` class handles the cross-validation logic.

```python
from grouped_timeserie_cv import GroupedTimeSerieCV

grouped_cv = GroupedTimeSerieCV()
result = grouped_cv.classify(data, pipelines, param_grids, 'D', 'DateTime', 'Label', 'accuracy')
```

**Optional parameters:**
- **Frequency (`'D'`)**: Resample data at daily intervals.
- **DateTime column (`'DateTime'`)**: The column containing timestamps.
- **Label column (`'Label'`)**: The target label for classification.
- **Scoring method (`'accuracy'`)**: Metric for evaluating model performance.

_Note:_ If a group contains more than one unique label, it may negatively impact the model's performance.

## 5. Expected Output
During training, you will see output like the following in the console:

```
Process model: GaussianNB
Score: 0.781
Process model: DecisionTreeClassifier
Score: 0.811
Process model: LogisticRegression
Score: 0.836
Best model: LogisticRegression
Best parameters: {
 'model__C': 1,
 'model__class_weight': 'balanced',
 'model__max_iter': 1000,
 'model__penalty': 'l2',
 'model__solver': 'liblinear',
 'scaler__with_mean': True,
 'scaler__with_std': True,
 'selector__k': 3
}
Selected features: ['Moisture', 'Temperature', 'MeanTemperaturePeak']
```

In this example, Logistic Regression is the best model with an accuracy of 83.6%.

## 6. Define Result Data Class
The `CrossValidationResult` class encapsulates the results from the cross-validation process, including confusion matrices, model performance, and selected features.

```python
class CrossValidationResult:
    confusion_matrices: np.ndarray
    class_labels: list
    train_sizes: np.ndarray
    train_mean: np.ndarray
    train_std: np.ndarray
    test_mean: np.ndarray
    test_std: np.ndarray
    best_model: object
    selected_feature_names: list
    best_params: dict
    incorrect_dates: np.ndarray
    actual_values: np.ndarray
    predicted_values: np.ndarray
```

## 7. Plot Results
Once the classification is complete, use the plotting utilities to visualize the results, such as the confusion matrix and learning curve.

```python
# Plot confusion matrix
grouped_cv.plotter.plot_confusion_matrix(result.confusion_matrices, result.class_labels)

# Plot learning curve
grouped_cv.plotter.plot_learning_curve(result.train_sizes, result.train_mean, result.train_std, result.test_mean, result.test_std)
```

## 8. Regression
In addition to classification, the framework supports regression models. Below is an example using Multilayer perceptron (MLP), KNeighbors and Linear Regression models .

```python
from sklearn.neural_network import MLPRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import LinearRegression
from sklearn.feature_selection import mutual_info_regression

pipelines = [
    Pipeline([
        ('scaler', StandardScaler()),
        ('selector', SelectKBest()),
        ('model', MLPRegressor())
    ]),
    Pipeline([
        ('scaler', StandardScaler()),
        ('selector', SelectKBest()),
        ('model', KNeighborsRegressor())
    ]),
    Pipeline([
        ('scaler', StandardScaler()),
        ('selector', SelectKBest()),
        ('model', LinearRegression())
    ])
]

param_grids = [
    # MLPRegressor
    {
        'selector__k': [3, 5, 'all'],
        'selector__score_func': [mutual_info_regression],
        'model__hidden_layer_sizes': [(50,), (100,), (50, 50)],
        'model__activation': ['relu', 'tanh', 'logistic'],
        'model__solver': ['adam', 'sgd'],
        'model__alpha': [0.0001, 0.001, 0.01],
        'model__learning_rate': ['constant', 'adaptive'],
        'model__random_state': [0, 12, 22, 42]
    },
    
    # KNeighborsRegressor
    {
        'selector__k': [3, 5, 'all'],
        'selector__score_func': [mutual_info_regression],
        'model__n_neighbors': [3, 5, 7, 9],
        'model__weights': ['uniform', 'distance'],
        'model__algorithm': ['auto', 'ball_tree', 'kd_tree', 'brute'],
        'model__p': [1, 2]
    },
    
    # LinearRegression
    {
        'selector__k': [3, 5, 'all'],
        'selector__score_func': [mutual_info_regression]
    }
]

grouped_cv = GroupedTimeSerieCV()
result = grouped_cv.predict(data, pipelines, param_grids, 'D', 'DateTime', 'Label', 'neg_mean_squared_error')

# Plot predictions vs. actual values
grouped_cv.plotter.plot_prediction_vs_actual(result.actual_values, result.predicted_values)
```
