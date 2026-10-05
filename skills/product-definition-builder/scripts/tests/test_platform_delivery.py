import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))

import check_product_package  # noqa: E402
from platform_delivery import parse_platform_delivery  # noqa: E402


def release_target(
    target_id: str,
    *,
    surface: str,
    surface_class: str,
    suffix: str,
    stage: str,
) -> str:
    source_policy = (
        "stage=development; ref=run.integration.branch; "
        "sha=run.integration.integration_head_sha"
        if stage == "development"
        else "stage=production; ref=refs/heads/main; sha=promotion.verified_main_sha"
    )
    return f"""### Release Target: {target_id}
- Surface: {surface}
- Surface class: {surface_class}
- Public discoverability: {'yes' if surface_class == 'hosted_web' else 'no'}
- Surface suffix: {suffix}
- Release name: fixture-{suffix}{'-dev' if stage == 'development' else ''}
- Provider: Fixture provider
- Stage: {stage}
- Source policy: {source_policy}
- Artifact kind: fixture artifact
- Signing requirement: not required
- Exact channel / track: fixture-{stage}
- Submission / promotion / review / manual approval path: candidate checks then owner approval
- Availability signal: smoke check passes and the audience reaches the fixture
- Rollout: all users after smoke passes
- Rollback / forward-fix: deploy the prior fixture artifact
"""


def targets_for(specifications: tuple[tuple[str, str, str], ...]) -> str:
    rows = []
    for surface, surface_class, suffix in specifications:
        for stage in ("development", "production"):
            rows.append(release_target(
                f"{surface}-{stage}",
                surface=surface,
                surface_class=surface_class,
                suffix=suffix,
                stage=stage,
            ))
    return "\n".join(rows)


WEB_API_IOS = (
    ("web-app", "hosted_web", "web"),
    ("public-api", "hosted_api", "api"),
    ("ios-app", "ios", "ios"),
)
WEB_API = (
    ("web-app", "hosted_web", "web"),
    ("public-api", "hosted_api", "api"),
)


def sequence(
    *,
    mode: str = "whole_platform_sequential",
    rows: str | None = None,
    shared: str = "public-api",
    arch_ids: str = "ARCH-002",
    status: str = "approved",
    owner: str = "Owner",
    protocol: str = "platform-delivery/1",
) -> str:
    if rows is None:
        rows = (
            "| 1 | web | web-app,public-api | TEST-001 | web smoke passes |\n"
            "| 2 | ios | ios-app | TEST-002 | installed ios smoke passes |"
        )
    return f"""## Platform Delivery Sequence
Platform delivery contract: {protocol}
Delivery mode: {mode}
Decision owner: {owner}
Decision status: {status}
Shared surfaces: {shared}
Shared interface ARCH IDs: {arch_ids}

| Order | Stage | Release surfaces | Required TEST IDs | Completion signal |
| --- | --- | --- | --- | --- |
{rows}
"""


def architecture(
    *,
    specifications: tuple[tuple[str, str, str], ...] = WEB_API_IOS,
    platform: str = "",
) -> str:
    target_rows = targets_for(specifications)
    expected = ", ".join(surface for surface, _, _ in specifications)
    return f"""# Architecture: Fixture

## Component Architecture
| ARCH ID | Component | Responsibility | Upstream trace IDs | Notes |
| --- | --- | --- | --- | --- |
| ARCH-001 | Fixture client | Execute the product journey | PRD-001 | Owned by Owner |

## API and Interface Contracts
| ARCH ID | Interface | Method or Trigger | Input | Output | Errors | TEST IDs |
| --- | --- | --- | --- | --- | --- | --- |
| ARCH-002 | Fixture API | request | request | response | validation error | TEST-001 |

## Release Targets
Expected deployable surfaces: {expected}

{target_rows}
{platform}
## Observability
Fixture events are recorded.
"""


def prd(*, required: tuple[str, ...] = ("TEST-001", "TEST-002")) -> str:
    rows = "\n".join(
        f"| {test_id} | Fixture obligation | integration | Yes | PRD-001 | Fixture signal passes |"
        for test_id in required
    )
    return f"""# PRD: Fixture

## Test Obligations
| TEST ID | Obligation | Test type | Required | Upstream trace IDs | Expected signal |
| --- | --- | --- | --- | --- | --- |
{rows}
"""


def parse(
    *,
    architecture_text: str,
    prd_text: str | None = None,
    require: bool = False,
):
    return parse_platform_delivery(
        architecture_text,
        prd_text if prd_text is not None else prd(),
        require=require,
    )


class PlatformDeliveryTests(unittest.TestCase):
    def test_web_to_ios_with_shared_api_parses(self) -> None:
        contract, findings = parse(architecture_text=architecture(platform=sequence()))
        self.assertEqual([], findings)
        self.assertEqual("platform-delivery/1", contract.protocol)
        self.assertEqual("whole_platform_sequential", contract.mode)
        self.assertEqual("Owner", contract.decision_owner)
        self.assertEqual("approved", contract.decision_status)
        self.assertEqual(("public-api",), contract.shared_surfaces)
        self.assertEqual(("ARCH-002",), contract.shared_arch_ids)
        self.assertEqual(
            (1, 2),
            tuple(stage.order for stage in contract.stages),
        )
        self.assertEqual(("web-app", "public-api"), contract.stages[0].surfaces)
        self.assertEqual(("ios-app",), contract.stages[1].surfaces)
        self.assertEqual(("TEST-001",), contract.stages[0].test_ids)
        self.assertEqual(("TEST-002",), contract.stages[1].test_ids)
        self.assertEqual("ios", contract.stages[1].id)

    def test_ios_to_web_order_is_preserved(self) -> None:
        rows = (
            "| 1 | ios | ios-app | TEST-002 | installed ios smoke passes |\n"
            "| 2 | web | web-app,public-api | TEST-001 | web smoke passes |"
        )
        contract, findings = parse(
            architecture_text=architecture(platform=sequence(rows=rows))
        )
        self.assertEqual([], findings)
        self.assertEqual(("ios", "web"), tuple(stage.id for stage in contract.stages))

    def test_single_user_facing_platform_may_be_not_required(self) -> None:
        candidate = sequence(
            mode="not_required — One hosted web product is released with its shared API.",
            rows="",
            shared="",
            arch_ids="",
        )
        contract, findings = parse(
            architecture_text=architecture(specifications=WEB_API, platform=candidate)
        )
        self.assertEqual([], findings)
        self.assertIsNotNone(contract)
        self.assertEqual("not_required", contract.mode)
        self.assertEqual((), contract.stages)

    def test_absent_marker_is_legacy(self) -> None:
        contract, findings = parse(architecture_text=architecture())
        self.assertIsNone(contract)
        self.assertEqual([], findings)

    def test_hidden_spoofed_marker_is_not_a_contract(self) -> None:
        hidden = "\n```markdown\n" + sequence() + "```\n"
        contract, findings = parse(
            architecture_text=architecture(platform=hidden), require=True
        )
        self.assertIsNone(contract)
        self.assertTrue(any("requires platform-delivery/1" in item for item in findings))

    def test_active_contract_and_malformed_statuses_fail_closed(self) -> None:
        cases = (
            ("duplicate heading", architecture(platform=sequence()) + "\n" + architecture(platform=sequence())),
            ("unsupported protocol", architecture(platform=sequence(protocol="platform-delivery/2"))),
            ("missing section marker", "# Architecture: Fixture\n\nPlatform delivery contract: platform-delivery/1\n"),
            ("draft require", architecture(platform=sequence(status="draft"))),
            ("revision require", architecture(platform=sequence(status="revision_requested"))),
            ("blocked require", architecture(platform=sequence(status="blocked"))),
            ("nonhuman owner", architecture(platform=sequence(owner="Agent"))),
        )
        for label, candidate in cases:
            with self.subTest(case=label):
                _, findings = parse(architecture_text=candidate, require=True)
                self.assertTrue(findings)

    def test_active_duplicate_protocol_marker_outside_section_fails(self) -> None:
        # The explicit Notes section makes the second marker visible outside
        # the sequence body, where section-local duplicate fields cannot see it.
        candidate = architecture(platform=sequence()) + (
            "\n## Notes\n\nPlatform delivery contract: platform-delivery/1\n"
        )
        _, findings = parse(architecture_text=candidate)
        self.assertTrue(
            any(
                "Platform delivery contract must occur exactly once" in item
                for item in findings
            )
        )

    def test_stage_topology_and_coverage_failures_are_visible(self) -> None:
        cases = {
            "duplicate surface": sequence(rows=(
                "| 1 | web | web-app,public-api | TEST-001 | web smoke passes |\n"
                "| 2 | ios | web-app,ios-app | TEST-002 | ios smoke passes |"
            )),
            "surface omission": sequence(rows=(
                "| 1 | web | web-app | TEST-001 | web smoke passes |\n"
                "| 2 | ios | ios-app | TEST-002 | ios smoke passes |"
            )),
            "duplicate stage": sequence(rows=(
                "| 1 | web | web-app,public-api | TEST-001 | web smoke passes |\n"
                "| 1 | web | web-app,public-api | TEST-001 | web smoke passes |\n"
                "| 2 | ios | ios-app | TEST-002 | ios smoke passes |"
            )),
            "invalid order": sequence(rows=(
                "| 2 | ios | ios-app | TEST-002 | ios smoke passes |\n"
                "| 3 | web | web-app,public-api | TEST-001 | web smoke passes |"
            )),
            "missing table": sequence(rows=""),
            "uppercase stage": sequence(rows=(
                "| 1 | Web | web-app,public-api | TEST-001 | web smoke passes |\n"
                "| 2 | ios | ios-app | TEST-002 | ios smoke passes |"
            )),
            "space stage": sequence(rows=(
                "| 1 | web first | web-app,public-api | TEST-001 | web smoke passes |\n"
                "| 2 | ios | ios-app | TEST-002 | ios smoke passes |"
            )),
            "placeholder stage": sequence(rows=(
                "| 1 | todo | web-app,public-api | TEST-001 | web smoke passes |\n"
                "| 2 | ios | ios-app | TEST-002 | ios smoke passes |"
            )),
        }
        for label, candidate in cases.items():
            with self.subTest(case=label):
                _, findings = parse(architecture_text=architecture(platform=candidate))
                self.assertTrue(findings)
                if label == "placeholder stage":
                    self.assertTrue(
                        any(
                            "stage ID is missing or uses placeholder text" in item
                            for item in findings
                        )
                    )

    def test_not_required_cannot_hide_multiple_user_facing_platforms(self) -> None:
        candidate = sequence(
            mode="not_required — The owner wants one product without another sequence.",
            rows="",
            shared="none",
            arch_ids="none",
        )
        _, findings = parse(architecture_text=architecture(platform=candidate))
        self.assertTrue(any("multi-platform user-facing scope" in item for item in findings))

    def test_shared_labels_do_not_replace_inventory_or_interface_authority(self) -> None:
        candidate = sequence(shared="shared-layer", arch_ids="ARCH-999")
        _, findings = parse(architecture_text=architecture(platform=candidate))
        self.assertTrue(any("shared-layer" in item for item in findings))
        self.assertTrue(any("ARCH-999" in item for item in findings))

    def test_required_tests_must_be_canonical_required_rows(self) -> None:
        _, findings = parse(
            architecture_text=architecture(platform=sequence()),
            prd_text=prd(required=("TEST-001",)),
        )
        self.assertTrue(any("TEST-002" in item for item in findings))

    def test_duplicate_required_ids_fail_closed(self) -> None:
        candidate = sequence(
            rows=(
                "| 1 | web | web-app,public-api | TEST-001,TEST-001 | web smoke passes |\n"
                "| 2 | ios | ios-app | TEST-002 | ios smoke passes |"
            ),
            arch_ids="ARCH-002,ARCH-002",
        )
        _, findings = parse(architecture_text=architecture(platform=candidate))
        self.assertTrue(any("duplicate ID 'TEST-001'" in item for item in findings))
        self.assertTrue(any("duplicate ID 'ARCH-002'" in item for item in findings))

    def test_not_required_may_not_reuse_sequence_or_shared_contract(self) -> None:
        candidate = sequence(
            mode="not_required — One hosted web product is released with its shared API.",
            shared="public-api",
            arch_ids="ARCH-002",
        )
        _, findings = parse(
            architecture_text=architecture(specifications=WEB_API, platform=candidate)
        )
        self.assertTrue(any("cannot contain platform stages" in item for item in findings))
        self.assertTrue(any("cannot declare shared surfaces" in item for item in findings))

    def test_package_checker_option_is_integrated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prd_path = root / "PRD.md"
            architecture_path = root / "architecture.md"
            stack_path = root / "stack-decisions.md"
            prd_path.write_text(prd(), encoding="utf-8")
            architecture_path.write_text(architecture(), encoding="utf-8")
            stack_path.write_text("# Stack Decisions: Fixture\n", encoding="utf-8")
            argv = [
                "--prd", str(prd_path),
                "--architecture", str(architecture_path),
                "--stack-decisions", str(stack_path),
                "--platform-delivery", "platform-delivery/1",
            ]
            args = check_product_package.parse_args(argv)
            self.assertEqual("platform-delivery/1", args.platform_delivery)
            findings = check_product_package.validate(
                prd_path,
                architecture_path,
                stack_path,
                platform_delivery=args.platform_delivery,
            )
            self.assertIn(
                "architecture: --platform-delivery requires platform-delivery/1",
                findings,
            )

            architecture_path.write_text(
                architecture(platform=sequence(status="draft")),
                encoding="utf-8",
            )
            findings = check_product_package.validate(
                prd_path,
                architecture_path,
                stack_path,
                platform_delivery=args.platform_delivery,
            )
            self.assertIn(
                "architecture: --platform-delivery requires an approved platform contract",
                findings,
            )

            architecture_path.write_text(
                architecture(platform=sequence()), encoding="utf-8"
            )
            findings = check_product_package.validate(
                prd_path,
                architecture_path,
                stack_path,
                platform_delivery=args.platform_delivery,
            )
            self.assertNotIn(
                "architecture: --platform-delivery requires platform-delivery/1",
                findings,
            )
            self.assertNotIn(
                "architecture: --platform-delivery requires an approved platform contract",
                findings,
            )


if __name__ == "__main__":
    unittest.main()
