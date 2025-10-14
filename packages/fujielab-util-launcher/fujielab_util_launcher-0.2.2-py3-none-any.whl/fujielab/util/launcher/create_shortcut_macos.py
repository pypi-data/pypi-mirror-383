"""
macOS 環境でのショートカット作成機能。
"""

import os
import re
import sys
import stat
import subprocess
from pathlib import Path

from .i18n import tr
from .debug_util import error_print, debug_print

DEFAULT_APP_NAME = "Fujielab Launcher.app"
FALLBACK_APP_BASENAME = "Fujielab Launcher (User)"


def _add_user_write_permission(target_path):
    """Ensure the current user has write permission on the given path."""
    try:
        mode = os.stat(target_path).st_mode
        if not (mode & stat.S_IWUSR):
            os.chmod(target_path, mode | stat.S_IWUSR)
    except OSError:
        # best effort only
        debug_print(f"[debug] Unable to adjust permissions for: {target_path}")


def _make_tree_user_writable(base_path):
    """Recursively grant user write access to everything under base_path."""
    _add_user_write_permission(base_path)
    for root, dirs, files in os.walk(base_path):
        for dname in dirs:
            _add_user_write_permission(os.path.join(root, dname))
        for fname in files:
            _add_user_write_permission(os.path.join(root, fname))


def _try_remove_app_bundle(app_dir: Path):
    """Attempt to remove an existing macOS app bundle."""
    if not app_dir.exists():
        return True, None

    try:
        import shutil

        shutil.rmtree(app_dir)
        return True, None
    except PermissionError as first_err:
        debug_print(f"[debug] Removal failed, fixing permissions: {first_err}")
        _make_tree_user_writable(str(app_dir))
        try:
            import shutil

            shutil.rmtree(app_dir)
            return True, None
        except Exception as retry_err:  # pragma: no cover - guarded path
            return False, retry_err
    except Exception as err:  # pragma: no cover - unexpected
        return False, err


def _pick_app_dir(base_dir: Path):
    """Decide where to place the macOS app bundle."""
    preferred = base_dir / DEFAULT_APP_NAME
    success, err = _try_remove_app_bundle(preferred)
    if success:
        return preferred, False, None

    error_print(
        tr(
            "Warning: Could not replace existing shortcut. Keeping the old app bundle: {}"
        ).format(preferred)
    )
    if err:
        debug_print(f"[debug] Preferred removal error: {err}")

    # Try fallbacks such as "Fujielab Launcher (User).app", "(User) 2", etc.
    for idx in range(0, 10):
        suffix = "" if idx == 0 else f" {idx + 1}"
        fallback_name = f"{FALLBACK_APP_BASENAME}{suffix}.app"
        fallback = base_dir / fallback_name
        success, fallback_err = _try_remove_app_bundle(fallback)
        if success:
            if idx == 0:
                print(tr("Creating shortcut at fallback location: {}").format(fallback))
            else:
                print(tr("Using alternative fallback location: {}").format(fallback))
            return fallback, True, err
        if fallback_err:
            debug_print(
                f"[debug] Fallback removal error for {fallback}: {fallback_err}"
            )

    return None, True, err


def _ensure_icon(resources_dir: Path, package_dir: str):
    """Create or copy application icon without leaking sips errors."""
    import shutil

    icon_png = os.path.join(package_dir, "resources", "icon.png")
    icon_icns = resources_dir / "icon.icns"

    if not os.path.exists(icon_png):
        debug_print("[debug] icon.png not found; skipping icon generation")
        return icon_icns

    try:
        result = subprocess.run(
            [
                "sips",
                "-s",
                "format",
                "icns",
                icon_png,
                "--out",
                str(icon_icns),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        if result.stderr.strip():
            debug_print(f"[debug] sips stderr: {result.stderr.strip()}")
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        debug_print(f"[debug] sips failed ({exc}); copying PNG fallback")
        try:
            shutil.copy(icon_png, resources_dir / "icon.png")
        except Exception as copy_err:
            error_print(tr("Warning: Could not prepare icon file: {}").format(copy_err))
            return icon_icns

    return icon_icns


def create_macos_shortcut():
    """Create an Application bundle in ``~/Applications`` for macOS."""
    try:
        base_dir = Path.home() / "Applications"
        base_dir.mkdir(parents=True, exist_ok=True)

        app_dir, used_fallback, last_err = _pick_app_dir(base_dir)
        if app_dir is None:
            error_print(
                tr(
                    "Error: Could not find a writable location for the shortcut. "
                    "Remove the existing bundle manually or adjust permissions."
                )
            )
            if last_err:
                error_print(str(last_err))
            return False

        contents = app_dir / "Contents"
        macos_dir = contents / "MacOS"
        resources_dir = contents / "Resources"

        macos_dir.mkdir(parents=True, exist_ok=True)
        resources_dir.mkdir(parents=True, exist_ok=True)

        package_dir = os.path.dirname(os.path.abspath(__file__))
        icon_icns = _ensure_icon(resources_dir, package_dir)

        bundle_name = app_dir.stem
        identifier_suffix = (
            re.sub(r"[^A-Za-z0-9]+", "-", bundle_name).strip("-").lower()
        )
        bundle_identifier = "com.fujielab.launcher"
        if identifier_suffix and identifier_suffix != "fujielab-launcher":
            bundle_identifier = f"{bundle_identifier}.{identifier_suffix}"

        info_plist = contents / "Info.plist"
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key><string>{bundle_name}</string>
    <key>CFBundleIdentifier</key><string>{bundle_identifier}</string>
    <key>CFBundleVersion</key><string>1.0</string>
    <key>CFBundleExecutable</key><string>run.sh</string>
    <key>CFBundleIconFile</key><string>{icon_icns.name if icon_icns.exists() else 'icon.png'}</string>
</dict>
</plist>
"""
        with open(info_plist, "w", encoding="utf-8") as f:
            f.write(plist_content)

        run_sh = macos_dir / "run.sh"
        with open(run_sh, "w", encoding="utf-8") as f:
            f.write(
                f'#!/bin/bash\n"{sys.executable}" -m fujielab.util.launcher.run "$@"\n'
            )
        os.chmod(run_sh, 0o755)

        if used_fallback:
            print(tr("Shortcut created successfully at {}").format(app_dir))
        else:
            print(tr("Shortcut created successfully in the Applications folder."))
        return True
    except Exception as e:
        print(tr("Error creating shortcut:"), str(e))
        return False
