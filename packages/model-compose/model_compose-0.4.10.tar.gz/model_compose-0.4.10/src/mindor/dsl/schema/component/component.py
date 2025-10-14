from typing import Type, Union, Literal, Optional, Dict, List, Tuple, Set, Annotated, Any
from pydantic import BaseModel, Field
from .impl import *

ComponentConfig = Annotated[
    Union[ 
        HttpServerComponentConfig, 
        HttpClientComponentConfig,
        McpServerComponentConfig,
        McpClientComponentConfig,
        ModelComponentConfig,
        DatasetsComponentConfig,
        VectorStoreComponentConfig,
        WorkflowComponentConfig,
        ShellComponentConfig,
        TextSplitterComponentConfig,
        ImageProcessorComponentConfig
    ],
    Field(discriminator="type")
]
