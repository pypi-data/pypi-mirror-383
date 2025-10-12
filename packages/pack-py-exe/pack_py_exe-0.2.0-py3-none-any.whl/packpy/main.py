import sys
import os
import ctypes
import winreg
from PyQt5.QtWidgets import QApplication
from packpy.gui import PackPyGUI  # 固定导入（与gui.py类名一致）

def get_user_scripts_dir():
    """获取当前用户的Python Scripts目录（pack-py-exe.exe所在位置）"""
    return os.path.join(
        os.path.expanduser("~"),  # 用户主目录（如 C:\Users\38326）
        "AppData", "Roaming", "Python",
        f"Python{sys.version_info.major}{sys.version_info.minor}",  # 适配Python版本
        "Scripts"
    )

def auto_config_path():
    """自动将Scripts目录添加到PATH（临时+永久），无需用户手动操作"""
    scripts_dir = get_user_scripts_dir()
    current_path = os.environ.get("PATH", "")

    # 1. 临时添加（当前会话立即生效，解决首次启动问题）
    if scripts_dir not in current_path:
        os.environ["PATH"] = f"{scripts_dir};{current_path}"

    # 2. 永久添加（写入注册表，重启后仍生效）
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            "Environment",
            0,
            winreg.KEY_READ | winreg.KEY_WRITE
        ) as key:
            # 读取现有PATH
            reg_path, _ = winreg.QueryValueEx(key, "PATH")
            if scripts_dir not in reg_path:
                new_reg_path = f"{scripts_dir};{reg_path}"
                winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_reg_path)
                # 广播系统消息，通知环境变量更新
                ctypes.windll.user32.SendMessageTimeoutW(
                    0xFFFF,  # 广播到所有窗口
                    0x001A,  # WM_SETTINGCHANGE：系统设置变更
                    0,
                    "Environment",  # 通知环境变量更新
                    0,
                    5000,  # 超时时间
                    None
                )
    except Exception:
        # 即使注册表写入失败，临时PATH也已生效，不影响使用
        pass

def main():
    # 自动配置路径（首次启动后永久生效）
    auto_config_path()

    # 启动GUI（与gui.py中的主类名一致）
    app = QApplication(sys.argv)
    window = PackPyGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()