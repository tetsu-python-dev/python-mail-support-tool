# Pythonによるメール送信業務支援ツール

日々のメール送信業務を効率化するために開発したデスクトップアプリケーションです。

Python・Playwright・Tkinterを組み合わせ、メール送信ページへの自動入力や送信予約をGUIから簡単に操作できるよう設計しました。

---

# 📋 概要

本ツールは、メール送信業務における入力作業や送信予約を自動化し、業務時間の短縮と入力ミスの防止を目的として開発しました。

GUIからテンプレートや予約時間を編集できるため、コードを書き換えることなく柔軟に運用できます。

---

# 🛠 使用技術

- Python
- Playwright
- Tkinter
- JSON

---

# ✨ 主な機能

- メール送信ページへの自動入力
- メールテンプレート編集
- 送信予約時間編集
- GUIによる各種設定
- 処理状況のリアルタイム表示

---

# 🖥️ 画面イメージ

## メイン画面

<img width="871" height="1510" alt="ポートフォリオ用" src="https://github.com/user-attachments/assets/a8a2c8de-b9f2-44d3-8c2e-b3f6e81a298f" />


---

## テンプレート編集

<img width="1571" height="1485" alt="ポートフォリオ用定型" src="https://github.com/user-attachments/assets/dcc3ce5e-b8c4-49f0-81e5-eee78fe9c893" />


---

## 予約時間編集

<img width="859" height="1438" alt="ポートフォリオ用時間" src="https://github.com/user-attachments/assets/b69fac48-b6f6-4b16-944e-2d4c2e214dac" />


---

# 💡 工夫した点

- GUIから直感的に操作できる画面構成を採用
- テンプレート・予約時間をJSONで管理し、コードを書き換えることなく編集可能
- Playwrightを利用し、ブラウザ操作を自動化
- 実際の業務利用を想定し、処理状況をリアルタイム表示

---

# 📁 フォルダ構成

```text
python-mail-support-tool/
│
├── main.py
├── browser.py
├── data.py
├── messages.json
├── times.json
└── README.md
```

---

# 🚀 実行方法

1. 必要なライブラリをインストール

```bash
pip install playwright
playwright install
```

2. `main.py` を実行

```bash
python main.py
```

---

# 🔮 今後の改善予定

- ログ出力機能の追加
- エラーハンドリングの強化
- 設定項目の拡張
- UIデザインの改善

---

# 👤 開発者

GitHub: **tetsu-python-dev**

Pythonを用いた業務効率化ツールやブラウザ自動化ツールの開発に取り組んでいます。
