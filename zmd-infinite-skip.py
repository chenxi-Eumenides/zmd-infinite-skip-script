# /// script
# requires-python = ">=3.13"
# dependencies = [
#     'pynput',
#     'toml',
#     'pyautogui',
# ]
# ///

from threading import Event, Thread
from toml import load, dump
from pathlib import Path
from time import sleep

from pynput import keyboard, mouse
import pyautogui

CONFIG_FILE = "zmd-fly.toml"
DEFAULT_CONFIG = {
    "start_keys": [
        "space",
    ],
    "next_keys": [
        "m_right",
    ],
    "delays": {
        "start_delay": 0.1,
        "duration_1": 0.02,
        "delay_1": 0.08,
        "duration_2": 0.02,
        "delay_2": 0.06,
        "duration_3": 0.02,
        "delay_3": 0.06,
        "put_duration": 0.02,
        "put_delay": 0.02,
    },
}


def fly_loop(delays: dict[str, float], stop_event: Event):
    duration_1 = delays.get("duration_1", DEFAULT_CONFIG["delays"]["duration_1"])
    delay_1 = delays.get("delay_1", DEFAULT_CONFIG["delays"]["delay_1"])
    duration_2 = delays.get("duration_2", DEFAULT_CONFIG["delays"]["duration_2"])
    delay_2 = delays.get("delay_2", DEFAULT_CONFIG["delays"]["delay_2"])
    duration_3 = delays.get("duration_3", DEFAULT_CONFIG["delays"]["duration_3"])
    delay_3 = delays.get("delay_3", DEFAULT_CONFIG["delays"]["delay_3"])
    while not stop_event.is_set():
        # 左键
        pyautogui.mouseDown(button="left")
        if stop_event.wait(timeout=duration_1):
            break
        pyautogui.mouseUp(button="left")
        if stop_event.wait(timeout=delay_1):
            break
        # r键
        pyautogui.keyDown("r")
        if stop_event.wait(timeout=duration_2):
            break
        pyautogui.keyUp("r")
        if stop_event.wait(timeout=delay_2):
            break
        # esc键
        pyautogui.keyDown("esc")
        if stop_event.wait(timeout=duration_3):
            break
        pyautogui.keyUp("esc")
        if stop_event.wait(timeout=delay_3):
            break


def put_loop(delays: dict[str, float], stop_event: Event):
    put_duration = delays.get("put_duration", DEFAULT_CONFIG["delays"]["put_duration"])
    put_delay = delays.get("put_delay", DEFAULT_CONFIG["delays"]["put_delay"])
    pyautogui.press(keys="tab")
    pyautogui.press(keys="1")
    while not stop_event.is_set():
        pyautogui.mouseDown(button="left")
        if stop_event.wait(timeout=put_duration):
            break
        pyautogui.mouseUp(button="left")
        if stop_event.wait(timeout=put_delay):
            break


def start_check(
    key: keyboard.Key | mouse.Button,
    pressed: bool,
    start_key_list: list[str],
    start_event: Event,
):
    if hasattr(key, "name") and key.name in start_key_list:
        start_event.set()
    elif hasattr(key, "char") and key.char in start_key_list:
        start_event.set()
    elif hasattr(key, "name") and "m_" + key.name in start_key_list and pressed:
        start_event.set()


def stop_check(
    key: keyboard.Key | mouse.Button,
    pressed: bool,
    next_key_list: list[str],
    stop_event: Event,
):
    if hasattr(key, "name") and key.name in next_key_list:
        stop_event.set()
    elif hasattr(key, "char") and key.char in next_key_list:
        stop_event.set()
    elif hasattr(key, "name") and "m_" + key.name in next_key_list and pressed:
        stop_event.set()


def wait_start(delays: dict[str, float], start_key_list: list[str]):
    start_event = Event()
    keyboard_start_listener = keyboard.Listener(
        on_press=lambda key: start_check(key, True, start_key_list, start_event),
    )
    mouse_start_listener = mouse.Listener(
        on_click=lambda x, y, button, pressed: start_check(
            button, pressed, start_key_list, start_event
        ),
    )
    # 等待跳跃键
    print(f"+ 等待按下开始键{[key for key in start_key_list]}，Ctrl+C 结束脚本")
    try:
        mouse_start_listener.start()
        keyboard_start_listener.start()
        while not start_event.is_set():
            start_event.wait(timeout=0.01)
        start_event.set()
        mouse_start_listener.stop()
        keyboard_start_listener.stop()
        sleep(delays.get("start_delay", DEFAULT_CONFIG["delays"]["start_delay"]))
    except KeyboardInterrupt as e:
        start_event.set()
        if mouse_start_listener.is_alive():
            mouse_start_listener.stop()
        if keyboard_start_listener.is_alive():
            keyboard_start_listener.stop()
        raise e


def main_loop(delays: dict[str, float], next_key_list: list[str]) -> bool:
    stop_event = Event()
    fly_thread = Thread(
        target=fly_loop,
        args=(
            delays,
            stop_event,
        ),
    )
    keyboard_stop_listener = keyboard.Listener(
        on_press=lambda key: stop_check(key, True, next_key_list, stop_event),
    )
    mouse_stop_listener = mouse.Listener(
        on_click=lambda x, y, button, pressed: stop_check(
            button, pressed, next_key_list, stop_event
        ),
    )
    try:
        # 开始循环
        print(f"+ 开始无限跳跃")
        print(
            f"  - 等待下一步按键{[key for key in next_key_list]}，Ctrl+C 中止当前循环"
        )
        fly_thread.start()
        keyboard_stop_listener.start()
        mouse_stop_listener.start()
        while fly_thread.is_alive():
            fly_thread.join(timeout=0.01)
        # 结束循环
        print("  - 结束无限跳跃")
        stop_event.set()
        mouse_stop_listener.stop()
        keyboard_stop_listener.stop()
        return True
    except KeyboardInterrupt as e:
        stop_event.set()
        if mouse_stop_listener.is_alive():
            mouse_stop_listener.stop()
        if keyboard_stop_listener.is_alive():
            keyboard_stop_listener.stop()
        if fly_thread.is_alive():
            fly_thread.join()
        # raise e
        return False


def put_building(delays: dict[str, float], next_key_list: list[str]):
    stop_event = Event()
    put_thread = Thread(
        target=put_loop,
        args=(
            delays,
            stop_event,
        ),
    )
    keyboard_stop_listener = keyboard.Listener(
        on_press=lambda key: stop_check(key, True, next_key_list, stop_event),
    )
    mouse_stop_listener = mouse.Listener(
        on_click=lambda x, y, button, pressed: stop_check(
            button, pressed, next_key_list, stop_event
        ),
    )
    try:
        # 开始循环
        print("+ 开始连点放置建筑")
        print(
            f"  - 等待下一步按键{[key for key in next_key_list]}，Ctrl+C 中止当前循环"
        )
        put_thread.start()
        keyboard_stop_listener.start()
        mouse_stop_listener.start()
        while put_thread.is_alive():
            put_thread.join(timeout=0.01)
        # 结束循环
        print("  - 结束连点放置建筑")
        stop_event.set()
        mouse_stop_listener.stop()
        keyboard_stop_listener.stop()
    except KeyboardInterrupt as e:
        stop_event.set()
        if mouse_stop_listener.is_alive():
            mouse_stop_listener.stop()
        if keyboard_stop_listener.is_alive():
            keyboard_stop_listener.stop()
        if put_thread.is_alive():
            put_thread.join()
        # raise e


def read_config() -> dict[str, dict[str, float | str]]:
    if not Path(CONFIG_FILE).exists():
        return DEFAULT_CONFIG
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = load(f)
    return check_config(config)


def update_delays(
    config: dict[str, dict[str, float]],
) -> dict[str, dict[str, float | str]]:
    if not Path(CONFIG_FILE).exists():
        return
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        new_config = load(f)
    if config.get("delays") != new_config.get("delays"):
        config["delays"] = new_config.get("delays")
    return check_config(config)


def save_config(config: dict[str, dict[str, float | str]]):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        dump(config, f)


def check_config(config):
    if not config.get("start_keys"):
        config["start_keys"] = DEFAULT_CONFIG.get("start_keys")
    if not config.get("next_keys"):
        config["next_keys"] = DEFAULT_CONFIG.get("next_keys")
    if not config.get("delays"):
        config["delays"] = DEFAULT_CONFIG.get("delays")
    else:
        if not config["delays"].get("start_delay"):
            config["delays"]["start_delay"] = DEFAULT_CONFIG["delays"]["start_delay"]
        if not config["delays"].get("delay_1"):
            config["delays"]["delay_1"] = DEFAULT_CONFIG["delays"]["delay_1"]
        if not config["delays"].get("duration_1"):
            config["delays"]["duration_1"] = DEFAULT_CONFIG["delays"]["duration_1"]
        if not config["delays"].get("delay_2"):
            config["delays"]["delay_2"] = DEFAULT_CONFIG["delays"]["delay_2"]
        if not config["delays"].get("duration_2"):
            config["delays"]["duration_2"] = DEFAULT_CONFIG["delays"]["duration_2"]
        if not config["delays"].get("delay_3"):
            config["delays"]["delay_3"] = DEFAULT_CONFIG["delays"]["delay_3"]
        if not config["delays"].get("duration_3"):
            config["delays"]["duration_3"] = DEFAULT_CONFIG["delays"]["duration_3"]
        if not config["delays"].get("put_duration"):
            config["delays"]["put_duration"] = DEFAULT_CONFIG["delays"]["put_duration"]
        if not config["delays"].get("put_delay"):
            config["delays"]["put_delay"] = DEFAULT_CONFIG["delays"]["put_delay"]
    return config


def print_help(config: dict[str, dict[str, float | str]]):
    print(f"本脚本用于终末地无限跳\n")
    print(f"请确保当前位于探索模式，索道位于1号位。")
    print(f"默认延迟参数不可用，请自行调整配置文件")
    print(f"开始按键 : {[key for key in config.get('start_keys')]}")
    print(f"下一步按键 : {[key for key in config.get('next_keys')]}")
    print(f"'m_' 开头的按键为鼠标按键")


def main() -> None:
    config = read_config()
    print_help(config)
    try:
        while True:
            print("")
            update_delays(config)
            wait_start(config.get("delays"), config.get("start_keys"))
            if main_loop(config.get("delays"), config.get("next_keys")):
                put_building(config.get("delays"), config.get("next_keys"))
    except KeyboardInterrupt:
        save_config(config)
        print("\n保存配置文件并退出")
    except Exception as e:
        print(f"报错：{e}")
        save_config(config)
        print("保存配置文件并退出")


if __name__ == "__main__":
    main()
