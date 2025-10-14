import os
import locale
from .debug_util import debug_print


def _detect_language():
    """Return 'ja' if system locale is Japanese, otherwise 'en'."""
    # First, check explicit environment override
    env_lang = os.environ.get("FUJIELAB_LANG")
    if env_lang:
        debug_print(
            f"[debug] Language set from environment variable FUJIELAB_LANG: {env_lang}"
        )
        return env_lang
    # locale.getdefaultlocale relies on gettext environment variables such as
    # LANG or LC_MESSAGES.
    lang, _ = locale.getdefaultlocale()
    if isinstance(lang, str) and lang.lower().startswith("ja"):
        debug_print(f"[debug] Detected Japanese locale: {lang}")
        return "ja"
    debug_print(f"[debug] Using default English (detected locale: {lang})")
    return "en"


LANG = _detect_language()

_translations = {
    "en": {},
    "ja": {
        # ショートカット作成関連の翻訳
        "Create a shortcut on the Windows Desktop. Windows only.": "Windowsデスクトップにショートカットを作成します。Windows専用。",
        "Error: pywin32 package is required for creating shortcuts.": "エラー: ショートカット作成には pywin32 パッケージが必要です。",
        "Please install it using: pip install pywin32": "pip install pywin32 でインストールしてください。",
        "Error: Could not find the Desktop folder.": "エラー: デスクトップフォルダが見つかりません。",
        "Shortcut created successfully on the Desktop.": "デスクトップにショートカットを作成しました。",
        "Create a shortcut in the Applications folder. macOS only.": "macOSのApplicationsフォルダにショートカットを作成します。macOS専用。",
        "Error: Could not find the Applications folder.": "エラー: Applicationsフォルダが見つかりません。",
        "Shortcut created successfully in the Applications folder.": "Applicationsフォルダにショートカットを作成しました。",
        "Error creating shortcut:": "ショートカット作成エラー:",
        "File": "ファイル",
        "New Python Launcher": "新規Pythonランチャー",
        "New Shell Launcher": "新規シェルランチャー",
        "Import Settings": "設定のインポート",
        "Export Settings": "設定のエクスポート",
        "Exit": "終了",
        "Arrange": "整列",
        "Tile": "タイル",
        "Cascade": "カスケード",
        "Settings": "設定",
        "Global Settings": "グローバル設定",
        "Import Settings File": "設定ファイルのインポート",
        "Export Settings File": "設定ファイルのエクスポート",
        "Restart Confirmation": "再起動確認",
        "Configuration imported. Restart?": "設定ファイルをインポートしました。再起動しますか？",
        "Export Completed": "エクスポート完了",
        "Configuration exported.": "設定ファイルをエクスポートしました。",
        "Interpreter:": "インタプリタ:",
        "Script:": "スクリプト:",
        "Working Directory:": "作業ディレクトリ:",
        "Select": "選択",
        "Run": "実行",
        "Stop": "停止",
        "Enter stdin here and press Enter": "標準入力をここに入力しEnterで送信",
        "No script selected": "スクリプトが選択されていません",
        "Starting script...": "スクリプトを開始します...",
        "Starting program...": "プログラムを開始します...",
        "Program finished": "プログラムが終了しました",
        "Script finished": "スクリプトが終了しました",
        "Default Python interpreter": "デフォルトPythonインタプリタ",
        "Refresh interpreter list": "インタプリタリストの更新",
        "Default working directory": "デフォルト作業ディレクトリ",
        "Select directory": "ディレクトリ選択",
        "Interpreter": "インタプリタ",
        "Command line:": "コマンドライン:",
        "Arguments:": "引数:",
        "Main Menu": "メインメニュー",
        "Select script": "スクリプトを選択",
        "Select executable file": "実行ファイルを選択",
        "Select working directory": "作業ディレクトリを選択",
        "Select default working directory": "デフォルト作業ディレクトリを選択",
        "Confirm recreate config": "設定ファイルの再作成確認",
        "Create new config from command line?\n(Existing settings will be overwritten)": "コマンドラインオプションにより設定ファイルを新規作成します。よろしいですか？\n(既存の設定は上書きされます)",
        "No command line specified": "コマンドラインが入力されていません",
        "Enable debug mode. Detailed log messages will be displayed.": "デバッグモードを有効にします。詳細なログメッセージが表示されます。",
        "Reset the configuration file. Existing settings will be overwritten.": "設定ファイルを初期化します。既存の設定は上書きされます。",
        "Specify the path of the settings file to load at startup.": "起動時に読み込む設定ファイルのパスを指定します。",
        "Display version information and exit.": "バージョン情報を表示して終了します。",
        "Language for UI (en or ja). If omitted, system locale is used.": "UIの言語を指定します (en または ja)。省略した場合はシステムのロケールに従います。",
    },
}


def set_language(lang=None):
    """Set UI language.

    If *lang* is provided, it overrides the detected language.
    Otherwise the language is re-detected from the system locale.
    """
    global LANG
    if lang:
        debug_print(f"[debug] Setting language to: {lang}")
        LANG = lang
    else:
        LANG = _detect_language()
    debug_print(f"[debug] Current language set to: {LANG}")


def tr(text):
    translated = _translations.get(LANG, {}).get(text, text)
    # if translated != text and LANG == 'ja':  # Only log actual translations for Japanese
    #     print(f"Translated: '{text}' -> '{translated}'")
    return translated
