"""
Data preprocessing utilities for preparing dataframes before pipeline execution.

This module centralizes all data preparation logic including:
- Score column conversion (score_columns parameter)
- Dataset sampling (sample_size parameter)
- Tidy to side-by-side conversion (model_a/model_b parameters)
- Data validation
"""

from __future__ import annotations

from typing import Optional, List
import pandas as pd
import numpy as np
from stringsight.logging_config import get_logger

logger = get_logger(__name__)


def convert_score_columns_to_dict(
    df: pd.DataFrame,
    score_columns: List[str],
    method: str
) -> pd.DataFrame:
    """
    Convert separate score columns into consolidated score dictionary columns.
    
    For single_model: Creates 'score' column containing {metric: value} dict
    For side_by_side: Creates 'score_a' and 'score_b' columns containing {metric: value} dicts
    
    Args:
        df: Input dataframe with separate score columns
        score_columns: List of column names (base names) containing score values
        method: Either "single_model" or "side_by_side"
        
    Returns:
        DataFrame with score dict column(s) added
        
    Raises:
        ValueError: If required score columns are missing or contain non-numeric values
        
    Examples:
        >>> # Single model
        >>> df = pd.DataFrame({
        ...     "prompt": ["What is AI?"],
        ...     "model": ["gpt-4"],
        ...     "model_response": ["AI is..."],
        ...     "accuracy": [0.9],
        ...     "helpfulness": [4.2]
        ... })
        >>> df = convert_score_columns_to_dict(df, ["accuracy", "helpfulness"], "single_model")
        >>> # df now has "score" column: {"accuracy": 0.9, "helpfulness": 4.2}
        
        >>> # Side-by-side
        >>> df = pd.DataFrame({
        ...     "prompt": ["What is AI?"],
        ...     "model_a": ["gpt-4"],
        ...     "model_b": ["claude-3"],
        ...     "model_a_response": ["AI is..."],
        ...     "model_b_response": ["AI is..."],
        ...     "accuracy_a": [0.9],
        ...     "accuracy_b": [0.8],
        ...     "helpfulness_a": [4.2],
        ...     "helpfulness_b": [4.5]
        ... })
        >>> df = convert_score_columns_to_dict(df, ["accuracy", "helpfulness"], "side_by_side")
        >>> # df now has "score_a" and "score_b" columns with dicts
    """
    df = df.copy()
    
    if method == "single_model":
        # Validate columns exist
        missing_cols = [col for col in score_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(
                f"Score columns not found in dataframe: {missing_cols}. "
                f"Available columns: {list(df.columns)}"
            )
        
        # Validate columns are numeric
        non_numeric = []
        for col in score_columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                # Try to coerce to numeric
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except:
                    non_numeric.append(col)
        
        if non_numeric:
            raise ValueError(
                f"Score columns contain non-numeric values: {non_numeric}. "
                f"Please ensure all score columns contain numeric data."
            )
        
        # Create score dictionary for each row
        def row_to_score_dict(row):
            return {col: row[col] for col in score_columns if pd.notna(row[col])}
        
        df['score'] = df.apply(row_to_score_dict, axis=1)
        
    elif method == "side_by_side":
        # For side-by-side, we need both _a and _b versions
        missing_cols_a = [f"{col}_a" for col in score_columns if f"{col}_a" not in df.columns]
        missing_cols_b = [f"{col}_b" for col in score_columns if f"{col}_b" not in df.columns]
        missing_cols = missing_cols_a + missing_cols_b
        
        if missing_cols:
            raise ValueError(
                f"Side-by-side score columns not found in dataframe: {missing_cols}. "
                f"Expected columns ending in '_a' and '_b' for each metric. "
                f"Available columns: {list(df.columns)}"
            )
        
        # Validate all _a and _b columns are numeric
        non_numeric = []
        for col in score_columns:
            col_a, col_b = f"{col}_a", f"{col}_b"
            for c in [col_a, col_b]:
                if not pd.api.types.is_numeric_dtype(df[c]):
                    try:
                        df[c] = pd.to_numeric(df[c], errors='coerce')
                    except:
                        non_numeric.append(c)
        
        if non_numeric:
            raise ValueError(
                f"Score columns contain non-numeric values: {non_numeric}. "
                f"Please ensure all score columns contain numeric data."
            )
        
        # Create score_a and score_b dictionaries
        def row_to_score_dict_a(row):
            return {col: row[f"{col}_a"] for col in score_columns if pd.notna(row[f"{col}_a"])}
        
        def row_to_score_dict_b(row):
            return {col: row[f"{col}_b"] for col in score_columns if pd.notna(row[f"{col}_b"])}
        
        df['score_a'] = df.apply(row_to_score_dict_a, axis=1)
        df['score_b'] = df.apply(row_to_score_dict_b, axis=1)
    
    else:
        raise ValueError(f"Invalid method: {method}. Must be 'single_model' or 'side_by_side'")
    
    return df


def sample_prompts_evenly(
    df: pd.DataFrame,
    *,
    sample_size: Optional[int],
    method: str = "single_model",
    prompt_column: str = "prompt",
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Sample prompts evenly across models.
    
    For single_model datasets, this function attempts to sample K = int(N / M) prompts per 
    model, where N is the desired total sample size and M is the number of unique models.
    
    Strategy:
    1. Find prompts that have responses from all models
    2. If there are >= K prompts with all models, sample K of those prompts
    3. Otherwise, sample K prompts independently from each model
    
    For side_by_side or when no model column exists, falls back to row-level sampling.
    
    Args:
        df: Input dataframe containing at least a ``prompt`` column and model columns as
            determined by ``method``.
        sample_size: Desired total number of rows across all models. If None or greater
            than the dataset size, the input dataframe is returned unchanged.
        method: Either "single_model" or "side_by_side".
        prompt_column: Name of the prompt column to use for grouping.
        random_state: Random seed for reproducible sampling.
        
    Returns:
        A dataframe filtered to the sampled prompts. If ``sample_size`` is None or not
        smaller than the input size, the input dataframe is returned.
        
    Raises:
        ValueError: If the inferred number of models is greater than 0 and
            int(sample_size / num_models) equals 0 (i.e., sample_size is too small).
    """
    if sample_size is None or sample_size <= 0 or sample_size >= len(df):
        return df
    
    if prompt_column not in df.columns:
        # Fallback to row-level sampling if no prompt column exists
        return df.sample(n=int(sample_size), random_state=random_state)
    
    models = _infer_models(df, method)
    num_models = max(1, len(models))
    
    prompts_per_model = int(sample_size // num_models)
    if prompts_per_model <= 0:
        raise ValueError(
            "Requested sample_size is smaller than the number of models; "
            "int(N/M) == 0 prompts. Increase sample_size or reduce models."
        )
    
    # For single_model: find prompts that have responses from all models
    if method == "single_model" and "model" in df.columns and num_models > 0:
        # Find prompts that have all models
        coverage = df.groupby(prompt_column)["model"].nunique()
        prompts_with_all_models = coverage[coverage == num_models].index.tolist()
        
        # If we have enough prompts with all models, sample from those
        if len(prompts_with_all_models) >= prompts_per_model:
            sampled_prompts = pd.Series(prompts_with_all_models).sample(
                n=prompts_per_model, random_state=random_state
            ).tolist()
            return df[df[prompt_column].isin(sampled_prompts)]
        else:
            # Sample prompts_per_model prompts from each model independently
            sampled_rows = []
            for model in models:
                model_df = df[df["model"] == model]
                model_prompts = model_df[prompt_column].dropna().unique().tolist()
                if len(model_prompts) > 0:
                    n_sample = min(prompts_per_model, len(model_prompts))
                    sampled_model_prompts = pd.Series(model_prompts).sample(
                        n=n_sample, random_state=random_state
                    ).tolist()
                    sampled_rows.append(
                        model_df[model_df[prompt_column].isin(sampled_model_prompts)]
                    )
            if sampled_rows:
                return pd.concat(sampled_rows, ignore_index=True)
            else:
                return df.head(0)
    
    # Fall back to row-level sampling for side_by_side or if no model column
    return df.sample(n=int(sample_size), random_state=random_state)


def _infer_models(df: pd.DataFrame, method: str) -> list[str]:
    """
    Infer the list of models present in the dataset.
    
    Args:
        df: Input dataframe.
        method: Either "single_model" or "side_by_side".
        
    Returns:
        List of unique model names across the dataset.
    """
    if method == "single_model":
        if "model" in df.columns:
            return sorted([m for m in df["model"].dropna().unique().tolist()])
        return []
    elif method == "side_by_side":
        models: set[str] = set()
        if "model_a" in df.columns:
            models.update([m for m in df["model_a"].dropna().unique().tolist()])
        if "model_b" in df.columns:
            models.update([m for m in df["model_b"].dropna().unique().tolist()])
        return sorted(list(models))
    else:
        return []


def tidy_to_side_by_side(
    df: pd.DataFrame,
    *,
    model_a: str,
    model_b: str,
    score_columns: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Convert tidy single-model format to side-by-side format.
    
    Expects tidy data with columns: prompt, model, model_response, and optionally score or score columns.
    Pivots to create: prompt, model_a, model_b, model_a_response, model_b_response, score_a, score_b.
    
    Args:
        df: Tidy format dataframe
        model_a: First model name to select
        model_b: Second model name to select
        score_columns: Optional list of score column names to pivot alongside responses
        
    Returns:
        Side-by-side format dataframe
        
    Raises:
        ValueError: If required columns are missing or models not found
    """
    # Validate required columns
    required = ["prompt", "model", "model_response"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Tidy format requires columns: {required}. Missing: {missing}")
    
    # Check models exist
    available_models = df["model"].unique().tolist()
    if model_a not in available_models:
        raise ValueError(f"model_a '{model_a}' not found. Available models: {available_models}")
    if model_b not in available_models:
        raise ValueError(f"model_b '{model_b}' not found. Available models: {available_models}")
    
    # Filter to just the two models
    df_filtered = df[df["model"].isin([model_a, model_b])].copy()
    
    # Check for question_id
    has_qid = "question_id" in df_filtered.columns
    
    # Pivot responses
    if has_qid:
        wide_response = df_filtered.pivot(
            index=["question_id", "prompt"],
            columns="model",
            values="model_response"
        ).reset_index()
    else:
        wide_response = df_filtered.pivot(
            index="prompt",
            columns="model",
            values="model_response"
        ).reset_index()
    
    # Initialize score series
    score_a = pd.Series(dtype=object)
    score_b = pd.Series(dtype=object)
    
    # Handle scores
    if score_columns:
        # User specified score columns - pivot each one
        for col in score_columns:
            if col not in df_filtered.columns:
                raise ValueError(f"Score column '{col}' not found in dataframe")
        
        # Pivot all score columns at once
        if has_qid:
            wide_scores = df_filtered.pivot(
                index=["question_id", "prompt"],
                columns="model",
                values=score_columns
            ).reset_index()
        else:
            wide_scores = df_filtered.pivot(
                index="prompt",
                columns="model",
                values=score_columns
            ).reset_index()
        
        # Build score dictionaries from pivoted columns
        def build_score_dict(row, model, cols):
            score_dict = {}
            for col in cols:
                # MultiIndex column access for pivoted data
                if (col, model) in wide_scores.columns:
                    val = row[(col, model)] if isinstance(row, pd.Series) else wide_scores.loc[row.name, (col, model)]
                    if pd.notna(val):
                        score_dict[col] = val
            return score_dict
        
        # Apply to create score_a and score_b
        if len(score_columns) > 1:
            # Multiple score columns create MultiIndex
            score_a = wide_scores.apply(lambda row: build_score_dict(row, model_a, score_columns), axis=1)
            score_b = wide_scores.apply(lambda row: build_score_dict(row, model_b, score_columns), axis=1)
        else:
            # Single score column might not create MultiIndex
            col = score_columns[0]
            if (col, model_a) in wide_scores.columns:
                score_a = wide_scores[(col, model_a)].apply(lambda x: {col: x} if pd.notna(x) else {})
                score_b = wide_scores[(col, model_b)].apply(lambda x: {col: x} if pd.notna(x) else {})
            elif model_a in wide_scores.columns:
                # No MultiIndex (shouldn't happen with pivot, but just in case)
                score_a = wide_scores[model_a].apply(lambda x: {col: x} if pd.notna(x) else {})
                score_b = wide_scores[model_b].apply(lambda x: {col: x} if pd.notna(x) else {})
    
    elif "score" in df_filtered.columns:
        # User has a score column (could be dict or scalar)
        if has_qid:
            wide_score = df_filtered.pivot(
                index=["question_id", "prompt"],
                columns="model",
                values="score"
            ).reset_index()
        else:
            wide_score = df_filtered.pivot(
                index="prompt",
                columns="model",
                values="score"
            ).reset_index()
        
        if model_a in wide_score.columns:
            score_a = wide_score[model_a]
        if model_b in wide_score.columns:
            score_b = wide_score[model_b]
    
    # Build the side-by-side schema
    base = {
        "prompt": wide_response["prompt"],
        "model_a": model_a,
        "model_b": model_b,
        "model_a_response": wide_response[model_a],
        "model_b_response": wide_response[model_b],
    }
    
    # Add scores if they exist
    if isinstance(score_a, pd.Series) and not score_a.empty:
        base["score_a"] = score_a.values
    if isinstance(score_b, pd.Series) and not score_b.empty:
        base["score_b"] = score_b.values
    
    if has_qid:
        base = {"question_id": wide_response["question_id"], **base}
    
    sxs = pd.DataFrame(base)
    return sxs


def validate_and_prepare_dataframe(
    df: pd.DataFrame,
    method: str,
    *,
    score_columns: Optional[List[str]] = None,
    sample_size: Optional[int] = None,
    model_a: Optional[str] = None,
    model_b: Optional[str] = None,
    verbose: bool = True,
    **kwargs
) -> pd.DataFrame:
    """
    Main preprocessing entry point - handles all data preparation steps.
    
    This function orchestrates the complete data preparation pipeline:
    1. Convert tidy to side-by-side if model_a/model_b specified
    2. Convert score_columns to score dicts if specified
    3. Sample data if sample_size specified
    4. Validate required columns exist
    
    Args:
        df: Input dataframe
        method: Either "single_model" or "side_by_side"
        score_columns: Optional list of column names containing scores to convert to dict format
        sample_size: Optional number of rows to sample
        model_a: For tidy→side_by_side conversion, first model name
        model_b: For tidy→side_by_side conversion, second model name
        verbose: Whether to print progress messages
        **kwargs: Additional arguments (ignored, for forward compatibility)
        
    Returns:
        Preprocessed dataframe ready for PropertyDataset.from_dataframe()
        
    Raises:
        ValueError: If data validation fails
    """
    df = df.copy()
    
    # Step 1: Convert tidy to side-by-side if needed
    if method == "side_by_side" and model_a is not None and model_b is not None:
        if verbose:
            logger.info(f"Converting tidy data to side-by-side format (model_a={model_a}, model_b={model_b})")
        df = tidy_to_side_by_side(df, model_a=model_a, model_b=model_b, score_columns=score_columns)
        # Note: if score_columns was provided, tidy_to_side_by_side already created score_a/score_b dicts
        # So we should skip score column conversion below
        score_columns_already_converted = score_columns is not None
    else:
        score_columns_already_converted = False
    
    # Step 2: Convert score_columns to score dict if specified (and not already done)
    if score_columns and not score_columns_already_converted:
        if verbose:
            logger.info(f"Converting score columns {score_columns} to dictionary format")
        df = convert_score_columns_to_dict(df, score_columns, method)
    
    # Step 3: Sample data if requested
    if sample_size is not None and sample_size > 0 and sample_size < len(df):
        if verbose:
            logger.info(f"Sampling evenly by prompts for target size {sample_size} from {len(df)} total rows")
        df = sample_prompts_evenly(
            df,
            sample_size=int(sample_size),
            method=method,
            prompt_column="prompt",
            random_state=42
        )
        if verbose:
            logger.info(f"After sampling: {len(df)} rows")
    
    # Step 4: Basic validation
    if method == "single_model":
        required = ["prompt", "model", "model_response"]
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"Single model format requires columns: {required}. Missing: {missing}")
    
    elif method == "side_by_side":
        required = ["prompt", "model_a", "model_b", "model_a_response", "model_b_response"]
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"Side-by-side format requires columns: {required}. Missing: {missing}")
    
    return df


__all__ = [
    "convert_score_columns_to_dict",
    "sample_prompts_evenly",
    "tidy_to_side_by_side",
    "validate_and_prepare_dataframe",
]

