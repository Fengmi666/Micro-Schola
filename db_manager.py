import sqlite3
import logging
from typing import Optional, Dict

class DatabaseManager:
    """处理 SQLite 本地缓存的数据库管理器"""
    
    def __init__(self, db_path: str = "scholar_cache.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """初始化数据库 Schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # 创建飞书笔记缓存表
                # 包含增量更新所需的 document_id 和 hash，避免重复拉取
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS feishu_notes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        document_id TEXT UNIQUE NOT NULL,
                        title TEXT NOT NULL,
                        snippet TEXT NOT NULL,
                        link TEXT NOT NULL,
                        content_hash TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
                logging.info("Database schema initialized successfully.")
        except sqlite3.Error as e:
            logging.error(f"Database initialization failed: {e}")

    def upsert_note(self, document_id: str, title: str, snippet: str, link: str, content_hash: str) -> bool:
        """
        插入或更新笔记（增量更新逻辑）
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO feishu_notes (document_id, title, snippet, link, content_hash)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(document_id) DO UPDATE SET
                        title=excluded.title,
                        snippet=excluded.snippet,
                        link=excluded.link,
                        content_hash=excluded.content_hash,
                        updated_at=CURRENT_TIMESTAMP
                    WHERE content_hash != excluded.content_hash
                ''', (document_id, title, snippet, link, content_hash))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logging.error(f"Failed to upsert note {document_id}: {e}")
            return False

    def get_random_note(self) -> Optional[Dict[str, str]]:
        """
        随机抽取一条笔记用于碎片时间展示
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 设置 row_factory 以便返回字典格式
                conn.row_factory = sqlite3.Row 
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT title, snippet, link 
                    FROM feishu_notes 
                    ORDER BY RANDOM() LIMIT 1
                ''')
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except sqlite3.Error as e:
            logging.error(f"Failed to fetch random note: {e}")
            return None