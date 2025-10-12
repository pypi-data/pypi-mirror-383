"""
Public API for LMM-Vibes.

This module provides the main explain() function that users will interact with.
"""

from typing import Dict, List, Any, Callable, Optional, Union, Tuple
import pandas as pd
from .core.data_objects import PropertyDataset
from .pipeline import Pipeline, PipelineBuilder
from .prompts import get_default_system_prompt, single_model_system_prompt_custom
from .utils.validation import validate_openai_api_key
from .logging_config import get_logger
import time

logger = get_logger(__name__)


def extract_properties_only(
    df: pd.DataFrame,
    *,
    method: str = "single_model",
    system_prompt: str | None = None,
    task_description: str | None = None,
    # Extraction parameters
    model_name: str = "gpt-4.1",
    temperature: float = 0.7,
    top_p: float = 0.95,
    max_tokens: int = 16000,
    max_workers: int = 16,
    include_scores_in_prompt: bool = True,
    # Logging & output
    use_wandb: bool = False,
    wandb_project: str | None = None,
    verbose: bool = True,
    output_dir: str | None = None,
    # Caching
    extraction_cache_dir: str | None = None,
    return_debug: bool = False,
) -> PropertyDataset | tuple[PropertyDataset, list[dict[str, Any]]]:
    """Run only the extraction → parsing → validation stages and return a PropertyDataset.

    Args:
        df: Input conversations dataframe (single_model or side_by_side format)
        method: "single_model" | "side_by_side"
        system_prompt: Explicit system prompt text or a short prompt name from stringsight.prompts
        task_description: Optional task-aware description (used only if the chosen prompt has {task_description})
        model_name, temperature, top_p, max_tokens, max_workers: LLM config for extraction
        include_scores_in_prompt: Whether to include any provided score fields in the prompt context
        use_wandb, wandb_project, verbose: Logging configuration
        output_dir: If provided, stages will auto-save their artefacts to this directory
        extraction_cache_dir: Optional cache directory for extractor

    Returns:
        PropertyDataset containing parsed Property objects (no clustering or metrics).
    """
    # Validate OpenAI API key is set if using GPT models
    validate_openai_api_key(
        model_name=model_name
    )
    
    # Resolve system prompt
    if system_prompt is None:
        contains_score = _check_contains_score(df, method)
        if method == "single_model" and task_description:
            system_prompt = single_model_system_prompt_custom.format(task_description=task_description)
            if verbose:
                logger.info(f"Using custom single-model system prompt with task_description (contains_score={contains_score})")
        else:
            system_prompt = get_default_system_prompt(method, contains_score)
            if verbose:
                logger.info(f"Auto-selected system prompt for method '{method}' (contains_score={contains_score})")
    else:
        # Treat short strings as prompt names and resolve from stringsight.prompts
        if len(system_prompt) < 50:
            try:
                from . import prompts
                system_prompt = getattr(prompts, system_prompt)
            except AttributeError:
                from inspect import getmembers
                available_prompts = sorted([
                    name for name, value in getmembers(prompts)
                    if isinstance(value, str) and 'prompt' in name
                ])
                raise ValueError(f"Unknown prompt name: '{system_prompt}'. Available prompts: {available_prompts}")
        if "{task_description}" in system_prompt and task_description is not None:
            system_prompt = system_prompt.format(task_description=task_description)

    if verbose:
        logger.info("\n" + "="*80)
        logger.info("SYSTEM PROMPT")
        logger.info("="*80)
        logger.info(system_prompt)
        logger.info("="*80 + "\n")
    if len(system_prompt) < 50:
        raise ValueError("System prompt is too short. Please provide a longer system prompt.")

    # Prepare dataset
    dataset = PropertyDataset.from_dataframe(df, method=method)

    # Align env with wandb toggle early
    import os as _os
    if not use_wandb:
        _os.environ["WANDB_DISABLED"] = "true"
    else:
        _os.environ.pop("WANDB_DISABLED", None)

    # Build a minimal pipeline: extractor → parser → validator
    from .extractors import get_extractor
    from .postprocess import LLMJsonParser, PropertyValidator

    common_cfg = {"verbose": verbose, "use_wandb": use_wandb, "wandb_project": wandb_project or "lmm-vibes"}

    extractor_kwargs = {
        "model_name": model_name,
        "system_prompt": system_prompt,
        "prompt_builder": None,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "max_workers": max_workers,
        "include_scores_in_prompt": include_scores_in_prompt,
        "output_dir": output_dir,
        **({"cache_dir": extraction_cache_dir} if extraction_cache_dir else {}),
        **common_cfg,
    }

    extractor = get_extractor(**extractor_kwargs)
    # Do not fail the whole run on parsing errors – collect failures and drop those rows
    parser = LLMJsonParser(fail_fast=False, output_dir=output_dir, **common_cfg)
    validator = PropertyValidator(output_dir=output_dir, **common_cfg)

    pipeline = PipelineBuilder(name=f"LMM-Vibes-extract-{method}") \
        .extract_properties(extractor) \
        .parse_properties(parser) \
        .add_stage(validator) \
        .configure(output_dir=output_dir, **common_cfg) \
        .build()

    result_dataset = pipeline.run(dataset)
    if return_debug:
        try:
            failures = parser.get_parsing_failures()
        except Exception:
            failures = []
        return result_dataset, failures
    return result_dataset

def explain(
    df: pd.DataFrame,
    method: str = "single_model",
    system_prompt: str = None,
    prompt_builder: Optional[Callable[[pd.Series], str]] = None,
    task_description: Optional[str] = None,
    *,
    # Data preparation
    sample_size: Optional[int] = None,
    model_a: Optional[str] = None,
    model_b: Optional[str] = None,
    score_columns: Optional[List[str]] = None,
    # Extraction parameters
    model_name: str = "gpt-4.1",
    temperature: float = 0.7,
    top_p: float = 0.95,
    max_tokens: int = 16000,
    max_workers: int = 16,
    include_scores_in_prompt: bool = True,
    # Clustering parameters  
    clusterer: Union[str, "PipelineStage"] = "hdbscan",
    min_cluster_size: int | None = None,
    embedding_model: str = "text-embedding-3-small",
    prettify_labels: bool = False,
    assign_outliers: bool = False,
    # Metrics parameters
    metrics_kwargs: Optional[Dict[str, Any]] = None,
    # Caching & logging
    use_wandb: bool = True,
    wandb_project: Optional[str] = None,
    include_embeddings: bool = True,
    verbose: bool = True,
    # Output parameters
    output_dir: Optional[str] = None,
    # Pipeline configuration
    custom_pipeline: Optional[Pipeline] = None,
    # Cache configuration
    extraction_cache_dir: Optional[str] = None,
    clustering_cache_dir: Optional[str] = None,
    metrics_cache_dir: Optional[str] = None,
    **kwargs
) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    Explain model behavior patterns from conversation data.
    
    This is the main entry point for LMM-Vibes. It takes a DataFrame of conversations
    and returns the same data with extracted properties and clusters.
    
    Args:
        df: DataFrame with conversation data
        method: "side_by_side" or "single_model"
        system_prompt: System prompt for property extraction (if None, will be auto-determined)
        prompt_builder: Optional custom prompt builder function
        task_description: Optional description of the task; when provided with
            method="single_model" and no explicit system_prompt, a task-aware
            system prompt is constructed from single_model_system_prompt_custom.
        
        # Data preparation
        sample_size: Optional number of rows to sample from the dataset before processing.
                    If None, uses the entire dataset. For single_model method with balanced
                    datasets (each prompt answered by all models), automatically samples prompts
                    evenly across models. Otherwise falls back to row-level sampling.
        model_a: For side_by_side method with tidy data, specifies first model to select
        model_b: For side_by_side method with tidy data, specifies second model to select
        score_columns: Optional list of column names containing score metrics. Instead of
                    providing scores as a dictionary in a 'score' column, you can specify
                    separate columns for each metric. For single_model: columns should be
                    named like 'accuracy', 'helpfulness'. For side_by_side: columns should
                    be named like 'accuracy_a', 'accuracy_b', 'helpfulness_a', 'helpfulness_b'.
                    If provided, these columns will be converted to the expected score dict format.
        
        # Extraction parameters
        model_name: LLM model for property extraction
        temperature: Temperature for LLM
        top_p: Top-p for LLM
        max_tokens: Max tokens for LLM
        max_workers: Max parallel workers for API calls
        
        # Clustering parameters
        clusterer: Clustering method ("hdbscan", "hdbscan_native") or PipelineStage
        min_cluster_size: Minimum cluster size
        embedding_model: Embedding model ("openai" or sentence-transformer model)
        assign_outliers: Whether to assign outliers to nearest clusters
        
        # Metrics parameters
        metrics_kwargs: Additional metrics configuration
        
        # Caching & logging
        use_wandb: Whether to log to Weights & Biases
        wandb_project: W&B project name
        include_embeddings: Whether to include embeddings in output
        verbose: Whether to print progress
        
        # Output parameters
        output_dir: Directory to save results (optional). If provided, saves:
                   - clustered_results.parquet: DataFrame with all results
                   - full_dataset.json: Complete PropertyDataset (JSON format)
                   - full_dataset.parquet: Complete PropertyDataset (parquet format)
                   - model_stats.json: Model statistics and rankings
                   - summary.txt: Human-readable summary
        
        # Pipeline configuration
        custom_pipeline: Custom pipeline to use instead of default
        **kwargs: Additional configuration options
        
    Returns:
        Tuple of (clustered_df, model_stats)
        - clustered_df: Original DataFrame with added property and cluster columns
        - model_stats: Dictionary containing three DataFrames:
            - "model_cluster_scores": Per model-cluster metrics (size, proportion, quality, etc.)
            - "cluster_scores": Per cluster aggregated metrics (across all models)
            - "model_scores": Per model aggregated metrics (across all clusters)
        
    Notes on input format:
        - For method="single_model": expect columns [question_id, prompt, model, model_response, (optional) score]
        - For method="side_by_side": expect columns [question_id, prompt, model_a, model_b, model_a_response, model_b_response]
        - Alternatively, for method="side_by_side" you may pass tidy single-model-like data
          (columns [prompt, model, model_response] and optionally question_id) and specify
          `model_a` and `model_b` parameters. The function will select these two
          models and convert the input to the expected side-by-side schema.
        
    Example:
        >>> import pandas as pd
        >>> from stringsight import explain
        >>> 
        >>> # Load your conversation data
        >>> df = pd.read_csv("conversations.csv")
        >>> 
        >>> # Explain model behavior and save results
        >>> clustered_df, model_stats = explain(
        ...     df,
        ...     method="side_by_side",
        ...     min_cluster_size=20,
        ...     output_dir="results/"  # Automatically saves results
        ... )
        >>> 
        >>> # Explore the results
        >>> print(clustered_df.columns)
        >>> print(model_stats.keys())
    """
    
    # Validate OpenAI API key is set if using GPT models
    validate_openai_api_key(
        model_name=model_name,
        embedding_model=embedding_model,
        **kwargs
    )
    
    # Preprocess data: handle score_columns, sampling, tidy→side_by_side conversion
    from .core.preprocessing import validate_and_prepare_dataframe
    df = validate_and_prepare_dataframe(
        df,
        method=method,
        score_columns=score_columns,
        sample_size=sample_size,
        model_a=model_a,
        model_b=model_b,
        verbose=verbose,
    )
    
    # Auto-determine system prompt if not provided
    if system_prompt is None:
        # Check if data contains score/preference information
        contains_score = _check_contains_score(df, method)
        # If user provided task_description, use the custom template
        if task_description:
            if method == "single_model":
                system_prompt = single_model_system_prompt_custom.format(task_description=task_description)
                if verbose:
                    logger.info(f"Using custom single-model system prompt with task_description (contains_score={contains_score})")
            elif method == "side_by_side":
                from .prompts import sbs_system_prompt_custom
                system_prompt = sbs_system_prompt_custom.format(task_description=task_description)
                if verbose:
                    logger.info(f"Using custom side-by-side system prompt with task_description (contains_score={contains_score})")
        else:
            system_prompt = get_default_system_prompt(method, contains_score)
            if verbose:
                logger.info(f"Auto-selected system prompt for method '{method}' (contains_score={contains_score})")
    else:
        # If prompt is less than 50 characters, assume it's a prompt name and resolve it
        if len(system_prompt) < 50:
            try:
                from . import prompts
                system_prompt = getattr(prompts, system_prompt)
            except AttributeError:
                # Build a clear list of available prompt names (string-valued attrs containing 'prompt')
                from inspect import getmembers
                available_prompts = sorted([
                    name for name, value in getmembers(prompts)
                    if isinstance(value, str) and 'prompt' in name
                ])
                raise ValueError(f"Unknown prompt name: '{system_prompt}'. Available prompts: {available_prompts}")
        # If the resolved/explicit prompt contains a task_description placeholder, format it when provided
        if "{task_description}" in system_prompt and task_description is not None:
            system_prompt = system_prompt.format(task_description=task_description)
    
    # Print the system prompt for verification
    if verbose:
        logger.info("\n" + "="*80)
        logger.info("SYSTEM PROMPT")
        logger.info("="*80)
        logger.info(system_prompt)
        logger.info("="*80 + "\n")
    if len(system_prompt) < 50:
        raise ValueError("System prompt is too short. Please provide a longer system prompt.")
    
    # Create PropertyDataset from input DataFrame
    dataset = PropertyDataset.from_dataframe(df, method=method)
    
    # Print initial dataset information
    if verbose:
        logger.info(f"\n📋 Initial dataset summary:")
        logger.info(f"   • Conversations: {len(dataset.conversations)}")
        logger.info(f"   • Models: {len(dataset.all_models)}")
        if len(dataset.all_models) <= 20:
            logger.info(f"   • Model names: {', '.join(sorted(dataset.all_models))}")
        logger.info("")
    
    # 2️⃣  Initialize wandb if enabled (and explicitly disable via env when off)
    # Ensure environment flag aligns with the provided setting to prevent
    # accidental logging by submodules that import wandb directly.
    import os as _os
    if not use_wandb:
        _os.environ["WANDB_DISABLED"] = "true"
    else:
        _os.environ.pop("WANDB_DISABLED", None)

    # 2️⃣  Initialize wandb if enabled
    # Create run name based on input filename if available
    if use_wandb:
        try:
            import wandb
            # import weave
            import os
            
            # Try to get input filename from the DataFrame or use a default
            input_filename = "unknown_dataset"
            if hasattr(df, 'name') and df.name:
                input_filename = df.name
            elif hasattr(df, '_metadata') and df._metadata and 'filename' in df._metadata:
                input_filename = df._metadata['filename']
            else:
                # Try to infer from the DataFrame source if it has a path attribute
                # This is a fallback for when we can't determine the filename
                input_filename = f"dataset_{len(df)}_rows"
            
            # Clean the filename for wandb (remove extension, replace spaces/special chars)
            if isinstance(input_filename, str):
                # Remove file extension and clean up the name
                input_filename = os.path.splitext(os.path.basename(input_filename))[0]
                # Replace spaces and special characters with underscores
                input_filename = input_filename.replace(' ', '_').replace('-', '_')
                # Remove any remaining special characters
                import re
                input_filename = re.sub(r'[^a-zA-Z0-9_]', '', input_filename)
            
            wandb_run_name = os.path.basename(os.path.normpath(output_dir)) if output_dir else f"{input_filename}_{method}"
            
            wandb.init(
                project=wandb_project or "lmm-vibes",
                name=wandb_run_name,
                config={
                    "method": method,
                    "system_prompt": system_prompt,
                    "model_name": model_name,
                    "temperature": temperature,
                    "top_p": top_p,
                    "max_tokens": max_tokens,
                    "max_workers": max_workers,
                    "clusterer": clusterer,
                    "min_cluster_size": min_cluster_size,
                    "embedding_model": embedding_model,
                    "assign_outliers": assign_outliers,
                    "include_embeddings": include_embeddings,
                    "output_dir": output_dir,
                },
                reinit=False  # Don't reinitialize if already exists
            )
        except ImportError:
            # wandb not installed or not available
            use_wandb = False
    
    # Use custom pipeline if provided, otherwise build default pipeline
    if custom_pipeline is not None:
        pipeline = custom_pipeline
        # Ensure the custom pipeline uses the same wandb configuration
        if hasattr(pipeline, 'use_wandb'):
            pipeline.use_wandb = use_wandb
            pipeline.wandb_project = wandb_project or "lmm-vibes"
            if use_wandb:
                pipeline._wandb_ok = True  # Mark that wandb is already initialized
    else:
        pipeline = _build_default_pipeline(
            method=method,
            system_prompt=system_prompt,
            prompt_builder=prompt_builder,
            model_name=model_name,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            max_workers=max_workers,
            include_scores_in_prompt=include_scores_in_prompt,
            clusterer=clusterer,
            min_cluster_size=min_cluster_size,
            embedding_model=embedding_model,
            assign_outliers=assign_outliers,
            prettify_labels=prettify_labels,
            metrics_kwargs=metrics_kwargs,
            use_wandb=use_wandb,
            wandb_project=wandb_project,
            include_embeddings=include_embeddings,
            verbose=verbose,
            extraction_cache_dir=extraction_cache_dir,
            clustering_cache_dir=clustering_cache_dir,
            metrics_cache_dir=metrics_cache_dir,
            output_dir=output_dir,
            **kwargs
        )
    
    # 4️⃣  Execute pipeline
    result_dataset = pipeline.run(dataset)

       # Check for 0 properties before attempting to save
    if len([p for p in result_dataset.properties if p.property_description is not None]) == 0:
        raise RuntimeError(
            "\n" + "="*60 + "\n"
            "ERROR: Pipeline completed with 0 valid properties!\n"
            "="*60 + "\n"
            "This indicates that all property extraction attempts failed.\n"
            "Common causes:\n\n"
            "1. JSON PARSING FAILURES:\n"
            "   - LLM returning natural language instead of JSON\n"
            "   - Check logs above for 'Failed to parse JSON' errors\n\n"
            "2. SYSTEM PROMPT MISMATCH:\n"
            "   - Current system_prompt may not suit your data format\n"
            "   - Try a different system_prompt parameter\n\n"
            "3. API/MODEL ISSUES:\n"
            "   - OpenAI API key invalid or quota exceeded\n"
            "   - Model configuration problems\n\n"
            "Cannot save results with 0 properties.\n"
            "="*60
        )
    
    # Convert back to DataFrame format
    clustered_df = result_dataset.to_dataframe(type="all", method=method)
    model_stats = result_dataset.model_stats
    
    # Save final summary if output_dir is provided
    if output_dir is not None:
        _save_final_summary(result_dataset, clustered_df, model_stats, output_dir, verbose)
        
        # Also save the full dataset for backward compatibility with compute_metrics_only and other tools
        import pathlib
        import json
        
        output_path = pathlib.Path(output_dir)
        
        # Save full dataset as JSON
        full_dataset_json_path = output_path / "full_dataset.json"
        result_dataset.save(str(full_dataset_json_path))
        if verbose:
            logger.info(f"  ✓ Saved full dataset: {full_dataset_json_path}")
    
    # Log accumulated summary metrics from pipeline stages
    if use_wandb and hasattr(pipeline, 'log_final_summary'):
        pipeline.log_final_summary()
    
    # Log final results to wandb if enabled
    if use_wandb:
        try:
            import wandb
            # import weave
            _log_final_results_to_wandb(clustered_df, model_stats)
        except ImportError:
            # wandb not installed or not available
            use_wandb = False
    
    # Print analysis summary if verbose
    _print_analysis_summary(model_stats, max_behaviors=5)
    
    return clustered_df, model_stats


def _check_contains_score(df: pd.DataFrame, method: str) -> bool:
    """
    Check if the DataFrame contains score/preference information.
    
    Args:
        df: Input DataFrame
        method: Analysis method
        
    Returns:
        True if the data contains scores, False otherwise
    """
    if method == "side_by_side":
        if "score" in df.columns:
            # Check if score column has any non-empty, non-None values
            return df["score"].notna().any() and (df["score"] != {}).any()
        return False
    
    elif method == "single_model":
        # Check for score column
        if "score" in df.columns:
            # Check if score column has any non-empty, non-None values
            return df["score"].notna().any() and (df["score"] != {}).any()
        return False
    
    else:
        # Default to False for unknown methods
        return False


def _build_default_pipeline(
    method: str,
    system_prompt: str,
    prompt_builder: Optional[Callable],
    model_name: str,
    temperature: float,
    top_p: float,
    max_tokens: int,
    max_workers: int,
    include_scores_in_prompt: bool,
    clusterer: Union[str, "PipelineStage"],
    min_cluster_size: int,
    embedding_model: str,
    assign_outliers: bool,
    prettify_labels: bool,
    metrics_kwargs: Optional[Dict[str, Any]],
    use_wandb: bool,
    wandb_project: Optional[str],
    include_embeddings: bool,
    verbose: bool,
    extraction_cache_dir: Optional[str] = None,
    clustering_cache_dir: Optional[str] = None,
    metrics_cache_dir: Optional[str] = None,
    output_dir: Optional[str] = "./results",
    **kwargs
) -> Pipeline:
    """
    Build the default pipeline based on configuration.
    
    This function constructs the standard pipeline stages based on the user's
    configuration. It handles the complexity of importing and configuring
    the appropriate stages.
    """
    
    # Import stages (lazy imports to avoid circular dependencies)
    from .extractors import get_extractor
    from .postprocess import LLMJsonParser, PropertyValidator
    from .clusterers import get_clusterer
    from .metrics import get_metrics
    
    # Build pipeline using PipelineBuilder
    builder = PipelineBuilder(name=f"LMM-Vibes-{method}")
    
    # Configure common options
    common_config = {
        'verbose': verbose,
        'use_wandb': use_wandb,
        'wandb_project': wandb_project or "lmm-vibes"
    }
    
    # Create stage-specific output directories if output_dir is provided
    if output_dir:
        extraction_output = output_dir
        parsing_output = output_dir
        validation_output = output_dir
        clustering_output = output_dir
        metrics_output = output_dir
    else:
        extraction_output = parsing_output = validation_output = clustering_output = metrics_output = None
    
    # 1. Property extraction stage
    extractor_kwargs = {
        'model_name': model_name,
        'system_prompt': system_prompt,
        'prompt_builder': prompt_builder,
        'temperature': temperature,
        'top_p': top_p,
        'max_tokens': max_tokens,
        'max_workers': max_workers,
        'include_scores_in_prompt': include_scores_in_prompt,
        'output_dir': extraction_output,
        **common_config
    }
    
    # Add cache directory for extraction if provided
    if extraction_cache_dir:
        extractor_kwargs['cache_dir'] = extraction_cache_dir
    
    extractor = get_extractor(**extractor_kwargs)
    builder.extract_properties(extractor)
    
    # 2. JSON parsing stage
    parser_kwargs = {
        'output_dir': parsing_output,
        **common_config
    }
    parser = LLMJsonParser(**parser_kwargs)
    builder.parse_properties(parser)
    
    # 3. Property validation stage
    validator_kwargs = {
        'output_dir': validation_output,
        **common_config
    }
    validator = PropertyValidator(**validator_kwargs)
    builder.add_stage(validator)
    
    # 4. Clustering stage
    clusterer_kwargs = {
        'min_cluster_size': min_cluster_size,
        'embedding_model': embedding_model,
        'assign_outliers': assign_outliers,
        'include_embeddings': include_embeddings,
        'prettify_labels': prettify_labels,
        'output_dir': clustering_output,
        **common_config
    }
    # Default to stratified clustering by behavior_type unless overridden by caller
    if not kwargs or 'groupby_column' not in kwargs:
        clusterer_kwargs['groupby_column'] = 'behavior_type'
    # Forward any additional clusterer-specific kwargs (e.g., groupby_column)
    if kwargs:
        clusterer_kwargs.update(kwargs)
    
    # Add cache directory for clustering if provided
    if clustering_cache_dir:
        clusterer_kwargs['cache_dir'] = clustering_cache_dir
    
    if isinstance(clusterer, str):
        clusterer_stage = get_clusterer(clusterer, **clusterer_kwargs)
    else:
        clusterer_stage = clusterer
    
    builder.cluster_properties(clusterer_stage)
    
    # 5. Metrics computation stage
    metrics_kwargs = {
        'method': method,
        'output_dir': metrics_output,
        'compute_bootstrap': metrics_kwargs.get('compute_confidence_intervals', True) if metrics_kwargs else True,
        'bootstrap_samples': metrics_kwargs.get('bootstrap_samples', 100) if metrics_kwargs else 100,
        'log_to_wandb': use_wandb,
        'generate_plots': True,
        **(metrics_kwargs or {}),
        **common_config
    }
    
    # Add cache directory for metrics if provided
    if metrics_cache_dir:
        metrics_kwargs['cache_dir'] = metrics_cache_dir
    
    metrics_stage = get_metrics(**metrics_kwargs)
    builder.compute_metrics(metrics_stage)
    
    # Build and return the pipeline
    pipeline = builder.configure(output_dir=output_dir, **common_config).build()
    
    # If wandb is already initialized globally, mark the pipeline as having wandb available
    if use_wandb:
        import wandb
        # import weave
        if wandb.run is not None and hasattr(pipeline, '_wandb_ok'):
            pipeline._wandb_ok = True
    
    return pipeline


def _print_analysis_summary(model_stats: Dict[str, pd.DataFrame], max_behaviors: int = 3):
    """Print a quick analysis summary of model behaviors and performance patterns."""
    if not model_stats or "model_cluster_scores" not in model_stats:
        return
    
    model_cluster_scores = model_stats['model_cluster_scores']
    
    if model_cluster_scores.empty:
        return
    
    logger.info("\n" + "="*80)
    logger.info("📊 ANALYSIS SUMMARY")
    logger.info("="*80)
    
    for model in model_cluster_scores.model.unique():
        model_data = model_cluster_scores[model_cluster_scores.model == model]
        
        logger.info(f"\n🤖 {model}")
        logger.info("-" * 80)
        
        # Most common behaviors
        logger.info(f"\n  Most common behaviors:")
        top_behaviors = model_data.sort_values(by='proportion', ascending=False).head(max_behaviors)
        for _, row in top_behaviors.iterrows():
            cluster = row['cluster']
            proportion = row['proportion']
            logger.info(f"    • {cluster} ({proportion:.1%})")
        
        # Find quality delta columns
        score_delta_columns = [c for c in model_cluster_scores.columns 
                             if c.startswith("quality_delta_") 
                             and not c.endswith("_ci_lower") 
                             and not c.endswith("_ci_upper") 
                             and not c.endswith("_ci_mean")
                             and not c.endswith("_significant")]
        
        if score_delta_columns:
            for col in score_delta_columns:
                metric_name = col.replace("quality_delta_", "")
                
                # Behaviors leading to worse performance
                logger.info(f"\n  Behaviors leading to worse {metric_name}:")
                worst = model_data.sort_values(by=col, ascending=True).head(max_behaviors)
                for _, row in worst.iterrows():
                    cluster = row['cluster']
                    delta = row[col]
                    if pd.notna(delta):
                        logger.info(f"    • {cluster} ({delta:+.3f})")
                
                # Behaviors leading to better performance
                logger.info(f"\n  Behaviors leading to better {metric_name}:")
                best = model_data.sort_values(by=col, ascending=False).head(max_behaviors)
                for _, row in best.iterrows():
                    cluster = row['cluster']
                    delta = row[col]
                    if pd.notna(delta):
                        logger.info(f"    • {cluster} ({delta:+.3f})")
    
    logger.info("\n" + "="*80)


def _log_final_results_to_wandb(df: pd.DataFrame, model_stats: Dict[str, pd.DataFrame]):
    """Log final results to wandb."""
    try:
        import wandb
        # import weave
        
        # Log dataset summary as summary metrics (not regular metrics)
        if wandb.run is not None:
            wandb.run.summary["final_dataset_shape"] = str(df.shape)
            wandb.run.summary["final_total_conversations"] = len(df['question_id'].unique()) if 'question_id' in df.columns else len(df)
            wandb.run.summary["final_total_properties"] = len(df)
            wandb.run.summary["final_unique_models"] = len(df['model'].unique()) if 'model' in df.columns else 0
        
        # Log clustering results if present
        cluster_cols = [col for col in df.columns if 'cluster' in col.lower()]
        if cluster_cols:
            for col in cluster_cols:
                if col.endswith('_id'):
                    cluster_ids = df[col].unique()
                    n_clusters = len([c for c in cluster_ids if c is not None and c >= 0])
                    n_outliers = sum(1 for c in cluster_ids if c is not None and c < 0)
                    
                    level = "fine" if "fine" in col else "coarse" if "coarse" in col else "main"
                    # Log these as summary metrics
                    if wandb.run is not None:
                        wandb.run.summary[f"final_{level}_clusters"] = n_clusters
                        wandb.run.summary[f"final_{level}_outliers"] = n_outliers
                        wandb.run.summary[f"final_{level}_outlier_rate"] = n_outliers / len(df) if len(df) > 0 else 0

        # Handle new dataframe format
        if model_stats and isinstance(model_stats, dict):
            model_scores_df = model_stats.get("model_scores")
            cluster_scores_df = model_stats.get("cluster_scores")
            model_cluster_scores_df = model_stats.get("model_cluster_scores")
            
            # Log summary statistics
            if wandb.run is not None and model_scores_df is not None:
                wandb.run.summary["final_models_analyzed"] = len(model_scores_df)
                
                # Log model-level summary statistics
                for _, row in model_scores_df.iterrows():
                    model_name = row.get("model", "unknown")
                    size = row.get("size", 0)
                    
                    wandb.run.summary[f"model_{model_name}_total_size"] = size
                    
                    # Log quality metrics (columns starting with quality_)
                    quality_cols = [col for col in model_scores_df.columns if col.startswith("quality_") and not col.endswith("_ci_lower") and not col.endswith("_ci_upper") and not col.endswith("_ci_mean") and not col.endswith("_significant")]
                    for col in quality_cols:
                        metric_name = col.replace("quality_", "").replace("quality_delta_", "")
                        value = row.get(col)
                        if pd.notna(value):
                            wandb.run.summary[f"model_{model_name}_avg_{metric_name}"] = value
            
            if wandb.run is not None and cluster_scores_df is not None:
                wandb.run.summary["final_clusters_analyzed"] = len(cluster_scores_df)
            
            logger.info("✅ Successfully logged metrics to wandb")
            logger.info(f"   • Dataset summary metrics")
            logger.info(f"   • Clustering results")
            logger.info(f"   • Metrics: {len(model_scores_df) if model_scores_df is not None else 0} models, {len(cluster_scores_df) if cluster_scores_df is not None else 0} clusters")
            logger.info(f"   • Summary metrics logged to run summary")
    except ImportError:
        # wandb not installed or not available
        return


def _save_final_summary(
    result_dataset: PropertyDataset,
    clustered_df: pd.DataFrame,
    model_stats: Dict[str, pd.DataFrame],
    output_dir: str,
    verbose: bool = True
):
    """Save a final summary of the explain run to a text file."""
    import pathlib
    import json
    
    output_path = pathlib.Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if verbose:
        logger.info(f"\nSaving final summary to: {output_path / 'summary.txt'}")
    
    summary_path = output_path / "summary.txt"
    with open(summary_path, 'w') as f:
        f.write("LMM-Vibes Results Summary\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total conversations: {len(clustered_df['question_id'].unique()) if 'question_id' in clustered_df.columns else len(clustered_df)}\n")
        f.write(f"Total properties: {len(clustered_df)}\n")
        
        # Count models from dataframe
        model_scores_df = model_stats.get("model_scores") if model_stats else None
        num_models = len(model_scores_df) if model_scores_df is not None else 0
        f.write(f"Models analyzed: {num_models}\n")
        
        # Clustering info
        if 'property_description_cluster_id' in clustered_df.columns:
            n_clusters = len(clustered_df['property_description_cluster_id'].unique())
            f.write(f"Clusters: {n_clusters}\n")
        
        f.write(f"\nOutput files:\n")
        f.write(f"  - raw_properties.jsonl: Raw LLM responses\n")
        f.write(f"  - extraction_stats.json: Extraction statistics\n")
        f.write(f"  - extraction_samples.jsonl: Sample inputs/outputs\n")
        f.write(f"  - parsed_properties.jsonl: Parsed property objects\n")
        f.write(f"  - parsing_stats.json: Parsing statistics\n")
        f.write(f"  - parsing_failures.jsonl: Failed parsing attempts\n")
        f.write(f"  - validated_properties.jsonl: Validated properties\n")
        f.write(f"  - validation_stats.json: Validation statistics\n")
        f.write(f"  - clustered_results.jsonl: Complete clustered data\n")
        f.write(f"  - embeddings.parquet: Embeddings data\n")
        f.write(f"  - clustered_results_lightweight.jsonl: Data without embeddings\n")
        f.write(f"  - summary_table.jsonl: Clustering summary\n")
        f.write(f"  - model_cluster_scores.json: Per model-cluster combination metrics\n")
        f.write(f"  - cluster_scores.json: Per cluster metrics (aggregated across models)\n")
        f.write(f"  - model_scores.json: Per model metrics (aggregated across clusters)\n")
        f.write(f"  - full_dataset.json: Complete PropertyDataset (JSON format)\n")
        f.write(f"  - full_dataset.parquet: Complete PropertyDataset (parquet format, or .jsonl if mixed data types)\n")
        
        # Model rankings - extract from dataframes
        f.write(f"\nModel Rankings (by average quality score):\n")
        model_avg_scores = {}
        
        if model_scores_df is not None and not model_scores_df.empty:
            # Find the first quality column to use for ranking
            quality_cols = [col for col in model_scores_df.columns 
                          if col.startswith("quality_") 
                          and not col.endswith("_ci_lower") 
                          and not col.endswith("_ci_upper") 
                          and not col.endswith("_ci_mean") 
                          and not col.endswith("_significant")
                          and not col.startswith("quality_delta_")]
            
            if quality_cols:
                ranking_col = quality_cols[0]  # Use first quality metric for ranking
                for _, row in model_scores_df.iterrows():
                    model_name = row.get("model", "unknown")
                    score = row.get(ranking_col)
                    if pd.notna(score):
                        model_avg_scores[model_name] = score
        
        if model_avg_scores:
            for i, (model_name, avg_score) in enumerate(sorted(model_avg_scores.items(), key=lambda x: x[1], reverse=True)):
                f.write(f"  {i+1}. {model_name}: {avg_score:.3f}\n")
        else:
            f.write(f"  (No quality scores available)\n")
    
    if verbose:
        logger.info(f"  ✓ Saved final summary: {summary_path}")


# ------------------------------------------------------------------
# 🆕  Fixed-taxonomy "label" entry point
# ------------------------------------------------------------------

def _build_fixed_axes_pipeline(
    *,
    extractor: "FixedAxesLabeler",
    taxonomy: Dict[str, str],
    model_name: str,
    temperature: float,
    top_p: float,
    max_tokens: int,
    max_workers: int,
    metrics_kwargs: Optional[Dict[str, Any]],
    use_wandb: bool,
    wandb_project: Optional[str],
    include_embeddings: bool,
    verbose: bool,
    output_dir: Optional[str],
    extraction_cache_dir: Optional[str] = None,
    metrics_cache_dir: Optional[str] = None,
    **kwargs,
):
    """Internal helper that constructs a pipeline for *label()* calls."""

    from .postprocess import LLMJsonParser, PropertyValidator
    from .clusterers.dummy_clusterer import DummyClusterer
    from .metrics import get_metrics

    builder = PipelineBuilder(name="LMM-Vibes-fixed-axes")

    common_cfg = {"verbose": verbose, "use_wandb": use_wandb, "wandb_project": wandb_project or "lmm-vibes"}

    # 1️⃣  Extraction / labeling (use pre-created extractor)
    builder.extract_properties(extractor)

    # 2️⃣  JSON parsing
    parser = LLMJsonParser(output_dir=output_dir, fail_fast=True, **common_cfg)
    builder.parse_properties(parser)

    # 3️⃣  Validation
    validator = PropertyValidator(output_dir=output_dir, **common_cfg)
    builder.add_stage(validator)

    # 4️⃣  Dummy clustering
    dummy_clusterer = DummyClusterer(allowed_labels=list(taxonomy.keys()), output_dir=output_dir, **common_cfg)
    builder.cluster_properties(dummy_clusterer)

    # 5️⃣  Metrics (single-model only)
    metrics_stage = get_metrics(method="single_model", output_dir=output_dir, **(metrics_kwargs or {}), **({"cache_dir": metrics_cache_dir} if metrics_cache_dir else {}), **common_cfg)
    builder.compute_metrics(metrics_stage)

    return builder.configure(output_dir=output_dir, **common_cfg).build()


def label(
    df: pd.DataFrame,
    *,
    taxonomy: Dict[str, str],
    sample_size: Optional[int] = None,
    score_columns: Optional[List[str]] = None,
    model_name: str = "gpt-4.1",
    temperature: float = 0.0,
    top_p: float = 1.0,
    max_tokens: int = 2048,
    max_workers: int = 8,
    metrics_kwargs: Optional[Dict[str, Any]] = None,
    use_wandb: bool = True,
    wandb_project: Optional[str] = None,
    include_embeddings: bool = True,
    verbose: bool = True,
    output_dir: Optional[str] = None,
    extraction_cache_dir: Optional[str] = None,
    metrics_cache_dir: Optional[str] = None,
    **kwargs,
) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """Run the *fixed-taxonomy* analysis pipeline. This is just you're run of the mill LLM-judge with a given rubric. 

    The user provides a dataframe with a model and its responses alone with a taxonomy.

    Unlike :pyfunc:`explain`, this entry point does **not** perform clustering;
    each taxonomy label simply becomes its own cluster.  The input `df` **must**
    be in *single-model* format (columns `question_id`, `prompt`, `model`, `model_response`, …).
    
    Args:
        df: DataFrame with single-model conversation data
        taxonomy: Dictionary mapping label names to their descriptions
        sample_size: Optional number of rows to sample from the dataset before processing.
                    If None, uses the entire dataset. For balanced datasets (each prompt answered
                    by all models), automatically samples prompts evenly across models.
        score_columns: Optional list of column names containing score metrics. Instead of
                    providing scores as a dictionary in a 'score' column, you can specify
                    separate columns for each metric (e.g., ['accuracy', 'helpfulness']).
                    If provided, these columns will be converted to the expected score dict format.
        model_name: LLM model for property extraction (default: "gpt-4.1")
        temperature: Temperature for LLM (default: 0.0)
        top_p: Top-p for LLM (default: 1.0)
        max_tokens: Max tokens for LLM (default: 2048)
        max_workers: Max parallel workers for API calls (default: 8)
        metrics_kwargs: Additional metrics configuration
        use_wandb: Whether to log to Weights & Biases (default: True)
        wandb_project: W&B project name
        include_embeddings: Whether to include embeddings in output (default: True)
        verbose: Whether to print progress (default: True)
        output_dir: Directory to save results (optional)
        extraction_cache_dir: Cache directory for extraction results
        metrics_cache_dir: Cache directory for metrics results
        **kwargs: Additional configuration options
    
    Returns:
        Tuple of (clustered_df, model_stats)
        - clustered_df: Original DataFrame with added property and cluster columns
        - model_stats: Dictionary containing three DataFrames:
            - "model_cluster_scores": Per model-cluster metrics (size, proportion, quality, etc.)
            - "cluster_scores": Per cluster aggregated metrics (across all models)
            - "model_scores": Per model aggregated metrics (across all clusters)
    """

    method = "single_model"  # hard-coded, we only support single-model here

    # Align environment with wandb toggle early to avoid accidental logging on import
    import os as _os
    if not use_wandb:
        _os.environ["WANDB_DISABLED"] = "true"
    else:
        _os.environ.pop("WANDB_DISABLED", None)
    if "model_b" in df.columns:
        raise ValueError("label() currently supports only single-model data.  Use explain() for side-by-side analyses.")

    # Preprocess data: handle score_columns and sampling
    from .core.preprocessing import validate_and_prepare_dataframe
    df = validate_and_prepare_dataframe(
        df,
        method=method,
        score_columns=score_columns,
        sample_size=sample_size,
        verbose=verbose,
    )

    # ------------------------------------------------------------------
    # Create extractor first to get the system prompt
    # ------------------------------------------------------------------
    from .extractors.fixed_axes_labeler import FixedAxesLabeler
    
    # Create the extractor to generate the system prompt from taxonomy
    extractor = FixedAxesLabeler(
        taxonomy=taxonomy,
        model=model_name,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        max_workers=max_workers,
        cache_dir=extraction_cache_dir or ".cache/stringsight",
        output_dir=output_dir,
        verbose=verbose,
        use_wandb=use_wandb,
        wandb_project=wandb_project or "lmm-vibes"
    )
    
    # Print the system prompt for verification
    if verbose:
        logger.info("\n" + "="*80)
        logger.info("SYSTEM PROMPT")
        logger.info("="*80)
        logger.info(extractor.system_prompt)
        logger.info("="*80 + "\n")
    
    # ------------------------------------------------------------------
    # Build dataset & pipeline
    # ------------------------------------------------------------------
    dataset = PropertyDataset.from_dataframe(df, method=method)

    # Initialize wandb if enabled
    if use_wandb:
        try:
            import wandb
            # import weave
            import os
            
            # Try to get input filename from the DataFrame or use a default
            input_filename = "unknown_dataset"
            if hasattr(df, 'name') and df.name:
                input_filename = df.name
            elif hasattr(df, '_metadata') and df._metadata and 'filename' in df._metadata:
                input_filename = df._metadata['filename']
            else:
                # Try to infer from the DataFrame source if it has a path attribute
                # This is a fallback for when we can't determine the filename
                input_filename = f"dataset_{len(df)}_rows"
            
            # Clean the filename for wandb (remove extension, replace spaces/special chars)
            if isinstance(input_filename, str):
                # Remove file extension and clean up the name
                input_filename = os.path.splitext(os.path.basename(input_filename))[0]
                # Replace spaces and special characters with underscores
                input_filename = input_filename.replace(' ', '_').replace('-', '_')
                # Remove any remaining special characters
                import re
                input_filename = re.sub(r'[^a-zA-Z0-9_]', '', input_filename)
            
            wandb_run_name = os.path.basename(os.path.normpath(output_dir)) if output_dir else f"{input_filename}_label"
            
            wandb.init(
                project=wandb_project or "lmm-vibes",
                name=wandb_run_name,
                config={
                    "method": method,
                    "model_name": model_name,
                    "temperature": temperature,
                    "top_p": top_p,
                    "max_tokens": max_tokens,
                    "max_workers": max_workers,
                    "taxonomy_size": len(taxonomy),
                    "include_embeddings": include_embeddings,
                    "output_dir": output_dir,
                },
                reinit=False  # Don't reinitialize if already exists
            )
        except ImportError:
            # wandb not installed or not available
            use_wandb = False

    pipeline = _build_fixed_axes_pipeline(
        extractor=extractor,
        taxonomy=taxonomy,
        model_name=model_name,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        max_workers=max_workers,
        metrics_kwargs=metrics_kwargs,
        use_wandb=use_wandb,
        wandb_project=wandb_project,
        include_embeddings=include_embeddings,
        verbose=verbose,
        output_dir=output_dir,
        extraction_cache_dir=extraction_cache_dir,
        metrics_cache_dir=metrics_cache_dir,
        **kwargs,
    )

    # ------------------------------------------------------------------
    # Execute
    # ------------------------------------------------------------------
    result_dataset = pipeline.run(dataset)
    clustered_df = result_dataset.to_dataframe(type="clusters", method=method)

    # Save final summary and full dataset if output_dir is provided (same as explain() function)
    if output_dir is not None:
        _save_final_summary(result_dataset, clustered_df, result_dataset.model_stats, output_dir, verbose)
        
        # Also save the full dataset for backward compatibility with compute_metrics_only and other tools
        import pathlib
        import json
        
        output_path = pathlib.Path(output_dir)
        
        # Save full dataset as JSON
        full_dataset_json_path = output_path / "full_dataset.json"
        result_dataset.save(str(full_dataset_json_path))
        if verbose:
            logger.info(f"  ✓ Saved full dataset: {full_dataset_json_path}")

    # Print analysis summary if verbose
    _print_analysis_summary(result_dataset.model_stats, max_behaviors=5)
    
    return clustered_df, result_dataset.model_stats


# Convenience functions for common use cases
def explain_side_by_side(
    df: pd.DataFrame,
    system_prompt: str = None,
    tidy_side_by_side_models: Optional[Tuple[str, str]] = None,
    **kwargs
) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    Convenience function for side-by-side model comparison.
    
    Args:
        df: DataFrame with columns: model_a, model_b, model_a_response, model_b_response, winner
        system_prompt: System prompt for extraction (if None, will be auto-determined)
        **kwargs: Additional arguments passed to explain()
        
    Returns:
        Tuple of (clustered_df, model_stats)
    """
    return explain(
        df,
        method="side_by_side",
        system_prompt=system_prompt,
        tidy_side_by_side_models=tidy_side_by_side_models,
        **kwargs,
    )


def explain_single_model(
    df: pd.DataFrame,
    system_prompt: str = None,
    **kwargs
) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    Convenience function for single model analysis.
    
    Args:
        df: DataFrame with columns: model, model_response, score
        system_prompt: System prompt for extraction (if None, will be auto-determined)
        **kwargs: Additional arguments passed to explain()
        
    Returns:
        Tuple of (clustered_df, model_stats)
    """
    return explain(df, method="single_model", system_prompt=system_prompt, **kwargs)


def explain_with_custom_pipeline(
    df: pd.DataFrame,
    pipeline: Pipeline,
    method: str = "single_model"
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Explain model behavior using a custom pipeline.
    
    Args:
        df: DataFrame with conversation data
        pipeline: Custom pipeline to use
        method: "side_by_side" or "single_model"
        
    Returns:
        Tuple of (clustered_df, model_stats)
    """
    dataset = PropertyDataset.from_dataframe(df)
    result_dataset = pipeline.run(dataset)
    return result_dataset.to_dataframe(), result_dataset.model_stats


def compute_metrics_only(
    input_path: str,
    method: str = "single_model",
    output_dir: Optional[str] = None,
    metrics_kwargs: Optional[Dict[str, Any]] = None,
    use_wandb: bool = False,
    verbose: bool = True
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Run only the metrics computation stage on existing pipeline results.
    
    This function loads existing pipeline results (from extraction and clustering stages)
    and runs only the metrics computation stage. Useful for:
    - Recomputing metrics with different parameters
    - Running metrics on results from previous pipeline runs
    - Debugging metrics computation without re-running the full pipeline
    
    Args:
        input_path: Path to existing pipeline results (file or directory)
        method: "single_model" or "side_by_side"
        output_dir: Directory to save metrics results (optional)
        metrics_kwargs: Additional arguments for metrics computation
        use_wandb: Whether to enable wandb logging
        verbose: Whether to print verbose output
        
    Returns:
        Tuple of (clustered_df, model_stats)
        
    Example:
        >>> from stringsight import compute_metrics_only
        >>> 
        >>> # Run metrics on existing pipeline results
        >>> clustered_df, model_stats = compute_metrics_only(
        ...     input_path="results/previous_run/full_dataset.json",
        ...     method="single_model",
        ...     output_dir="results/metrics_only"
        ... )
        >>> 
        >>> # Or run on a directory containing pipeline outputs
        >>> clustered_df, model_stats = compute_metrics_only(
        ...     input_path="results/previous_run/",
        ...     method="side_by_side"
        ... )
    """
    from pathlib import Path
    from .metrics import get_metrics
    from .pipeline import Pipeline
    import json

    # Align environment with wandb toggle early to avoid accidental logging on import
    import os as _os
    if not use_wandb:
        _os.environ["WANDB_DISABLED"] = "true"
    else:
        _os.environ.pop("WANDB_DISABLED", None)
    
    input_path = Path(input_path)
    
    # Load existing dataset
    if input_path.is_dir():
        # Try to load from a directory containing pipeline outputs
        possible_files = [
            input_path / "full_dataset.json",
            input_path / "full_dataset.parquet", 
            input_path / "clustered_results.parquet",
            input_path / "dataset.json",
            input_path / "dataset.parquet"
        ]
        
        for file_path in possible_files:
            if file_path.exists():
                if verbose:
                    logger.info(f"Loading from: {file_path}")
                dataset = PropertyDataset.load(str(file_path))
                break
        else:
            raise FileNotFoundError(f"No recognizable dataset file found in {input_path}")
    
    elif input_path.is_file():
        # Load from a specific file
        if verbose:
            logger.info(f"Loading from: {input_path}")
        dataset = PropertyDataset.load(str(input_path))
    
    else:
        raise FileNotFoundError(f"Input path does not exist: {input_path}")
    
    # Verify we have the required data for metrics
    if not dataset.clusters:
        raise ValueError("No clusters found in the dataset. Metrics computation requires clustered data.")
    
    if not dataset.properties:
        raise ValueError("No properties found in the dataset. Metrics computation requires extracted properties.")
    
    if verbose:
        logger.info(f"Loaded dataset with:")
        logger.info(f"  - {len(dataset.conversations)} conversations")
        logger.info(f"  - {len(dataset.properties)} properties")
        logger.info(f"  - {len(dataset.clusters)} clusters")
        logger.info(f"  - Models: {dataset.all_models}")
        
        # Count unique models from conversations for verification
        unique_models = set()
        for conv in dataset.conversations:
            if isinstance(conv.model, list):
                unique_models.update(conv.model)
            else:
                unique_models.add(conv.model)
        
        logger.info(f"  - Total unique models: {len(unique_models)}")
        if len(unique_models) <= 20:
            model_list = sorted(list(unique_models))
            logger.info(f"  - Model names: {', '.join(model_list)}")
        logger.info("")
    
    # Create metrics stage
    metrics_config = {
        'method': method,
        'use_wandb': use_wandb,
        'verbose': verbose,
        **(metrics_kwargs or {})
    }
    
    # Add output directory if provided
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        metrics_config['output_dir'] = str(output_path)
    
    # Initialize wandb if enabled
    if use_wandb:
        try:
            import wandb
            # import weave
            import os
            
            # Try to get input filename from the input path
            input_filename = "unknown_dataset"
            if input_path.is_file():
                input_filename = input_path.name
            elif input_path.is_dir():
                # Try to find a recognizable dataset file in the directory
                possible_files = [
                    input_path / "full_dataset.json",
                    input_path / "full_dataset.parquet", 
                    input_path / "clustered_results.parquet",
                    input_path / "dataset.json",
                    input_path / "dataset.parquet"
                ]
                
                for file_path in possible_files:
                    if file_path.exists():
                        input_filename = file_path.name
                        break
                else:
                    # If no recognizable file found, use the directory name
                    input_filename = input_path.name
            
            # Clean the filename for wandb (remove extension, replace spaces/special chars)
            if isinstance(input_filename, str):
                # Remove file extension and clean up the name
                input_filename = os.path.splitext(os.path.basename(input_filename))[0]
                # Replace spaces and special characters with underscores
                input_filename = input_filename.replace(' ', '_').replace('-', '_')
                # Remove any remaining special characters
                import re
                input_filename = re.sub(r'[^a-zA-Z0-9_]', '', input_filename)
            
            wandb_run_name = os.path.basename(os.path.normpath(output_dir)) if output_dir else f"{input_filename}_metrics_only"
            
            wandb.init(
                project="lmm-vibes",
                name=wandb_run_name,
                config={
                    "method": method,
                    "input_path": str(input_path),
                    "output_dir": output_dir,
                    "metrics_kwargs": metrics_kwargs,
                },
                reinit=False  # Don't reinitialize if already exists
            )
        except ImportError:
            # wandb not installed or not available
            use_wandb = False
    
    metrics_stage = get_metrics(**metrics_config)
    
    # Create a minimal pipeline with just the metrics stage
    pipeline = Pipeline("Metrics-Only", [metrics_stage])
    
    # Run metrics computation
    if verbose:
        logger.info("\n" + "="*60)
        logger.info("COMPUTING METRICS")
        logger.info("="*60)
    
    result_dataset = pipeline.run(dataset)
    
    # Convert back to DataFrame format
    clustered_df = result_dataset.to_dataframe()
    model_stats = result_dataset.model_stats
    
    # Save results if output_dir is provided
    if output_dir:
        if verbose:
            logger.info(f"\nSaving results to: {output_dir}")
        
        # Use the same saving mechanism as the full pipeline
        _save_final_summary(
            result_dataset=result_dataset,
            clustered_df=clustered_df,
            model_stats=model_stats,
            output_dir=output_dir,
            verbose=verbose
        )
        
        # Print summary
        logger.info(f"\n📊 Metrics Summary:")
        logger.info(f"  - Models analyzed: {len(model_stats)}")
        
        # Handle new functional metrics format
        if model_stats and "functional_metrics" in model_stats:
            functional_metrics = model_stats["functional_metrics"]
            model_scores = functional_metrics.get("model_scores", {})
            cluster_scores = functional_metrics.get("cluster_scores", {})
            
            logger.info(f"  - Functional metrics computed:")
            logger.info(f"    • Model scores: {len(model_scores)} models")
            logger.info(f"    • Cluster scores: {len(cluster_scores)} clusters")
            
            # Print model-level summary
            for model_name, model_data in model_scores.items():
                if isinstance(model_data, dict):
                    size = model_data.get("size", 0)
                    quality = model_data.get("quality", {})
                    logger.info(f"    • {model_name}: {size} conversations")
                    if quality:
                        for metric_name, metric_value in quality.items():
                            if isinstance(metric_value, (int, float)):
                                logger.info(f"      - {metric_name}: {metric_value:.3f}")
        
        # Handle legacy format for backward compatibility
        else:
            for model_name, stats in model_stats.items():
                if "fine" in stats:
                    logger.info(f"  - {model_name}: {len(stats['fine'])} fine clusters")
                if "coarse" in stats:
                    logger.info(f"    {len(stats['coarse'])} coarse clusters")
    
    return clustered_df, model_stats 
