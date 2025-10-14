import os
import sys
import platform

from .config_manager import LauncherConfigManager
from .i18n import set_language, tr
import time
import argparse
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QPropertyAnimation, QTimer, QEasingCurve, pyqtProperty
from .debug_util import debug_print, set_debug_mode
from .main_window import MainWindow

# Windows限定機能がある場合にインポート
if platform.system() == "Windows":
    from .create_shortcut import create_windows_shortcut
elif platform.system() == "Darwin":
    from .create_shortcut import create_macos_shortcut


class FadingSplashScreen(QSplashScreen):
    def __init__(self, pixmap):
        super().__init__(pixmap, Qt.WindowStaysOnTopHint)
        self.setWindowOpacity(1.0)
        self._opacity = 1.0

    def get_opacity(self):
        return self._opacity

    def set_opacity(self, opacity):
        self._opacity = opacity
        self.setWindowOpacity(opacity)

    opacity = pyqtProperty(float, get_opacity, set_opacity)

    def fadeOut(self, duration=500, callback=None):
        # アニメーションのパフォーマンスを最適化
        self.animation = QPropertyAnimation(self, b"opacity")
        self.animation.setDuration(duration)  # ミリ秒
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(
            QEasingCurve.Linear
        )  # よりスムーズなアニメーション

        # コールバック前に事前準備を行う
        if callback:
            self.animation.valueChanged.connect(
                lambda v: QApplication.processEvents()
            )  # アニメーション中もUIを更新

            # アニメーション完了前（80%まで進んだ時点）で事前にコールバックを実行
            def early_callback(v):
                if v <= 0.2 and not hasattr(self, "_callback_executed"):
                    self._callback_executed = True
                    callback()

            self.animation.valueChanged.connect(early_callback)

        self.animation.start(
            QPropertyAnimation.DeleteWhenStopped
        )  # 使い終わったらメモリを解放
        debug_print("[debug] Starting splash screen fade-out")


def get_default_config_path():
    """Return the path to the launcher's default YAML configuration file."""
    return LauncherConfigManager.get_default_config_path()


def create_default_config(config_path):
    """Create a default YAML configuration using ``LauncherConfigManager``."""
    import platform
    import subprocess

    try:
        if platform.system() == "Windows":
            sys_path = (
                subprocess.check_output(["where", "python"], universal_newlines=True)
                .strip()
                .split("\n")[0]
            )
        else:
            sys_path = subprocess.check_output(
                ["which", "python3"], universal_newlines=True
            ).strip()
    except Exception:
        sys_path = sys.executable

    manager = LauncherConfigManager(config_path)
    manager.set_default_interpreter("system", sys_path)
    manager.set_default_workdir(os.getcwd())


def ensure_config(reset=False, ask_dialog=None):
    """Ensure that the YAML configuration file exists."""
    config_path = get_default_config_path()

    if reset and os.path.exists(config_path):
        if ask_dialog:
            res = ask_dialog()
            if res == QMessageBox.No:
                return config_path
        os.remove(config_path)

    if not os.path.exists(config_path):
        create_default_config(config_path)

    return config_path


def ask_reset_dialog():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Question)
    msg.setWindowTitle(tr("Confirm recreate config"))
    msg.setText(
        tr(
            "Create new config from command line?\n(Existing settings will be overwritten)"
        )
    )
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    return msg.exec_()


def parse_arguments():
    """Parse command line arguments with language support."""
    # Pre-parse only --lang to determine language for help messages
    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument(
        "--lang",
        choices=["en", "ja"],
        default=None,
        help=tr("Language for UI (en or ja). If omitted, system locale is used."),
    )
    known, remaining = pre.parse_known_args()

    # Set language early so translation works for help strings
    set_language(known.lang)

    parser = argparse.ArgumentParser(
        description="Fujielab Utility Launcher", parents=[pre]
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help=tr("Enable debug mode. Detailed log messages will be displayed."),
    )
    parser.add_argument(
        "-r",
        "--reset-config",
        action="store_true",
        help=tr("Reset the configuration file. Existing settings will be overwritten."),
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default=None,
        help=tr("Specify the path of the settings file to load at startup."),
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help=tr("Display version information and exit."),
    )

    # Shortcut creation option for supported OS
    if platform.system() == "Windows":
        parser.add_argument(
            "--create-shortcut",
            action="store_true",
            help=tr("Create a shortcut on the Windows Desktop. Windows only."),
        )
    elif platform.system() == "Darwin":
        parser.add_argument(
            "--create-shortcut",
            action="store_true",
            help=tr("Create a shortcut in the Applications folder. macOS only."),
        )

    return parser.parse_args(remaining), known.lang


def main():
    # コマンドライン引数の解析
    args, lang = parse_arguments()

    # UI language
    set_language(lang)
    debug_print(f"[debug] UI language set to: {lang if lang else 'system default'}")

    # デバッグモードの設定
    set_debug_mode(args.debug)
    if args.debug:
        debug_print("[debug] Launcher started in debug mode")

    # バージョン情報表示
    if args.version:
        print("Fujielab Utility Launcher v0.2.2")
        return 0

    # Shortcut creation for supported OS
    if hasattr(args, "create_shortcut") and args.create_shortcut:
        if platform.system() == "Windows":
            success = create_windows_shortcut()
        elif platform.system() == "Darwin":
            success = create_macos_shortcut()
        else:
            print(tr("Error creating shortcut:"), "Unsupported OS")
            success = False
        return 0 if success else 1

    # 設定ファイルのリセットフラグ
    # -cオプションが指定されている場合は、常に設定をリセットする
    reset_config = args.reset_config or (args.config is not None)

    # コマンドラインで指定された設定ファイルパス
    config_import_path = args.config

    app = QApplication(sys.argv)

    # スプラッシュスクリーン表示開始時間を記録
    splash_start_time = time.time()

    # スプラッシュスクリーンの表示
    splash_pix = QPixmap(
        os.path.join(os.path.dirname(__file__), "resources", "splash.png")
    )
    splash = FadingSplashScreen(splash_pix)
    splash.setAutoFillBackground(True)
    splash.show()
    app.processEvents()

    # アプリケーションアイコンを設定 - すぐに開始して並行処理
    try:
        # まず.icoファイルを優先して試す（Windowsでより適切）
        ico_path = os.path.join(os.path.dirname(__file__), "resources", "icon.ico")
        png_path = os.path.join(os.path.dirname(__file__), "resources", "icon.png")

        if os.path.exists(ico_path):
            app.setWindowIcon(QIcon(ico_path))
            debug_print(f"[debug] Set icon: {ico_path}")
        elif os.path.exists(png_path):
            app.setWindowIcon(QIcon(png_path))
            debug_print(f"[debug] Set icon: {png_path}")
        else:
            debug_print("[debug] Icon file not found")
    except Exception as e:
        debug_print(f"[debug] Icon set error: {e}")

    # 1秒間スプラッシュスクリーンを表示中にメインウィンドウの初期化を行う
    # -cオプションが指定された場合は確認なしで強制的にリセット
    if config_import_path:
        config_path = ensure_config(reset=True, ask_dialog=None)  # force reset
        debug_print("[debug] Forced reset to import configuration file")
    else:
        config_path = ensure_config(
            reset=reset_config, ask_dialog=ask_reset_dialog if reset_config else None
        )
    debug_print("[debug] Starting main window pre-initialization")
    win = MainWindow()
    # メインウィンドウを非表示で準備する（初期化処理やリソース読み込みを完了させる）
    win.hide()
    app.processEvents()  # UIイベントを処理してレスポンシブさを維持
    debug_print("[debug] Main window initialization complete")

    # 残りのスプラッシュスクリーン表示時間を計算（最低1秒間は表示）
    elapsed_time = time.time() - splash_start_time
    remaining_time = max(0, 1.0 - elapsed_time)
    debug_print(
        f"[debug] Elapsed: {elapsed_time:.2f}s, remaining: {remaining_time:.2f}s"
    )
    if remaining_time > 0:
        time.sleep(remaining_time)

    # スプラッシュスクリーンをフェードアウトさせてから、メインウィンドウを表示する
    def show_main_window():
        # コマンドラインで設定ファイルが指定されていれば、それをインポートする
        if config_import_path and os.path.exists(config_import_path):
            debug_print(
                f"[debug] Importing configuration file from command line: {config_import_path}"
            )
            win.importConfigFromFile(config_import_path)

        win.show()
        splash.hide()  # finish()より高速
        debug_print("[debug] Showing main window after splash screen")

    # フェードアウト開始（短くして200ミリ秒に）
    splash.fadeOut(200, show_main_window)

    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
