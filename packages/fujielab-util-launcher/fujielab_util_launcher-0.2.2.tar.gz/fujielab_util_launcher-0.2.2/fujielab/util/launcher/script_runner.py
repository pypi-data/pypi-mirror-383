import os
from PyQt5.QtWidgets import (
    QWidget,
    QTextEdit,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QFormLayout,
    QVBoxLayout,
    QSizePolicy,
    QComboBox,
    QFileDialog,
    QGridLayout,
)
from PyQt5.QtCore import QProcess, Qt
import shlex
from PyQt5.QtGui import QFontDatabase
import subprocess
import json
from pathlib import Path
from .debug_util import debug_print, error_print
from .i18n import tr

interpreter_cache = {}


class ScriptRunnerWidget(QWidget):
    def __init__(self, config=None):
        super().__init__()
        self.process = None
        self.interpreter_path = ""
        self.script_path = ""
        self.script_args = ""
        self.working_dir = ""
        self.interpreter_map = {}
        # バッファーを追加
        self.stdout_buffer = ""
        self.stderr_buffer = ""
        self.output_view = QTextEdit()
        self.output_view.setReadOnly(True)
        fixed_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.output_view.setFont(fixed_font)
        self.interpreter_label = QLabel(tr("Interpreter:"))
        self.script_label = QLabel(tr("Script:"))
        self.dir_label = QLabel(tr("Working Directory:"))
        # --- UI部品をComboBox/ボタン付きに変更 ---
        self.interpreter_combo = QComboBox()
        self.script_value = QLineEdit()
        self.script_value.setReadOnly(True)
        self.script_select_button = QPushButton(tr("Select"))
        self.dir_value = QLineEdit()
        self.dir_value.setReadOnly(True)
        self.dir_select_button = QPushButton(tr("Select"))
        self.args_label = QLabel(tr("Arguments:"))
        self.args_value = QLineEdit()

        # インタプリタリストをセット (エラー処理を強化)
        try:
            interp_map = self.get_interpreters()
            if not interp_map:
                # もしインタープリタが見つからない場合、現在の実行環境を追加
                debug_print(
                    "[debug] No interpreters found, using current Python as fallback"
                )
                import sys
                import os

                # 環境名を正確に取得
                env_name = self.get_current_env_name()
                fallback_label = f"Python {sys.version.split()[0]} ({env_name})"
                interp_map[fallback_label] = sys.executable
            self.interpreter_map = interp_map
            self.interpreter_combo.addItems(list(interp_map.keys()))
        except Exception as e:
            error_print(f"Error getting interpreters: {e}")
            # 致命的なエラーが発生した場合のフォールバック
            import sys

            fallback_label = f"Python {sys.version.split()[0]} (エラー回復)"
            self.interpreter_map = {fallback_label: sys.executable}
            self.interpreter_combo.addItems([fallback_label])
            # エラーをUI上で表示
            self.output_view.append(
                f"<span style='color:red;'>インタープリタリスト取得エラー: {e}</span>"
            )
            self.output_view.append(
                f"<span style='color:blue;'>現在の実行環境を使用します: {sys.executable}</span>"
            )
        # --- レイアウト ---
        for lineedit in [self.script_value, self.dir_value, self.args_value]:
            lineedit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        for label in [
            self.interpreter_label,
            self.script_label,
            self.args_label,
            self.dir_label,
        ]:
            label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.run_button = QPushButton(tr("Run"))
        self.stop_button = QPushButton(tr("Stop"))
        self.run_button.setFixedHeight(26)
        self.stop_button.setFixedHeight(26)
        self.script_select_button.setFixedSize(48, 24)
        self.dir_select_button.setFixedSize(48, 24)
        self.interpreter_combo.setFixedHeight(24)
        self.script_value.setFixedHeight(24)
        self.dir_value.setFixedHeight(24)
        self.args_value.setFixedHeight(24)
        control_layout = QHBoxLayout()
        control_layout.setSpacing(2)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.addWidget(self.run_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addStretch()
        form_layout = QGridLayout()
        form_layout.setSpacing(2)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.addWidget(self.interpreter_label, 0, 0)
        form_layout.addWidget(self.interpreter_combo, 0, 1, 1, 2)
        form_layout.addWidget(self.dir_label, 1, 0)
        form_layout.addWidget(self.dir_value, 1, 1)
        form_layout.addWidget(self.dir_select_button, 1, 2)
        form_layout.addWidget(self.script_label, 2, 0)
        form_layout.addWidget(self.script_value, 2, 1)
        form_layout.addWidget(self.script_select_button, 2, 2)
        form_layout.addWidget(self.args_label, 3, 0)
        form_layout.addWidget(self.args_value, 3, 1, 1, 2)
        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addLayout(control_layout)
        layout.addLayout(form_layout)
        layout.addWidget(self.output_view)
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText(tr("Enter stdin here and press Enter"))
        self.input_line.setFixedHeight(22)
        self.input_line.setFont(fixed_font)
        self.input_line.returnPressed.connect(self.send_stdin)
        layout.addWidget(self.input_line)
        self.setLayout(layout)

        from .config_manager import LauncherConfigManager

        self.config_manager = LauncherConfigManager()
        default_label = self.config_manager.get_default_interpreter_label()
        default_path = self.config_manager.get_default_interpreter_path()
        default_workdir = self.config_manager.get_default_workdir()
        if config:
            self.apply_config(config)
        else:
            if default_label and default_path:
                self.interpreter_combo.setCurrentText(default_label)
                self.interpreter_path = default_path
            elif interp_map:
                first_label = next(iter(interp_map.keys()))
                self.interpreter_combo.setCurrentText(first_label)
                self.interpreter_path = interp_map[first_label]
            if default_workdir:
                self.working_dir = default_workdir
                self.dir_value.setText(
                    Path(self.working_dir).name if self.working_dir else ""
                )
            self.args_value.setText("")
        self.config_changed_callback = None

        # イベント接続を追加
        self.run_button.clicked.connect(self.run_script)
        self.stop_button.clicked.connect(self.stop_script)
        self.interpreter_combo.currentIndexChanged.connect(self.on_interpreter_changed)
        self.script_select_button.clicked.connect(self.select_script)
        self.dir_select_button.clicked.connect(self.select_dir)
        self.args_value.textChanged.connect(self.on_args_changed)

        # 初期状態では実行されていないためUIを更新
        self.update_ui_state(running=False)

    def on_interpreter_changed(self):
        label = self.interpreter_combo.currentText()
        self.interpreter_path = self.interpreter_map.get(label, "python")

    def on_args_changed(self, text):
        self.script_args = text
        if self.config_changed_callback:
            self.config_changed_callback()

    def send_stdin(self):
        text = self.input_line.text()
        if self.process and self.process.state() != QProcess.NotRunning:
            self.process.write((text + "\n").encode("utf-8"))
            self.output_view.append(f"<span style='color:blue;'>{text}</span>")
            self.input_line.clear()
        else:
            self.output_view.append(
                "<span style='color:red;'>プロセスが起動していません</span>"
            )

    def update_ui_state(self, running: bool):
        """Enable or disable widgets depending on running state."""
        self.run_button.setEnabled(not running)
        self.stop_button.setEnabled(running)
        self.script_select_button.setEnabled(not running)
        self.dir_select_button.setEnabled(not running)
        self.interpreter_combo.setEnabled(not running)
        self.input_line.setEnabled(running)

    def get_interpreters(self, force_refresh=False):
        global interpreter_cache
        if interpreter_cache and not force_refresh:
            return interpreter_cache
        interpreters = {}

        # バックアップとして、最低でも現在のPythonは確実に含める
        import sys
        import os

        # 環境名を正確に取得するためのロジック
        env_name = "現在の環境"
        try:
            # Condaの環境変数から環境名を取得
            conda_default_env = os.environ.get("CONDA_DEFAULT_ENV")
            if conda_default_env:
                env_name = f"conda: {conda_default_env}"
            else:
                # 実行パスからの推定
                py_path = sys.executable
                # パスからcondaの環境名を推測
                path_parts = Path(py_path).parts
                if "envs" in path_parts:
                    # パスがenvs/環境名を含む場合
                    idx = path_parts.index("envs")
                    if idx + 1 < len(path_parts):
                        env_name = f"conda: {path_parts[idx + 1]}"
                elif "venv" in path_parts or "virtualenv" in path_parts:
                    # 仮想環境と思われる場合
                    env_name = "venv"
        except Exception as e:
            debug_print(f"[debug] Error determining environment name: {e}")

        fallback_label = f"Python {sys.version.split()[0]} ({env_name})"
        fallback_path = sys.executable
        interpreters[fallback_label] = fallback_path
        import platform
        import sys

        is_windows = platform.system() == "Windows"

        if is_windows:
            # Windows環境の詳細情報を取得
            debug_print(f"[debug] Windows version: {platform.version()}")
            debug_print(f"[debug] Windows release: {platform.release()}")
            debug_print(f"[debug] Python executable: {sys.executable}")
            # 環境変数PATHの内容を表示
            path_entries = os.environ.get("PATH", "").split(";")
            debug_print(f"[debug] PATH environment variable entries:")
            for entry in path_entries:
                debug_print(f"[debug]   - {entry}")
            # PYTHONPATHの内容を表示
            debug_print(f"[debug] PYTHONPATH: {os.environ.get('PYTHONPATH', '')}")
            # 現在のワーキングディレクトリを表示
            debug_print(f"[debug] Current working directory: {os.getcwd()}")
            # conda関連の環境変数を確認
            for env_var in [
                "CONDA_PREFIX",
                "CONDA_PYTHON_EXE",
                "CONDA_EXE",
                "CONDA_SHLVL",
                "CONDA_DEFAULT_ENV",
            ]:
                value = os.environ.get(env_var, "Not set")
                debug_print(f"{env_var}: {value}")

        try:
            # システムPythonを取得
            if is_windows:
                python_cmd = "python"
                where_cmd = "where"
            else:
                python_cmd = "python3"
                where_cmd = "which"

            debug_print(f"[debug] Looking for system Python using {python_cmd}")
            try:
                sys_version = subprocess.check_output(
                    [python_cmd, "--version"], universal_newlines=True
                ).strip()
                debug_print(f"System Python version command output: {sys_version}")
                sys_version = sys_version.split()[1]  # "Python 3.9.5" -> "3.9.5"

                # Windows環境ではwhereコマンドを使用してPythonのパスを取得
                if is_windows:
                    try:
                        sys_path = (
                            subprocess.check_output(
                                [where_cmd, python_cmd], universal_newlines=True
                            )
                            .strip()
                            .split("\n")[0]
                        )
                    except subprocess.SubprocessError:
                        # whereコマンドが失敗した場合はshutilを使用
                        import shutil

                        sys_path = shutil.which(python_cmd)
                        if not sys_path:
                            error_print(
                                f"Could not find system Python path using {where_cmd} or shutil.which"
                            )
                            raise FileNotFoundError(f"Python path not found")
                else:
                    sys_path = subprocess.check_output(
                        [where_cmd, python_cmd], universal_newlines=True
                    ).strip()

                debug_print(f"[debug] Found system Python at: {sys_path}")

                # システムPythonの適切な表示名を決定
                if is_windows:
                    if "WindowsApps" in sys_path:
                        env_type = "Microsoft Store"
                    elif "Program Files" in sys_path:
                        env_type = "System (Program Files)"
                    elif "ProgramData" in sys_path:
                        env_type = "System (ProgramData)"
                    elif "AppData" in sys_path or "Local" in sys_path:
                        env_type = "User"
                    else:
                        env_type = "System"
                else:
                    if "/usr/bin" in sys_path:
                        env_type = "System"
                    elif "/usr/local/bin" in sys_path:
                        env_type = "Local"
                    elif "/opt" in sys_path:
                        env_type = "Optional"
                    else:
                        env_type = "System"

                label = f"Python {sys_version} ({env_type})"
                interpreters[label] = sys_path
            except Exception as e:
                error_print(f"Error getting system Python version: {e}")
                # バックアップとして、実行中のPythonを使用
                import sys

                sys_path = sys.executable
                sys_version = ".".join(map(str, sys.version_info[:3]))
                debug_print(
                    f"Using current Python as fallback: {sys_path}, version {sys_version}"
                )
                label = f"Python {sys_version} (current)"
                interpreters[label] = sys_path
        except Exception as e:
            error_print(f"[warn] Failed to get system Python: {e}")
        try:
            # Check if conda command exists before running
            import shutil

            conda_cmd = "conda"
            if is_windows:
                # On Windows, check if conda is in PATH
                conda_path = shutil.which("conda")
                conda_exists = conda_path is not None
                debug_print(
                    f"[debug] Conda in PATH: {conda_exists}, Path: {conda_path}"
                )

                # On Windows, conda.BAT is often found but causes problems
                # Try to find the actual conda.exe instead
                if conda_exists and conda_path.lower().endswith(".bat"):
                    debug_print(
                        f"[debug] Found conda.BAT, will try to find the actual conda.exe instead"
                    )
                    # Try to locate conda.exe based on conda.BAT location
                    bat_path = Path(conda_path)
                    # condabin/conda.BAT usually points to ../Scripts/conda.exe
                    if "condabin" in str(bat_path).lower():
                        possible_conda_exe = (
                            bat_path.parent.parent / "Scripts" / "conda.exe"
                        )
                        if possible_conda_exe.exists():
                            conda_cmd = str(possible_conda_exe)
                            debug_print(f"[debug] Found conda.exe at: {conda_cmd}")
                        else:
                            # Or it might be in the Library/bin directory
                            possible_conda_exe = (
                                bat_path.parent.parent / "Library" / "bin" / "conda.exe"
                            )
                            if possible_conda_exe.exists():
                                conda_cmd = str(possible_conda_exe)
                                debug_print(f"[debug] Found conda.exe at: {conda_cmd}")

                # If we still have conda.BAT or couldn't find it, try common locations
                if not conda_exists or conda_cmd.lower().endswith(".bat"):
                    possible_paths = [
                        Path(os.environ.get("USERPROFILE", ""))
                        / "Anaconda3"
                        / "Scripts"
                        / "conda.exe",
                        Path(os.environ.get("USERPROFILE", ""))
                        / "Miniconda3"
                        / "Scripts"
                        / "conda.exe",
                        Path(os.environ.get("ProgramData", ""))
                        / "Anaconda3"
                        / "Scripts"
                        / "conda.exe",
                        Path(os.environ.get("USERPROFILE", ""))
                        / "AppData"
                        / "Local"
                        / "anaconda3"
                        / "Scripts"
                        / "conda.exe",
                        Path(os.environ.get("USERPROFILE", ""))
                        / "AppData"
                        / "Local"
                        / "miniconda3"
                        / "Scripts"
                        / "conda.exe",
                        Path(os.environ.get("LOCALAPPDATA", ""))
                        / "Continuum"
                        / "anaconda3"
                        / "Scripts"
                        / "conda.exe",
                        Path(os.environ.get("LOCALAPPDATA", ""))
                        / "Continuum"
                        / "miniconda3"
                        / "Scripts"
                        / "conda.exe",
                        # Anaconda3ディレクトリを直接確認
                        Path(os.environ.get("USERPROFILE", ""))
                        / "anaconda3"
                        / "Scripts"
                        / "conda.exe",
                    ]
                    for path in possible_paths:
                        debug_print(f"[debug] Checking conda at: {path}")
                        if path.exists():
                            conda_cmd = str(path)
                            conda_exists = True
                            debug_print(f"[debug] Found conda at: {conda_cmd}")
                            break

                # conda.exeが見つからなかった場合は別の方法を試す
                if not conda_exists or conda_cmd.lower().endswith(".bat"):
                    # condaが見つからない場合は、現在のPythonのインストールパスから推測
                    import sys

                    python_path = Path(sys.executable)
                    possible_conda_paths = [
                        python_path.parent / "conda.exe",
                        python_path.parent / "Scripts" / "conda.exe",
                        python_path.parent.parent / "Scripts" / "conda.exe",
                    ]
                    for path in possible_conda_paths:
                        debug_print(f"[debug] Checking conda at: {path}")
                        if path.exists():
                            conda_cmd = str(path)
                            conda_exists = True
                            debug_print(f"[debug] Found conda at: {conda_cmd}")
                            break

                if not conda_exists:
                    error_print("Conda command not found in PATH or common locations")
                    error_print(f"PATH: {os.environ.get('PATH', '')}")
                    raise FileNotFoundError(
                        "Conda command not found in PATH or common locations"
                    )

            debug_print(f"[debug] Running conda command: {conda_cmd} info --json")
            # Windowsの場合、複数の方法を試す
            envs = []

            if is_windows:
                # 方法1: conda.exeを直接実行
                try:
                    debug_print("[debug] Trying direct execution of conda.exe")
                    output = subprocess.check_output(
                        [conda_cmd, "info", "--json"], universal_newlines=True
                    )
                    debug_print(f"[debug] Conda info output length: {len(output)}")
                    info = json.loads(output)
                    envs = info.get("envs", [])
                    debug_print(f"[debug] Found {len(envs)} conda environments")
                except Exception as e:
                    error_print(f"Direct conda execution failed: {e}")

                    # 方法2: shellを使用して実行
                    if not envs:
                        try:
                            debug_print("[debug] Trying to run conda with shell=True")
                            output = subprocess.check_output(
                                f'"{conda_cmd}" info --json',
                                shell=True,
                                universal_newlines=True,
                            )
                            info = json.loads(output)
                            envs = info.get("envs", [])
                            debug_print(
                                f"[debug] Found {len(envs)} conda environments using shell=True"
                            )
                        except Exception as e2:
                            error_print(f"Shell conda execution failed: {e2}")

                    # 方法3: パスを考慮してcmd.exeで実行
                    if not envs:
                        try:
                            debug_print("Trying to run conda through cmd.exe")
                            cmd = f'cmd.exe /c "{conda_cmd}" info --json'
                            output = subprocess.check_output(
                                cmd, shell=True, universal_newlines=True
                            )
                            info = json.loads(output)
                            envs = info.get("envs", [])
                            debug_print(
                                f"Found {len(envs)} conda environments using cmd.exe"
                            )
                        except Exception as e3:
                            error_print(f"Cmd.exe conda execution failed: {e3}")

                    # 方法4: 環境変数の変更を行う最終手段
                    if not envs:
                        try:
                            # 環境変数を調整して実行
                            debug_print(
                                "[debug] Trying to run conda with modified PATH"
                            )
                            env_copy = os.environ.copy()
                            conda_dir = str(Path(conda_cmd).parent)
                            env_copy["PATH"] = f"{conda_dir};{env_copy.get('PATH', '')}"
                            output = subprocess.check_output(
                                [conda_cmd, "info", "--json"],
                                env=env_copy,
                                universal_newlines=True,
                            )
                            info = json.loads(output)
                            envs = info.get("envs", [])
                            debug_print(
                                f"[debug] Found {len(envs)} conda environments with modified PATH"
                            )
                        except Exception as e4:
                            error_print(f"Modified PATH conda execution failed: {e4}")

                    # 最終手段: フォールバックとして現在の環境だけを追加
                    if not envs:
                        debug_print(
                            "[debug] All conda methods failed. Using current environment as fallback."
                        )
                        import sys

                        current_env = os.path.dirname(sys.executable)
                        envs = [current_env]
                        debug_print(f"[debug] Using current environment: {current_env}")
            else:
                # 非Windows環境でのconda実行
                try:
                    output = subprocess.check_output(
                        [conda_cmd, "info", "--json"], universal_newlines=True
                    )
                    debug_print(f"[debug] Conda info output length: {len(output)}")
                    info = json.loads(output)
                    envs = info.get("envs", [])
                    debug_print(f"[debug] Found {len(envs)} conda environments")
                except Exception as e:
                    error_print(f"Error executing conda: {e}")
                    raise

            for env_path in envs:
                if is_windows:
                    python_path = str(Path(env_path) / "python.exe")
                else:
                    python_path = str(Path(env_path) / "bin" / "python")

                debug_print(f"[debug] Checking Python at: {python_path}")
                if not os.path.exists(python_path):
                    debug_print(
                        f"[debug] Python executable not found at: {python_path}"
                    )
                    continue

                try:
                    version = (
                        subprocess.check_output(
                            [python_path, "--version"], universal_newlines=True
                        )
                        .strip()
                        .split()[1]
                    )

                    # 環境名を適切に抽出
                    if "envs" in str(env_path):
                        # パスの中でenvsが見つかる場合、その次の部分を環境名として使用
                        path_parts = Path(env_path).parts
                        try:
                            idx = list(map(str.lower, path_parts)).index("envs")
                            if idx + 1 < len(path_parts):
                                env_name = f"conda: {path_parts[idx + 1]}"
                            else:
                                env_name = "conda: " + Path(env_path).name
                        except ValueError:
                            env_name = "conda: " + Path(env_path).name
                    else:
                        # envs を含まないが conda パスの場合はbase環境
                        if any(
                            x in str(env_path).lower()
                            for x in ["anaconda", "miniconda", "conda"]
                        ):
                            env_name = "conda: base"
                        else:
                            env_name = Path(env_path).name

                    label = f"Python {version} ({env_name})"
                    interpreters[label] = python_path
                    debug_print(f"[debug] Added interpreter: {label} -> {python_path}")
                except Exception as e:
                    error_print(f"Failed to get Python version for {python_path}: {e}")
                    continue
        except Exception as e:
            error_print(f"[warn] Failed to get conda environments: {e}")
        # フォールバック: ディレクトリスキャンで環境を探す
        if is_windows and not envs:
            debug_print(
                "[debug] No environments found using conda command. Attempting directory scan..."
            )
            # 一般的なAnaconda/Condaのディレクトリ構造から環境を検出
            common_conda_base_dirs = [
                os.path.join(os.environ.get("USERPROFILE", ""), "anaconda3"),
                os.path.join(os.environ.get("USERPROFILE", ""), "Anaconda3"),
                os.path.join(os.environ.get("USERPROFILE", ""), "miniconda3"),
                os.path.join(os.environ.get("USERPROFILE", ""), "Miniconda3"),
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "anaconda3"),
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Anaconda3"),
            ]

            for base_dir in common_conda_base_dirs:
                if os.path.exists(base_dir):
                    debug_print(
                        f"[debug] Found potential conda base directory: {base_dir}"
                    )

                    # ベース環境
                    base_python = os.path.join(base_dir, "python.exe")
                    if os.path.exists(base_python):
                        envs.append(base_dir)
                        debug_print(f"[debug] Added base environment: {base_dir}")

                    # envs ディレクトリ内の環境
                    envs_dir = os.path.join(base_dir, "envs")
                    if os.path.exists(envs_dir):
                        debug_print(f"[debug] Checking for environments in: {envs_dir}")
                        try:
                            for env_name in os.listdir(envs_dir):
                                env_path = os.path.join(envs_dir, env_name)
                                env_python = os.path.join(env_path, "python.exe")
                                if os.path.isdir(env_path) and os.path.exists(
                                    env_python
                                ):
                                    envs.append(env_path)
                                    debug_print(
                                        f"[debug] Added environment: {env_path} (name: {env_name})"
                                    )
                        except Exception as e:
                            error_print(f"Error listing environments directory: {e}")

            if envs:
                debug_print(
                    f"[debug] Found {len(envs)} conda environments from directory scanning"
                )
            else:
                # それでも見つからない場合は、現在のPythonだけを使用
                debug_print(
                    "[debug] No environments found. Using current Python as last resort."
                )
                import sys

                current_env = os.path.dirname(sys.executable)
                envs = [current_env]
                debug_print(f"[debug] Using current environment: {current_env}")

        for env_path in envs:
            if is_windows:
                python_path = str(Path(env_path) / "python.exe")
            else:
                python_path = str(Path(env_path) / "bin" / "python")

            debug_print(f"[debug] Checking Python at: {python_path}")
            if not os.path.exists(python_path):
                debug_print(f"[debug] Python executable not found at: {python_path}")
                continue

            try:
                version = (
                    subprocess.check_output(
                        [python_path, "--version"], universal_newlines=True
                    )
                    .strip()
                    .split()[1]
                )

                # 環境名を適切に抽出
                if "envs" in str(env_path):
                    # パスの中でenvsが見つかる場合、その次の部分を環境名として使用
                    path_parts = Path(env_path).parts
                    try:
                        idx = list(map(str.lower, path_parts)).index("envs")
                        if idx + 1 < len(path_parts):
                            env_name = f"conda: {path_parts[idx + 1]}"
                        else:
                            env_name = "conda: " + Path(env_path).name
                    except ValueError:
                        env_name = "conda: " + Path(env_path).name
                else:
                    # envs を含まないが conda パスの場合はbase環境
                    if any(
                        x in str(env_path).lower()
                        for x in ["anaconda", "miniconda", "conda"]
                    ):
                        env_name = "conda: base"
                    else:
                        env_name = Path(env_path).name

                label = f"Python {version} ({env_name})"
                interpreters[label] = python_path
                debug_print(f"[debug] Added interpreter: {label} -> {python_path}")
            except Exception as e:
                error_print(f"Failed to get Python version for {python_path}: {e}")
                continue

        interpreter_cache = interpreters
        return interpreters

    def get_config(self):
        return {
            "interpreter": self.interpreter_path,
            "script": self.script_path,
            "workdir": self.working_dir,
            "args": self.script_args,
        }

    def apply_config(self, config):
        self.interpreter_path = config.get("interpreter", "")
        interp_map = self.get_interpreters()
        # パスからラベルを逆引き
        label = next(
            (k for k, v in interp_map.items() if v == self.interpreter_path),
            self.interpreter_path,
        )
        self.interpreter_combo.setCurrentText(label)
        self.script_path = config.get("script", "")
        self.working_dir = config.get("workdir", "")
        self.script_args = config.get("args", "")
        self.script_value.setText(
            Path(self.script_path).name if self.script_path else ""
        )
        self.dir_value.setText(Path(self.working_dir).name if self.working_dir else "")
        self.args_value.setText(self.script_args)

    def run_script(self, checked=False):
        self.output_view.append(f"[debug] run_script called (checked={checked})")
        if not self.script_path:
            self.output_view.append(tr("No script selected"))
            return
        self.output_view.append(f"[debug] Interpreter: {self.interpreter_path}")
        self.output_view.append(f"[debug] Script: {self.script_path}")
        self.output_view.append(f"[debug] Working directory: {self.working_dir}")

        # プロセス作成前に環境変数を設定
        self.process = QProcess(self)

        # システム環境変数を取得し、QProcessEnvironmentに変換
        from PyQt5.QtCore import QProcessEnvironment

        env = QProcessEnvironment.systemEnvironment()

        # Pythonのバッファリングを無効化
        env.insert("PYTHONUNBUFFERED", "1")
        env.insert("PYTHONIOENCODING", "utf-8:unbuffered")

        # 他の言語のバッファリングも制御（gccなど）
        env.insert("GCCNOBUFFERED", "1")

        # 環境変数を設定
        self.process.setProcessEnvironment(env)
        self.process.setProgram(self.interpreter_path)

        # コマンドライン引数調整 - Pythonの場合は-uオプションを追加
        args = [self.script_path]
        if self.interpreter_path.endswith("python") or self.interpreter_path.endswith(
            "python3"
        ):
            args = ["-u", self.script_path]

        user_args = shlex.split(self.script_args) if self.script_args else []
        args += user_args

        self.process.setArguments(args)
        self.process.setWorkingDirectory(self.working_dir)

        # 標準出力と標準エラー出力を別々に処理するモードを設定
        self.process.setProcessChannelMode(QProcess.SeparateChannels)

        # シグナル接続
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)
        self.process.errorOccurred.connect(self.handle_process_error)
        self.process.stateChanged.connect(self.handle_state_changed)

        # バッファをクリア
        self.stdout_buffer = ""
        self.stderr_buffer = ""
        self.output_view.clear()
        self.output_view.append(tr("Starting script..."))
        # Disable controls *before* starting. If the process fails to start,
        # the error signal may fire immediately and re-enable the UI.
        self.update_ui_state(running=True)
        self.process.start()

    def handle_process_error(self, error):
        self.output_view.append(
            f"<span style='color:red;'>QProcessエラー: {error}</span>"
        )
        if self.process:
            self.output_view.append(f"詳細: {self.process.errorString()}")
        # エラー発生時にもUIを復旧させる
        self.update_ui_state(running=False)

    def handle_state_changed(self, state):
        """Update UI whenever the process state changes."""
        self.update_ui_state(state != QProcess.NotRunning)

    def stop_script(self):
        if self.process and self.process.state() != QProcess.NotRunning:
            from PyQt5.QtCore import QCoreApplication

            # 段階的なプロセス停止を試みる
            self.output_view.append("スクリプトの停止を試みています...")
            self.output_view.repaint()  # UIの更新を強制
            QCoreApplication.processEvents()  # イベントループを処理してUIを更新

            # ステップ1: SIGINT (Ctrl+C相当) で停止を促す
            self.process.terminate()  # QProcess.terminateはSIGINTを送信
            self.output_view.append("SIGINT送信 - 正常終了を2秒間待機中...")
            self.output_view.repaint()
            QCoreApplication.processEvents()

            if self.process.waitForFinished(2000):  # 2秒待機
                self.output_view.append("✓ スクリプトが正常に停止しました (SIGINT)")
                self.output_view.repaint()
                return

            # ステップ2: SIGTERM (通常のkill) で終了を要求
            self.output_view.append(
                "<span style='color:orange;'>⚠ SIGINTでの停止に失敗しました</span>"
            )
            self.output_view.append("SIGTERM送信 - 終了を2秒間待機中...")
            self.output_view.repaint()
            QCoreApplication.processEvents()

            self.process.kill()  # QProcess.killはSIGTERMを送信
            if self.process.waitForFinished(2000):  # 2秒待機
                self.output_view.append("✓ スクリプトが停止しました (SIGTERM)")
                self.output_view.repaint()
                return

            # ステップ3: SIGKILL (kill -9) で強制終了
            import signal
            import os

            self.output_view.append(
                "<span style='color:red;'>❌ SIGTERMでの停止に失敗しました</span>"
            )
            self.output_view.append("SIGKILL送信 - 強制終了を実行中...")
            self.output_view.repaint()
            QCoreApplication.processEvents()

            try:
                pid = self.process.processId()
                os.kill(pid, signal.SIGKILL)
                self.output_view.append("SIGKILL送信完了 - プロセス終了を待機中...")
                self.output_view.repaint()
                QCoreApplication.processEvents()

                self.process.waitForFinished(1000)  # 1秒待機
                self.output_view.append("✓ スクリプトを強制終了しました (SIGKILL)")
                self.output_view.repaint()
            except Exception as e:
                self.output_view.append(
                    f"<span style='color:red;'>❌ プロセスの強制終了に失敗しました: {e}</span>"
                )
                self.output_view.repaint()

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        text = bytes(data).decode("utf-8", errors="replace")
        # バッファリング対応
        self.stdout_buffer += text
        lines = self.stdout_buffer.split("\n")

        # 空のリストの場合（分割結果なし）は処理しない
        if not lines:
            return

        # 最後の行以外をすべて処理
        for line in lines[:-1]:
            self.output_view.append(line)

        # 最後の行はバッファに残す
        self.stdout_buffer = lines[-1]

        # スクロールを最新に保つ
        scrollbar = self.output_view.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        text = bytes(data).decode("utf-8", errors="replace")
        # バッファリング対応
        self.stderr_buffer += text
        lines = self.stderr_buffer.split("\n")

        # 空のリストの場合（分割結果なし）は処理しない
        if not lines:
            return

        # 最後の行以外をすべて処理
        for line in lines[:-1]:
            self.output_view.append(f"<span style='color:red;'>{line}</span>")

        # 最後の行はバッファに残す
        self.stderr_buffer = lines[-1]

        # スクロールを最新に保つ
        scrollbar = self.output_view.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def process_finished(self):
        # 残りのバッファをフラッシュ
        if self.stdout_buffer:
            self.output_view.append(self.stdout_buffer)
            self.stdout_buffer = ""

        if self.stderr_buffer:
            self.output_view.append(
                f"<span style='color:red;'>{self.stderr_buffer}</span>"
            )
            self.stderr_buffer = ""

        self.output_view.append(tr("Script finished"))
        self.update_ui_state(running=False)

    def select_script(self):
        default_dir = self.working_dir or str(Path.cwd())
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr("Select script"),
            directory=default_dir,
            filter="Python Scripts (*.py)",
        )
        if path:
            self.script_path = path  # フルパスを保持
            self.script_value.setText(Path(self.script_path).name)  # 表示はbasename
            if self.config_changed_callback:
                self.config_changed_callback()

    def select_dir(self):
        path = QFileDialog.getExistingDirectory(
            self,
            tr("Select working directory"),
            directory=self.working_dir or str(Path.cwd()),
        )
        if path:
            self.working_dir = path
            self.dir_value.setText(
                Path(self.working_dir).name if self.working_dir else ""
            )
            if self.config_changed_callback:
                self.config_changed_callback()

    def closeEvent(self, event):
        """ウィンドウが閉じられるときにプロセスを終了させる"""
        from PyQt5.QtCore import QCoreApplication

        self.output_view.append("[debug] closeEvent: process termination")
        self.output_view.repaint()
        QCoreApplication.processEvents()

        if self.process and self.process.state() != QProcess.NotRunning:
            # 段階的なプロセス停止を試みる（短い待機時間で）

            # ステップ1: SIGINT
            self.output_view.append("SIGINT送信中...")
            self.output_view.repaint()
            QCoreApplication.processEvents()

            self.process.terminate()
            if self.process.waitForFinished(500):  # 0.5秒待機
                self.output_view.append("プロセスが停止しました (SIGINT)")
                self.output_view.repaint()
                QCoreApplication.processEvents()
                event.accept()
                return

            # ステップ2: SIGTERM
            self.output_view.append("SIGTERM送信中...")
            self.output_view.repaint()
            QCoreApplication.processEvents()

            self.process.kill()
            if self.process.waitForFinished(500):  # 0.5秒待機
                self.output_view.append("プロセスが停止しました (SIGTERM)")
                self.output_view.repaint()
                QCoreApplication.processEvents()
                event.accept()
                return

            # ステップ3: SIGKILL
            self.output_view.append("SIGKILL送信中...")
            self.output_view.repaint()
            QCoreApplication.processEvents()

            try:
                import signal
                import os

                pid = self.process.processId()
                os.kill(pid, signal.SIGKILL)
                self.process.waitForFinished(500)  # 0.5秒待機
                self.output_view.append("プロセスが強制終了しました (SIGKILL)")
                self.output_view.repaint()
                QCoreApplication.processEvents()
            except:
                self.output_view.append("プロセス終了処理に失敗しました")
                self.output_view.repaint()
                QCoreApplication.processEvents()
        event.accept()

    def __del__(self):
        """インスタンスが破棄されるときにプロセスを終了させる"""
        if (
            hasattr(self, "process")
            and self.process
            and self.process.state() != QProcess.NotRunning
        ):
            try:
                # 段階的なプロセス停止（超短い待機時間で）
                self.process.terminate()
                if self.process.waitForFinished(200):  # 0.2秒待機
                    return

                self.process.kill()
                if self.process.waitForFinished(200):  # 0.2秒待機
                    return

                import signal
                import os

                pid = self.process.processId()
                os.kill(pid, signal.SIGKILL)
            except:
                pass

    def get_current_env_name(self):
        """
        現在の実行環境の名前を取得する

        Returns:
            str: 環境名 (例: "base", "conda: myenv", "venv" など)
        """
        import sys
        import os
        from pathlib import Path

        # デフォルト値
        env_name = "system"

        try:
            # Condaの環境変数から環境名を取得
            conda_default_env = os.environ.get("CONDA_DEFAULT_ENV")
            if conda_default_env:
                if conda_default_env == "base":
                    env_name = "conda: base"
                else:
                    env_name = f"conda: {conda_default_env}"
            else:
                # 実行パスからの推定
                py_path = sys.executable
                path_parts = Path(py_path).parts

                # Anaconda/Miniconda検出
                anaconda_indicators = ["anaconda", "miniconda", "conda"]
                if any(
                    indicator in str(py_path).lower()
                    for indicator in anaconda_indicators
                ):
                    if "envs" in path_parts:
                        # パスがenvs/環境名を含む場合
                        try:
                            idx = list(map(str.lower, path_parts)).index("envs")
                            if idx + 1 < len(path_parts):
                                env_name = f"conda: {path_parts[idx + 1]}"
                            else:
                                env_name = "conda: unknown"
                        except ValueError:
                            env_name = "conda: unknown"
                    else:
                        # envs を含まないが anaconda/miniconda にある場合は base 環境
                        env_name = "conda: base"
                # 仮想環境検出
                elif "venv" in path_parts or "virtualenv" in path_parts:
                    # venvの名前を抽出
                    for i, part in enumerate(path_parts):
                        if part.lower() == "venv" or part.lower() == "virtualenv":
                            if i > 0:
                                venv_name = path_parts[i - 1]
                                env_name = f"venv: {venv_name}"
                            else:
                                env_name = "venv"
                            break
                # Pythonインストール環境検出
                elif "python" in str(py_path).lower():
                    if os.name == "nt":  # Windows
                        if "windows" in str(py_path).lower():
                            env_name = "system"
                        elif "program files" in str(py_path).lower():
                            env_name = "system"
                        elif "appdata" in str(py_path).lower():
                            env_name = "user"
                    else:  # Unix-like
                        if "/usr/bin" in str(py_path):
                            env_name = "system"
                        elif "/usr/local" in str(py_path):
                            env_name = "local"
                        elif "/opt" in str(py_path):
                            env_name = "optional"
                        elif str(Path.home()) in str(py_path):
                            env_name = "user"
        except Exception as e:
            debug_print(f"[debug] Error determining environment name: {e}")
            env_name = "unknown"

        return env_name
