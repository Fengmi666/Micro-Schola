from feishu_manager import FeishuManager
from db_manager import DatabaseManager

def main():
    # 1. 初始化 Manager
    try:
        fm = FeishuManager()
    except Exception as e:
        print(f"初始化失败: {e}")
        return

    # 2. 填入你刚才在飞书获取的底层 obj_token (注意：必须是 doxcn 或类似开头的底层 ID)
    # 替换成你刚才真实获取到的 obj_token
    test_document_id = "QQI5d2v3woTAqnxdcHgc9Ep8ned" 
    
    # 3. 执行同步
    print("正在从飞书拉取并解析文档...")
    fm.sync_single_document(test_document_id, title="Micro-Schola 测试文档")
    
    # 4. 从本地数据库随机抽取一条进行展示验证
    print("\n--- 模拟碎片时间触发 ---")
    db = DatabaseManager()
    note = db.get_random_note()
    if note:
        print(f"【标题】: {note['title']}")
        print(f"【内容】: {note['snippet']}")
        print(f"【来源】: {note['link']}")
    else:
        print("数据库为空，拉取失败。")

if main.__name__ == "__main__":
    main()