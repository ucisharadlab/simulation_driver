#!/usr/bin/env python3

import numpy as np
import pandas as pd
import sys
import xgboost as xgb

from pathlib import Path
from sklearn import metrics
from sklearn.linear_model import LinearRegression,ElasticNet
from sklearn.model_selection import train_test_split


def load_and_prepare(csv_path: Path) -> pd.DataFrame:
	df = pd.read_csv(csv_path)

	# Spacing is "X Y". We split the column and store is as numeric.
	df[["SPACING_X_STR", "SPACING_Y_STR"]] = df["OUTPUT_GRIDS__SPACING"].str.split(" ", n=1, expand=True)
	df["INVERSE_SPACING_X"] = 1.0 / pd.to_numeric(df.SPACING_X_STR)
	df["INVERSE_SPACING_Y"] = 1.0 / pd.to_numeric(df.SPACING_Y_STR)

	# From the sampling string, we obtain the last 5 characters (HH MM), split, and convert to seconds.
	df["SAMPLING_STR"] = df["OUTPUT_GRIDS__SAMPLING"].str[-5:]
	df[["SAMPLING_H_STR", "SAMPLING_MIN_STR"]] = df["SAMPLING_STR"].str.split(" ", n=1, expand=True)
	df["INVERSE_SAMPLING_RATE"] = 1.0 / (pd.to_numeric(df.SAMPLING_H_STR) * 3600 + pd.to_numeric(df.SAMPLING_MIN_STR) * 60)

	X = df[["TOTAL_RUN_TIME", "INVERSE_SPACING_X", "INVERSE_SPACING_Y", "INVERSE_SAMPLING_RATE"]]
	y = df["DURATION_S"]

	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.333, random_state=17)

	return X_train, X_test, y_train, y_test


def train_linear_regression_model(X_train, X_test, y_train, y_test):
	regression = LinearRegression().fit(X_train, y_train)

	return regression


def train_adapted_linear_regression_model(X_train, X_test, y_train, y_test):
	X_adapted = X_train.div(y_train, axis=0)
	y_adapted = y_train.div(y_train, axis=0)
	regression = LinearRegression(fit_intercept = False).fit(X_adapted, y_adapted)

	return regression


def train_adapted_elasticnet_linear_regression_model(X_train, X_test, y_train, y_test):
	X_adapted = X_train.div(y_train, axis=0)
	y_adapted = y_train.div(y_train, axis=0)
	regression = ElasticNet(fit_intercept = False).fit(X_adapted, y_adapted)

	return regression


# Might overfit quite a lot. We need a sufficiently large data set here.
def train_XGB_regression_model(X_train, X_test, y_train, y_test):
	model = xgb.XGBRegressor(n_estimators=200, max_depth=7, eta=0.2).fit(X_train, y_train)

	return model


def evaluate_model(model, csv_path, X_train, X_test, y_train, y_test):
	y_predicted = model.predict(X_test)

	mae = metrics.mean_absolute_error(y_test, y_predicted)
	mse = metrics.mean_squared_error(y_test, y_predicted)
	mape = metrics.mean_absolute_percentage_error(y_test, y_predicted)
	r2 = metrics.r2_score(y_test, y_predicted)

	model_name = type(model).__name__
	if model_name == "LinearRegression" and model.intercept_ == 0.0:
		# Changes for a linreg with intercept of 0.0 are low. Should be okay here.
		model_name = "AdaptedLinearRegression"

	if hasattr(model, "intercept_"):
		print(f"Model: {model_name}")
		print("--------------------------------------")
		print(f"Intercept: {model.intercept_}")
		print(f"Coefficients: {list(zip(X_train.columns, model.coef_))}")
		print()
	print("Model performance:")
	print("--------------------------------------")
	print(f"MAE is {mae}")
	print(f"MSE is {mse}")
	print(f"MAPE is {mape}")
	print(f"R2 score is {r2}")

	# For easier analysis, stitch all data together and export as CSV.
	y_predicted2 = model.predict(X_train)
	X_stitched = pd.concat([pd.concat([X_train, y_train], axis=1).reset_index(), pd.DataFrame(y_predicted2)], axis=1)
	y_stitched = pd.concat([pd.concat([X_test, y_test], axis=1).reset_index(), pd.DataFrame(y_predicted)], axis=1)
	df = pd.concat([X_stitched, y_stitched], axis=0)

	assert "runtime_measurements" in str(csv_path)
	df.to_csv(str(csv_path).replace("runtime_measurements", f"results_debugging__{model_name}"))


if __name__ == '__main__':
	if len(sys.argv) == 1:
		exit("Please pass CSV file with runtime measurements.")

	csv_path = Path(sys.argv[1])

	X_train, X_test, y_train, y_test = load_and_prepare(csv_path)
	
	linear_regression_model = train_linear_regression_model(X_train, X_test, y_train, y_test)
	adapted_regression_model = train_adapted_linear_regression_model(X_train, X_test, y_train, y_test)
	adapted_elasticnet_regression_model = train_adapted_elasticnet_linear_regression_model(X_train, X_test, y_train, y_test)
	xgb_regression_model = train_XGB_regression_model(X_train, X_test, y_train, y_test)

	evaluate_model(linear_regression_model, csv_path, X_train, X_test, y_train, y_test)
	print()
	evaluate_model(adapted_regression_model, csv_path, X_train, X_test, y_train, y_test)
	print()
	evaluate_model(adapted_elasticnet_regression_model, csv_path, X_train, X_test, y_train, y_test)
	print()
	evaluate_model(xgb_regression_model, csv_path, X_train, X_test, y_train, y_test)
