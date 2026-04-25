import os
import json
import logging
import hashlib
from typing import List, Dict
from dotenv import load_dotenv

# 引入飞书 SDK
import lark_oapi as lark
from lark_oapi.api.docx.v1 import *

# 引入我们刚才写的数据库管理器
from db_manager import DatabaseManager

# 配置基础日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FeishuManager:
    def __init__(self):
        # 严格遵守规则：从环境变量加载凭证
        load_dotenv()
        self.app_id = os.getenv("FEISHU_APP_ID")
        self.app_secret = os.getenv("FEISHU_APP_SECRET")
        
        if not self.app_id or not self.app_secret:
            raise ValueError("Missing Feishu API credentials in .env file.")

        # 初始化 Lark Client
        self.client = lark.Client.builder() \
            .app_id(self.app_id) \
            .app_secret(self.app_secret) \
            .log_level(lark.LogLevel.WARNING) \
            .build()
            
        self.db = DatabaseManager()

    def _extract_text_from_blocks(self, blocks: List[dict]) -> List[str]:
        """
        核心解析逻辑：遍历文档块，只提取纯文本内容
        (这里正是基于你抓取的 JSON 事实锚点编写的)
        """
        extracted_snippets = []
        for block in blocks:
            # block_type 2 通常是文本段落, 3 是标题等。我们提取这部分包含 text 的块
            if "text" in block and "elements" in block["text"]:
                paragraph_text = ""
                for element in block["text"]["elements"]:
                    if "text_run" in element:
                        paragraph_text += element["text_run"]["content"]
                
                # 过滤掉太短的无意义段落（比如只有空格或两三个字的行）
                cleaned_text = paragraph_text.strip()
                if len(cleaned_text) > 10: 
                    extracted_snippets.append(cleaned_text)
                    
        return extracted_snippets

    def sync_single_document(self, document_id: str, title: str = "Feishu Note"):
        """
        同步单篇飞书文档到本地数据库
        """
        logging.info(f"Start syncing document: {document_id}")
        
        # 构造请求
        request: ListDocumentBlockRequest = ListDocumentBlockRequest.builder() \
            .document_id(document_id) \
            .build()

        # 发起调用
        response: ListDocumentBlockResponse = self.client.docx.v1.document_block.list(request)

        if not response.success():
            logging.error(f"Feishu API Error: code={response.code}, msg={response.msg}")
            return False

        # 飞书 SDK 返回的是对象，我们将其转为字典列表方便处理
        blocks_data = [json.loads(block.to_json()) for block in response.data.items]
        
        # 提取文本段落
        snippets = self._extract_text_from_blocks(blocks_data)
        
        if not snippets:
            logging.warning("No valid text found in this document.")
            return False
            
        # 为了适合“碎片时间”阅读，我们把整篇文档按段落或者固定长度截断成多个微知识点
        # 这里为了演示，我们把前3个长段落存入数据库
        success_count = 0
        for i, snippet in enumerate(snippets[:10]): # 最多取前10个有效段落
            # 生成该段落的唯一 Hash，用于增量更新
            content_hash = hashlib.md5(snippet.encode('utf-8')).hexdigest()
            snippet_id = f"{document_id}_part_{i}"
            link = f"https://feishu.cn/docx/{document_id}"
            
            if self.db.upsert_note(snippet_id, title, snippet, link, content_hash):
                success_count += 1
                
        logging.info(f"Successfully synced {success_count} snippets from document {document_id}.")
        return True