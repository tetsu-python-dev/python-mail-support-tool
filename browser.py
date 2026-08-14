import asyncio
import time
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright


INPUT_WAIT_TIMEOUT = 2.0
SEND_WAIT_SECONDS = 0.3


BASE_DIR = Path(__file__).resolve().parent
PROFILE_DIR = BASE_DIR / "chrome_profile"

# ポートフォリオ公開用:
# 以下で使用するHTMLセレクタは、実際の業務環境とは異なる汎用的な名称に置き換えています。


class BrowserController:
    def __init__(self):
        self.playwright = None
        self.context = None
        self.page = None
        self.stop_flag = False
        self.current_url = None

    async def start(self):
        self.playwright = await async_playwright().start()

        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
        )

        self.page = (
            self.context.pages[0]
            if self.context.pages
            else await self.context.new_page()
        )

    async def open_url(self, url):
        if self.page is None:
            await self.start()

        self.current_url = url
        await self.page.goto(
            url,
            wait_until="domcontentloaded"
        )

    def stop(self):
        self.stop_flag = True

    def is_past_time(self, item):
        now = datetime.now()

        reserve_time = now.replace(
            hour=item["hour"],
            minute=item["minute"],
            second=0,
            microsecond=0
        )

        return reserve_time <= now

    async def safe_eval(
        self,
        script,
        arg=None,
        timeout=0.5,
        label="未指定"
    ):
        start_time = time.perf_counter()

        try:
            if arg is None:
                result = await asyncio.wait_for(
                    self.page.evaluate(script),
                    timeout=timeout
                )

            else:
                result = await asyncio.wait_for(
                    self.page.evaluate(
                        script,
                        arg
                    ),
                    timeout=timeout
                )

            elapsed = (
                time.perf_counter()
                - start_time
            )

            print(
                f"safe_eval [{label}] OK: "
                f"{elapsed:.3f}秒",
                flush=True
            )

            return result

        except Exception as e:
            elapsed = (
                time.perf_counter()
                - start_time
            )

            print(
                f"safe_eval [{label}] エラー: "
                f"{elapsed:.3f}秒 "
                f"{repr(e)}",
                flush=True
            )

            return None

    async def run_reservations(
        self,
        reservations,
        mode,
        progress_callback
    ):
        self.stop_flag = False
        total = len(reservations)

        all_start_time = time.perf_counter()

        print("実行開始", flush=True)
        print("件数:", total, flush=True)
        print("モード:", mode, flush=True)

        for index, item in enumerate(
            reservations,
            start=1
        ):
            item_start_time = time.perf_counter()

            if self.stop_flag:
                progress_callback(
                    index - 1,
                    total,
                    "停止",
                    ""
                )
                break

            if mode == "normal":
                reserve_time = (
                    f"{item['hour']:02d}:"
                    f"{item['minute']:02d}"
                )

                if self.is_past_time(item):
                    print(
                        f"{reserve_time} は"
                        "過去時間なのでスキップ",
                        flush=True
                    )

                    progress_callback(
                        index,
                        total,
                        "過去時間スキップ",
                        reserve_time
                    )

                    continue

            else:
                reserve_time = (
                    f"{item['after_min']}分後"
                )

            print("", flush=True)

            print(
                f"========== "
                f"{index}/{total} "
                f"{reserve_time} "
                f"==========",
                flush=True
            )

            progress_callback(
                index,
                total,
                "実行中",
                reserve_time
            )

            input_start_time = (
                time.perf_counter()
            )

            await self.input_one(
                item,
                mode
            )

            input_elapsed = (
                time.perf_counter()
                - input_start_time
            )

            print(
                f"入力処理合計: "
                f"{input_elapsed:.3f}秒",
                flush=True
            )

            match_start_time = (
                time.perf_counter()
            )

            ok = await self.wait_until_form_matches(
                item,
                mode
            )

            match_elapsed = (
                time.perf_counter()
                - match_start_time
            )

            print(
                f"入力反映確認合計: "
                f"{match_elapsed:.3f}秒",
                flush=True
            )

            if ok:
                print(
                    "入力反映OK",
                    flush=True
                )

            else:
                print(
                    "入力反映確認タイムアウト。"
                    "画面上の値を確認してください",
                    flush=True
                )

            print(
                "送信クリック",
                flush=True
            )

            click_start_time = (
                time.perf_counter()
            )

            try:
                await asyncio.wait_for(
                    self.page.click(
                        "#submitButton"
                    ),
                    timeout=0.5
                )

                click_elapsed = (
                    time.perf_counter()
                    - click_start_time
                )

                print(
                    f"送信クリック OK: "
                    f"{click_elapsed:.3f}秒",
                    flush=True
                )

            except Exception as e:
                click_elapsed = (
                    time.perf_counter()
                    - click_start_time
                )

                print(
                    "送信クリック "
                    "タイムアウト/エラー: "
                    f"{click_elapsed:.3f}秒 "
                    f"{repr(e)}",
                    flush=True
                )

            sleep_start_time = (
                time.perf_counter()
            )

            # 送信確定前に次の文章を
            # 上書きしないための待機
            await asyncio.sleep(
                SEND_WAIT_SECONDS
            )

            sleep_elapsed = (
                time.perf_counter()
                - sleep_start_time
            )

            print(
                f"送信後待機: "
                f"{sleep_elapsed:.3f}秒",
                flush=True
            )

            item_elapsed = (
                time.perf_counter()
                - item_start_time
            )

            print(
                f"1件合計: "
                f"{item_elapsed:.3f}秒",
                flush=True
            )

            print(
                "次へ",
                flush=True
            )

        all_elapsed = (
            time.perf_counter()
            - all_start_time
        )

        if not self.stop_flag:
            progress_callback(
                total,
                total,
                "完了",
                ""
            )

            print(
                "完了",
                flush=True
            )

        print(
            f"全体処理時間: "
            f"{all_elapsed:.3f}秒",
            flush=True
        )

    async def input_one(
        self,
        item,
        mode
    ):
        print(
            "----- 入力開始 -----",
            flush=True
        )

        print(
            "mode:",
            mode,
            flush=True
        )

        print(
            "message:",
            item["message"],
            flush=True
        )

        print(
            "after_min:",
            item.get("after_min"),
            flush=True
        )

        print(
            "hour:",
            item.get("hour"),
            flush=True
        )

        print(
            "minute:",
            item.get("minute"),
            flush=True
        )

        await self.safe_eval(
            """
            message => {
                const el = document.querySelector(
                    "#messageInput"
                );

                if (el) {
                    el.value = "";
                    el.value = message;
                }
            }
            """,
            item["message"],
            label="メッセージ入力"
        )

        if mode == "normal":
            await self.safe_eval(
                """
                () => {
                    const el =
                        document.querySelector(
                            'input[name="reservation_type"]'
                            + '[value="scheduled"]'
                        );

                    if (el) {
                        el.checked = true;
                    }
                }
                """,
                label="通常予約ラジオ"
            )

            today = datetime.now().strftime(
                "%Y/%m/%d"
            )

            await self.safe_eval(
                """
                dateText => {
                    const el =
                        document.querySelector(
                            'input[name="reservation_date"]'
                        );

                    if (el) {
                        el.value = "";
                        el.value = dateText;
                    }
                }
                """,
                today,
                label="日付入力"
            )

            await self.safe_eval(
                """
                hour => {
                    const el =
                        document.querySelector(
                            'select[name="reservation_hour"]'
                        );

                    if (el) {
                        el.value = String(hour);
                    }
                }
                """,
                item["hour"],
                label="時入力"
            )

            await self.safe_eval(
                """
                minute => {
                    const el =
                        document.querySelector(
                            'select[name="reservation_minute"]'
                        );

                    if (el) {
                        el.value = String(minute);
                    }
                }
                """,
                item["minute"],
                label="分入力"
            )

        else:
            await self.safe_eval(
                """
                () => {
                    const el =
                        document.querySelector(
                            'input[name="reservation_type"]'
                            + '[value="delay"]'
                        );

                    if (el) {
                        el.checked = true;
                    }
                }
                """,
                label="分後予約ラジオ"
            )

            await self.safe_eval(
                """
                minute => {
                    const el =
                        document.querySelector(
                            "#delayMinutes"
                        );

                    if (el) {
                        el.value = "";
                        el.value = String(minute);
                    }
                }
                """,
                item["after_min"],
                label="何分後入力"
            )

    async def get_form_state(self):
        return await self.safe_eval(
            """
            () => {
                const messageEl =
                    document.querySelector(
                        "#messageInput"
                    );

                const reserveType2 =
                    document.querySelector(
                        'input[name="reservation_type"]'
                        + '[value="delay"]'
                    );

                const reserveType3 =
                    document.querySelector(
                        'input[name="reservation_type"]'
                        + '[value="scheduled"]'
                    );

                const minEl =
                    document.querySelector(
                        "#delayMinutes"
                    );

                const hourEl =
                    document.querySelector(
                        'select[name="reservation_hour"]'
                    );

                const minuteEl =
                    document.querySelector(
                        'select[name="reservation_minute"]'
                    );

                return {
                    message: messageEl
                        ? messageEl.value
                        : null,

                    type2: reserveType2
                        ? reserveType2.checked
                        : null,

                    type3: reserveType3
                        ? reserveType3.checked
                        : null,

                    after_min: minEl
                        ? minEl.value
                        : null,

                    hour: hourEl
                        ? hourEl.value
                        : null,

                    minute: minuteEl
                        ? minuteEl.value
                        : null
                };
            }
            """,
            timeout=0.5,
            label="画面状態取得"
        )

    async def wait_until_form_matches(
        self,
        item,
        mode
    ):
        start_time = time.perf_counter()
        check_count = 0

        while True:
            check_count += 1

            print(
                f"入力反映確認 "
                f"{check_count}回目",
                flush=True
            )

            state = await self.get_form_state()

            if state:
                print(
                    "画面状態:",
                    state,
                    flush=True
                )

                if mode == "normal":
                    if (
                        state["message"]
                        == item["message"]
                        and state["type3"] is True
                        and state["hour"]
                        == str(item["hour"])
                        and state["minute"]
                        == str(item["minute"])
                    ):
                        elapsed = (
                            time.perf_counter()
                            - start_time
                        )

                        print(
                            "入力反映一致: "
                            f"{check_count}回目 "
                            f"{elapsed:.3f}秒",
                            flush=True
                        )

                        return True

                else:
                    if (
                        state["message"]
                        == item["message"]
                        and state["type2"] is True
                        and state["after_min"]
                        == str(item["after_min"])
                    ):
                        elapsed = (
                            time.perf_counter()
                            - start_time
                        )

                        print(
                            "入力反映一致: "
                            f"{check_count}回目 "
                            f"{elapsed:.3f}秒",
                            flush=True
                        )

                        return True

            elapsed = (
                time.perf_counter()
                - start_time
            )

            if elapsed >= INPUT_WAIT_TIMEOUT:
                print(
                    "入力反映確認終了: "
                    f"{check_count}回 "
                    f"{elapsed:.3f}秒",
                    flush=True
                )

                return False

            await asyncio.sleep(0.1)
