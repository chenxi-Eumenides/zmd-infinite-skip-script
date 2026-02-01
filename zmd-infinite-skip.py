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

CONFIG_FILE = "zmd-infinite-skip.toml"
DEFAULT_CONFIG = {
    "start_keys": [
        "space",
    ],
    "next_keys": [
        "m_right",
    ],
    "delays": {
        "start_delay": 0.4,
        "duration_attack": 0.05,
        "delay_attack": 0.18,
        "duration_R": 0.05,
        "delay_R": 0.19,
        "duration_ESC": 0.05,
        "delay_ESC": 0.15,
        "put_duration": 0.05,
        "put_delay": 0.05,
    },
}
pyautogui.PAUSE = 0.002


def skip_loop(delays: dict[str, float], stop_event: Event):
    """
    执行无限跳跃循环。

    通过模拟鼠标左键、R键和ESC键的按下/释放操作来实现游戏中的无限跳跃。
    循环会持续执行直到 stop_event 被设置。

    Args:
        delays: 包含各阶段延迟时间的字典
        stop_event: 线程停止事件，当被设置时循环终止
    """
    duration_attack = delays.get(
        "duration_attack", DEFAULT_CONFIG["delays"]["duration_attack"]
    )
    delay_attack = delays.get("delay_attack", DEFAULT_CONFIG["delays"]["delay_attack"])
    duration_R = delays.get("duration_R", DEFAULT_CONFIG["delays"]["duration_R"])
    delay_R = delays.get("delay_R", DEFAULT_CONFIG["delays"]["delay_R"])
    duration_ESC = delays.get("duration_ESC", DEFAULT_CONFIG["delays"]["duration_ESC"])
    delay_ESC = delays.get("delay_ESC", DEFAULT_CONFIG["delays"]["delay_ESC"])

    sleep(delays.get("start_delay", DEFAULT_CONFIG["delays"]["start_delay"]))
    while not stop_event.is_set():
        # 左键r
        pyautogui.mouseDown(button="left")
        sleep(duration_attack)
        pyautogui.mouseUp(button="left")
        sleep(delay_attack)
        # r键
        pyautogui.keyDown("r")
        sleep(duration_R)
        pyautogui.keyUp("r")
        sleep(delay_R)
        # esc键
        pyautogui.keyDown("esc")
        sleep(duration_ESC)
        pyautogui.keyUp("esc")
        if stop_event.wait(timeout=delay_ESC):
            break


def put_loop(delays: dict[str, float], stop_event: Event):
    """
    执行连点放置建筑循环。

    先按Tab和1键切换到建筑模式，然后持续点击鼠标左键放置建筑。
    循环会持续执行直到 stop_event 被设置。

    Args:
        delays: 包含放置延迟时间的字典
        stop_event: 线程停止事件，当被设置时循环终止
    """
    put_duration = delays.get("put_duration", DEFAULT_CONFIG["delays"]["put_duration"])
    put_delay = delays.get("put_delay", DEFAULT_CONFIG["delays"]["put_delay"])
    pyautogui.press(keys="tab")
    sleep(0.1)
    pyautogui.press(keys="1")
    sleep(0.1)
    while not stop_event.is_set():
        pyautogui.mouseDown(button="left")
        sleep(put_duration)
        pyautogui.mouseUp(button="left")
        if stop_event.wait(timeout=put_delay):
            break


def start_check(
    key: keyboard.Key | mouse.Button,
    pressed: bool,
    start_key_list: list[str],
    start_event: Event,
):
    """
    检查是否按下了开始键。

    根据按键事件判断是否按下了配置的开始键，如果是则设置开始事件。

    Args:
        key: 键盘按键或鼠标按钮对象
        pressed: 按键是否被按下（True表示按下，False表示释放）
        start_key_list: 开始键列表
        start_event: 开始事件，当检测到开始键时被设置
    """
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
    """
    检查是否按下了停止/下一步键。

    根据按键事件判断是否按下了配置的下一步键，如果是则设置停止事件。

    Args:
        key: 键盘按键或鼠标按钮对象
        pressed: 按键是否被按下（True表示按下，False表示释放）
        next_key_list: 下一步键列表
        stop_event: 停止事件，当检测到下一步键时被设置
    """
    if hasattr(key, "name") and key.name in next_key_list:
        stop_event.set()
    elif hasattr(key, "char") and key.char in next_key_list:
        stop_event.set()
    elif hasattr(key, "name") and "m_" + key.name in next_key_list and pressed:
        stop_event.set()


def wait_start(start_key_list: list[str]):
    """
    等待开始按键。

    启动键盘和鼠标监听器，等待用户按下配置的开始键。
    检测到开始键后，等待指定的开始延迟，然后返回。

    Args:
        delays: 包含延迟时间的字典
        start_key_list: 开始键列表

    Raises:
        KeyboardInterrupt: 当用户按下Ctrl+C时抛出
    """
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
    except KeyboardInterrupt as e:
        start_event.set()
        if mouse_start_listener.is_alive():
            mouse_start_listener.stop()
        if keyboard_start_listener.is_alive():
            keyboard_start_listener.stop()
        raise e


def infinite_skip(delays: dict[str, float], next_key_list: list[str]) -> bool:
    """
    主循环，执行无限跳跃。

    启动无限跳跃线程和键盘鼠标监听器，等待用户按下下一步键或Ctrl+C。

    Args:
        delays: 包含延迟时间的字典
        next_key_list: 下一步键列表

    Returns:
        bool: 是否正常结束（True表示正常结束，False表示被中断）
    """
    stop_event = Event()
    skip_thread = Thread(
        target=skip_loop,
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
        skip_thread.start()
        keyboard_stop_listener.start()
        mouse_stop_listener.start()
        while skip_thread.is_alive():
            skip_thread.join(timeout=0.01)
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
        if skip_thread.is_alive():
            skip_thread.join()
        # raise e
        return False


def put_building(delays: dict[str, float], next_key_list: list[str]):
    """
    放置建筑功能。

    启动连点放置建筑线程和键盘鼠标监听器，等待用户按下下一步键或Ctrl+C。

    Args:
        delays: 包含延迟时间的字典
        next_key_list: 下一步键列表
    """
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


def reset_control():
    pyautogui.mouseUp(button="left")
    pyautogui.press(keys="tab")


def read_config() -> dict[str, dict[str, float | str]]:
    """
    读取配置文件。

    如果配置文件不存在，则返回默认配置。
    如果配置文件存在，则读取并检查配置完整性。

    Returns:
        dict: 完整的配置字典
    """
    if not Path(CONFIG_FILE).exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = load(f)
    return check_config(config)


def update_delays(
    config: dict[str, dict[str, float]],
) -> dict[str, dict[str, float | str]]:
    """
    更新延迟配置。

    检查配置文件是否有更新，如果有则更新配置中的延迟参数。

    Args:
        config: 当前配置字典

    Returns:
        dict: 更新后的配置字典
    """
    if not Path(CONFIG_FILE).exists():
        return config
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        new_config = load(f)
    if config.get("delays") != new_config.get("delays"):
        config["delays"] = new_config.get("delays")
    return check_config(config)


def save_config(config: dict[str, dict[str, float | str]]):
    """
    保存配置文件。

    Args:
        config: 配置字典
    """
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        dump(config, f)


def check_config(config):
    """
    检查并补全配置。

    确保配置字典中包含所有必要的键，缺失的键使用默认值填充。

    Args:
        config: 待检查的配置字典

    Returns:
        dict: 完整的配置字典
    """
    if not config.get("start_keys"):
        config["start_keys"] = DEFAULT_CONFIG.get("start_keys")
    if not config.get("next_keys"):
        config["next_keys"] = DEFAULT_CONFIG.get("next_keys")
    if not config.get("delays"):
        config["delays"] = DEFAULT_CONFIG.get("delays")
    else:
        if config["delays"].get("start_delay") is None:
            config["delays"]["start_delay"] = DEFAULT_CONFIG["delays"]["start_delay"]
        if config["delays"].get("delay_attack") is None:
            config["delays"]["delay_attack"] = DEFAULT_CONFIG["delays"]["delay_attack"]
        if config["delays"].get("duration_attack") is None:
            config["delays"]["duration_attack"] = DEFAULT_CONFIG["delays"][
                "duration_attack"
            ]
        if config["delays"].get("delay_R") is None:
            config["delays"]["delay_R"] = DEFAULT_CONFIG["delays"]["delay_R"]
        if config["delays"].get("duration_R") is None:
            config["delays"]["duration_R"] = DEFAULT_CONFIG["delays"]["duration_R"]
        if config["delays"].get("delay_ESC") is None:
            config["delays"]["delay_ESC"] = DEFAULT_CONFIG["delays"]["delay_ESC"]
        if config["delays"].get("duration_ESC") is None:
            config["delays"]["duration_ESC"] = DEFAULT_CONFIG["delays"]["duration_ESC"]
        if config["delays"].get("put_duration") is None:
            config["delays"]["put_duration"] = DEFAULT_CONFIG["delays"]["put_duration"]
        if config["delays"].get("put_delay") is None:
            config["delays"]["put_delay"] = DEFAULT_CONFIG["delays"]["put_delay"]
    return config


def print_help(config: dict[str, dict[str, float | str]]):
    """
    打印帮助信息。

    Args:
        config: 配置字典
    """
    print(f"本脚本用于终末地无限跳")
    print(f"")
    print(f"请确保当前位于探索模式，索道位于1号位。")
    print(f"默认参数为大潘，其他干员请自行调整配置文件")
    print(f"延迟配置每次循环前会热更新")
    print(f"")
    print(f"开始按键 : {[key for key in config.get('start_keys')]}")
    print(f"下一步按键 : {[key for key in config.get('next_keys')]}")
    print(f"'m_' 开头的按键为鼠标按键")


def main() -> None:
    """
    主函数。

    程序入口点，负责读取配置、打印帮助信息，并进入主循环。
    主循环包括等待开始、执行无限跳跃、放置建筑等步骤。
    支持通过Ctrl+C优雅退出并保存配置。
    """
    config = read_config()
    print_help(config)
    try:
        while True:
            print("")
            wait_start(config.get("start_keys"))
            update_delays(config)
            if infinite_skip(config.get("delays"), config.get("next_keys")):
                put_building(config.get("delays"), config.get("next_keys"))
            reset_control()
    except KeyboardInterrupt:
        reset_control()
        update_delays(config)
        save_config(config)
        print("\n保存配置文件并退出")
    except Exception as e:
        print(f"报错：{e}")


if __name__ == "__main__":
    main()
