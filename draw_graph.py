"""Export the compiled LangGraph as docs/state_machine.mmd and docs/state_machine.png."""

from __future__ import annotations

import base64
import os
from pathlib import Path

import httpx

os.chdir(Path(__file__).resolve().parent)

from matching_agent import build_graph  # noqa: E402
from tls import use_system_certificates  # noqa: E402


def main() -> None:
    docs = Path("docs")
    docs.mkdir(exist_ok=True)
    mermaid = build_graph().get_graph().draw_mermaid()
    (docs / "state_machine.mmd").write_text(mermaid, encoding="utf-8")
    print("wrote docs/state_machine.mmd")

    encoded = base64.urlsafe_b64encode(mermaid.encode("utf-8")).decode("ascii")
    use_system_certificates()
    response = httpx.get("https://mermaid.ink/img/{0}?type=png&bgColor=white".format(encoded), timeout=60)
    response.raise_for_status()
    (docs / "state_machine.png").write_bytes(response.content)
    print("wrote docs/state_machine.png ({0} bytes)".format(len(response.content)))


if __name__ == "__main__":
    main()
