"""
Core data objects for LMM-Vibes pipeline.

These objects define the data contract that flows between pipeline stages.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
import pandas as pd
from pydantic import BaseModel, Field, validator
import numpy as np
import random
from stringsight.logging_config import get_logger

logger = get_logger(__name__)

def simple_to_oai_format(prompt: str, response: str) -> list:
    """
    Convert a simple prompt-response pair to OAI format.
    
    Args:
        prompt: The user's prompt/question
        response: The model's response
        
    Returns:
        List of dictionaries in OAI conversation format
    """
    return [
        {
            "role": "user",
            "content": prompt
        },
        {
            "role": "assistant", 
            "content": response
        }
    ]

def check_and_convert_to_oai_format(prompt: str, response: str) -> tuple[list, bool]:
    """
    Check if response is a string and convert to OAI format if needed.
    
    Args:
        prompt: The user's prompt/question
        response: The model's response (could be string or already OAI format)
        
    Returns:
        Tuple of (conversation_in_oai_format, was_converted)
    """
    # If response is already a list (OAI format), return as is
    if isinstance(response, list):
        return response, False
    
    # If response is a string, convert to OAI format
    if isinstance(response, str):
        return simple_to_oai_format(prompt, response), True
    
    # For other types, try to convert to string first
    try:
        response_str = str(response)
        return simple_to_oai_format(prompt, response_str), True
    except Exception:
        # If conversion fails, return as is
        return response, False


@dataclass
class ConversationRecord:
    """A single conversation with prompt, responses, and metadata."""
    question_id: str 
    prompt: str
    model: str | List[str]  # model name(s) - single string or list for side-by-side comparisons
    responses: str | List[str] # model response(s) - single string or list for side-by-side comparisons
    scores: Dict[str, Any] | List[Dict[str, Any]]     # For single model: {score_name: score_value}. For side-by-side: [scores_a, scores_b] 
    meta: Dict[str, Any] = field(default_factory=dict)  # winner, language, etc. (winner stored here for side-by-side)
    
    def __post_init__(self):
        """Migrate legacy score formats to the new list format for side-by-side."""
        # Handle migration of score_a/score_b from meta field to scores list for side-by-side
        if isinstance(self.model, list) and len(self.model) == 2:
            # Check if scores is empty and we have score_a/score_b in meta
            if (not self.scores or self.scores == {}) and ('score_a' in self.meta and 'score_b' in self.meta):
                # Migrate scores from meta to scores field
                scores_a = self.meta.pop('score_a', {})
                scores_b = self.meta.pop('score_b', {})
                self.scores = [scores_a, scores_b]

@dataclass
class Property:
    """An extracted behavioral property from a model response."""
    id: str # unique id for the property
    question_id: str
    model: str
    # Parsed fields (filled by LLMJsonParser)
    property_description: Optional[str] = None
    category: Optional[str] = None
    reason: Optional[str] = None
    evidence: Optional[str] = None
    behavior_type: Optional[str] = None # Positive|Negative (non-critical)|Negative (critical)|Style

    # Raw LLM response (captured by extractor before parsing)
    raw_response: Optional[str] = None
    contains_errors: Optional[bool] = None
    unexpected_behavior: Optional[bool] = None
    meta: Dict[str, Any] = field(default_factory=dict) # all other metadata

    def to_dict(self):
        return asdict(self)
    
    def __post_init__(self):
        """Validate property fields after initialization."""
        # Require that the model has been resolved to a known value
        if isinstance(self.model, str) and self.model.lower() == "unknown":
            raise ValueError("Property must have a known model; got 'unknown'.")

@dataclass
class Cluster:
    """A cluster of properties."""
    id: str # cluster id
    label: str # cluster label
    size: int # cluster size
    property_descriptions: List[str] = field(default_factory=list) # property descriptions in the cluster
    property_ids: List[str] = field(default_factory=list) # property ids in the cluster
    question_ids: List[str] = field(default_factory=list) # ids of the conversations in the cluster
    meta: Dict[str, Any] = field(default_factory=dict) # all other metadata

    def to_dict(self):
        return asdict(self)
    
    def to_sample_dict(self, n: int = 5):
        """Return a dictionary that samples n property descriptions and ids from the cluster."""
        return {
            "id": self.id,
            "label": self.label,
            "size": self.size,
            "parent_id": self.parent_id,
            "parent_label": self.parent_label,
            "property_descriptions": random.sample(self.property_descriptions, n),
            "question_ids": random.sample(self.question_ids, n),
            "property_ids": random.sample(self.property_ids, n),
            "meta": self.meta,
        }
    
@dataclass
class ModelStats:
    """Model statistics."""
    property_description: str # name of proprty cluster (either fine or coarse)
    model_name: str # name of model we are comparing
    score: float # score of the property cluster
    quality_score: Dict[str, Any] # quality score of the property cluster (dict with score keys and model names as keys)
    size: int # number of properties in the cluster
    proportion: float # proportion of model's properties that are in the cluster
    cluster_size: int # number of properties in the cluster
    examples: List[str] # example property id's in the cluster
    metadata: Dict[str, Any] = field(default_factory=dict) # all other metadata

    # Confidence intervals for uncertainty quantification
    score_ci: Optional[Dict[str, float]] = None  # 95% CI for distinctiveness score: {"lower": x, "upper": y}
    quality_score_ci: Optional[Dict[str, Dict[str, float]]] = None  # CI bounds for each quality score key: {"key": {"lower": x, "upper": y}}

    # Statistical significance
    score_statistical_significance: Optional[bool] = None
    quality_score_statistical_significance: Optional[Dict[str, bool]] = None

    def to_dict(self):
        return asdict(self)
    

@dataclass
class PropertyDataset:
    """
    Container for all data flowing through the pipeline.
    
    This is the single data contract between all pipeline stages.
    """
    conversations: List[ConversationRecord] = field(default_factory=list)
    all_models: List[str] = field(default_factory=list)
    properties: List[Property] = field(default_factory=list)
    clusters: List[Cluster] = field(default_factory=list)
    model_stats: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """Return a readable string representation of the PropertyDataset."""
        lines = [
            "PropertyDataset:",
            f"  conversations: List[ConversationRecord] ({len(self.conversations)} items)",
            f"  all_models: List[str] ({len(self.all_models)} items) - {self.all_models}",
            f"  properties: List[Property] ({len(self.properties)} items)",
            f"  clusters: List[Cluster] ({len(self.clusters)} items)",
            f"  model_stats: Dict[str, Any] ({len(self.model_stats)} entries)"
        ]
        
        return "\n".join(lines)
    
    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, method: str = "single_model") -> "PropertyDataset":
        """
        Create PropertyDataset from existing DataFrame formats.
        
        Args:
            df: Input DataFrame with conversation data
            method: "side_by_side" for comparison data, "single_model" for single responses
            
        Returns:
            PropertyDataset with populated conversations
        """
        conversations = []
        if method == "side_by_side":
            all_models = list(set(df["model_a"].unique().tolist() + df["model_b"].unique().tolist()))
            # Expected columns: question_id, prompt, model_a, model_b, 
            # model_a_response, model_b_response, scores_a, scores_b, winner, etc.
            for idx, row in df.iterrows():
                prompt = str(row.get('prompt', row.get('user_prompt', '')))
                model_a_response = row.get('model_a_response', '')
                model_b_response = row.get('model_b_response', '')
                
                # Convert responses to OAI format if they're strings
                oai_response_a, was_converted_a = check_and_convert_to_oai_format(prompt, model_a_response)
                oai_response_b, was_converted_b = check_and_convert_to_oai_format(prompt, model_b_response)
                
                # Convert score formats to list format [scores_a, scores_b]
                def parse_score_field(score_value):
                    """Parse score field that might be a string, dict, or other type."""
                    if isinstance(score_value, dict):
                        return score_value
                    elif isinstance(score_value, str) and score_value.strip():
                        try:
                            import ast
                            parsed = ast.literal_eval(score_value.strip())
                            return parsed if isinstance(parsed, dict) else {}
                        except (ValueError, SyntaxError):
                            return {}
                    else:
                        return {}
                
                if 'score_a' in row and 'score_b' in row:
                    # Format: score_a, score_b columns
                    scores_a = parse_score_field(row.get('score_a', {}))
                    scores_b = parse_score_field(row.get('score_b', {}))
                else:
                    # No score data found
                    scores_a, scores_b = {}, {}
                
                scores = [scores_a, scores_b]
                
                # Store winner and other metadata
                meta_with_winner = {k: v for k, v in row.items() 
                                  if k not in ['question_id', 'prompt', 'user_prompt', 'model_a', 'model_b', 
                                             'model_a_response', 'model_b_response', 'score', 'score_a', 'score_b']}
                
                # Add winner to meta if present
                winner = row.get('winner')
                if winner is not None:
                    meta_with_winner['winner'] = winner
                
                conversation = ConversationRecord(
                    question_id=str(idx),  # Auto-generate as row index
                    prompt=prompt,
                    model=[row.get('model_a', 'model_a'), row.get('model_b', 'model_b')],
                    responses=[oai_response_a, oai_response_b],
                    scores=scores,
                    meta=meta_with_winner
                )
                conversations.append(conversation)
                
        elif method == "single_model":
            all_models = df["model"].unique().tolist()
            # Expected columns: question_id, prompt, model, model_response, score, etc.
            
            def parse_single_score_field(score_value):
                """Parse single model score field that might be a string, dict, number, or other type."""
                if isinstance(score_value, dict):
                    return score_value
                elif isinstance(score_value, (int, float)):
                    return {'score': score_value}
                elif isinstance(score_value, str) and score_value.strip():
                    try:
                        import ast
                        parsed = ast.literal_eval(score_value.strip())
                        if isinstance(parsed, dict):
                            return parsed
                        elif isinstance(parsed, (int, float)):
                            return {'score': parsed}
                        else:
                            return {'score': 0}
                    except (ValueError, SyntaxError):
                        return {'score': 0}
                else:
                    return {'score': 0}
            
            for idx, row in df.iterrows():
                scores = parse_single_score_field(row.get('score'))

                prompt = str(row.get('prompt', row.get('user_prompt', '')))
                response = row.get('model_response', '')
                
                # Convert response to OAI format if it's a string
                oai_response, was_converted = check_and_convert_to_oai_format(prompt, response)
                
                conversation = ConversationRecord(
                    question_id=str(idx),  # Auto-generate as row index
                    prompt=prompt,
                    model=str(row.get('model', 'model')),
                    responses=oai_response,
                    scores=scores,
                    meta={k: v for k, v in row.items() 
                          if k not in ['question_id', 'prompt', 'user_prompt', 'model', 'model_response', 'score']}
                )
                conversations.append(conversation)
        else:
            raise ValueError(f"Unknown method: {method}. Must be 'side_by_side' or 'single_model'")
            
        return cls(conversations=conversations, all_models=all_models)
    
    def to_dataframe(self, type: str = "all", method: str = "side_by_side") -> pd.DataFrame:
        """
        Convert PropertyDataset back to DataFrame format.
        
        Returns:
            DataFrame with original data plus extracted properties and clusters
        """

        assert type in ["base", "properties", "clusters", "all"], f"Invalid type: {type}. Must be 'all' or 'base'"
        # Start with conversation data
        rows = []
        for conv in self.conversations:
            if isinstance(conv.model, str):
                base_row = {
                    'question_id': conv.question_id,
                    'prompt': conv.prompt,
                    'model': conv.model,
                    'model_response': conv.responses,
                    'score': conv.scores,
                    **conv.meta
                }
            elif isinstance(conv.model, list):
                # Side-by-side format: scores stored as [scores_a, scores_b]
                if isinstance(conv.scores, list) and len(conv.scores) == 2:
                    scores_a, scores_b = conv.scores[0], conv.scores[1]
                else:
                    # Fallback if scores isn't properly formatted
                    scores_a, scores_b = {}, {}
                
                base_row = {
                    'question_id': conv.question_id,
                    'prompt': conv.prompt,
                    'model_a': conv.model[0],
                    'model_b': conv.model[1],
                    'model_a_response': conv.responses[0],
                    'model_b_response': conv.responses[1],
                    'score_a': scores_a,
                    'score_b': scores_b,
                    'winner': conv.meta.get('winner'),  # Winner stored in meta
                    **{k: v for k, v in conv.meta.items() if k != 'winner'}  # Exclude winner from other meta
                }
            else:
                raise ValueError(f"Invalid model type: {type(conv.model)}. Must be str or list.")

            rows.append(base_row)
        
        df = pd.DataFrame(rows)
        logger.debug(f"Original unique questions: {df.question_id.nunique()}")
        
        # Add properties if they exist
        if self.properties and type in ["all", "properties", "clusters"]:
            # Create a mapping from (question_id, model) to properties
            prop_map = {}
            for prop in self.properties:
                key = (prop.question_id, prop.model)
                if key not in prop_map:
                    prop_map[key] = []
                prop_map[key].append(prop)
            
            # create property df
            prop_df = pd.DataFrame([p.to_dict() for p in self.properties])
            logger.debug(f"len of base df {len(df)}")
            if "model_a" in df.columns and "model_b" in df.columns:
                df = df.merge(prop_df, on=["question_id"], how="left").drop_duplicates(subset="id")
            else:
                # CHANGE: Use left join to preserve all conversations, including those without properties
                # Don't drop duplicates to ensure conversations without properties are preserved
                df = df.merge(prop_df, on=["question_id", "model"], how="left")
            logger.debug(f"len of df after merge with properties {len(df)}")

            # ------------------------------------------------------------------
            # Ensure `model` column is present (avoid _x / _y duplicates)
            # ------------------------------------------------------------------
            if "model" not in df.columns:
                if "model_y" in df.columns:
                    print(f"df.model_y.value_counts(): {df.model_y.value_counts()}")
                if "model_x" in df.columns:
                    print(f"df.model_x.value_counts(): {df.model_x.value_counts()}")
                if "model_x" in df.columns or "model_y" in df.columns:
                    df["model"] = df.get("model_y").combine_first(df.get("model_x"))
                    df.drop(columns=[c for c in ["model_x", "model_y"] if c in df.columns], inplace=True)
                    
        # Only print model value counts if the column exists
        if "model" in df.columns:
            logger.debug(f"df.model.value_counts() NEW: {df.model.value_counts()}")
        logger.debug(f"total questions: {df.question_id.nunique()}")

        if self.clusters and type in ["all", "clusters"]:
            # If cluster columns already exist (e.g. after reload from parquet)
            # skip the merge to avoid duplicate _x / _y columns.
            if "cluster_id" not in df.columns:
                cluster_df = pd.DataFrame([c.to_dict() for c in self.clusters])
                cluster_df.rename(
                    columns={
                        "id": "cluster_id",
                        "label": "cluster_label",
                        "size": "cluster_size",
                        "property_descriptions": "property_description",
                    },
                    inplace=True,
                )
                # Explode aligned list columns so each row maps to a single property
                list_cols = [
                    col for col in [
                        "property_description",
                        "property_ids",
                        "question_ids",
                    ] if col in cluster_df.columns
                ]
                if list_cols:
                    try:
                        cluster_df = cluster_df.explode(list_cols, ignore_index=True)
                    except TypeError:
                        # Fallback for older pandas: explode sequentially to preserve alignment
                        for col in list_cols:
                            cluster_df = cluster_df.explode(col, ignore_index=True)
                df = df.merge(cluster_df, on=["property_description"], how="left")
        
        # CHANGE: Handle conversations without properties by creating a "No properties" cluster
        # This ensures all conversations are considered in metrics calculation
        if type in ["all", "clusters"]:
            # Identify rows without properties (no property_description or it's NaN)
            mask_no_properties = df["property_description"].isna() | (df["property_description"].astype(str).str.strip() == "")

            # Only add the synthetic cluster if *all* rows lack a property description.
            # If at least one property exists, we skip to avoid mixing partially
            # processed conversations into a global "No properties" cluster.

            if mask_no_properties.all():
                logger.info("All conversations lack properties – creating 'No properties' cluster")
                
                # Fill in missing data for conversations without properties
                df.loc[mask_no_properties, "property_description"] = "No properties"
                df.loc[mask_no_properties, "cluster_id"] = -2  # Use -2 since -1 is for outliers
                df.loc[mask_no_properties, "cluster_label"] = "No properties"
                
                # Handle missing scores for conversations without properties
                mask_no_score = mask_no_properties & (df["score"].isna() | (df["score"] == {}))
                if mask_no_score.any():
                    df.loc[mask_no_score, "score"] = df.loc[mask_no_score, "score"].apply(lambda x: {"score": 0} if pd.isna(x) or x == {} else x)
        
        return df
    
    def add_property(self, property: Property):
        """Add a property to the dataset."""
        self.properties.append(property)
        if isinstance(property.model, str) and property.model not in self.all_models:
            self.all_models.append(property.model)
        if isinstance(property.model, list):
            for model in property.model:
                if model not in self.all_models:
                    self.all_models.append(model)
    
    def get_properties_for_model(self, model: str) -> List[Property]:
        """Get all properties for a specific model."""
        return [p for p in self.properties if p.model == model]
    
    def get_properties_for_question(self, question_id: str) -> List[Property]:
        """Get all properties for a specific question."""
        return [p for p in self.properties if p.question_id == question_id]

    def _json_safe(self, obj: Any):
        """Recursively convert *obj* into JSON-safe types (lists, dicts, ints, floats, strings, bool, None)."""
        if isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.generic):
            return obj.item()
        if isinstance(obj, (list, tuple, set)):
            return [self._json_safe(o) for o in obj]
        if isinstance(obj, dict):
            # Convert keys to strings if they're not JSON-safe
            json_safe_dict = {}
            for k, v in obj.items():
                # Convert tuple/list keys to string representation
                if isinstance(k, (tuple, list)):
                    safe_key = str(k)
                elif isinstance(k, (str, int, float, bool)) or k is None:
                    safe_key = k
                else:
                    safe_key = str(k)
                json_safe_dict[safe_key] = self._json_safe(v)
            return json_safe_dict

        return str(obj)

    def to_serializable_dict(self) -> Dict[str, Any]:
        """Convert the whole dataset into a JSON-serialisable dict."""
        return {
            "conversations": [self._json_safe(asdict(conv)) for conv in self.conversations],
            "properties": [self._json_safe(asdict(prop)) for prop in self.properties],
            "clusters": [self._json_safe(asdict(cluster)) for cluster in self.clusters],
            "model_stats": self._json_safe(self.model_stats),
            "all_models": self.all_models,
        }
    
    def get_valid_properties(self):
        """Get all properties where the property model is unknown, there is no property description, or the property description is empty."""
        logger.debug(f"All models: {self.all_models}")
        logger.debug(f"Properties: {self.properties[0].model}")
        logger.debug(f"Property description: {self.properties[0].property_description}")
        return [prop for prop in self.properties if prop.model in self.all_models and prop.property_description is not None and prop.property_description.strip() != ""]

    # ------------------------------------------------------------------
    # 📝 Persistence helpers
    # ------------------------------------------------------------------
    def save(self, path: str, format: str = "json") -> None:
        """Save the dataset to *path* in either ``json``, ``dataframe``, ``parquet`` or ``pickle`` format.

        The JSON variant produces a fully human-readable file while the pickle
        variant preserves the exact Python objects.
        """
        import json, pickle, os

        fmt = format.lower()
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

        if fmt == "json":
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.to_serializable_dict(), f, ensure_ascii=False, indent=2)
        elif fmt == "dataframe":
            self.to_dataframe().to_json(path, orient="records", lines=True)
        elif fmt == "parquet":
            self.to_dataframe().to_parquet(path)
        elif fmt in {"pkl", "pickle"}:
            with open(path, "wb") as f:
                pickle.dump(self, f)
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'json' or 'pickle'.")
        
    @staticmethod
    def get_all_models(conversations: List[ConversationRecord]):
        """Get all models in the dataset."""
        models = set()
        for conv in conversations:
            if isinstance(conv.model, list):
                models.update(conv.model)
            else:
                models.add(conv.model)
        return list(models)

    @classmethod
    def load(cls, path: str, format: str = "json") -> "PropertyDataset":
        """Load a dataset previously saved with :py:meth:`save`."""
        import json, pickle

        fmt = format.lower()
        logger.info(f"Loading dataset from {path} with format {fmt}")
        if fmt == "json":
            logger.info(f"Loading dataset from {path}")
            with open(path, "r") as f:
                data = json.load(f)
            logger.debug(f"Data: {data.keys()}")
            
            # Expected format: dictionary with keys like "conversations", "properties", etc.
            conversations = [ConversationRecord(**conv) for conv in data["conversations"]]
            properties = [Property(**prop) for prop in data.get("properties", [])]
            
            # Convert cluster data to Cluster objects
            clusters = [Cluster(**cluster) for cluster in data.get("clusters", [])]
            
            model_stats = data.get("model_stats", {})
            all_models = data.get("all_models", PropertyDataset.get_all_models(conversations))
            return cls(conversations=conversations, properties=properties, clusters=clusters, model_stats=model_stats, all_models=all_models)
        elif fmt == "dataframe":
            # Handle dataframe format - this creates a list of objects when saved
            import pandas as pd
            try:
                # Try to load as JSON Lines first
                df = pd.read_json(path, orient="records", lines=True)
            except ValueError:
                # If that fails, try regular JSON
                df = pd.read_json(path, orient="records")
            
            # Detect method based on columns
            method = "side_by_side" if {"model_a", "model_b"}.issubset(df.columns) else "single_model"
            
            return cls.from_dataframe(df, method=method)
        elif fmt in {"pkl", "pickle"}:
            with open(path, "rb") as f:
                obj = pickle.load(f)
            if not isinstance(obj, cls):
                raise TypeError("Pickle file does not contain a PropertyDataset object")
            return obj
        elif fmt == "parquet":
            # Load DataFrame and reconstruct minimal PropertyDataset with clusters
            import pandas as pd
            df = pd.read_parquet(path)

            # Attempt to detect method
            method = "side_by_side" if {"model_a", "model_b"}.issubset(df.columns) else "single_model"

            dataset = cls.from_dataframe(df, method=method)

            # Reconstruct Cluster objects if cluster columns are present
            required_cols = {
                "cluster_id",
                "cluster_label",
                "property_description",
            }
            if required_cols.issubset(df.columns):
                clusters_dict = {}
                for _, row in df.iterrows():
                    cid = row["cluster_id"]
                    if pd.isna(cid):
                        continue
                    cluster = clusters_dict.setdefault(
                        cid,
                        Cluster(
                            id=int(cid),
                            label=row.get("cluster_label", str(cid)),
                            size=0,
                        ),
                    )
                    cluster.size += 1
                    pd_desc = row.get("property_description")
                    if pd_desc and pd_desc not in cluster.property_descriptions:
                        cluster.property_descriptions.append(pd_desc)
                    cluster.question_ids.append(str(row.get("question_id", "")))

                dataset.clusters = list(clusters_dict.values())

            return dataset
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'json', 'dataframe', 'parquet', or 'pickle'.") 