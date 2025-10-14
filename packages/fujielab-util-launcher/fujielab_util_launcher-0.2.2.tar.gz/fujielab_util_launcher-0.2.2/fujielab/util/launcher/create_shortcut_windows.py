"""
Windows 環境でのショートカット作成機能。
"""

import os
import sys
import platform

from .i18n import tr
from .debug_util import error_print

# Windows環境でのショートカット作成に必要
if platform.system() == "Windows":
    try:
        import win32com.client
        import pythoncom  # noqa: F401

        HAS_WIN32COM = True
    except ImportError:
        HAS_WIN32COM = False
else:
    HAS_WIN32COM = False


def create_windows_shortcut():
    """
    Windows環境でデスクトップにショートカットを作成する関数。

    Returns:
        bool: ショートカット作成の成否
    """
    if not HAS_WIN32COM:
        print(tr("Error: pywin32 package is required for creating shortcuts."))
        print(tr("Please install it using: pip install pywin32"))
        return False

    try:
        # ユーザーのデスクトップパスを取得
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.exists(desktop_path):
            # 日本語環境など、デスクトップパスが異なる場合のフォールバック
            desktop_path = os.path.join(os.path.expanduser("~"), "デスクトップ")
            if not os.path.exists(desktop_path):
                error_print(tr("Error: Could not find the Desktop folder."))
                return False

        # 実行ファイルのパスを取得
        pythonw_exe = sys.executable.replace("python.exe", "pythonw.exe")

        package_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(package_dir, "resources", "icon.ico")
        if not os.path.exists(icon_path):
            error_print(tr("Error: Icon file not found at {}").format(icon_path))
            icon_path = ""

        # ショートカットのパス
        shortcut_path = os.path.join(desktop_path, "Fujielab Launcher.lnk")

        # COM オブジェクトを作成
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)

        # ショートカットのプロパティを設定
        shortcut.TargetPath = pythonw_exe
        shortcut.Arguments = "-m fujielab.util.launcher.run"
        shortcut.WorkingDirectory = os.path.expanduser("~")
        if icon_path:
            shortcut.IconLocation = icon_path
        shortcut.Description = "Fujielab Utility Launcher"

        # ショートカットを保存
        shortcut.Save()

        print(tr("Shortcut created successfully on the Desktop."))
        return True
    except Exception as e:
        print(tr("Error creating shortcut:"), str(e))
        return False
