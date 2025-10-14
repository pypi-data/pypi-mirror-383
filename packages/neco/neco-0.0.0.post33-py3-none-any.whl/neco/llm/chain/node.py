from typing import Dict, Any, List, Literal, Optional, TypedDict, Union

import json_repair
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from neco.core.utils.template_loader import TemplateLoader
from loguru import logger
from neco.llm.chain.entity import BasicLLMRequest
from neco.llm.common.structured_output_parser import StructuredOutputParser
from neco.llm.rag.graph_rag.graphiti.graphiti_rag import GraphitiRAG
from neco.llm.rag.naive_rag.pgvector.pgvector_rag import PgvectorRag
from neco.llm.tools.tools_loader import ToolsLoader
from pydantic import BaseModel
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph
from langgraph.constants import END
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage

class BasicNode:
        
    def log(self, config: RunnableConfig, message: str):
        trace_id = config["configurable"]['trace_id']
        logger.debug(f"[{trace_id}] {message}")

    def get_llm_client(self, request: BasicLLMRequest, disable_stream=False) -> ChatOpenAI:
        llm = ChatOpenAI(model=request.model, base_url=request.openai_api_base,
                         disable_streaming=disable_stream,
                         timeout=3000,
                         api_key=request.openai_api_key, temperature=request.temperature)
        if llm.extra_body is None:
            llm.extra_body = {}

        if disable_stream and 'qwen' in request.model.lower():
            llm.extra_body["enable_thinking"] = False
        return llm

    def prompt_message_node(self, state: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
        system_message_prompt = TemplateLoader.render_template('prompts/graph/base_node_system_message', {
            "user_system_message": config["configurable"]["graph_request"].system_message_prompt
        })

        state["messages"].append(
            SystemMessage(content=system_message_prompt)
        )

        return state

    def suggest_question_node(self, state: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
        if config["configurable"]["graph_request"].enable_suggest:
            suggest_question_prompt = TemplateLoader.render_template(
                'prompts/graph/suggest_question_prompt', {})
            state["messages"].append(SystemMessage(
                content=suggest_question_prompt))
        return state

    def add_chat_history_node(self, state: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
        if config["configurable"]['graph_request'].chat_history:
            for chat in config["configurable"]['graph_request'].chat_history:
                if chat.event == 'user':
                    if chat.image_data:
                        state['messages'].append(HumanMessage(content=[
                            {"type": "text", "text": "describe the weather in this image"},
                            {"type": "image_url", "image_url": {
                                "url": chat.image_data}},
                        ]))
                    else:
                        state['messages'].append(
                            HumanMessage(content=chat.message))
                elif chat.event == 'assistant':
                    state['messages'].append(AIMessage(content=chat.message))
        return state

    async def naive_rag_node(self, state: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
        naive_rag_request = config["configurable"]["graph_request"].naive_rag_request
        if len(naive_rag_request) == 0:
            return state

        # 智能知识路由选择
        selected_knowledge_ids = []
        if 'km_info' in config["configurable"]:
            selected_knowledge_ids = self._select_knowledge_ids(config)

        rag_result = []

        for rag_search_request in naive_rag_request:
            rag_search_request.search_query = config["configurable"]["graph_request"].graph_user_message

            if len(selected_knowledge_ids) != 0 and rag_search_request.index_name not in selected_knowledge_ids:
                logger.info(
                    f"智能知识路由判断:[{rag_search_request.index_name}]不适合当前问题,跳过检索")
                continue
            
            rag = PgvectorRag(config["configurable"]["naive_rag_db_url"])
            naive_rag_search_result = rag.search(rag_search_request)

            rag_documents = []
            for doc in naive_rag_search_result:
                # 根据 is_doc 字段处理文档内容
                processed_doc = self._process_document_content(doc)
                rag_documents.append(processed_doc)

            rag_result.extend(rag_documents)

            # 执行图谱 RAG 检索
            if rag_search_request.enable_graph_rag:
                graph_results = await self._execute_graph_rag(rag_search_request,config)
                rag_result.extend(graph_results)

        # 准备模板数据
        template_data = self._prepare_template_data(rag_result, config)

        # 使用模板生成 RAG 消息
        rag_message = TemplateLoader.render_template(
            'prompts/graph/naive_rag_node_prompt', template_data)

        logger.info(f"RAG增强Prompt: {rag_message}")
        state["messages"].append(HumanMessage(content=rag_message))
        return state

    def _select_knowledge_ids(self, config: RunnableConfig) -> list:
        """智能知识路由选择"""
        km_info = config["configurable"]["km_info"]
        llm = ChatOpenAI(model=config["configurable"]['km_route_llm_model'],
                         base_url=config["configurable"]['km_route_llm_api_base'],
                         api_key=config["configurable"]['km_route_llm_api_key'],
                         temperature=0.01)

        # 使用模板生成知识路由选择prompt
        template_data = {
            'km_info': km_info,
            'user_message': config["configurable"]["graph_request"].user_message
        }
        selected_knowledge_prompt = TemplateLoader.render_template(
            'prompts/graph/knowledge_route_selection_prompt',
            template_data
        )

        logger.debug(f"知识路由选择Prompt: {selected_knowledge_prompt}")
        selected_km_response = llm.invoke(selected_knowledge_prompt)
        return json_repair.loads(selected_km_response.content)

    async def _execute_graph_rag(self, rag_search_request, config: RunnableConfig) -> list:
        """执行图谱RAG检索并处理结果"""
        try:
            # 执行图谱检索
            graph_result = await self._perform_graph_search(rag_search_request, config)
            if not graph_result:
                logger.warning("GraphRAG检索结果为空")
                return []

            # 处理检索结果
            return self._process_graph_results(graph_result, rag_search_request.graph_rag_request.group_ids)

        except Exception as e:
            logger.error(f"GraphRAG检索处理异常: {str(e)}")
            return []

    async def _perform_graph_search(self, rag_search_request, config: RunnableConfig) -> list:
        """执行图谱搜索"""
        graphiti = GraphitiRAG(
            config["configurable"]["graph_rag_host"],
            config["configurable"]["graph_rag_username"],
            config["configurable"]["graph_rag_password"],
            config["configurable"]["graph_rag_port"],
            config["configurable"]["graph_rag_database"]
        )
        rag_search_request.graph_rag_request.search_query = rag_search_request.search_query
        graph_result = await graphiti.search(req=rag_search_request.graph_rag_request)

        logger.info(
            f"GraphRAG模式检索知识库: {rag_search_request.graph_rag_request.group_ids}, "
            f"结果数量: {len(graph_result)}"
        )
        return graph_result

    def _process_graph_results(self, graph_result: list, group_ids: list) -> list:
        """处理图谱检索结果"""
        seen_relations = set()
        summary_dict = {}  # 用于去重summary
        processed_results = []

        # 使用默认的group_id，避免在循环中重复获取
        default_group_id = group_ids[0] if group_ids else ''

        for graph_item in graph_result:
            # 处理关系事实
            relation_result = self._process_relation_fact(
                graph_item, seen_relations, default_group_id
            )
            if relation_result:
                processed_results.append(relation_result)

            # 收集summary信息
            self._collect_summary_info(graph_item, summary_dict)

        # 生成去重的summary结果
        summary_results = self._generate_summary_results(
            summary_dict, default_group_id)
        processed_results.extend(summary_results)

        return processed_results

    def _process_relation_fact(self, graph_item: dict, seen_relations: set, group_id: str):
        """处理单个关系事实"""
        source_node = graph_item.get('source_node', {})
        target_node = graph_item.get('target_node', {})
        source_name = source_node.get('name', '')
        target_name = target_node.get('name', '')
        fact = graph_item.get('fact', '')

        if not (fact and source_name and target_name):
            return None

        relation_content = f"关系事实: {source_name} - {fact} - {target_name}"
        if relation_content in seen_relations:
            return None

        seen_relations.add(relation_content)
        return self._create_relation_result_object(
            relation_content, source_name, target_name, group_id
        )

    def _collect_summary_info(self, graph_item: dict, summary_dict: dict):
        """收集并去重summary信息"""
        source_node = graph_item.get('source_node', {})
        target_node = graph_item.get('target_node', {})

        for node_data in [source_node, target_node]:
            node_name = node_data.get('name', '')
            node_summary = node_data.get('summary', '')

            if node_name and node_summary:
                if node_summary not in summary_dict:
                    summary_dict[node_summary] = set()
                summary_dict[node_summary].add(node_name)

    def _generate_summary_results(self, summary_dict: dict, group_id: str) -> list:
        """生成去重的summary结果"""
        summary_results = []
        for summary_content, associated_nodes in summary_dict.items():
            nodes_list = ', '.join(sorted(associated_nodes))
            summary_with_nodes = f"节点详情: 以下内容与节点 [{nodes_list}] 相关:\n{summary_content}"

            summary_result = self._create_summary_result_object(
                summary_with_nodes, nodes_list, group_id, summary_content
            )
            summary_results.append(summary_result)

        return summary_results

    def _create_relation_result_object(self, relation_content: str, source_name: str,
                                       target_name: str, group_id: str):
        """创建关系事实结果对象"""
        content_hash = hash(relation_content) % 100000

        class RelationResult:
            def __init__(self):
                self.page_content = relation_content
                self.metadata = {
                    'knowledge_title': f"图谱关系: {source_name} - {target_name}",
                    'knowledge_id': group_id,
                    'chunk_number': 1,
                    'chunk_id': f"relation_{content_hash}",
                    'segment_number': 1,
                    'segment_id': f"relation_{content_hash}",
                    'chunk_type': 'Graph'
                }

        return RelationResult()

    def _create_summary_result_object(self, summary_with_nodes: str, nodes_list: str,
                                      group_id: str, summary_content: str):
        """创建summary结果对象"""
        content_hash = hash(summary_content) % 100000

        class SummaryResult:
            def __init__(self):
                self.page_content = summary_with_nodes
                self.metadata = {
                    'knowledge_title': f"图谱节点详情: {nodes_list}",
                    'knowledge_id': group_id,
                    'chunk_number': 1,
                    'chunk_id': f"summary_{content_hash}",
                    'segment_number': 1,
                    'segment_id': f"summary_{content_hash}",
                    'chunk_type': 'Document'
                }

        return SummaryResult()

    def _prepare_template_data(self, rag_result: list, config: RunnableConfig) -> dict:
        """准备模板渲染所需的数据"""
        # 转换RAG结果为模板友好的格式
        rag_results = []
        for r in rag_result:
            # 直接从metadata获取数据（PgvectorRag返回扁平结构）
            metadata = getattr(r, 'metadata', {})
            rag_results.append({
                'title': metadata.get('knowledge_title', 'N/A'),
                'knowledge_id': metadata.get('knowledge_id', 0),
                'chunk_number': metadata.get('chunk_number', 0),
                'chunk_id': metadata.get('chunk_id', 'N/A'),
                'segment_number': metadata.get('segment_number', 0),
                'segment_id': metadata.get('segment_id', 'N/A'),
                'content': r.page_content,
                'chunk_type': metadata.get('chunk_type', 'Document')
            })

        # 准备模板数据
        template_data = {
            'rag_results': rag_results,
            'enable_rag_source': config["configurable"].get("enable_rag_source", False),
            'enable_rag_strict_mode': config["configurable"].get("enable_rag_strict_mode", False)
        }

        return template_data

    def _process_document_content(self, doc):
        """
        根据 is_doc 字段处理文档内容

        Args:
            doc: 文档对象，包含 page_content 和 metadata

        Returns:
            处理后的文档对象
        """
        # 获取元数据
        metadata = getattr(doc, 'metadata', {})
        is_doc = metadata.get('is_doc')

        logger.debug(f"处理文档内容 - is_doc: {is_doc}")

        if is_doc == "0":
            # QA类型：用 qa_question 和 qa_answer 组合替换 page_content
            qa_question = metadata.get('qa_question')
            qa_answer = metadata.get('qa_answer')

            if qa_question and qa_answer:
                doc.page_content = f"问题: {qa_question}\n答案: {qa_answer}"
                doc.metadata['knowledge_title'] = qa_question
            doc.metadata['chunk_type'] = 'QA'
        elif is_doc == "1":
            # 文档类型：直接 append qa_answer
            qa_answer = metadata.get('qa_answer')
            if qa_answer:
                doc.page_content += f"\n{qa_answer}"
            doc.metadata['chunk_type'] = 'Document'
        else:
            # 默认为文档类型
            doc.metadata['chunk_type'] = 'Document'

        return doc

    def _rewrite_query(self, request: BasicLLMRequest, config: RunnableConfig) -> str:
        """
        使用聊天历史上下文改写用户问题

        Args:
            request: 基础LLM请求对象
            config: 运行时配置

        Returns:
            改写后的问题字符串
        """
        try:
            # 准备模板数据
            template_data = {
                'user_message': request.user_message,
                'chat_history': request.chat_history
            }

            # 渲染问题改写prompt
            rewrite_prompt = TemplateLoader.render_template(
                'prompts/graph/query_rewrite_prompt', template_data)

            # 获取LLM客户端
            llm = self.get_llm_client(request, disable_stream=True)

            # 执行问题改写
            response = llm.invoke([HumanMessage(content=rewrite_prompt)])
            rewritten_query = response.content.strip()
            return rewritten_query

        except Exception as e:
            logger.error(f"问题改写过程中发生异常: {str(e)}")
            raise

    def user_message_node(self, state: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
        request = config["configurable"]["graph_request"]
        user_message = request.user_message

        # 如果启用问题改写功能
        if config["configurable"]["graph_request"].enable_query_rewrite:
            try:
                rewritten_message = self._rewrite_query(request, config)
                if rewritten_message and rewritten_message.strip():
                    user_message = rewritten_message
                    self.log(
                        config, f"问题改写完成: {request.user_message} -> {user_message}")
            except Exception as e:
                logger.warning(f"问题改写失败，使用原始问题: {str(e)}")
                user_message = request.user_message

        state["messages"].append(HumanMessage(content=user_message))
        request.graph_user_message = user_message
        return state

    def chat_node(self, state: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
        request = config["configurable"]["graph_request"]

        # 获取LLM客户端并调用
        llm = self.get_llm_client(request)
        result = llm.invoke(state["messages"])

        return {
            'messages': result
        }


class ToolsNodes(BasicNode):
    def __init__(self) -> None:
        self.tools = []
        self.mcp_client = None
        self.mcp_config = {}
        self.tools_prompt_tokens = 0
        self.tools_completions_tokens = 0

    async def call_with_structured_output(self, llm, prompt, pydantic_model,
                                          messages: Union[Dict, List], max_retries: int = 3):
        """
        通用结构化输出调用方法

        Args:
            llm: LangChain LLM实例
            prompt: LangChain prompt模板
            pydantic_model: 目标Pydantic模型类
            messages: 消息内容 (dict或list格式)
            max_retries: 最大重试次数

        Returns:
            解析后的Pydantic模型实例
        """
        parser = StructuredOutputParser(llm, max_retries=max_retries)
        return await parser.parse_with_structured_output(prompt, messages, pydantic_model)

    async def setup(self, request: BaseModel):
        """初始化工具节点"""
        # 初始化MCP客户端配置
        logger.info({len(request.tools_servers)})
        for server in request.tools_servers:
            logger.info(f"Tools Server: {server}")
            if server.url.startswith("langchain:"):
                continue

            if server.url.startswith("stdio-mcp:"):
                # stdio-mcp:name
                self.mcp_config[server.name] = {
                    "command": server.command,
                    "args": server.args,
                    "transport": 'stdio'
                }
            else:
                self.mcp_config[server.name] = {
                    "url": server.url,
                    "transport": 'sse'
                }

        if self.mcp_config:
            self.mcp_client = MultiServerMCPClient(self.mcp_config)
            self.tools = await self.mcp_client.get_tools()

        # 初始化LangChain工具
        for server in request.tools_servers:
            if server.url.startswith("langchain:"):
                langchain_tools = ToolsLoader.load_tools(server.url, server.extra_tools_prompt, server.extra_param_prompt)
                self.tools.extend(langchain_tools)

    async def build_tools_node(self) -> ToolNode:
        """构建工具节点"""
        try:
            if self.tools:
                tool_node = ToolNode(self.tools, handle_tool_errors=True)
                logger.info(f"成功构建工具节点，包含 {len(self.tools)} 个工具")
                return tool_node
            else:
                logger.info("未找到可用工具，返回空工具节点")
                return ToolNode([])
        except Exception as e:
            logger.error(f"构建工具节点失败: {e}")
            return ToolNode([])

    # ========== 简化的 ReAct 节点组合构建器 ==========

    def build_react_nodes(self,
                          graph_builder: StateGraph,
                          composite_node_name: str = "react_agent",
                          system_prompt: Optional[str] = None,
                          end_node: str = END,
                          tools_node: Optional[ToolNode] = None,
                          max_iterations: int = 10) -> str:
        """
        构建独立闭环的 ReAct Agent 组合节点

        这是一个可复用的组合节点，Agent 负责执行工具，有解决方案就结束，
        没有解决方案就继续循环，直到达到最大迭代次数。

        Args:
            graph_builder: StateGraph 构建器
            composite_node_name: 组合节点名称
            system_prompt: 系统提示
            end_node: 结束节点  
            tools_node: 外部工具节点
            max_iterations: 最大迭代次数

        Returns:
            str: 组合节点的出口节点名称
        """
        # 内部节点名称
        llm_node_name = f"{composite_node_name}_llm"
        tool_node_name = f"{composite_node_name}_tools"

        # 添加 LLM 节点
        async def llm_node(state: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
            try:
                messages = state["messages"]
                graph_request = config["configurable"]["graph_request"]

                # 获取 LLM 并绑定工具
                llm = self.get_llm_client(graph_request).bind_tools(self.tools)

                # 构建提示 - 使用现有的模板系统
                if system_prompt:
                    # 使用传入的自定义系统提示
                    prompt = ChatPromptTemplate.from_messages([
                        ("system", system_prompt),
                        MessagesPlaceholder(variable_name="messages"),
                    ])
                else:
                    # 使用专门的ReAct Agent模板系统
                    from neco.core.utils.template_loader import TemplateLoader
                    system_message_prompt = TemplateLoader.render_template(
                        'prompts/graph/react_agent_system_message', {
                            "user_system_message": getattr(graph_request, 'system_message_prompt', "你是一个智能助手，能够使用工具来帮助解决问题。请仔细分析问题，按照ReAct模式工作：先获取必要信息（如当前时间），然后使用合适的工具，最后提供完整的解答。")
                        })
                    prompt = ChatPromptTemplate.from_messages([
                        ("system", system_message_prompt),
                        MessagesPlaceholder(variable_name="messages"),
                    ])

                # 调用 LLM
                response = await (prompt | llm).ainvoke({"messages": messages})

                # 更新迭代计数
                current_iteration = state.get("react_iteration", 0) + 1
                return {
                    "messages": [response],
                    "react_iteration": current_iteration
                }

            except Exception as e:
                logger.error(f"ReAct LLM 节点失败: {e}")
                return {"messages": [AIMessage(content=f"处理失败: {str(e)}")]}

        graph_builder.add_node(llm_node_name, llm_node)

        # 添加工具节点
        async def tool_node(state: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
            try:
                current_tools_node = tools_node or await self.build_tools_node()
                return await current_tools_node.ainvoke(state)
            except Exception as e:
                logger.error(f"ReAct 工具节点失败: {e}")
                return {"messages": [ToolMessage(content=f"工具执行失败: {str(e)}", tool_call_id="error")]}

        graph_builder.add_node(tool_node_name, tool_node)

        # 条件判断函数 - 决定是否继续循环或结束
        def should_continue(state: Dict[str, Any]) -> Literal["tools", "end"]:
            messages = state.get("messages", [])
            current_iteration = state.get("react_iteration", 0)

            # 检查是否达到最大迭代次数
            if current_iteration >= max_iterations:
                logger.warning(f"ReAct Agent 达到最大迭代次数 {max_iterations}，强制结束")
                return "end"

            # 检查最后一条消息是否有工具调用
            if messages and hasattr(messages[-1], 'tool_calls') and messages[-1].tool_calls:
                return "tools"

            # 没有工具调用，表示 Agent 认为已经有了解决方案
            return "end"

        # 添加条件边和回环边
        graph_builder.add_conditional_edges(
            llm_node_name,
            should_continue,
            {"tools": tool_node_name, "end": end_node}
        )
        # 工具执行后回到 LLM 继续思考
        graph_builder.add_edge(tool_node_name, llm_node_name)

        return llm_node_name  # 返回组合节点的入口节点
