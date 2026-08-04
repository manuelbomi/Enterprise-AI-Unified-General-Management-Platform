"""Enterprise AI General Management Platform CLI entrypoint.

This module launches the FastAPI backend for the platform and can also
generate sample enterprise AI service scaffolding from the shared backend
generator.
"""

from __future__ import annotations

import argparse

import uvicorn

from backend.api import app
from backend.generator import AIServiceGenerator


def main() -> None:
    """Run the platform server or generate sample services from the CLI."""
    parser = argparse.ArgumentParser(
        description="Enterprise AI General Management Platform CLI"
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Run the FastAPI backend server for the enterprise AI platform",
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate sample AI service scaffolding artifacts",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host address for the backend server",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for the backend server",
    )
    args = parser.parse_args()

    if args.serve:
        uvicorn.run(app, host=args.host, port=args.port)
        return

    if args.generate:
        print("Generating sample enterprise AI services...")
        for name, service_type in [
            ("document-analysis-rag", "rag"),
            ("content-generation-llm", "llm"),
            ("workflow-agent", "agent"),
        ]:
            generator = AIServiceGenerator(name, service_type)
            generator.generate()
        return

    parser.print_help()


if __name__ == "__main__":
    main()
