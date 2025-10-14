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
    QFileDialog,
    QGridLayout,
)
from PyQt5.QtCore import QProcess
from PyQt5.QtGui import QFontDatabase
import platform
import os  # EXEファイル実行のため追加
from pathlib import Path
from .debug_util import debug_print, error_print
from .i18n import tr


class ShellRunnerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.process = None
        self.program_cmdline = ""
        self.working_dir = ""
        self.exe_path = ""  # EXEファイルのパス（Windows環境用）
        self.is_windows = platform.system() == "Windows"  # Windows環境かどうか
        self.output_view = QTextEdit()
        self.output_view.setReadOnly(True)
        fixed_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.output_view.setFont(fixed_font)
        self.program_label = QLabel(tr("Command line:"))
        self.dir_label = QLabel(tr("Working Directory:"))
        self.program_value = QLineEdit()
        self.program_value.setReadOnly(False)  # 直接編集可能に
        self.dir_value = QLineEdit()
        self.dir_value.setReadOnly(True)
        self.dir_select_button = QPushButton(tr("Select"))
        self.run_button = QPushButton(tr("Run"))
        self.stop_button = QPushButton(tr("Stop"))
        self.run_button.setFixedHeight(26)
        self.stop_button.setFixedHeight(26)
        self.dir_select_button.setFixedSize(48, 24)
        self.program_value.setFixedHeight(24)
        self.dir_value.setFixedHeight(24)
        self.program_value.textChanged.connect(self.on_cmdline_changed)
        self.dir_select_button.clicked.connect(self.select_dir)
        self.run_button.clicked.connect(self.run_program)
        self.stop_button.clicked.connect(self.stop_program)
        control_layout = QHBoxLayout()
        control_layout.setSpacing(2)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.addWidget(self.run_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addStretch()
        form_layout = QGridLayout()
        form_layout.setSpacing(2)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.addWidget(self.program_label, 0, 0)
        form_layout.addWidget(self.program_value, 0, 1)
        form_layout.addWidget(self.dir_label, 1, 0)
        form_layout.addWidget(self.dir_value, 1, 1)
        form_layout.addWidget(self.dir_select_button, 1, 2)

        # Windows環境の場合のみEXEファイル選択UIを追加
        if self.is_windows:
            self.exe_label = QLabel("EXEファイル(オプション):")
            self.exe_value = QLineEdit()
            self.exe_value.setReadOnly(True)
            self.exe_select_button = QPushButton("選択")
            self.exe_select_button.setFixedSize(48, 24)
            self.exe_value.setFixedHeight(24)
            self.exe_select_button.clicked.connect(self.select_exe)
            form_layout.addWidget(self.exe_label, 2, 0)
            form_layout.addWidget(self.exe_value, 2, 1)
            form_layout.addWidget(self.exe_select_button, 2, 2)

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
        self.config_changed_callback = None

        # プログラムは起動していない状態でUIを初期化
        self.update_ui_state(running=False)

    def on_cmdline_changed(self, text):
        self.program_cmdline = text
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
            self.dir_value.setText(self.working_dir if self.working_dir else "")
            self.dir_value.setToolTip(self.working_dir if self.working_dir else "")
            if self.config_changed_callback:
                self.config_changed_callback()

    def select_exe(self):
        """EXEファイルを選択するダイアログを表示（Windows環境のみ）"""
        if not self.is_windows:
            return

        file_filter = "実行ファイル (*.exe);;すべてのファイル (*.*)"
        start_dir = self.working_dir if self.working_dir else str(Path.cwd())
        path, _ = QFileDialog.getOpenFileName(
            self, tr("Select executable file"), directory=start_dir, filter=file_filter
        )
        if path:
            self.exe_path = path
            # 作業ディレクトリが設定されている場合は相対パスに変換
            if self.working_dir:
                try:
                    rel_path = os.path.relpath(path, self.working_dir)
                    # 表示は相対パスにする
                    self.exe_value.setText(rel_path)
                    # ユーザーがコマンドラインを自分で入力していた場合は尊重する
                    if not self.program_value.text().strip():
                        # コマンドラインが空の場合のみEXEファイルのパスを設定
                        self.program_value.setText(f'"{rel_path}"')
                except ValueError:
                    # 異なるドライブの場合などは絶対パスを使用
                    self.exe_value.setText(path)
                    if not self.program_value.text().strip():
                        self.program_value.setText(f'"{path}"')
            else:
                # 作業ディレクトリが設定されていなければ絶対パスを使用
                self.exe_value.setText(path)
                if not self.program_value.text().strip():
                    self.program_value.setText(f'"{path}"')

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
        self.dir_select_button.setEnabled(not running)
        if self.is_windows:
            self.exe_select_button.setEnabled(not running)
        self.input_line.setEnabled(running)

    def run_program(self):
        self.output_view.append("[debug] run_program called")
        if not self.program_cmdline:
            self.output_view.append(tr("No command line specified"))
            return
        self.output_view.append(f"[debug] Command line: {self.program_cmdline}")
        self.output_view.append(f"[debug] Working directory: {self.working_dir}")
        # コマンドラインの種類を判断（EXEファイルかコマンドか）
        self.process = QProcess(self)
        command = self.program_cmdline.strip()

        if self.is_windows:  # Windows環境のみEXE直接実行対応
            exe_path, args = self._parse_exe_command(command)
            if exe_path and ".exe" in exe_path.lower():
                self.output_view.append(f"[debug] EXE execute mode: {exe_path}")
                self.output_view.append(f"[debug] Args: {args}")

                # 絶対パスでない場合、作業ディレクトリからの相対パスとして扱う
                if not os.path.isabs(exe_path) and self.working_dir:
                    full_exe_path = os.path.join(self.working_dir, exe_path)
                    self.output_view.append(
                        f"[debug] Converted to absolute path: {full_exe_path}"
                    )

                    # 実際に存在するか確認
                    if os.path.exists(full_exe_path):
                        self.output_view.append(
                            f"[debug] EXE file found: {full_exe_path}"
                        )
                        # EXEファイルを直接実行（シェルを介さない）・引数も渡す
                        self.process.setProgram(full_exe_path)
                        self.process.setArguments(args)
                    else:
                        self.output_view.append(
                            f"<span style='color:red;'>Warning: EXE not found: {full_exe_path}</span>"
                        )
                        # ファイルが見つからない場合も実行を試みる（エラーが発生する可能性あり）
                        self.process.setProgram(full_exe_path)
                        self.process.setArguments(args)
                else:
                    # 絶対パスの場合はそのまま実行
                    if os.path.exists(exe_path):
                        self.output_view.append(f"[debug] EXE file found: {exe_path}")
                        self.process.setProgram(exe_path)
                        self.process.setArguments(args)
                    else:
                        self.output_view.append(
                            f"<span style='color:red;'>Warning: EXE not found: {exe_path}</span>"
                        )
                        # ファイルが見つからない場合も実行を試みる（エラーが発生する可能性あり）
                        self.process.setProgram(exe_path)
                        self.process.setArguments(args)
            else:
                # 通常のコマンドラインの場合はシェル経由で実行
                self.output_view.append("[debug] Shell execution mode")
                shell = "cmd.exe"
                args = ["/C", command]
                self.process.setProgram(shell)
                self.process.setArguments(args)
        else:
            # Unixシステムの場合
            shell = "/bin/sh"
            args = ["-c", command]
            self.process.setProgram(shell)
            self.process.setArguments(args)
        self.process.setWorkingDirectory(self.working_dir)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)
        self.process.stateChanged.connect(self.handle_state_changed)
        self.output_view.clear()
        self.process.errorOccurred.connect(self.handle_process_error)
        self.output_view.append(tr("Starting program..."))
        # Disable controls before starting so failed starts restore the UI
        self.update_ui_state(running=True)
        self.process.start()

    def handle_process_error(self, error):
        self.output_view.append(
            f"<span style='color:red;'>QProcessエラー: {error}</span>"
        )
        if self.process:
            self.output_view.append(f"詳細: {self.process.errorString()}")
        self.update_ui_state(running=False)

    def handle_state_changed(self, state):
        """Update UI whenever the process state changes."""
        self.update_ui_state(state != QProcess.NotRunning)

    # Dockerコンテナに特化した処理は削除

    def stop_program(self):
        if self.process and self.process.state() != QProcess.NotRunning:
            from PyQt5.QtCore import QCoreApplication

            # 段階的なプロセス停止を試みる
            self.output_view.append("プログラムの停止を試みています...")
            self.output_view.repaint()
            QCoreApplication.processEvents()

            # ステップ1: SIGINT (Ctrl+C相当) で停止を促す
            self.output_view.append("SIGINT送信 - 正常終了を2秒間待機中...")
            self.output_view.repaint()
            QCoreApplication.processEvents()

            self.process.terminate()  # QProcess.terminateはSIGINTを送信
            if self.process.waitForFinished(2000):  # 2秒待機
                self.output_view.append("✓ プログラムが正常に停止しました (SIGINT)")
                self.output_view.repaint()
                QCoreApplication.processEvents()
                return

            # ステップ2: SIGTERM (通常のkill) で終了を要求
            self.output_view.append(
                "<span style='color:orange;'>⚠ SIGINTでの停止に失敗しました</span>"
            )
            self.output_view.append("SIGTERM送信 - 終了を2秒間待機中...")
            self.output_view.repaint()
            QCoreApplication.processEvents()

            self.process.kill()  # QProcess.killはSIGTERMを送信 (SIGKILL ではない)
            if self.process.waitForFinished(2000):  # 2秒待機
                self.output_view.append("✓ プログラムが停止しました (SIGTERM)")
                self.output_view.repaint()
                QCoreApplication.processEvents()
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
                self.output_view.append("✓ プログラムを強制終了しました (SIGKILL)")
                self.output_view.repaint()
                QCoreApplication.processEvents()
            except Exception as e:
                self.output_view.append(
                    f"<span style='color:red;'>❌ プロセスの強制終了に失敗しました: {e}</span>"
                )
                self.output_view.repaint()
                QCoreApplication.processEvents()

    def _decode_and_append_output(self, data, is_stderr=False):
        try:
            # Windowsの場合はShift-JIS（CP932）でデコードを試みる
            if platform.system() == "Windows":
                text = bytes(data).decode("cp932", errors="replace")
            else:
                text = bytes(data).decode("utf-8", errors="replace")
            if is_stderr:
                self.output_view.append(f"<span style='color:red;'>{text}</span>")
            else:
                self.output_view.append(text)
        except Exception as e:
            error_text = f"Decode error: {e}"
            self.output_view.append(f"<span style='color:red;'>{error_text}</span>")
            debug_print(
                f"[debug] {'StdErr' if is_stderr else 'StdOut'} decode error: {e}"
            )

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        self._decode_and_append_output(data, is_stderr=False)

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        self._decode_and_append_output(data, is_stderr=True)

    def process_finished(self):
        self.output_view.append(tr("Program finished"))
        self.update_ui_state(running=False)

    def _parse_exe_command(self, command):
        """コマンドライン文字列をEXEパスと引数に分割する

        Args:
            command (str): コマンドライン文字列

        Returns:
            tuple: (実行ファイルパス, 引数のリスト)
        """
        command = command.strip()

        # コマンドが空の場合
        if not command:
            return None, []

        # ダブルクォートで囲まれた部分を処理する
        parts = []
        in_quotes = False
        current_part = ""

        for char in command:
            if char == '"' and not in_quotes:
                in_quotes = True
                current_part += char
            elif char == '"' and in_quotes:
                in_quotes = False
                current_part += char
            elif char.isspace() and not in_quotes:
                if current_part:
                    parts.append(current_part)
                    current_part = ""
            else:
                current_part += char

        if current_part:
            parts.append(current_part)

        if not parts:
            return None, []

        # 実行ファイルパスからクォートを除去
        exe_path = parts[0]
        if exe_path.startswith('"') and exe_path.endswith('"'):
            exe_path = exe_path[1:-1]

        # 引数リストを作成（クォート処理も行う）
        args = []
        for arg in parts[1:]:
            if arg.startswith('"') and arg.endswith('"'):
                args.append(arg[1:-1])
            else:
                args.append(arg)

        return exe_path, args

    def get_config(self):
        config = {"cmdline": self.program_cmdline, "workdir": self.working_dir}
        # Windows環境の場合のみEXEパスを設定に含める
        if self.is_windows:
            config["exepath"] = self.exe_path
        return config

    def apply_config(self, config):
        self.program_cmdline = config.get("cmdline", "")
        self.working_dir = config.get("workdir", "")
        self.program_value.setText(self.program_cmdline)
        self.dir_value.setText(Path(self.working_dir).name if self.working_dir else "")

        # Windows環境の場合のみEXEパスを設定
        if self.is_windows:
            self.exe_path = config.get("exepath", "")
            if self.exe_path:
                if self.working_dir:
                    try:
                        # 作業ディレクトリからの相対パスを表示
                        rel_path = os.path.relpath(self.exe_path, self.working_dir)
                        self.exe_value.setText(rel_path)
                    except ValueError:
                        # 異なるドライブの場合は絶対パス
                        self.exe_value.setText(self.exe_path)
                else:
                    self.exe_value.setText(self.exe_path)

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
                # __del__メソッドではUI更新はできない可能性が高いため、
                # プロセスの終了処理のみを簡潔に行う

                # 段階的なプロセス停止（超短い待機時間で）
                # ここではログ出力や画面更新は行わない

                # ステップ1: SIGINT
                self.process.terminate()
                if self.process.waitForFinished(200):  # 0.2秒待機
                    return

                # ステップ2: SIGTERM
                self.process.kill()
                if self.process.waitForFinished(200):  # 0.2秒待機
                    return

                # ステップ3: SIGKILL
                import signal
                import os

                pid = self.process.processId()
                os.kill(pid, signal.SIGKILL)
            except:
                pass
