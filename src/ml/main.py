"""
Utilities for training and saving XGBoost regression models using data from
tabular CSV files. Includes functions for data loading, preprocessing,
model training, evaluation, and saving models with associated metadata.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error


def load_csv_data(data_folder: Path, feature_names: list[str], target_name: str) -> pd.DataFrame:
    """
    This function reads multiple feature columns and a target column from
    CSV files located in a specified folder path. Each feature and target
    column is extracted and combined into a single DataFrame. The target
    column is renamed with the suffix "_target" to differentiate it clearly.
    """
    series_list = []

    for feature_name in feature_names:
        feature_series = get_values_from_csv(data_folder, feature_name)
        series_list.append(feature_series.rename(feature_name))

    target_series = get_values_from_csv(data_folder, target_name)
    series_list.append(target_series.rename(target_name + "_target"))

    return pd.concat(series_list, axis=1)


def get_values_from_csv(data_folder: Path, col_name: str) -> pd.Series:
    """
    Extracts and returns a specific column's data from a CSV file located within the
    specified folder. The function expects the CSV file to be named as the column name
    with a `.csv` extension. It also requires the column to contain a "_value" column,
    which it then returns as a panda Series.
    """
    csv_path = data_folder / f"{col_name}.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path, comment="#")

    if "_value" not in df.columns:
        raise ValueError(f"_value column missing in {csv_path}")

    return df["_value"]



def shift_target_future(df: pd.DataFrame, target: str, steps_ahead: int) -> pd.DataFrame:
    """
    Shifts the target column backwards (negative shift) so that
    features at time t predict the target at time t + steps_ahead.

    This introduces NaNs at the end of the target column.
    Finally all target rows with NaNs are removed.
    TODO: One should do ΔT instead of the absolute value.
    TODO: Data should probably be processed there are a lot of NANs
    """
    df_copy = df.copy()
    df_copy[target] = df_copy[target].shift(-steps_ahead)
    df_copy = df_copy.dropna(subset=[target])

    return df_copy


def inject_random_nans(df: pd.DataFrame, features: list[str], dropout_prob: float, random_state: int) -> pd.DataFrame:
    """
    Randomly replaces feature values with NaN to make the model robust to missing data.
    """
    df_copy = df.copy()
    rng = np.random.default_rng(random_state)

    for feature in features:
        if feature in df_copy.columns:
            mask = rng.random(len(df_copy)) < dropout_prob
            df_copy.loc[mask, feature] = np.nan

    return df_copy


def train_and_save_model(
    df: pd.DataFrame,
    config: dict,
    output_folder: Path
):
    """
    Trains a single XGBoost model based on the config and saves it.
    """
    # Extract config
    target = config["target"] + "_target"
    features = config["features"]
    training = config["training"]
    hyperparams = config["hyperparameters"]

    steps_ahead = training["steps_ahead"]
    validation_fraction = training["validation_fraction"]
    dropout_prob = training["dropout_prob"]
    random_state = training["random_state"]

    print(f"\n{'='*60}")
    print(f"Training model for target: {target}")
    print(f"Features: {features}")
    print(f"Steps ahead: {steps_ahead}")
    print(f"{'='*60}")

    # Step 1: Shift target into the future
    df = shift_target_future(df, target, steps_ahead)

    if len(df) == 0:
        raise ValueError("No valid samples after shifting")

    # Step 2: Inject NaNs for robustness
    df = inject_random_nans(df, features, dropout_prob, random_state)

    # Step 3: Prepare data
    x = df[features]  # features
    y = df[[target]]  # target as DataFrame

    # Step 4: Split into train/validation (time-based)
    split_idx = int(len(x) * (1 - validation_fraction))
    x_train, x_val = x.iloc[:split_idx], x.iloc[split_idx:]
    y_train, y_val = y.iloc[:split_idx], y.iloc[split_idx:]

    # Step 5: Create DMatrix objects with feature names
    d_train = xgb.DMatrix(x_train, label=y_train, feature_names=features, enable_categorical=True)
    d_val = xgb.DMatrix(x_val, label=y_val, feature_names=features, enable_categorical=True)

    # Step 6: Train model using xgb.train (stores feature names in a model)
    params = {
        "objective": "reg:squarederror",
        "max_depth": hyperparams.get("max_depth", 5),
        "learning_rate": hyperparams.get("learning_rate", 0.05),
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "tree_method": "hist"
    }

    n_estimators = hyperparams.get("n_estimators", 300)

    evals = [(d_train, "train"), (d_val, "val")]
    evals_result = {}

    booster = xgb.train(
        params,
        d_train,
        num_boost_round=n_estimators,
        evals=evals,
        early_stopping_rounds=30,
        evals_result=evals_result,
        verbose_eval=False
    )

    # Step 7: Evaluate
    y_pred = booster.predict(d_val)
    mae = mean_absolute_error(y_val, y_pred)
    rmse = np.sqrt(mean_squared_error(y_val, y_pred))

    print(f"\nValidation Metrics:")
    print(f"  MAE:  {mae:.4f}")
    print(f"  RMSE: {rmse:.4f}")

    # Step 8: Save the model with the target name as filename
    output_folder.mkdir(parents=True, exist_ok=True)
    model_path = output_folder / f"{target.replace('_target', '')}.json"
    booster.save_model(str(model_path))

    return booster, mae, rmse


def main():
    """
    Main training pipeline:
    1. Discover all JSON configs in the configs folder
    2. For each config, load data and train a model
    3. Save each model with the target name
    """
    # Setup paths
    base_dir = Path(__file__).resolve().parent
    data_folder = base_dir / "data"
    config_folder = base_dir / "configs"
    output_folder = base_dir / "models"

    print(f"Base directory: {base_dir}")
    print(f"Data folder: {data_folder}")
    print(f"Config folder: {config_folder}")
    print(f"Output folder: {output_folder}")

    # Find all config files
    if not config_folder.exists():
        raise FileNotFoundError(f"Config folder not found: {config_folder}")

    config_files = list(config_folder.glob("*.json"))

    if not config_files:
        raise ValueError(f"No JSON config files found in {config_folder}")

    print(f"\nFound {len(config_files)} config file(s)")

    # Process each config
    for config_file in config_files:
        print(f"\n{'#' * 60}")
        print(f"Processing: {config_file.name}")
        print(f"{'#' * 60}")

        # Load config
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Load data
        target = config["target"]
        features = config["features"]

        print(f"\nLoading data for target '{target}' and {len(features)} features...")
        df = load_csv_data(data_folder, features, target)
        print(f"Loaded {len(df)} rows")

        # Train and save
        train_and_save_model(df, config, output_folder)

    print(f"\n{'#' * 60}")
    print("All models trained successfully!")
    print(f"{'#' * 60}")


if __name__ == "__main__":
    main()
