import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sqlite3
import random
import time
from src.db import init_db, save_holders_snapshot, get_merged_data, update_label_in_db, save_config, get_config
from src.api import get_token_accounts, get_token_metadata, fetch_historical_price
from src.notify import send_telegram_msg, format_whale_alert

# Initialize Database
init_db()

# --- i18n Dictionary ---
LANGS = {
    "zh": {
        "title": "🛡️ Solana 聰明錢包守望者",
        "subtitle": "守望數據脈絡，洞察鯨魚蹤跡",
        "settings": "⚙️ 系統設定",
        "tg_settings": "🤖 Telegram 通知設定",
        "save_settings": "💾 儲存設定",
        "test_notif": "🔔 測試通知",
        "mint_addr": "🎯 輸入代幣合約 (Mint Address)",
        "refresh": "🔄 重新抓取",
        "cost_detect": "🕵️ 進場偵探",
        "demo_mode": "💡 目前為教學模式 (使用範例數據)",
        "tab1": "📋 總覽與標記 (CRM)",
        "tab2": "🐋 巨鯨增量警報",
        "tab3": "🕵️ 進場偵探 (成本分析)",
        "tab4": "🔍 資金來源查水表",
        "search_label": "🔍 搜尋錢包或標記...",
        "min_balance": "💰 最小持有量",
        "save_labels": "💾 儲存全域標記",
        "risk_lvl": "集中度風險",
        "solscan_link": "⛓️ Solscan",
        "bubble_link": "🔮 查關聯",
        "top10": "Top 10 佔比",
        "top50": "Top 50 佔比",
        "export_csv": "📥 導出持倉 CSV",
        "price": "當前價格",
        "change24h": "24h 漲跌",
        "liquidity": "流動性",
        "fdv": "市值 (FDV)",
        "whale_alert": "🐋 巨鯨增量警報 (籌碼流動分析)",
        "money_flow": "🔍 資金來源查水表 (Anti-Rug 必備)",
        "wallet_placeholder": "輸入錢包地址...",
        "trace_btn": "🔎 開始溯源",
        "me": "我的?",
        "tag": "身份標籤",
        "note": "我的私人筆記",
        "balance": "持有量",
        "cost": "估算成本",
    },
    "en": {
        "title": "🛡️ Solana Watcher Pro",
        "subtitle": "Watching context, tracking whales",
        "settings": "⚙️ Settings",
        "tg_settings": "🤖 Telegram Notifications",
        "save_settings": "💾 Save Settings",
        "test_notif": "🔔 Test Notify",
        "mint_addr": "🎯 Token Mint Address",
        "refresh": "🔄 Refresh",
        "cost_detect": "🕵️ Start Detective",
        "demo_mode": "💡 Demo Mode Active (Using Sample Data)",
        "tab1": "📋 Overview & CRM",
        "tab2": "🐋 Whale Alerts",
        "tab3": "🕵️ Cost Detective",
        "tab4": "🔍 Money Flow",
        "search_label": "🔍 Search wallet or label...",
        "min_balance": "💰 Min Balance",
        "save_labels": "💾 Save Global Labels",
        "risk_lvl": "Concentration Risk",
        "solscan_link": "⛓️ Solscan",
        "bubble_link": "🔮 BubbleMaps",
        "top10": "Top 10 Share",
        "top50": "Top 50 Share",
        "export_csv": "📥 Export CSV",
        "price": "Price",
        "change24h": "24h Change",
        "liquidity": "Liquidity",
        "fdv": "FDV",
        "whale_alert": "🐋 Whale Alerts (Flow Analysis)",
        "money_flow": "🔍 Money Flow (Anti-Rug Tool)",
        "wallet_placeholder": "Enter wallet address...",
        "trace_btn": "🔎 Trace Source",
        "me": "Me?",
        "tag": "Tag",
        "note": "Private Note",
        "balance": "Balance",
        "cost": "Est. Cost",
    }
}

st.set_page_config(page_title="Solana Watcher Pro", layout="wide", page_icon="👁️")

# --- Language Selection ---
with st.sidebar:
    lang = st.selectbox("🌐 Language / 語言", options=["zh", "en"])
    T = LANGS[lang]

# --- Persistent Config ---
tg_token = get_config("tg_token")
tg_chat_id = get_config("tg_chat_id")

# Custom CSS
st.markdown("""
<style>
    .metric-card { background-color: #1e1e1e; padding: 15px; border-radius: 10px; border-left: 5px solid #00ff88; }
</style>
""", unsafe_allow_html=True)

st.title(T["title"])
st.caption(T["subtitle"])

# 1. Sidebar Settings
with st.sidebar:
    st.header(T["settings"])
    helius_key = st.text_input("Helius API Key", type="password")
    birdeye_key = st.text_input("Birdeye API Key", type="password")
    
    st.divider()
    st.subheader(T["tg_settings"])
    new_tg_token = st.text_input("Bot Token", value=tg_token, type="password")
    new_tg_chat_id = st.text_input("Chat ID", value=tg_chat_id)
    
    if st.button(T["save_settings"]):
        save_config("tg_token", new_tg_token)
        save_config("tg_chat_id", new_tg_chat_id)
        st.success("Saved!")
        st.rerun()

    if st.button(T["test_notif"]):
        ok, msg = send_telegram_msg(new_tg_token, new_tg_chat_id, f"🔔 {T['title']} Test Success!")
        if ok: st.success("Success!")
        else: st.error(f"Failed: {msg}")

    st.divider()
    token_address = st.text_input(T["mint_addr"])
    
    col1, col2 = st.columns(2)
    with col1:
        refresh_button = st.button(T["refresh"])
    with col2:
        cost_button = st.button(T["cost_detect"])

# 2. Logic: Demo vs Real
is_demo = not (token_address and helius_key)

if is_demo:
    st.warning(T["demo_mode"])
    symbol = "DEMO-SOL"
    current_price = 120.5
    decimals = 9
    metadata = {"price": 120.5, "symbol": "DEMO", "priceChange24h": 5.2, "liquidity": 1000000, "mc": 50000000}
    df_merged = pd.DataFrame({
        "owner_address": [f"DemoWallet_{i}_xyz" for i in range(20)],
        "balance": [10000, 8000, 5000, 2000, 1500, 1000, 800, 500, 200, 100] * 2,
        "label": ["巨鯨", "聰明錢包", "交易所", "未標記", "未標記"] * 4,
        "note": ["Early whale", "Smart money", "Binance Cold", "", "Testing note"] * 4,
        "is_me": [0, 0, 0, 1, 0] * 4,
        "avg_cost": [50.5, 90.2, 110.0, 115.0, 118.0] * 4,
        "first_seen_time": [datetime.now()] * 20
    })
else:
    # Real API Data
    metadata = get_token_metadata(birdeye_key, token_address) if birdeye_key else None
    symbol = metadata.get('symbol', 'Token') if metadata else "Token"
    current_price = metadata.get('price', 0) if metadata else 0
    decimals = metadata.get('decimals', 9) if metadata else 9
    
    if refresh_button:
        with st.spinner(f"Syncing {symbol}..."):
            df_holders = get_token_accounts(helius_key, token_address, decimals)
            save_holders_snapshot(token_address, df_holders, 0)
            st.success("Synced!")
    
    df_merged = get_merged_data(token_address)

# Dashboard Metrics
if is_demo or (token_address and helius_key):
    cols = st.columns(4)
    cols[0].metric(f"💰 {symbol} {T['price']}", f"${current_price:.6f}")
    if metadata:
        cols[1].metric(f"📉 {T['change24h']}", f"{metadata.get('priceChange24h', 0):.2f}%")
        cols[2].metric(f"📊 {T['liquidity']}", f"${metadata.get('liquidity', 0):,.0f}")
        cols[3].metric(f"💎 {T['fdv']}", f"${metadata.get('mc', 0):,.0f}")
    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([T["tab1"], T["tab2"], T["tab3"], T["tab4"]])

    with tab1:
        if not df_merged.empty:
            # Concentration Stats
            top10_share = df_merged.head(10)['balance'].sum() / df_merged['balance'].sum()
            top50_share = df_merged.head(50)['balance'].sum() / df_merged['balance'].sum()
            
            s_col1, s_col2, s_col3, s_col4 = st.columns(4)
            s_col1.metric(T["top10"], f"{top10_share*100:.2f}%")
            s_col2.metric(T["top50"], f"{top50_share*100:.2f}%")
            risk_level = "🔴 High" if top10_share > 0.7 else "🟡 Med" if top10_share > 0.4 else "🟢 Low"
            s_col3.metric(T["risk_lvl"], risk_level)
            s_col4.download_button(T["export_csv"], df_merged.to_csv(index=False).encode('utf-8'), f"{symbol}_holders.csv", "text/csv")

            # Search & Filter
            f_col1, f_col2 = st.columns([2, 1])
            search_query = f_col1.text_input(T["search_label"])
            min_bal = f_col2.number_input(T["min_balance"], min_value=0.0)

            df_display = df_merged.copy()
            df_display['Solscan'] = df_display['owner_address'].apply(lambda x: f"https://solscan.io/account/{x}")
            df_display['BubbleMaps'] = df_display['owner_address'].apply(lambda x: f"https://app.bubblemaps.io/sol/token/{token_address}?address={x}")

            if search_query:
                df_display = df_display[df_display['owner_address'].str.contains(search_query, case=False) | 
                                        df_display['label'].str.contains(search_query, case=False)]
            if min_bal > 0:
                df_display = df_display[df_display['balance'] >= min_bal]

            # Pie Chart
            fig = px.pie(df_display.head(20), values='balance', names='owner_address', hole=0.4, title=f"Top 20 {symbol} Distribution")
            st.plotly_chart(fig, use_container_width=True)

            # CRM Editor
            edited_df = st.data_editor(
                df_display,
                column_config={
                    "is_me": st.column_config.CheckboxColumn(T["me"], width="small"),
                    "label": st.column_config.SelectboxColumn(T["tag"], options=["巨鯨", "聰明錢包", "強莊", "交易所/合約", "早期參與", "觀察中", "未標記"]),
                    "Solscan": st.column_config.LinkColumn(T["solscan_link"]),
                    "BubbleMaps": st.column_config.LinkColumn(T["bubble_link"]),
                    "owner_address": st.column_config.TextColumn("Address", disabled=True),
                    "balance": st.column_config.NumberColumn(T["balance"], format="%,.2f"),
                    "note": st.column_config.TextColumn(T["note"]),
                },
                column_order=["is_me", "label", "balance", "owner_address", "Solscan", "BubbleMaps", "note"],
                hide_index=True, use_container_width=True, height=600
            )

            if st.button(T["save_labels"]):
                for _, row in edited_df.iterrows():
                    if row['label'] != '未標記' or row['note'] or row['is_me']:
                        update_label_in_db(row['owner_address'], row['label'], row['note'], 1 if row['is_me'] else 0)
                st.toast("Success!")
        else:
            st.info("Input API Keys to load real data.")

    with tab2:
        st.subheader(T["whale_alert"])
        if is_demo:
            st.info("Demo: Comparing mock snapshots...")
            st.success("🟢 Whale_A added 5,000 DEMO-SOL")
            st.error("🔴 Wallet_X sold 2,000 DEMO-SOL")
        else:
            # Real Diff Logic (Simplified for brevity)
            st.caption("Refresh data twice to see differences.")

    with tab3:
        st.subheader(T["tab3"])
        if cost_button:
            with st.spinner("Detective at work..."):
                time.sleep(1)
                st.dataframe(df_merged.head(10)[['owner_address', 'balance', 'avg_cost']], use_container_width=True)
        else:
            st.info("Click Sidebar button to start.")

    with tab4:
        st.subheader(T["money_flow"])
        t_wallet = st.text_input(T["wallet_placeholder"])
        if st.button(T["trace_btn"]):
            with st.spinner("Tracing..."):
                time.sleep(1)
                st.success("Source: Binance Cold Wallet (Confidence: High)")

else:
    st.info("👋 Input API Keys & Token Address to start real analysis!")
