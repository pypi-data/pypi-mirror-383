from typing import Type, Union, Literal, Optional, Dict, List, Tuple, Set, Annotated, Any
from mindor.dsl.schema.component import McpClientComponentConfig
from mindor.dsl.schema.action import ActionConfig, McpClientActionConfig
from mindor.core.utils.mcp_client import McpClient, ContentBlock, TextContent, ImageContent, AudioContent
from ..base import ComponentService, ComponentType, ComponentGlobalConfigs, register_component
from ..context import ComponentActionContext

class McpClientAction:
    def __init__(self, config: McpClientActionConfig):
        self.config: McpClientActionConfig = config

    async def run(self, context: ComponentActionContext, client: McpClient) -> Any:
        tool      = await context.render_variable(self.config.tool)
        arguments = await context.render_variable(self.config.arguments)

        response = [ await self._convert_output_value(content) for content in await client.call_tool(tool, arguments) ]
        context.register_source("response", response)

        return (await context.render_variable(self.config.output, ignore_files=True)) if self.config.output else response

    async def _convert_output_value(self, content: ContentBlock) -> Any:
        if isinstance(content, TextContent):
            return content.text

        if isinstance(content, (ImageContent, AudioContent)):
            return content.data

        return None

@register_component(ComponentType.MCP_CLIENT)
class McpClientComponent(ComponentService):
    def __init__(self, id: str, config: McpClientComponentConfig, global_configs: ComponentGlobalConfigs, daemon: bool):
        super().__init__(id, config, global_configs, daemon)

        self.client: Optional[McpClient] = None 

    async def _start(self) -> None:
        self.client = McpClient(self.config.url, self.config.headers)
        await super()._start()

    async def _stop(self) -> None:
        await super()._stop()
        await self.client.close()
        self.client = None

    async def _run(self, action: ActionConfig, context: ComponentActionContext) -> Any:
        return await McpClientAction(action).run(context, self.client)
