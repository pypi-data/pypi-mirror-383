import pytest
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import SelectKBest, f_classif

from grouped_timeserie_cv import GroupedTimeSerieCV, DataPreprocessor, HyperparameterTuning, ModelEvaluator

# Sample data for testing
@pytest.fixture
def sample_data():
    data = {
        'DateTime': pd.date_range(start='2021-01-01', periods=100, freq='D'),
        'Feature1': range(100),
        'Feature2': range(100, 200),
        'Label': [0, 1] * 50
    }
    return pd.DataFrame(data)

@pytest.fixture
def pipelines():
    pipeline = Pipeline([
        ('selector', SelectKBest(f_classif, k=2)),
        ('scaler', StandardScaler()),
        ('model', LogisticRegression())
    ])
    return [pipeline]

@pytest.fixture
def param_grids():
    param_grid = {
        'selector__k': [1, 2],
        'model__C': [0.1, 1.0, 10.0]
    }
    return [param_grid]

# Test data preprocessing
def test_preprocess_data(sample_data):
    preprocessor = DataPreprocessor()
    X, y, groups = preprocessor.preprocess_data(sample_data)   
    assert not X.empty
    assert not y.empty
    assert len(groups) == len(sample_data)

# Test model training
def test_perform_grid_search(sample_data, pipelines, param_grids):
    preprocessor = DataPreprocessor()
    trainer = HyperparameterTuning()
    X, y, groups = preprocessor.preprocess_data(sample_data)
    
    best_model, best_params, selected_feature_names = trainer.perform_grid_search(X, y, groups, pipelines, param_grids, 'accuracy')
    
    assert best_model is not None
    assert best_params is not None
    assert selected_feature_names is not None

# Test model evaluation
def test_evaluate_model(sample_data, pipelines, param_grids):
    preprocessor = DataPreprocessor()
    trainer = HyperparameterTuning()
    evaluator = ModelEvaluator()
    X, y, groups = preprocessor.preprocess_data(sample_data)
    
    best_model, _, _ = trainer.perform_grid_search(X, y, groups, pipelines, param_grids, 'accuracy')
    confusion_matrices, incorrect_dates = evaluator.evaluate_model(best_model, X, y, groups, sample_data)
    
    assert confusion_matrices is not None
    assert incorrect_dates is not None

# Test cross-validation integration
def test_cross_validate(sample_data, pipelines, param_grids):
    cross_validator =  GroupedTimeSerieCV()
    result = cross_validator.classify(sample_data, pipelines, param_grids)
    
    assert result is not None
    assert result.confusion_matrices is not None
    assert result.class_labels is not None
    assert result.train_sizes is not None
    assert result.train_mean is not None
    assert result.train_std is not None
    assert result.test_mean is not None
    assert result.test_std is not None
    assert result.best_model is not None
    assert result.selected_feature_names is not None
    assert result.best_params is not None
    assert result.incorrect_dates is not None