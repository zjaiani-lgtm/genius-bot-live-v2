import os
import pandas as pd


class ExcelReader:
    """
    Reads first-row control signals from Excel.
    Institutional-safe behavior:
      - If optional safety sheets are missing, we return safe defaults (RUN/OK),
        so the bot doesn't crash.
      - Decision sheet is REQUIRED: AI_MASTER_LIVE_DECISION
    """

    def __init__(self, path: str):
        self.path = path
        self.engine = os.getenv("PANDAS_EXCEL_ENGINE", "openpyxl")

    def _excel(self) -> pd.ExcelFile:
        return pd.ExcelFile(self.path, engine=self.engine)

    def _read_first_row_required(self, sheet: str) -> dict:
        xl = self._excel()
        if sheet not in xl.sheet_names:
            raise RuntimeError(f"EXCEL_SHEET_MISSING: {sheet} | available={xl.sheet_names}")

        df = pd.read_excel(self.path, sheet_name=sheet, engine=self.engine)
        if df is None or df.empty:
            raise RuntimeError(f"EXCEL_SHEET_EMPTY: {sheet}")
        return df.iloc[0].to_dict()

    def _read_first_row_optional(self, sheet: str, default_row: dict) -> dict:
        """
        Optional sheet: if missing/empty -> return defaults
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

    # --- Public API ---

    def read_decision(self) -> dict:
        # REQUIRED
        return self._read_first_row_required("AI_MASTER_LIVE_DECISION")

    def read_sell_firewall(self) -> dict:
        # OPTIONAL
        return self._read_first_row_optional("SELL_FIREWALL", {"SELL_ALLOWED_FINAL": "YES"})

    def read_heartbeat(self) -> dict:
        # OPTIONAL: fallback so bot never crashes because this sheet isn't present
        return self._read_first_row_optional("SYSTEM_HEARTBEAT", {"GLOBAL_STATUS": "RUN"})

    def read_risk_lock(self) -> dict:
        # OPTIONAL
        return self._read_first_row_optional("RISK_ENVELOPE_LOCK", {"KILL_SWITCH": "OK"})
