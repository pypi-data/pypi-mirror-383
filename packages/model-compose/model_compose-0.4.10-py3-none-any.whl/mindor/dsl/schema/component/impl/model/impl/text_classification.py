from typing import Type, Union, Literal, Optional, Dict, List, Tuple, Set, Annotated, Any
from pydantic import BaseModel, Field
from pydantic import model_validator
from mindor.dsl.schema.action import TextClassificationModelActionConfig
from .common import LanguageModelComponentConfig, ModelTaskType

class TextClassificationModelComponentConfig(LanguageModelComponentConfig):
    task: Literal[ModelTaskType.TEXT_CLASSIFICATION]
    labels: Optional[List[str]] = Field(default=None, description="List of text classification labels.")
    actions: List[TextClassificationModelActionConfig] = Field(default_factory=list)

    @model_validator(mode="before")
    def inflate_single_action(cls, values: Dict[str, Any]):
        if "actions" not in values:
            action_keys = set(TextClassificationModelActionConfig.model_fields.keys()) - set(LanguageModelComponentConfig.model_fields.keys())
            if any(k in values for k in action_keys):
                values["actions"] = [ { k: values.pop(k) for k in action_keys if k in values } ]
        return values
