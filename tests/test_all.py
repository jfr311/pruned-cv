from prunedcv import PrunerCV
from sklearn.datasets import fetch_california_housing, load_iris
from lightgbm import LGBMRegressor, LGBMClassifier
import numpy as np
import pandas as pd
import pytest


def test_pruner_prun_yes():
    
    pruner = PrunerCV(4, 0.1)

    for i in range(6):
        pruner.add_split_value_and_prun(1.0)

    pruner.add_split_value_and_prun(10000.0)

    assert pruner.prun


def test_pruner_prun_no():

    pruner = PrunerCV(4, 0.1)

    for i in range(4):
        pruner.add_split_value_and_prun(1.0)

    for i in range(3):
        pruner.add_split_value_and_prun(.6)

    assert not pruner.prun


def test_pruner_prun_back():

    pruner = PrunerCV(4, 0.1)

    for i in range(4):
        pruner.add_split_value_and_prun(1.0)

    for i in range(2):
        pruner.add_split_value_and_prun(10000.0)

    for i in range(3):
        pruner.add_split_value_and_prun(1.0)

    assert not pruner.prun


def test_prun_first_run():

    pruner = PrunerCV(4, 0.1)

    for i in range(4):
        pruner.add_split_value_and_prun(1.0)

    assert pruner.best_splits_list_ == [1.0, 1.0, 1.0, 1.0]


def test_prun_first_run_check():

    pruner = PrunerCV(4, 0.1)

    for i in range(4):
        pruner.add_split_value_and_prun(1.0)

    assert not pruner.first_run_


def test_prun_folds_int():

    with pytest.raises(TypeError):
        pruner = PrunerCV(1.1, 0.1)
        pruner.add_split_value_and_prun(1)


def test_prun_folds_num():

    with pytest.raises(ValueError):
        pruner = PrunerCV(1, 0.1)
        pruner.add_split_value_and_prun(1)


def test_prun_vals_type():

    with pytest.raises(TypeError):
        pruner = PrunerCV(4, 0.1)
        pruner.add_split_value_and_prun(1)


def test_prun_score_val_constant():

    pruner = PrunerCV(4, 0.1)

    for i in range(8):
        pruner.add_split_value_and_prun(1.0)

    assert pruner.cross_val_score == 1.0


def test_prun_score_val_dec():

    pruner = PrunerCV(4, 0.1)

    for i in range(7):
        pruner.add_split_value_and_prun(1.0)

    pruner.add_split_value_and_prun(.9)

    assert pruner.cross_val_score < 1.0


def test_prun_score_val_inc():

    pruner = PrunerCV(4, 0.1)

    for i in range(7):
        pruner.add_split_value_and_prun(1.0)

    pruner.add_split_value_and_prun(1.1)

    assert pruner.cross_val_score > 1.0


def test_prun_score_val_best():

    pruner = PrunerCV(4, 0.1)

    for i in range(7):
        pruner.add_split_value_and_prun(1.0)

    pruner.add_split_value_and_prun(1.1)

    assert sum(pruner.best_splits_list_) / pruner.n_splits == 1.0


def test_prun_pruned_cv_score():

    pruner = PrunerCV(4, 0.1)

    for i in range(4):
        pruner.add_split_value_and_prun(1.0)

    for i in range(2):
        pruner.add_split_value_and_prun(2.0)

    assert pruner.cross_val_score == 2.0


def test_prun_3models():

    data = fetch_california_housing()
    x = data['data']
    y = data['target']

    pruner = PrunerCV(n_splits=8, tolerance=.1)

    model1 = LGBMRegressor(max_depth=25)
    model2 = LGBMRegressor(max_depth=10)
    model3 = LGBMRegressor(max_depth=2)

    score1 = pruner.cross_validate_score(model1, x, y, shuffle=True)
    score2 = pruner.cross_validate_score(model2, x, y, shuffle=True)
    score3 = pruner.cross_validate_score(model3, x, y, shuffle=True)

    assert (sum(pruner.best_splits_list_) / pruner.n_splits == score2) and (score2 < score1) and (score2 < score3)


def test_prun_cv_x():

    with pytest.raises(TypeError):
        pruner = PrunerCV(n_splits=4, tolerance=.1)

        model = LGBMRegressor()
        x = [1, 2, 3]
        y = np.array([1, 2, 3])
        pruner.cross_validate_score(model, x, y)


def test_prun_cv_y():

    with pytest.raises(TypeError):
        pruner = PrunerCV(n_splits=4, tolerance=.1)

        model = LGBMRegressor()
        y = [1, 2, 3]
        x = np.array([1, 2, 3])
        pruner.cross_validate_score(model, x, y)


def test_prun_cv_xy():

    with pytest.raises(TypeError):
        pruner = PrunerCV(n_splits=4, tolerance=.1)

        model = LGBMRegressor()
        y = [1, 2, 3]
        x = [1, 2, 3]
        pruner.cross_validate_score(model, x, y)


def test_prun_cv_x_df():

    data = fetch_california_housing()
    x = pd.DataFrame(data['data'])
    y = data['target']

    pruner = PrunerCV(n_splits=8, tolerance=.1)

    model = LGBMRegressor()

    pruner.cross_validate_score(model, x, y)

    assert len(pruner.best_splits_list_) == pruner.n_splits


def test_prun_cv_xy_df_ser():

    data = fetch_california_housing()
    x = pd.DataFrame(data['data'])
    y = pd.Series(data['target'])

    pruner = PrunerCV(n_splits=8, tolerance=.1)

    model = LGBMRegressor()

    pruner.cross_validate_score(model, x, y)

    assert len(pruner.best_splits_list_) == pruner.n_splits


def test_prun_cv_y_ser():

    data = fetch_california_housing()
    x = data['data']
    y = pd.Series(data['target'])

    pruner = PrunerCV(n_splits=8, tolerance=.1)

    model = LGBMRegressor()

    pruner.cross_validate_score(model, x, y)

    assert len(pruner.best_splits_list_) == pruner.n_splits


def test_prun_set_tolerance_1():

    with pytest.raises(TypeError):
        pruner = PrunerCV(4, 0.1)
        pruner.set_tolerance(1)


def test_prun_set_tolerance_2():

    with pytest.raises(ValueError):
        pruner = PrunerCV(4, 0.1)
        pruner.set_tolerance(-1.0)


def test_prun_cv_metric():

    with pytest.raises(ValueError):

        data = fetch_california_housing()
        x = data['data']
        y = pd.Series(data['target'])

        pruner = PrunerCV(4, 0.1)

        model = LGBMRegressor()

        pruner.cross_validate_score(model, x, y, metric='rmsle')


def test_pruner_mae():

    data = fetch_california_housing()
    x = data['data']
    y = pd.Series(data['target'])

    pruner = PrunerCV(4, 0.1)

    model = LGBMRegressor(objective='mae')

    pruner.cross_validate_score(model, x, y, metric='mae')


def test_pruner_higher_value1():

    pruner = PrunerCV(4, 0.1)

    assert pruner._significantly_higher_value(1.0, 2.0, True, .1)


def test_pruner_higher_value2():

    pruner = PrunerCV(4, 0.1)

    assert not pruner._significantly_higher_value(1.0, 1.05, True, .1)


def test_pruner_higher_value3():

    pruner = PrunerCV(4, 0.1)

    assert not pruner._significantly_higher_value(-1.0, -1.05, False, .1)


def test_pruner_higher_value4():

    pruner = PrunerCV(4, 0.1)

    assert pruner._significantly_higher_value(-1.0, -0.8, False, .1)
