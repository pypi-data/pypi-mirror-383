from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QMenuBar,
    QAction,
    QSizePolicy,
    QMdiArea,
    QFileDialog,
    QMessageBox,
    QToolBar,
    QMenu,
    QToolButton,
)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt, QPoint, QRect
from .i18n import tr, set_language, LANG
from .sticky_mdi import StickyMdiSubWindow
from .script_runner import ScriptRunnerWidget
from .shell_runner import ShellRunnerWidget
from .config_manager import LauncherConfigManager
from .debug_util import debug_print, error_print
import platform
from PyQt5.QtWidgets import QApplication
from pathlib import Path
import math
import sys
import os


class CustomMdiArea(QMdiArea):
    """
    カスタムMDIエリアクラス
    ウィンドウの元の位置に基づいて、最も近い適切なタイル位置に配置する機能を提供
    """

    def __init__(self, parent=None):
        super().__init__(parent)

    def tileSubWindows(self):
        """
        サブウィンドウをタイル状に配置する
        各ウィンドウの元の位置から最も近いタイル位置に配置
        """
        if not self.subWindowList():
            return

        # アクティブなサブウィンドウ数
        windows = self.subWindowList()
        windows_count = len(windows)

        # ウィンドウ無しまたは1つだけなら最大化
        if windows_count == 0:
            return
        if windows_count == 1:
            windows[0].showMaximized()
            return

        # タイルレイアウトのグリッドサイズを決定
        # できるだけ正方形に近くなるように列数と行数を計算
        cols = math.ceil(math.sqrt(windows_count))
        rows = math.ceil(windows_count / cols)

        # タイルのセルサイズを計算
        area_width = self.width()
        area_height = self.height()
        cell_width = area_width / cols
        cell_height = area_height / rows

        debug_print(
            f"[debug] Tile layout: {windows_count} windows, {cols} cols x {rows} rows, cell {cell_width}x{cell_height}"
        )

        # 各グリッドセル位置を計算
        grid_cells = []
        for row in range(rows):
            for col in range(cols):
                if len(grid_cells) < windows_count:
                    cell_rect = QRect(
                        int(col * cell_width),
                        int(row * cell_height),
                        int(cell_width),
                        int(cell_height),
                    )
                    # セルの中心点を計算
                    cell_center = QPoint(
                        int(cell_rect.left() + cell_rect.width() / 2),
                        int(cell_rect.top() + cell_rect.height() / 2),
                    )
                    grid_cells.append((cell_rect, cell_center))

        # 各ウィンドウの現在の位置を記憶
        window_positions = []
        for window in windows:
            # ウィンドウの中心点を計算
            window_rect = window.geometry()
            window_center = QPoint(
                int(window_rect.left() + window_rect.width() / 2),
                int(window_rect.top() + window_rect.height() / 2),
            )
            window_positions.append((window, window_center))

        # 各グリッドセルに最も近いウィンドウを割り当てる
        assigned_windows = set()
        assignments = []  # (window, cell_rect) のリスト

        # 各グリッドセルについて、最も近いまだ割り当てられていないウィンドウを見つける
        for cell_rect, cell_center in grid_cells:
            best_window = None
            min_distance = float("inf")

            for window, window_center in window_positions:
                if window in assigned_windows:
                    continue

                # 中心点間の距離を計算
                distance = math.sqrt(
                    (cell_center.x() - window_center.x()) ** 2
                    + (cell_center.y() - window_center.y()) ** 2
                )

                if distance < min_distance:
                    min_distance = distance
                    best_window = window

            if best_window:
                assigned_windows.add(best_window)
                assignments.append((best_window, cell_rect))

        # 残っているウィンドウがあれば、残りのセルに割り当て
        remaining_windows = [
            w for w, _ in window_positions if w not in assigned_windows
        ]
        remaining_cells = [cell for cell, _ in grid_cells[len(assignments) :]]

        for window, cell_rect in zip(remaining_windows, remaining_cells):
            assignments.append((window, cell_rect))

        # ウィンドウを新しい位置に移動
        for window, cell_rect in assignments:
            window.setGeometry(cell_rect)

        debug_print(f"[debug] Tile layout finished: placed {len(assignments)} windows")


class MainWindow(QMainWindow):
    def __init__(self):
        # `saveAllLaunchers` can be triggered by Qt events during the
        # QMainWindow initialisation (for example, moveEvent).  Ensure that the
        # `mdi` attribute always exists before calling `super().__init__()` so
        # that those early events do not cause attribute errors.
        self.mdi = None
        super().__init__()
        debug_print("[debug] ======== MainWindow initialization start ========")
        debug_print(f"[debug] Current UI language: {LANG}")
        self.setWindowTitle("FUJIE Lab. Program Launcher")
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # MacOSの場合は標準メニューバーを使用、その他のOSではツールバーを使用
        self.is_macos = platform.system() == "Darwin"

        # 先にメニューバーを初期化（両方の環境で必要）
        self.menu_bar = self.menuBar()

        if self.is_macos:
            # MacOSではグローバルメニューバーを使用
            self.tool_bar = None
        else:

            # MacOS以外ではカスタムツールバーを使用してメニューを作成
            self.tool_bar = QToolBar(tr("Main Menu"), self)
            self.tool_bar.setMovable(False)  # 移動できないように設定
            self.tool_bar.setFloatable(False)  # フロート不可
            self.tool_bar.setContextMenuPolicy(
                Qt.PreventContextMenu
            )  # コンテキストメニューを無効化
            self.tool_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.tool_bar.setMinimumHeight(28)  # メニューの高さを調整
            layout.addWidget(self.tool_bar, stretch=0)

            # 標準メニューバーは非表示（ツールバーを使うため）
            if not self.is_macos:
                self.menu_bar.hide()  # メニューバーを非表示
        self.mdi = CustomMdiArea()
        layout.addWidget(self.mdi, stretch=1)
        self.initMenu()

        self.global_config = {}
        # サブウィンドウの設定キャッシュ
        self.launcher_cache = []
        # 終了処理中フラグの初期化
        self.in_closing = False
        # MDIエリアのサブウィンドウアクティブ化時に設定を保存
        self.mdi.subWindowActivated.connect(self.saveAllLaunchers)
        # 設定マネージャの初期化
        self.config_manager = LauncherConfigManager()
        self._geometry_restored = False
        self._suppress_save = True

        # 前回の設定を復元
        debug_print("[debug] Restoring previous settings")
        self.restoreAllLaunchers()
        debug_print("[debug] ======== MainWindow initialization complete ========")

    def initMenu(self):
        # ツールバーとメニューバーをクリア
        if not self.is_macos and self.tool_bar:
            self.tool_bar.clear()
        self.menu_bar.clear()

        # ===== ファイルメニュー =====
        fileMenu = QMenu(tr("File"), self)

        # 新規Pythonランチャー
        newPythonLauncherAct = QAction(tr("New Python Launcher"), self)
        newPythonLauncherAct.setShortcut(QKeySequence("Ctrl+N"))
        newPythonLauncherAct.triggered.connect(
            lambda: self.createPythonLauncherWindow()
        )
        fileMenu.addAction(newPythonLauncherAct)

        # 新規シェルランチャー
        newShellLauncherAct = QAction(tr("New Shell Launcher"), self)
        newShellLauncherAct.setShortcut(QKeySequence("Shift+Ctrl+N"))
        newShellLauncherAct.triggered.connect(lambda: self.createShellLauncherWindow())
        fileMenu.addAction(newShellLauncherAct)

        fileMenu.addSeparator()

        # 設定のインポート
        importAct = QAction(tr("Import Settings"), self)
        importAct.setShortcut(QKeySequence("Ctrl+I"))
        importAct.triggered.connect(self.importConfig)
        fileMenu.addAction(importAct)

        # 設定のエクスポート
        exportAct = QAction(tr("Export Settings"), self)
        exportAct.setShortcut(QKeySequence("Shift+Ctrl+S"))
        exportAct.triggered.connect(self.exportConfig)
        fileMenu.addAction(exportAct)

        fileMenu.addSeparator()

        # 終了
        exitAct = QAction(tr("Exit"), self)
        exitAct.setShortcut(QKeySequence.Quit)
        exitAct.triggered.connect(self.close)
        fileMenu.addAction(exitAct)

        # MacOS以外の場合のみ、ツールバーにメニューアクションを追加
        if not self.is_macos:
            fileMenuAction = QAction(tr("File"), self)
            fileMenuAction.setMenu(fileMenu)
            self.addMenuActionToToolbar(fileMenuAction)

        # ===== 整列メニュー =====
        arrangeMenu = QMenu(tr("Arrange"), self)

        # タイル
        tileAct = QAction(tr("Tile"), self)
        tileAct.triggered.connect(self.mdi.tileSubWindows)
        arrangeMenu.addAction(tileAct)

        # カスケード
        cascadeAct = QAction(tr("Cascade"), self)
        cascadeAct.triggered.connect(self.mdi.cascadeSubWindows)
        arrangeMenu.addAction(cascadeAct)

        # MacOS以外の場合のみ、ツールバーにメニューアクションを追加
        if not self.is_macos:
            arrangeMenuAction = QAction(tr("Arrange"), self)
            arrangeMenuAction.setMenu(arrangeMenu)
            self.addMenuActionToToolbar(arrangeMenuAction)

        # ===== 設定メニュー =====
        settingsMenu = QMenu(tr("Settings"), self)

        # グローバル設定
        settingsAct = QAction(tr("Global Settings"), self)
        settingsAct.setShortcut(QKeySequence("Ctrl+,"))
        settingsAct.triggered.connect(self.openSettingsDialog)
        settingsMenu.addAction(settingsAct)

        # MacOS以外の場合のみ、ツールバーにメニューアクションを追加
        if not self.is_macos:
            settingsMenuAction = QAction(tr("Settings"), self)
            settingsMenuAction.setMenu(settingsMenu)
            self.addMenuActionToToolbar(settingsMenuAction)

        # メニューバーにメニューを追加
        self.menu_bar.addMenu(fileMenu)
        self.menu_bar.addMenu(arrangeMenu)
        self.menu_bar.addMenu(settingsMenu)  # ツールバーとメニューのスタイル設定
        style_sheet = """
        QToolBar {
            background: #ffffff;
            border-bottom: 1px solid #b0b0b0;
            spacing: 8px; /* 項目間のスペースを増加 */
            padding: 0px 8px;
            height: 28px;
        }
        QToolBar QToolButton {
            background: transparent;
            color: #222;
            font-size: 14px;
            font-weight: bold;
            padding: 2px 12px; /* 左右のパディングを増やして文字が切れないように */
            margin: 0 2px; /* マージンも少し増やす */
            border-radius: 4px;
            width: auto;
            min-width: 60px; /* 最小幅を設定して文字が切れないようにする */
            font-family: "Meiryo", "MS PGothic", sans-serif;
        }
        QToolBar QToolButton::menu-indicator {
            width: 0px;  /* インジケーターを非表示にする */
            height: 0px;
            image: none; /* 画像を削除 */
            subcontrol-position: right center;
            subcontrol-origin: padding;
        }
        QToolBar QToolButton:hover {
            background: #e6e6e6;
            color: #1565c0;
        }
        QToolBar QToolButton:pressed {
            background: #d0d0d0;
        }
        QMenu {
            background: #ffffff;
            border: 1px solid #b0b0b0;
            font-size: 14px;
            font-family: "Meiryo", "MS PGothic", sans-serif;
        }
        QMenu::item {
            padding: 4px 20px 4px 12px;
            border-radius: 4px;
        }
        QMenu::item:selected {
            background: #e6e6e6;
            color: #1565c0;
        }
        """
        self.setStyleSheet(style_sheet)

    def createPythonLauncherWindow(self, config=None, geometry=None):
        sub = StickyMdiSubWindow()
        # グローバル設定を反映したconfigを生成
        if config is None:
            config = {}
            config_manager = self.config_manager
            config["interpreter"] = config_manager.get_default_interpreter_path()
            config["workdir"] = config_manager.get_default_workdir()
        # print(config)
        # import ipdb; ipdb.set_trace()
        widget = ScriptRunnerWidget(config=config)
        sub.setWidget(widget)
        sub.setAttribute(Qt.WA_DeleteOnClose)
        sub.resize(500, 300)
        self.mdi.addSubWindow(sub)
        if geometry:
            sub.setGeometry(*geometry)
        sub.show()
        sub.installEventFilter(self)
        widget.config_changed_callback = self.saveAllLaunchers
        self.saveAllLaunchers()

    def createShellLauncherWindow(self, config=None, geometry=None):
        sub = StickyMdiSubWindow()
        from .shell_runner import ShellRunnerWidget

        # グローバル設定を反映したconfigを生成
        if config is None:
            config = {}
            config_manager = self.config_manager
            config["workdir"] = config_manager.get_default_workdir()
        widget = ShellRunnerWidget()
        widget.apply_config(config)
        sub.setWidget(widget)
        sub.setAttribute(Qt.WA_DeleteOnClose)
        sub.resize(500, 300)
        self.mdi.addSubWindow(sub)
        if geometry:
            sub.setGeometry(*geometry)
        sub.show()
        sub.installEventFilter(self)
        widget.config_changed_callback = self.saveAllLaunchers
        self.saveAllLaunchers()

    def eventFilter(self, obj, event):
        # ウィンドウ移動・リサイズ・クローズ時に保存
        from PyQt5.QtCore import QEvent

        if event.type() in (QEvent.Move, QEvent.Resize, QEvent.Close):
            self.saveAllLaunchers()
        return super().eventFilter(obj, event)

    def importConfig(self):
        path, _ = QFileDialog.getOpenFileName(
            self, tr("Import Settings File"), filter="YAML Files (*.yaml *.yml)"
        )
        if path:
            self.config_manager.import_config(path)
            reply = QMessageBox.question(
                self,
                tr("Restart Confirmation"),
                tr("Configuration imported. Restart?"),
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                import sys, os

                os.execv(sys.executable, [sys.executable] + sys.argv)

    def importConfigFromFile(self, path):
        """
        指定されたファイルから設定をインポートする
        Args:
            path: インポートする設定ファイルのパス
        """
        if path and os.path.exists(path):
            try:
                self.config_manager.import_config(path)
                debug_print(f"[debug] Imported config file: {path}")
                # 設定が変更されたので再起動せずに設定を即時反映
                self._suppress_save = True
                self.restoreAllLaunchers()
                self._suppress_save = False
            except Exception as e:
                error_print(f"[error] Failed to import settings file: {e}")

    def exportConfig(self):
        path, _ = QFileDialog.getSaveFileName(
            self, tr("Export Settings File"), filter="YAML Files (*.yaml *.yml)"
        )
        if path:
            self.config_manager.export(path)
            QMessageBox.information(
                self, tr("Export Completed"), tr("Configuration exported.")
            )

    def saveAllLaunchers(self):
        if getattr(self, "_suppress_save", False):
            debug_print(
                "[debug] saveAllLaunchers: skipping because saving is suppressed"
            )
            return

        launchers = []

        if not getattr(self, "mdi", None):
            debug_print("[debug] saveAllLaunchers: mdi area not initialised yet")
            return

        subwindow_count = len(self.mdi.subWindowList())
        in_closing = hasattr(self, "in_closing") and self.in_closing
        debug_print(
            f"[debug] saveAllLaunchers: subwindow count {subwindow_count}, closing={in_closing}"
        )

        # 終了処理中はキャッシュを使用（closeEventで更新済み）
        if in_closing and hasattr(self, "launcher_cache") and self.launcher_cache:
            debug_print(
                f"[debug] During closing: using cached launcher settings ({len(self.launcher_cache)} items)"
            )
            launchers = self.launcher_cache

            # キャッシュ内容のデバッグ出力
            for idx, launcher in enumerate(self.launcher_cache):
                ltype = launcher.get("type")
                config = launcher.get("config", {})
                if ltype == "python":
                    script = config.get("script", "(未設定)")
                    debug_print(
                        f"[debug] Cache[{idx}] Python config: script={Path(script).name if script else '(unset)'}"
                    )
                else:
                    cmdline = config.get("cmdline", "(未設定)")
                    debug_print(
                        f"[debug] Cache[{idx}] Shell config: cmdline={cmdline[:20] + '...' if len(cmdline) > 20 else cmdline}"
                    )

        # サブウィンドウが存在する場合、現在の状態からキャッシュを更新
        elif subwindow_count > 0:
            debug_print("[debug] Updating cache from current subwindows")

            # 終了処理中でなければキャッシュをクリア
            if not in_closing:
                self.launcher_cache = []

            for sub in self.mdi.subWindowList():
                widget = sub.widget()
                if isinstance(widget, ScriptRunnerWidget):
                    ltype = "python"
                elif isinstance(widget, ShellRunnerWidget):
                    ltype = "shell"
                else:
                    continue

                geo = sub.geometry()
                try:
                    config = widget.get_config()

                    # 設定内容のデバッグ出力
                    if ltype == "python":
                        script = config.get("script", "(unset)")
                        interpreter = config.get("interpreter", "(unset)")
                        workdir = config.get("workdir", "(unset)")
                        debug_print(
                            f"[debug] Python config: script={Path(script).name if script else '(unset)'}, "
                            f"interpreter={Path(interpreter).name if interpreter else '(unset)'}, "
                            f"workdir={Path(workdir).name if workdir else '(unset)'}"
                        )
                    else:
                        cmdline = config.get("cmdline", "(unset)")
                        workdir = config.get("workdir", "(unset)")
                        debug_print(
                            f"[debug] Shell config: cmdline={cmdline[:20] + '...' if len(cmdline) > 20 else cmdline}, "
                            f"workdir={Path(workdir).name if workdir else '(unset)'}"
                        )
                    launcher_info = {
                        "type": ltype,
                        "geometry": [geo.x(), geo.y(), geo.width(), geo.height()],
                        "config": config,
                    }

                    launchers.append(launcher_info)

                    # 終了処理中でなければキャッシュも更新
                    if not in_closing:
                        self.launcher_cache.append(launcher_info)

                except Exception as e:
                    error_print(f"[error] Error retrieving settings from widget: {e}")
        # サブウィンドウが0の場合でも、終了処理でなければキャッシュが破棄されないようにする
        elif not in_closing and hasattr(self, "launcher_cache") and self.launcher_cache:
            debug_print(
                f"[debug] No subwindows and not closing: using cached launcher settings ({len(self.launcher_cache)} items)"
            )
            launchers = self.launcher_cache

        main_geo = self.geometry()
        self.config_manager.set_launchers(launchers)
        self.config_manager.set_mainwindow_geometry(
            [main_geo.x(), main_geo.y(), main_geo.width(), main_geo.height()]
        )
        self.config_manager.set_mainwindow_state(self.isMaximized())
        debug_print(f"[debug] Saved settings: launcher count={len(launchers)}")

    def restoreWindowGeometry(self):
        geo = self.config_manager.get_mainwindow_geometry()
        maximized = self.config_manager.get_mainwindow_state()
        if geo and len(geo) == 4:
            self.setGeometry(*geo)
        if maximized:
            self.showMaximized()

    def restoreAllLaunchers(self):
        launchers = self.config_manager.get_launchers()
        debug_print(f"[debug] Loaded {len(launchers)} launcher settings from file")

        # キャッシュも復元
        self.launcher_cache = launchers.copy() if launchers else []

        for idx, l in enumerate(launchers):
            ltype = l.get("type")
            geometry = l.get("geometry")
            config = l.get("config", {})

            if ltype == "python":
                script = config.get("script", "(unset)")
                debug_print(f"[debug] Restoring entry {idx+1}: Python script={script}")
                self.createPythonLauncherWindow(config=config, geometry=geometry)
            elif ltype == "shell":
                cmdline = config.get("cmdline", "(unset)")
                debug_print(
                    f"[debug] Restoring entry {idx+1}: Shell cmdline={cmdline[:20]+'...' if len(cmdline) > 20 else cmdline}"
                )
                self.createShellLauncherWindow(config=config, geometry=geometry)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if not self.is_macos and self.tool_bar:
            # ツールバーの最大幅のみをウィンドウ幅に合わせる
            self.tool_bar.setMaximumWidth(self.width())

        # メニューバーも同様に最大幅のみを設定
        if not self.is_macos:
            self.menu_bar.setMaximumWidth(self.width())

        self.saveAllLaunchers()

    def moveEvent(self, event):
        super().moveEvent(event)
        self.saveAllLaunchers()

    def showEvent(self, event):
        super().showEvent(event)
        if not getattr(self, "_geometry_restored", False):
            geo = self.config_manager.get_mainwindow_geometry()
            maximized = self.config_manager.get_mainwindow_state()
            if maximized:
                if platform.system() == "Darwin":
                    screen = QApplication.primaryScreen().availableGeometry()
                    self.move(screen.x(), screen.y())
                    self.resize(screen.width(), screen.height())
                else:
                    self.showMaximized()
            elif geo and len(geo) == 4:
                self.setGeometry(*geo)
            self._geometry_restored = True
            self._suppress_save = False  # 復元後に保存許可

    def changeEvent(self, event):
        from PyQt5.QtCore import QEvent

        if event.type() == QEvent.WindowStateChange:
            self.saveAllLaunchers()
        super().changeEvent(event)

    def openSettingsDialog(self):
        from .settings_dialog import GlobalSettingsDialog
        from .script_runner import ScriptRunnerWidget

        interp_map = ScriptRunnerWidget().get_interpreters()
        current_label = self.config_manager.get_default_interpreter_label()
        current_dir = self.config_manager.get_default_workdir()
        dialog = GlobalSettingsDialog(
            self,
            envs=list(interp_map.keys()),
            current_env=current_label,
            current_dir=current_dir,
            get_interpreters_func=lambda force_refresh=False: ScriptRunnerWidget().get_interpreters(
                force_refresh
            ),
        )
        if dialog.exec_() == dialog.Accepted:
            label, workdir = dialog.get_values()
            path = interp_map.get(label, "python")
            self.config_manager.set_default_interpreter(label, path)
            self.config_manager.set_default_workdir(workdir)

    def closeEvent(self, event):
        """メインウィンドウが閉じられるときに設定を保存し、全てのサブウィンドウを明示的に閉じる"""
        debug_print("[debug] ======== MainWindow closeEvent: begin shutdown ========")

        # 終了処理中フラグをセット(先にセットして、サブウィンドウの個別保存を防止)
        self.in_closing = True
        self._suppress_save = False  # 強制的に保存を有効化

        # キャッシュ更新のために全サブウィンドウ設定を取得
        debug_print("[debug] Caching subwindow settings before shutdown")
        subwindow_count = len(self.mdi.subWindowList())
        debug_print(f"[debug] Current subwindow count: {subwindow_count}")

        # キャッシュをクリアして最新状態を反映
        self.launcher_cache = []

        for sub in self.mdi.subWindowList():
            widget = sub.widget()
            if not widget:
                continue

            if isinstance(widget, ScriptRunnerWidget):
                ltype = "python"
            elif isinstance(widget, ShellRunnerWidget):
                ltype = "shell"
            else:
                continue

            geo = sub.geometry()
            try:
                config = widget.get_config()
                launcher_info = {
                    "type": ltype,
                    "geometry": [geo.x(), geo.y(), geo.width(), geo.height()],
                    "config": config,
                }
                self.launcher_cache.append(launcher_info)

                # 設定内容のデバッグ出力
                if ltype == "python":
                    script = config.get("script", "(unset)")
                    interpreter = config.get("interpreter", "(unset)")
                    workdir = config.get("workdir", "(unset)")
                    debug_print(
                        f"[debug] Cached Python config: script={script}, interpreter={interpreter}"
                    )
                else:
                    cmdline = config.get("cmdline", "(unset)")
                    workdir = config.get("workdir", "(unset)")
                    debug_print(
                        f"[debug] Cached Shell config: cmdline={cmdline[:30]}..."
                    )

            except Exception as e:
                error_print(f"[error] Error retrieving widget settings on close: {e}")

        debug_print(f"[debug] Cached {len(self.launcher_cache)} launcher settings")

        # 設定を保存（キャッシュから保存される）
        self.saveAllLaunchers()
        debug_print("[debug] Settings file saved")

        # サブウィンドウを閉じる
        debug_print("[debug] Closing subwindows")
        for window in self.mdi.subWindowList():
            window.close()

        debug_print(
            "[debug] ======== MainWindow closeEvent: shutdown complete ========"
        )
        event.accept()

    def showMenuFromAction(self, action):
        """メニュー項目がクリックされたときにメニューを表示するヘルパーメソッド"""
        # MacOSでは不要（標準メニューバーが処理する）
        if self.is_macos or not self.tool_bar:
            return

        if action.menu():
            # アクションのボタンの位置と大きさを取得
            button = None
            for widget in self.tool_bar.children():
                if (
                    isinstance(widget, QWidget)
                    and hasattr(widget, "actions")
                    and widget.actions()
                    and action in widget.actions()
                ):
                    button = widget
                    break

            if button:
                # ボタンの下にメニューを表示
                pos = button.mapToGlobal(QPoint(0, button.height()))
                action.menu().popup(pos)

    def addMenuActionToToolbar(self, action):
        """メニューアクションをカスタマイズしてツールバーに追加する"""
        # MacOSの場合は何もしない（標準メニューバーを使用するため）
        if self.is_macos or not self.tool_bar:
            return

        # 専用のツールボタンを作成
        button = QToolButton(self.tool_bar)
        button.setText(action.text())
        button.setPopupMode(QToolButton.InstantPopup)  # クリックでメニューを即時表示
        button.setMenu(action.menu())
        button.setToolButtonStyle(Qt.ToolButtonTextOnly)
        button.setAutoRaise(True)  # フラットなスタイル

        # メニューインジケーター（"^"記号）を非表示にする
        button.setStyleSheet(
            "QToolButton::menu-indicator { width: 0; height: 0; image: none; }"
        )

        # ボタンのサイズポリシーを設定
        textWidth = button.fontMetrics().boundingRect(button.text()).width()
        button.setMinimumWidth(
            max(60, textWidth + 12)
        )  # 文字幅+余白（インジケーター無しなので余白減少）

        self.tool_bar.addWidget(button)
