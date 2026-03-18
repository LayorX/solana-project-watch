import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = "solana_watcher.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. 儲存代幣持有者最新狀態
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS holders (
        mint_address TEXT,
        owner_address TEXT,
        balance REAL,
        avg_cost REAL,
        last_updated_slot INTEGER,
        first_seen_time TIMESTAMP,
        PRIMARY KEY (mint_address, owner_address)
    )
    ''')
    
    # 2. 全域標記系統 (跨代幣通用)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS labels (
        address TEXT PRIMARY KEY,
        label TEXT,
        note TEXT,
        is_me INTEGER DEFAULT 0,
        updated_at TIMESTAMP
    )
    ''')
    
    # 3. 歷史快照 (用於增量分析與鯨魚變動)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mint_address TEXT,
        owner_address TEXT,
        balance REAL,
        snapshot_time TIMESTAMP
    )
    ''')
    
    # 4. 系統設定 (如 Telegram API 等)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

def save_config(key, value):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO config (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))
    conn.commit()
    conn.close()

def get_config(key, default=""):
    conn = sqlite3.connect(DB_PATH)
    res = conn.execute("SELECT value FROM config WHERE key=?", (key,)).fetchone()
    conn.close()
    return res[0] if res else default

def save_holders_snapshot(mint, df_holders, current_slot=0):
    """將 Helius 抓取的快照存入資料庫，並保存歷史紀錄"""
    if df_holders.empty:
        return
        
    conn = sqlite3.connect(DB_PATH)
    now = datetime.now()
    
    for _, row in df_holders.iterrows():
        # 更新最新狀態
        conn.execute('''
        INSERT INTO holders (mint_address, owner_address, balance, last_updated_slot, first_seen_time)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(mint_address, owner_address) DO UPDATE SET
            balance = excluded.balance,
            last_updated_slot = excluded.last_updated_slot
        ''', (mint, row['owner'], row['amount'], current_slot, now))
        
        # 寫入歷史快照
        conn.execute('''
        INSERT INTO snapshots (mint_address, owner_address, balance, snapshot_time)
        VALUES (?, ?, ?, ?)
        ''', (mint, row['owner'], row['amount'], now))
        
    conn.commit()
    conn.close()

def get_labels_map():
    """獲取所有已知的標記"""
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT * FROM labels", conn)
        return df.set_index('address').to_dict('index')
    except Exception:
        return {}
    finally:
        conn.close()

def update_label_in_db(address, label, note, is_me=0):
    conn = sqlite3.connect(DB_PATH)
    now = datetime.now()
    conn.execute('''
    INSERT INTO labels (address, label, note, is_me, updated_at)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(address) DO UPDATE SET
        label = excluded.label,
        note = excluded.note,
        is_me = excluded.is_me,
        updated_at = excluded.updated_at
    ''', (address, label, note, is_me, now))
    conn.commit()
    conn.close()

def get_merged_data(mint):
    """將 Holders 數據與全域 Labels 數據合併"""
    conn = sqlite3.connect(DB_PATH)
    query = f'''
    SELECT h.owner_address, h.balance, h.avg_cost, h.first_seen_time,
           COALESCE(l.label, '未標記') as label, 
           COALESCE(l.note, '') as note, 
           COALESCE(l.is_me, 0) as is_me
    FROM holders h
    LEFT JOIN labels l ON h.owner_address = l.address
    WHERE h.mint_address = '{mint}'
    ORDER BY h.balance DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
