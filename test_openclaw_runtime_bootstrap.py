from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from openclaw_runtime_bootstrap import _ensure_minimal_config_file


class OpenClawRuntimeBootstrapTests(unittest.TestCase):
    def test_minimal_config_file_applies_trusted_proxies_from_env(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home_dir = Path(temp_dir) / "openclaw-home"
            with patch.dict(
                os.environ,
                {
                    "OPENCLAW_HOME": str(home_dir),
                    "OPENCLAW_TRUSTED_PROXIES_JSON": json.dumps(
                        ["127.0.0.1/32", "::1/128", "169.254.0.0/16"]
                    ),
                },
                clear=False,
            ):
                _ensure_minimal_config_file(home_dir)

                payload = json.loads((home_dir / "openclaw.json").read_text(encoding="utf-8"))

        self.assertEqual(
            payload["gateway"]["trustedProxies"],
            ["127.0.0.1/32", "::1/128", "169.254.0.0/16"],
        )

    def test_minimal_config_file_rejects_invalid_trusted_proxies_env(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home_dir = Path(temp_dir) / "openclaw-home"
            with patch.dict(
                os.environ,
                {
                    "OPENCLAW_HOME": str(home_dir),
                    "OPENCLAW_TRUSTED_PROXIES_JSON": '{"invalid": true}',
                },
                clear=False,
            ):
                with self.assertRaisesRegex(
                    RuntimeError, "OPENCLAW_TRUSTED_PROXIES_JSON"
                ):
                    _ensure_minimal_config_file(home_dir)


if __name__ == "__main__":
    unittest.main()
