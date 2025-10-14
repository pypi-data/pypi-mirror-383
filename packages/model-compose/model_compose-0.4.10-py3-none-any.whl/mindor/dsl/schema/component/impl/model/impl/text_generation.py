from typing import Type, Union, Literal, Optional, Dict, List, Tuple, Set, Annotated, Any
from enum import Enum
from pydantic import BaseModel, Field
from pydantic import model_validator
from mindor.dsl.schema.action import TextGenerationModelActionConfig
from .common import LanguageModelComponentConfig, ModelTaskType

class TextGenerationModelArchitecture(str, Enum):
    CAUSAL  = "causal"
    SEQ2SEQ = "seq2seq"

class TextGenerationModelComponentConfig(LanguageModelComponentConfig):
    task: Literal[ModelTaskType.TEXT_GENERATION]
    architecture: TextGenerationModelArchitecture = Field(default=TextGenerationModelArchitecture.CAUSAL, description="Model architecture.")
    actions: List[TextGenerationModelActionConfig] = Field(default_factory=list)

    @model_validator(mode="before")
    def inflate_single_action(cls, values: Dict[str, Any]):
        if "actions" not in values:
            action_keys = set(TextGenerationModelActionConfig.model_fields.keys()) - set(LanguageModelComponentConfig.model_fields.keys())
            if any(k in values for k in action_keys):
                values["actions"] = [ { k: values.pop(k) for k in action_keys if k in values } ]
        return values
