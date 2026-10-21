import pyautogui
import pynput
import time
import json
import os
import sys

# 动作列表，用来存你的操作
actions = []
is_recording = False
is_playing = False

# 保存动作到本地文件，方便下次还能用
def save_actions():
    with open("macro_actions.json", "w", encoding="utf-8") as f:
        json.dump(actions, f)
    print(f"✅ 已保存 {len(actions)} 个动作到文件！")

# 读取本地文件
def load_actions():
    global actions
    if os.path.exists("macro_actions.json"):
        with open("macro_actions.json", "r", encoding="utf-8") as f:
            actions = json.load(f)
        print(f"✅ 成功加载了 {len(actions)} 个动作")
    else:
        print("❌ 没有找到录制文件，请先按 F9 录制！")

# --- 键鼠监听器部分 ---
def on_click(x, y, button, pressed):
    if is_recording and pressed:
        # 记录鼠标点击的坐标
        actions.append(("click", x, y))
        print(f"记录：鼠标点击 ({x}, {y})")

def on_press(key):
    global is_recording, is_playing
    # 快捷键监听：F9 开始录制，F10 停止录制，F11 开始回放，Esc 退出
    if key == pynput.keyboard.Key.f9:
        if is_playing: return
        is_recording = True
        actions.clear()
        print("\n🔴 --- 开始录制动作！请手动操作你的流程... ---")
        return
    elif key == pynput.keyboard.Key.f10:
        if is_recording:
            is_recording = False
            save_actions()
        return
    elif key == pynput.keyboard.Key.f11:
        if not is_recording:
            is_playing = True
            load_actions()
            play_actions()
        return
    elif key == pynput.keyboard.Key.esc:
        print("\n🛑 --- 紧急停止程序 ---")
        os._exit(0)

    # 如果在录制状态，记录普通按键（忽略F9/F10等）
    if is_recording:
        # 用 pynput 的 format 处理按键名字，转为 pyautogui 能识别的文字
        try:
            # 普通字符
            if hasattr(key, 'char') and key.char:
                actions.append(("key", key.char))
                print(f"记录：键盘输入 {key.char}")
            else:
                # 特殊键（回车、Tab等）
                key_name = str(key).replace('Key.', '')
                actions.append(("special_key", key_name))
                print(f"记录：特殊按键 [{key_name}]")
        except Exception:
            pass

def play_actions():
    global is_playing
    print(f"🟢 --- 开始无限循环回放 (共 {len(actions)} 个动作) ---")
    print("💡 提示：如果你发现鼠标跑偏了，只要把鼠标用力甩到屏幕最左上角，就能强行中断回放！")
    try:
        while True:  # 无限循环
            for act in actions:
                if act[0] == "click":
                    pyautogui.click(act[1], act[2])
                elif act[0] == "key":
                    pyautogui.write(act[1])
                elif act[0] == "special_key":
                    pyautogui.press(act[1])
                # 动作之间稍微停顿一下，防止太快把网页卡死
                time.sleep(0.1) 
            print("🔄 完成一轮回放...")
            time.sleep(1.5) # 每轮循环之间休息一下，防止被服务器封号
    except pyautogui.FailSafeException:
        print("🛑 触发左上角安全退出！停止回放。")
        is_playing = False

# 启动监听器
print("==== 极简宏录制器已启动 ====")
print("【F9】开始录制")
print("【F10】停止录制并保存")
print("【F11】开始无限循环回放")
print("【Esc】退出")
print("============================")
print("等待操作中...")

mouse_listener = pynput.mouse.Listener(on_click=on_click)
mouse_listener.start()

# 开始键盘监听，阻塞在这里
with pynput.keyboard.Listener(on_press=on_press) as listener:
    listener.join()
