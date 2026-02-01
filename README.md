# 《终末地》无限跳跃脚本

一个用于《终末地》无限跳跃的脚本

## 使用方法

下载exe文件或python文件

[release](https://github.com/chenxi-Eumenides/zmd-infinite-skip-script/releases/latest)

[蓝奏云](https://wwbmf.lanzoul.com/b00zyffp7i) 密码:49fy

1. **管理员身份**运行exe
2. 选择干员配置
3. 进入探索模式，确保索道在1号位
4. 默认按空格键开始跳跃
5. 跳到足够高度后，按右键结束无限跳跃，并开始连点放置1号位的索道
6. 放置成功后，按右键结束放置
7. 等待时，按 `Ctrl+C` 退出脚本

## 配置说明

### 配置文件
脚本使用 `zmd-infinite-skip.toml` 文件存储配置。首次运行时会自动创建默认配置。

该配置每次等待运行完成前会热更新，方便调试。

### 配置结构
```toml
# m_ 开头的按键为鼠标按键
start_keys = ["space"]          # 开始键列表
next_keys = ["m_right"]         # 下一步键列表

[delays.default]
start_delay = 0.1               # 开始延迟（秒）
duration_attack = 0.02          # 左键按下持续时间
delay_attack = 0.08             # 左键释放后延迟
duration_R = 0.02               # R键按下持续时间
delay_R = 0.06                  # R键释放后延迟
duration_ESC = 0.02             # ESC键按下持续时间
delay_ESC = 0.06                # ESC键释放后延迟
put_duration = 0.02             # 拿出索道的时间
put_delay = 0.02                # 拿出索道与左键连点之间的延迟

# 自定义配置
[delays."配置名称"]              # 自定义配置，中文需要用双引号括起来。
# 可以从上面复制
```

其中比较重要的是五个delay项，它们实际控制了每个按键的间隔。

duration项是按键按下的时间，0.02秒默认即可。配置为0也可以正常触发按键。

### 按键命名规则
- 键盘按键：使用标准键名，如 `"space"`, `"a"`, `"r"`, `"esc"`, `"tab"`, `"1"`
- 鼠标按键：使用 `"m_left"`, `"m_right"`, `"m_middle"` 格式
- 支持多个按键，使用数组格式：`["space", "m_right"]`
- 目前不支持组合键。

## 脚本原理

- 使用 `threading.Thread` 运行跳跃/放置循环
- 使用 `threading.Event` 实现安全停止
- 键盘鼠标监听器实时检测用户输入

## 免责声明
⚠️ **使用自动化脚本可能违反游戏服务条款** ⚠️
- 本脚本仅供学习和研究使用
- 使用前请了解游戏的相关规定
- 过度使用可能导致账号受到限制
- 作者不对因使用本脚本造成的任何后果负责
