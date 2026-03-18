# 👁️ Solana Watcher Pro

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)

**Solana Watcher Pro** is a powerful, open-source dashboard designed for Solana traders to track token distributions, identify whale movements, and manage private wallet labels (CRM).

**Solana Watcher Pro** 是一款專為 Solana 交易者設計的開源儀表板，用於追蹤代幣分佈、識別巨鯨動向並管理私人錢包標記 (CRM)。

---

## ✨ Features / 核心功能

- **📋 Wallet CRM**: Label whales, smart money, or your own wallets across all tokens.
  - **全域標記系統**：在所有代幣中標記巨鯨、聰明錢包或你自己的錢包。
- **🐋 Whale Alerts**: Track real-time balance changes and get Telegram notifications.
  - **巨鯨異動警報**：追蹤即時餘額變動，並透過 Telegram 接收通知。
- **🕵️ Cost Detective**: Estimate historical entry costs and holding time for any holder.
  - **進場偵探**：估算任何持有者的歷史進場成本與持倉時間。
- **🔍 Money Flow**: Trace the source of SOL for any wallet to identify "Insider/Cabal" wallets.
  - **資金來源溯源**：追蹤任何錢包的 SOL 來源，識別「老鼠倉/莊家」網路。
- **🌐 Dual Language**: Full support for English and Traditional Chinese.
  - **中英雙語**：完整支援繁體中文與英文切換。

---

## 🚀 Quick Start / 快速開始

### Prerequisites / 前置準備
- [uv](https://github.com/astral-sh/uv) (Recommended Python manager)
- [Helius API Key](https://helius.xyz/) (Free tier available)
- [Birdeye API Key](https://birdeye.so/) (Optional, for price data)

### Installation / 安裝步驟
```bash
# Clone the repository
git clone https://github.com/your-username/solana-project-watch.git
cd solana-project-watch

# Install dependencies and run
uv run streamlit run app.py
```

---

## 💡 Demo Mode / 教學模式
Don't have an API Key? No problem! Just run the app and it will automatically enter **Demo Mode** with sample data so you can explore all features immediately.

沒有 API Key？沒關係！直接執行程式，系統會自動進入**教學模式**並載入範例數據，讓你立即體驗所有功能。

---

## 🛠️ Tech Stack / 技術棧
- **Frontend**: Streamlit
- **Database**: SQLite (Local storage)
- **APIs**: Helius (DAS & RPC), Birdeye (Pricing)
- **Environment**: Python with `uv`

---

## 🤝 Contributing / 貢獻指南
Contributions are welcome! Please feel free to submit a Pull Request.
歡迎任何形式的貢獻！請隨時提交 Pull Request。

---

## 📄 License / 開源協議
This project is licensed under the **MIT License**.
本專案採用 **MIT 開源協議**。
