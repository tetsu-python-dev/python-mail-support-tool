import os

print("現在のフォルダ:", os.getcwd())
print("messages.jsonは存在する？", os.path.exists("messages.json"))
import json
import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import threading

from data import make_reservations
from browser import BrowserController


SITE_LABELS = {
    "site_a": "営業管理システム",
    "site_b": "顧客管理システム",
}

TYPE_LABELS = {
    "normal": "初回案内",
    "special": "フォローアップ",
    "qr": "リマインド",
}

TONE_LABELS = {
    "friend": "ビジネス",
    "polite": "カジュアル",
}

TYPE_VALUES = {v: k for k, v in TYPE_LABELS.items()}
TONE_VALUES = {v: k for k, v in TONE_LABELS.items()}
SITE_VALUES = {v: k for k, v in SITE_LABELS.items()}

class AsyncRunner:
    def __init__(self):
        self.loop = asyncio.new_event_loop()

        self.thread = threading.Thread(
            target=self._run_loop,
            daemon=True
        )

        self.thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run(self, coro):
        return asyncio.run_coroutine_threadsafe(
            coro,
            self.loop
        )

    def stop(self):
        self.loop.call_soon_threadsafe(
            self.loop.stop
        )


async_runner = AsyncRunner()
browser = BrowserController()


def run_async(coro):
    return async_runner.run(coro)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("メール送信業務支援ツール")
        self.root.geometry("420x710")
        self.root.attributes("-topmost", True)

        self.site_var = tk.StringVar(value="site_a")
        self.site_display_var = tk.StringVar(value=SITE_LABELS["site_a"])

        self.url_var = tk.StringVar()

        self.mode_var = tk.StringVar(value="normal")
        self.mode_display_var = tk.StringVar(value=TYPE_LABELS["normal"])

        self.tone_var = tk.StringVar(value="friend")
        self.tone_display_var = tk.StringVar(value=TONE_LABELS["friend"])
        self.hour_var = tk.StringVar(value="10:00")

        self.progress_var = tk.StringVar(value="0 / 0")
        self.current_time_var = tk.StringVar(value="－－－－")
        self.status_var = tk.StringVar(value="待機中")

        self.build_gui()

    def build_gui(self):
        tk.Label(self.root, text="メール送信ページURL").pack(anchor="w", padx=15, pady=(10, 0))
        tk.Entry(self.root, textvariable=self.url_var, width=50).pack(padx=15)

        tk.Button(
            self.root,
            text="送信ページを開く",
            command=self.open_url
        ).pack(pady=8)

        tk.Label(self.root, text="送信先サービス").pack(anchor="w", padx=15, pady=(10, 0))

        site_box = ttk.Combobox(
            self.root,
            textvariable=self.site_display_var,
            values=list(SITE_LABELS.values()),
            width=18,
            state="readonly"
        )
        site_box.pack(anchor="w", padx=30, pady=5)
        site_box.bind("<<ComboboxSelected>>", self.on_site_changed)

        tk.Label(self.root, text="テンプレート").pack(anchor="w", padx=15)

        mode_box = ttk.Combobox(
            self.root,
            textvariable=self.mode_display_var,
            values=list(TYPE_LABELS.values()),
            width=18,
            state="readonly"
        )   
        mode_box.pack(anchor="w", padx=30, pady=5)
        mode_box.bind("<<ComboboxSelected>>", self.on_mode_changed)

        tk.Label(self.root, text="文章スタイル").pack(anchor="w", padx=15, pady=(10, 0))

        tone_box = ttk.Combobox(
            self.root,
            textvariable=self.tone_display_var,
            values=list(TONE_LABELS.values()),
            width=18,
            state="readonly"
        )
        tone_box.pack(anchor="w", padx=30, pady=5)
        tone_box.bind("<<ComboboxSelected>>", self.on_tone_changed)

        tk.Label(self.root, text="送信予約時刻").pack(anchor="w", padx=15, pady=(10, 0))

        hour_box = ttk.Combobox(
            self.root,
            textvariable=self.hour_var,
            values=[f"{i:02d}:00" for i in range(24)],
            width=10,
            state="readonly"
        )
        hour_box.pack(anchor="w", padx=30)

        tk.Label(self.root, text="処理状況").pack(anchor="w", padx=15, pady=(15, 0))
        tk.Label(self.root, textvariable=self.progress_var, font=("Arial", 16)).pack()

        tk.Label(self.root, text="現在の処理").pack(anchor="w", padx=15)
        tk.Label(self.root, textvariable=self.current_time_var, font=("Arial", 16)).pack()

        tk.Label(self.root, text="状態").pack(anchor="w", padx=15)
        tk.Label(self.root, textvariable=self.status_var, font=("Arial", 14)).pack()

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        tk.Button(
            button_frame,
            text="送信予約開始",
            width=12,
            command=self.start_run
        ).pack(side="left", padx=10)

        tk.Button(
            button_frame,
            text="処理停止",
            width=12,
            command=self.stop_run
        ).pack(side="left", padx=10)

        tk.Button(
            self.root,
            text="テンプレート編集",
            command=self.open_message_editor
        ).pack(pady=10)

        tk.Button(
            self.root,
            text="予約時間編集",
            command=self.open_time_editor
        ).pack(pady=5)

        tk.Label(
            self.root,
            text="使用技術\nPython / Playwright / Tkinter",
            font=("Arial", 9),
            fg="gray"
        ).pack(pady=(20, 10))

    def on_site_changed(self, event=None):
        self.site_var.set(SITE_VALUES[self.site_display_var.get()])

    def on_mode_changed(self, event=None):
        self.mode_var.set(TYPE_VALUES[self.mode_display_var.get()])

    def on_tone_changed(self, event=None):
        self.tone_var.set(TONE_VALUES[self.tone_display_var.get()])

    def update_site_buttons(self):
        selected = self.site_var.get()

        for site, button in self.site_buttons.items():
            if site == selected:
                button.config(
                    relief="sunken",
                    font=("Arial", 11, "bold")
                )
            else:
                button.config(
                    relief="raised",
                    font=("Arial", 11)
                )

    def open_url(self):
        url = self.url_var.get().strip()

        if not url:
            messagebox.showwarning("確認", "URLを入力してください")
            return

        print("URLを開く:", url, flush=True)
        self.status_var.set("URLを開いています")

        run_async(browser.open_url(url))

    def start_run(self):
        site = self.site_var.get()
        mode = self.mode_var.get()
        tone = self.tone_var.get()
        base_hour = int(self.hour_var.get().split(":")[0])
        

        confirm = messagebox.askokcancel(
            "実行確認",
            "予約送信を開始します。\nよろしいですか？"
        )

        if not confirm:
            self.status_var.set("実行キャンセル")
            return

        print("実行ボタン押下", flush=True)
        print("site:", site, flush=True)
        print("mode:", mode, flush=True)
        print("tone:", tone, flush=True)
        print("base_hour:", base_hour, flush=True)

        reservations = make_reservations(base_hour, site, mode, tone)

        print("予約件数:", len(reservations), flush=True)

        self.progress_var.set(f"0 / {len(reservations)}")
        self.current_time_var.set("－－－－")
        self.status_var.set("実行中")

        run_async(
            browser.run_reservations(
                reservations,
                mode,
                self.update_progress
            )
        )

    def stop_run(self):
        browser.stop()
        self.status_var.set("停止要求中")
        print("停止要求", flush=True)

    def update_progress(self, current, total, status, reserve_time):
        self.root.after(0, lambda: self.progress_var.set(f"{current} / {total}"))
        self.root.after(0, lambda: self.status_var.set(status))

        if reserve_time:
            self.root.after(0, lambda: self.current_time_var.set(reserve_time))

    def open_message_editor(self):
        editor = tk.Toplevel(self.root)

        base_hour = int(self.hour_var.get().split(":")[0])
        
        site_name = SITE_LABELS[self.site_var.get()]
        editor.title(f"【{site_name}】テンプレート編集（基準 {base_hour:02d}時）")
        editor.geometry("760x700")
        editor.attributes("-topmost", True)

        editor_site_var = tk.StringVar(value=self.site_var.get())
        mode_var = tk.StringVar(value=self.mode_var.get())
        tone_var = tk.StringVar(value=self.tone_var.get())

        mode_display_var = tk.StringVar(value=TYPE_LABELS[mode_var.get()])
        tone_display_var = tk.StringVar(value=TONE_LABELS[tone_var.get()])

        entry_vars = []
        editor_site_buttons = {}

        def load_messages():
            with open("messages.json", "r", encoding="utf-8") as f:
                return json.load(f)

        def save_messages(data):
            with open("messages.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        def get_labels(mode):
            with open("times.json", "r", encoding="utf-8") as f:
                times = json.load(f)

            site = editor_site_var.get()

            if mode == "normal":
                labels = []

                EDIT_BASE_HOUR = base_hour

                for time_data in times[site]["normal"]:
                    hour = EDIT_BASE_HOUR + time_data["hour"]

                    if hour < 0:
                        hour += 24
                    elif hour > 23:
                        hour -= 24

                    minute = time_data["minute"]
                    labels.append(f"{hour:02d}:{minute:02d}")

                return labels

            if mode == "special":
                return [f'{time_data["after_min"]}分後' for time_data in times[site]["special"]]

            if mode == "qr":
                return [f'{time_data["after_min"]}分後' for time_data in times[site]["qr"]]

        def update_editor_site_buttons():
            selected = editor_site_var.get()

            for site, button in editor_site_buttons.items():
                if site == selected:
                    button.config(
                        relief="sunken",
                        font=("Arial", 11, "bold")
                    )
                else:
                    button.config(
                        relief="raised",
                        font=("Arial", 11)
                    )

        def select_editor_site(site):
            editor_site_var.set(site)
            update_editor_site_buttons()
            editor.after(50, redraw)

        top_frame = tk.Frame(editor)
        top_frame.pack(pady=(12, 8))

        app_frame = tk.Frame(top_frame)
        app_frame.pack(pady=(0, 12))

        tk.Label(app_frame, text="送信先サービス", font=("Arial", 12, "bold")).pack()

        app_button_frame = tk.Frame(app_frame)
        app_button_frame.pack(pady=6)

        app_a_button = tk.Button(
            app_button_frame,
            text=SITE_LABELS["site_a"],
            width=12,
            command=lambda: select_editor_site("site_a")
        )
        app_a_button.pack(side="left", padx=8)

        app_b_button = tk.Button(
            app_button_frame,
            text=SITE_LABELS["site_b"],
            width=12,
            command=lambda: select_editor_site("site_b")
        )
        app_b_button.pack(side="left", padx=8)

        editor_site_buttons["site_a"] = app_a_button
        editor_site_buttons["site_b"] = app_b_button

        update_editor_site_buttons()

        option_frame = tk.Frame(top_frame)
        option_frame.pack()

        tk.Label(option_frame, text="テンプレート").grid(row=0, column=0, padx=5)

        mode_box = ttk.Combobox(
            option_frame,
            textvariable=mode_display_var,
            values=list(TYPE_LABELS.values()),
            state="readonly",
            width=12
        )
        mode_box.grid(row=0, column=1, padx=5)

        tk.Label(option_frame, text="文章スタイル").grid(row=0, column=2, padx=5)

        tone_box = ttk.Combobox(
            option_frame,
            textvariable=tone_display_var,
            values=list(TONE_LABELS.values()),
            state="readonly",
            width=12
        )
        tone_box.grid(row=0, column=3, padx=5)

        body_frame = tk.Frame(editor)
        body_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(body_frame)
        scrollbar = tk.Scrollbar(body_frame, orient="vertical", command=canvas.yview)

        list_frame = tk.Frame(canvas)

        list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        def on_editor_close():
            canvas.unbind_all("<MouseWheel>")
            editor.destroy()

        editor.protocol("WM_DELETE_WINDOW", on_editor_close)

        canvas.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        scrollbar.pack(side="right", fill="y")

        def redraw():
            nonlocal entry_vars
            entry_vars = []

            for widget in list_frame.winfo_children():
                widget.destroy()

            data = load_messages()

            site = editor_site_var.get()
            mode = TYPE_VALUES[mode_display_var.get()]
            tone = TONE_VALUES[tone_display_var.get()]

            labels = get_labels(mode)
            messages = data[site][mode][tone]

            for i, label in enumerate(labels):
                tk.Label(list_frame, text=label, width=8, anchor="e").grid(
                    row=i,
                    column=0,
                    padx=5,
                    pady=3
                )

                text = messages[i] if i < len(messages) else ""
                var = tk.StringVar(value=text)
                entry_vars.append(var)

                tk.Entry(list_frame, textvariable=var, width=75).grid(
                    row=i,
                    column=1,
                    padx=5,
                    pady=3
                )

            editor.update_idletasks()
            list_frame.update_idletasks()
            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.yview_moveto(0)
            editor.update()

        def save_current():
            data = load_messages()

            site = editor_site_var.get()
            mode = TYPE_VALUES[mode_display_var.get()]
            tone = TONE_VALUES[tone_display_var.get()]

            data[site][mode][tone] = [v.get() for v in entry_vars]

            save_messages(data)
            messagebox.showinfo("保存", "定型文を保存しました")

        mode_box.bind("<<ComboboxSelected>>", lambda e: redraw())
        tone_box.bind("<<ComboboxSelected>>", lambda e: redraw())

        tk.Button(
            editor,
            text="保存",
            command=save_current,
            width=15
        ).pack(pady=10)

        redraw()

    def open_time_editor(self):
        editor = tk.Toplevel(self.root)
        editor.title("時間編集")
        editor.geometry("420x680")
        editor.attributes("-topmost", True)

        base_hour = int(self.hour_var.get().split(":")[0])
        site_name = SITE_LABELS[self.site_var.get()]
        editor.title(f"【{site_name}】時間編集（基準 {base_hour:02d}時）")

        mode_var = tk.StringVar(value=self.mode_var.get())
        mode_display_var = tk.StringVar(value=TYPE_LABELS[mode_var.get()])

        entry_vars = []

        EDIT_BASE_HOUR = int(self.hour_var.get().split(":")[0])

        def load_times():
            with open("times.json", "r", encoding="utf-8") as f:
                return json.load(f)

        def load_messages():
            with open("messages.json", "r", encoding="utf-8") as f:
                return json.load(f)

        def save_messages(data):
            with open("messages.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        def save_times(data):
            with open("times.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        def normal_to_display(time_data):
            hour = EDIT_BASE_HOUR + time_data["hour"]

            if hour < 0:
                hour += 24
            elif hour > 23:
                hour -= 24

            minute = time_data["minute"]

            return f"{hour:02d}:{minute:02d}"

        def display_to_normal(value):
            hour_text, minute_text = value.split(":")
            hour = int(hour_text)
            minute = int(minute_text)

            hour_offset = hour - EDIT_BASE_HOUR

            return {
                "hour": hour_offset,
                "minute": minute,
            }

        top_frame = tk.Frame(editor)
        top_frame.pack(pady=15)

        tk.Label(top_frame, text="モード").grid(row=0, column=0, padx=5)

        mode_box = ttk.Combobox(
            top_frame,
            textvariable=mode_display_var,
            values=list(TYPE_LABELS.values()),
            state="readonly",
            width=12
        )
        mode_box.grid(row=0, column=1, padx=5)

        list_frame = tk.Frame(editor)
        list_frame.pack(pady=10)

        def redraw():
            nonlocal entry_vars
            entry_vars = []

            for widget in list_frame.winfo_children():
                widget.destroy()

            data = load_times()

            site = self.site_var.get()
            mode = TYPE_VALUES[mode_display_var.get()]

            times = data[site][mode]

            for i, time_data in enumerate(times):
                if mode == "normal":
                    value = normal_to_display(time_data)
                    label = f"{i + 1}件目"
                else:
                    value = str(time_data["after_min"])
                    label = f"{i + 1}件目"

                tk.Label(list_frame, text=label, width=8, anchor="e").grid(
                    row=i,
                    column=0,
                    padx=5,
                    pady=4
                )

                var = tk.StringVar(value=value)
                entry_vars.append(var)

                tk.Entry(list_frame, textvariable=var, width=12).grid(
                    row=i,
                    column=1,
                    padx=5,
                    pady=4
                )

                if mode == "normal":
                    tk.Label(list_frame, text="時刻").grid(
                        row=i,
                        column=2,
                        padx=5
                    )
                else:
                    tk.Label(list_frame, text="分後").grid(
                        row=i,
                        column=2,
                        padx=5
                    )

        def format_time_text(value):
            value = value.strip()

            if ":" in value:
                parts = value.split(":")
                if len(parts) != 2:
                    raise ValueError

                hour = int(parts[0])
                minute = int(parts[1])

            else:
                if not value.isdigit():
                    raise ValueError

                if len(value) == 3:
                    hour = int(value[0])
                    minute = int(value[1:])

                elif len(value) == 4:
                    hour = int(value[:2])
                    minute = int(value[2:])

                else:
                    raise ValueError

            if hour < 0 or hour > 23:
                raise ValueError

            if minute < 0 or minute > 59:
                raise ValueError

            return f"{hour:02d}:{minute:02d}"

        def add_row():
            times_data = load_times()
            messages_data = load_messages()

            mode = TYPE_VALUES[mode_display_var.get()]
            site = self.site_var.get()

            if mode == "normal":
                times_data[site][mode].append({
                    "hour": 0,
                    "minute": 0,
                })
            else:
                times_data[site][mode].append({
                    "after_min": 5,
                })

            for tone in TONE_LABELS.keys():
                messages_data[site][mode][tone].append("")

            save_times(times_data)
            save_messages(messages_data)

            redraw()
            messagebox.showinfo("追加", "編集枠を1件追加しました")

        def delete_row():
            times_data = load_times()
            messages_data = load_messages()

            mode = TYPE_VALUES[mode_display_var.get()]
            site = self.site_var.get()

            if len(times_data[site][mode]) <= 1:
                messagebox.showwarning("確認", "これ以上削除できません")
                return

            confirm = messagebox.askokcancel(
                "削除確認",
                "最後の1件を削除します。\n対応する定型文も削除されます。\nよろしいですか？"
            )

            if not confirm:
                return

            times_data[site][mode].pop()
 
            for tone in TONE_LABELS.keys():
                if len(messages_data[site][mode][tone]) > 0:
                    messages_data[site][mode][tone].pop()

            save_times(times_data)
            save_messages(messages_data)

            redraw()
            messagebox.showinfo("削除", "最後の1件を削除しました")

        def save_current():
            data = load_times()
            mode = TYPE_VALUES[mode_display_var.get()]
            new_times = []

            try:
                if mode == "normal":
                    formatted_values = []

                    for var in entry_vars:
                        formatted = format_time_text(var.get())
                        formatted_values.append(formatted)

                        hour_text, minute_text = formatted.split(":")
                        hour = int(hour_text)
                        minute = int(minute_text)

                        hour_offset = hour - EDIT_BASE_HOUR

                        new_times.append({
                            "hour": hour_offset,
                            "minute": minute,
                        })

                    for i, var in enumerate(entry_vars):
                        var.set(formatted_values[i])

                else:
                    for var in entry_vars:
                        value_text = var.get().strip()

                        if not value_text.isdigit():
                            raise ValueError

                        value = int(value_text)

                        if value < 1 or value > 999:
                            raise ValueError

                        new_times.append({
                            "after_min": value,
                        })

            except:
                messagebox.showerror(
                    "入力エラー",
                    "通常定型は 08:05 / 8:5 / 805 の形式で入力してください。\nLINE・QR定型は 1〜999 の数字のみ入力してください。"
                )
                return

            site = self.site_var.get()

            data[site][mode] = new_times
            save_times(data)

            messagebox.showinfo("保存", "時間を保存しました")

        mode_box.bind("<<ComboboxSelected>>", lambda e: redraw())

        row_button_frame = tk.Frame(editor)
        row_button_frame.pack(pady=5)

        tk.Button(
            row_button_frame,
            text="＋追加",
            command=add_row,
            width=10
        ).pack(side="left", padx=5)

        tk.Button(
            row_button_frame,
            text="－削除",
            command=delete_row,
            width=10
        ).pack(side="left", padx=5)

        tk.Button(
            editor,
            text="保存",
            command=save_current,
            width=15
        ).pack(pady=15)

        redraw()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
