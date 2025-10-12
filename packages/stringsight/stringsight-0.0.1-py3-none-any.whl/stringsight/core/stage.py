"""
Pipeline stage interface for LMM-Vibes.

All pipeline stages must implement the PipelineStage interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from .data_objects import PropertyDataset


class PipelineStage(ABC):
    """
    Abstract base class for all pipeline stages.
    
    Each stage takes a PropertyDataset as input and returns a PropertyDataset as output.
    This allows stages to be composed into pipelines.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize the stage with configuration parameters and propagate to mixins."""
        # Store config before passing to mixins (copy to avoid mutating original)
        self.config = dict(kwargs)
        self.name = self.__class__.__name__
        
        # Call next __init__ in MRO – no kwargs so they don't reach object.__init__
        super().__init__()
    
    @abstractmethod
    def run(self, data: PropertyDataset) -> PropertyDataset:
        """
        Process the input data and return the modified data.
        
        Args:
            data: Input PropertyDataset
            
        Returns:
            Modified PropertyDataset
        """
        pass
    
    def validate_input(self, data: PropertyDataset) -> None:
        """
        Validate that the input data meets the requirements for this stage.
        
        Args:
            data: Input PropertyDataset
            
        Raises:
            ValueError: If the input data is invalid
        """
        if not isinstance(data, PropertyDataset):
            raise ValueError(f"Input must be a PropertyDataset, got {type(data)}")
    
    def validate_output(self, data: PropertyDataset) -> None:
        """
        Validate that the output data is valid.
        
        Args:
            data: Output PropertyDataset
            
        Raises:
            ValueError: If the output data is invalid
        """
        if not isinstance(data, PropertyDataset):
            raise ValueError(f"Output must be a PropertyDataset, got {type(data)}")
    
    def __call__(self, data: PropertyDataset) -> PropertyDataset:
        """
        Convenience method to run the stage.
        
        This allows stages to be called directly: stage(data)
        """
        self.validate_input(data)
        result = self.run(data)
        self.validate_output(result)
        return result
    
    def __repr__(self) -> str:
        return f"{self.name}({self.config})"


class PassthroughStage(PipelineStage):
    """A stage that passes data through unchanged. Useful for testing."""
    
    def run(self, data: PropertyDataset) -> PropertyDataset:
        return data 