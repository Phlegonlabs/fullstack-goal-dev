"""The non-strict frozen join hands repo_root to the schema-2 pair checker."""

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from harness_contract_join import validate_frozen_contract_joins  # noqa: E402

SOURCE_FILES = {
    "prd": "docs/product/PRD.md",
    "architecture": "docs/product/architecture.md",
    "stack": "docs/product/stack-decisions.md",
    "uiDesign": "docs/design/ui-design.md",
    "wireframe": "docs/design/wireframes.html",
    "hifi": "docs/design/ui-references/run-1/index.html",
}


def write(root: Path, relative: str, content: bytes) -> str:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return hashlib.sha256(content).hexdigest()


def join_errors(*, stale_prd: bool) -> list[str]:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        bindings = {}
        for key, relative in SOURCE_FILES.items():
            digest = write(root, relative, key.encode("utf-8"))
            bindings[key] = {"path": relative, "sha256": "0" * 64 if stale_prd and key == "prd" else digest}
        registry = {
            "schema": "design-system/2",
            "product": "Fixture",
            "platform": "web",
            "stylingMechanism": "plain CSS",
            "enforcement": "blocking",
            "sourceBindings": bindings,
            "tokenSources": ["src/styles/tokens.css"],
            "primitiveSources": [],
            "viewports": [390, 768, 1200],
            "tokens": {"color": {"text": "#101010"}},
            "primitives": {},
            "stateMatrix": ["ready"],
        }
        json_bytes = json.dumps(registry).encode("utf-8")
        md_bytes = b"# Design System\n"
        plan = {
            "schema_version": 6,
            "sources": [
                {
                    "kind": "design system",
                    "location": "docs/design/design-system.md",
                    "status": "frozen",
                    "content_sha256": write(root, "docs/design/design-system.md", md_bytes),
                },
                {
                    "kind": "design system json",
                    "location": "docs/design/design-system.json",
                    "status": "frozen",
                    "content_sha256": write(root, "docs/design/design-system.json", json_bytes),
                },
            ],
        }
        # run=None keeps the legacy (non-strict) join path.
        return validate_frozen_contract_joins(plan, root)


class NonStrictSchemaTwoJoinTests(unittest.TestCase):
    def test_schema_two_pair_is_checked_against_repo_root(self) -> None:
        errors = join_errors(stale_prd=False)
        self.assertFalse(any("require repo_root" in item for item in errors), errors)
        self.assertFalse(any("sourceBindings.prd sha256" in item for item in errors), errors)

    def test_stale_schema_two_binding_is_reported(self) -> None:
        errors = join_errors(stale_prd=True)
        self.assertFalse(any("require repo_root" in item for item in errors), errors)
        self.assertTrue(
            any("sourceBindings.prd sha256 does not match current bytes" in item for item in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
