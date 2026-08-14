# Pythonによるメール送信業務支援ツール

繰り返し発生するメール送信業務を効率化するために開発したデスクトップアプリケーションです。

Python・Playwright・Tkinterを組み合わせ、メール送信ページへの自動入力や送信予約をGUIから簡単に操作できるよう設計しました。

---

# 📋 概要

本ツールは、繰り返し発生するメール入力・送信予約作業を自動化し、作業時間の短縮と入力ミスの防止を目的として開発しました。

GUIから送信先やテンプレート、予約時間などを設定でき、コードを書き換えることなく運用できます。
また、テンプレートや予約時間もGUI上から編集・保存できるため、業務内容の変更にも柔軟に対応できる構成としています。

---

# 🛠 使用技術

- Python
- Playwright
- Tkinter
- JSON

---

# ✨ 主な機能

- メール送信ページへの自動入力・送信予約
- 複数パターンのメールテンプレート管理
- GUIからのテンプレート編集・保存
- GUIからの予約時間設定・編集
- Playwrightによるブラウザ操作の自動化
- 処理状況のリアルタイム表示

---

# 🖥️ 画面イメージ

## メイン画面

<img width="871" height="1510" alt="ポートフォリオ用" src="https://github.com/user-attachments/assets/a8a2c8de-b9f2-44d3-8c2e-b3f6e81a298f" />


---

## テンプレート編集

<img width="1557" height="1478" alt="ポートフォリオ定型" src="https://github.com/user-attachments/assets/eef9778a-d2e2-44b7-9f85-ef781c42fb01" />


---

## 予約時間編集

<img width="864" height="1437" alt="ポートフォリオ時間" src="https://github.com/user-attachments/assets/ca52c2b2-dc58-4da2-bfbd-da3148b719b2" />


---

# 💡 工夫した点

- GUIから直感的に操作できる画面構成を採用
- テンプレート・予約時間をJSONで管理し、コードを書き換えることなく編集可能
- Playwrightで画面の状態を確認しながら処理を進め、ブラウザ操作の安定性を考慮
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

Pythonがインストールされた環境で、必要なライブラリをインストールします。

```bash
pip install playwright
playwright install
```

その後、main.py を実行します。

```bash
python main.py
```
※ 本リポジトリはポートフォリオ用に構成しており、実際の業務環境に関する情報は含まれていません。

---

# 👤 開発者

GitHub: **tetsu-python-dev**

Pythonを用いた業務効率化ツールやブラウザ自動化ツールの開発に取り組んでいます。
