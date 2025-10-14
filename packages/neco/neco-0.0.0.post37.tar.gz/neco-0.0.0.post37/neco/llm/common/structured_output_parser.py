import json
from typing import Type, TypeVar

import json_repair
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
from loguru import logger

from neco.core.utils.template_loader import TemplateLoader

T = TypeVar('T', bound=BaseModel)


class StructuredOutputParser:
    """结构化输出解析器 - 统一使用聊天模式"""

    # 需要禁用thinking模式的模型列表（可以是模型名称的部分匹配）
    THINKING_DISABLED_MODELS = [
        "Qwen",  # Qwen系列模型
    ]

    def __init__(self, llm):
        """
        初始化结构化输出解析器

        Args:
            llm: LangChain LLM实例
        """
        self.llm = llm
        
        # 根据配置决定是否禁用thinking模式
        self._configure_thinking_mode()

    def _configure_thinking_mode(self):
        """根据模型配置决定是否禁用thinking模式"""
        model_name = getattr(self.llm, 'model_name', '') or getattr(self.llm, 'model', '')
        
        # 检查当前模型是否在需要禁用thinking的列表中
        should_disable = any(
            disabled_model.lower() in str(model_name).lower() 
            for disabled_model in self.THINKING_DISABLED_MODELS
        )
        
        if should_disable:
            if not hasattr(self.llm, 'extra_body') or self.llm.extra_body is None:
                self.llm.extra_body = {}
            self.llm.extra_body["enable_thinking"] = False

    def _build_schema_prompt(self, pydantic_class: Type[T]) -> str:
        """
        构建包含Pydantic模型schema的提示

        Args:
            pydantic_class: Pydantic模型类

        Returns:
            str: 格式化的schema提示
        """
        try:
            schema = pydantic_class.model_json_schema()

            # 构建字段信息
            fields = {}
            if 'properties' in schema:
                required_fields = set(schema.get('required', []))
                for field_name, field_info in schema['properties'].items():
                    fields[field_name] = {
                        'type': field_info.get('type', 'unknown'),
                        'description': field_info.get('description', '无描述'),
                        'required': field_name in required_fields
                    }

            template_data = {
                'model_name': pydantic_class.__name__,
                'description': schema.get('description'),
                'schema_json': json.dumps(schema, indent=2, ensure_ascii=False),
                'fields': fields
            }

            prompt = TemplateLoader.render_template(
                'prompts/graph/structured_output_schema', template_data)
            return prompt

        except Exception as e:
            logger.error(f"构建schema提示失败: {e}, 模型: {pydantic_class.__name__}")
            raise

    async def parse_with_structured_output(self, user_message: str, pydantic_class: Type[T]) -> T:
        """
        使用聊天模式进行结构化输出解析

        Args:
            user_message: 用户消息内容
            pydantic_class: 目标Pydantic模型类

        Returns:
            T: 解析后的Pydantic模型实例

        Raises:
            ValueError: 解析失败时抛出
        """
        response_text = ""
        try:
            # 构建schema提示
            schema_prompt = self._build_schema_prompt(pydantic_class)

            # 构建聊天消息列表
            chat_messages = [
                HumanMessage(content=user_message),
                HumanMessage(content=schema_prompt)
            ]

            # 调用LLM - 如果因为参数问题失败，自动清理参数重试
            try:
                response = await self.llm.ainvoke(chat_messages)
            except Exception as e:
                error_msg = str(e).lower()
                # 检查是否是参数相关错误
                if any(keyword in error_msg for keyword in ["unrecognized request argument", "enable_thinking", "invalid_request_error"]):
                    logger.warning(f"检测到参数错误，清理extra_body后重试: {e}")
                    # 清理可能有问题的参数
                    if hasattr(self.llm, 'extra_body') and self.llm.extra_body:
                        self.llm.extra_body.pop("enable_thinking", None)
                    response = await self.llm.ainvoke(chat_messages)
                else:
                    raise

            response_text = response.content

            # 解析JSON响应
            data = json_repair.loads(response_text)
            result = pydantic_class.model_validate(data)
            
            return result

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"JSON解析失败: {e}, 响应内容: {response_text}")
            raise ValueError(f"JSON解析失败: {e}")
        except Exception as e:
            logger.error(f"结构化输出解析失败: {e}, 响应内容: {response_text}")
            raise ValueError(f"解析结构化输出失败: {e}")
