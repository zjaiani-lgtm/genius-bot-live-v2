import os
import logging
import pandas as pd
from typing import Dict, Any

log = logging.getLogger("GENIUS")


class ExcelReader:
    """
    Reads first-row control signals from Excel.

    Institutional-safe behavior:
      - Optional safety sheets can be missing -> return safe defaults (RUN/OK)
      - Decision sheet is REQUIRED: AI_MASTER_LIVE_DECISION

    Path hardening:
      - Supports relative EXCEL_PATH (e.g. "LIVE.xlsx")
      - Resolves relative paths against project root ("/opt/render/project/src")
      - Also searches common folders: data/, assets/, /var/data/
      - Raises a clear error with tried paths if file is not found
    """

    def __init__(self, path: str):
        self.engine = os.getenv("PANDAS_EXCEL_ENGINE", "openpyxl")
        self.path = self._resolve_excel_path(path)

    # ---------- Path resolving ----------

    def _project_root(self) -> str:
        # core/excel_reader.py -> /opt/render/project/src/core/excel_reader.py
        # project root -> /opt/render/project/src
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _resolve_excel_path(self, path: str) -> str:
        if not path:
            raise RuntimeError("EXCEL_PATH is empty")

        # If absolute and exists -> done
        if os.path.isabs(path) and os.path.exists(path):
            log.info(f"EXCEL_PATH_RESOLVED | mode=abs | path={path}")
            return path

        root = self._project_root()

        candidates = []

        # 1) Relative to CWD
        candidates.append(os.path.abspath(path))

        # 2) Relative to project root
        candidates.append(os.path.join(root, path))

        # 3) Common subfolders in repo
        candidates.append(os.path.join(root, "data", path))
        candidates.append(os.path.join(root, "assets", path))
        candidates.append(os.path.join(root, "static", path))

        # 4) Render persistent disk common location
        candidates.append(os.path.join("/var/data", path))

        # Find first existing
        for c in candidates:
            if os.path.exists(c):
                log.info(f"EXCEL_PATH_RESOLVED | path={c}")
                return c

        # Debug info (helps you instantly)
        try:
            cwd = os.getcwd()
            root_files = os.listdir(root) if os.path.isdir(root) else []
            cwd_files = os.listdir(cwd) if os.path.isdir(cwd) else []
        except Exception:
            cwd = "?"
            root_files = []
            cwd_files = []

        msg = (
            "EXCEL_FILE_NOT_FOUND\n"
            f"  given={path}\n"
            f"  cwd={cwd}\n"
            f"  project_root={root}\n"
            f"  tried_paths={candidates}\n"
            f"  cwd_files_sample={cwd_files[:50]}\n"
            f"  root_files_sample={root_files[:50]}\n"
        )
        raise FileNotFoundError(msg)

    # ---------- Excel reading ----------

    def _excel(self) -> pd.ExcelFile:
        return pd.ExcelFile(self.path, engine=self.engine)

    def _read_first_row_required(self, sheet: str) -> Dict[str, Any]:
        xl = self._excel()
        if sheet not in xl.sheet_names:
            raise RuntimeError(f"EXCEL_SHEET_MISSING: {sheet} | available={xl.sheet_names}")

        df = pd.read_excel(self.path, sheet_name=sheet, engine=self.engine)
        if df is None or df.empty:
            raise RuntimeError(f"EXCEL_SHEET_EMPTY: {sheet}")

        return df.iloc[0].to_dict()

    def _read_first_row_optional(self, sheet: str, default_row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optional sheet: if missing/empty/error -> return defaults
        """
        try:
            xl = self._excel()
            if sheet not in xl.sheet_names:
                return default_row

            df = pd.read_excel(self.path, sheet_name=sheet, engine=self.engine)
            if df is None or df.empty:
                return default_row

            return df.iloc[0].to_dict()
        except Exception:
            return default_row

    # ---------- Public API ----------

    def read_decision(self) -> Dict[str, Any]:
        # REQUIRED
        return self._read_first_row_required("AI_MASTER_LIVE_DECISION")

    def read_sell_firewall(self) -> Dict[str, Any]:
        # OPTIONAL
        return self._read_first_row_optional("SELL_FIREWALL", {"SELL_ALLOWED_FINAL": "YES"})

    def read_heartbeat(self) -> Dict[str, Any]:
        # OPTIONAL
        return self._read_first_row_optional("SYSTEM_HEARTBEAT", {"GLOBAL_STATUS": "RUN"})

    def read_risk_lock(self) -> Dict[str, Any]:
        # OPTIONAL
        return self._read_first_row_optional("RISK_ENVELOPE_LOCK", {"KILL_SWITCH": "OK"})
