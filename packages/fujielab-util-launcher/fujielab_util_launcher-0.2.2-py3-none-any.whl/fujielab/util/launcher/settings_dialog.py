from PyQt5.QtWidgets import (
    QDialog,
    QComboBox,
    QLabel,
    QPushButton,
    QFormLayout,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
)
from .i18n import tr
from pathlib import Path


class GlobalSettingsDialog(QDialog):
    """
    グローバル設定ダイアログ
    スクリプト設定は不要で、インタプリタとディレクトリのみを扱います
    """

    def __init__(
        self,
        parent=None,
        envs=None,
        current_env="",
        current_dir="",
        get_interpreters_func=None,
    ):
        super().__init__(parent)
        self.setWindowTitle(tr("Global Settings"))
        self.env_combo = QComboBox()
        self.env_combo.addItems(envs or [])
        if current_env in (envs or []):
            self.env_combo.setCurrentText(current_env)
        self.dir_path_label = QLabel(current_dir)

        dir_button = QPushButton(tr("Select directory"))
        dir_button.clicked.connect(self.select_dir)

        layout = QFormLayout()
        # インタプリタセクションのフレームを作成
        # Create frames with consistent width
        interpreter_frame = QFrame()
        interpreter_frame.setFrameShape(QFrame.StyledPanel)
        interpreter_frame.setFrameShadow(QFrame.Raised)
        interpreter_frame.setMinimumWidth(400)  # Set minimum width
        interpreter_layout = QFormLayout(interpreter_frame)
        interpreter_layout.addRow(tr("Default Python interpreter"), self.env_combo)
        refresh_button = QPushButton(tr("Refresh interpreter list"))
        refresh_button.clicked.connect(self.refresh_interpreters)
        interpreter_layout.addRow("", refresh_button)
        layout.addRow("", interpreter_frame)

        workdir_frame = QFrame()
        workdir_frame.setFrameShape(QFrame.StyledPanel)
        workdir_frame.setFrameShadow(QFrame.Raised)
        workdir_frame.setMinimumWidth(400)  # Same minimum width
        workdir_layout = QFormLayout(workdir_frame)
        workdir_layout.addRow(tr("Default working directory"), self.dir_path_label)
        workdir_layout.addRow("", dir_button)
        layout.addRow("", workdir_frame)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)
        self.get_interpreters_func = get_interpreters_func

    def refresh_interpreters(self):
        # 現在選択されているテキストを保存
        current_text = self.env_combo.currentText()

        # コンボボックスをクリア
        self.env_combo.clear()

        if self.get_interpreters_func:
            new_list = self.get_interpreters_func(force_refresh=True)
            self.env_combo.addItems(new_list.keys())

            # 元々選択していたインタプリタが新しいリストにも存在するなら、それを選択
            if current_text in new_list:
                self.env_combo.setCurrentText(current_text)

    def select_dir(self):
        path = QFileDialog.getExistingDirectory(
            self, tr("Select default working directory")
        )
        if path:
            self.dir_path_label.setText(path)

    def get_values(self):
        return (self.env_combo.currentText(), self.dir_path_label.text())
