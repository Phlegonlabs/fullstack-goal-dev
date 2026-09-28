import re
import unittest
from pathlib import Path


def find_repo_root(start: Path) -> Path | None:
    for candidate in (start, *start.parents):
        if (
            (candidate / "skills" / "delivery-harness" / "SKILL.md").is_file()
            and (candidate / "package.json").is_file()
        ):
            return candidate
    return None


REPO_ROOT = find_repo_root(Path(__file__).resolve().parent)


def ui_design_prompt_problems(content: str) -> list[str]:
    """Return why the README's ui-design-builder prompts miss the ui-design/2 flow."""
    prompts = [
        block
        for block in re.findall(r"```text\n(.*?)```", content, flags=re.DOTALL)
        if "$ui-design-builder" in block
    ]
    if len(prompts) != 2:
        return [f"expected 2 ui-design-builder prompts, found {len(prompts)}"]
    problems = [
        f"prompt names a Wireframe stage: {prompt.strip()[:60]}"
        for prompt in prompts
        if "wireframe" in prompt.lower()
    ]
    joined = "\n".join(prompts)
    for required in (
        "`ui-design/2`",
        "PRD UI Surface Contract",
        "$frontend-design",
        "$impeccable",
        "H1-H9",
        "Visual Approval",
        "$design-system-compiler",
    ):
        if required not in joined:
            problems.append(f"missing {required}")
    for pattern in (r"\b(?:three|tres)\b", r"\b(?:completeness|completitud)\b"):
        if not re.search(pattern, joined):
            problems.append(f"missing {pattern}")
    return problems


class ReadmeStructureTests(unittest.TestCase):
    def structure_profile(self, path: Path) -> dict[str, object]:
        lines = path.read_text(encoding="utf-8").splitlines()
        headings = [
            (index, len(match.group(1)))
            for index, line in enumerate(lines)
            if (match := re.match(r"^(#{1,6})\s+\S", line))
        ]
        fence_lines = sum(1 for line in lines if line.startswith("```"))
        self.assertEqual(fence_lines % 2, 0, f"unclosed fence in {path.name}")

        section_starts = [0, *(index for index, _level in headings)]
        section_counts = []
        for section_index, start in enumerate(section_starts):
            end = (
                section_starts[section_index + 1]
                if section_index + 1 < len(section_starts)
                else len(lines)
            )
            body = lines[start:end]
            if section_index:
                body = body[1:]
            section_counts.append(
                (
                    sum(bool(line.strip()) for line in body),
                    sum(
                        bool(re.match(r"^\s*(?:[-*+] |\d+\. )", line))
                        for line in body
                    ),
                )
            )

        return {
            "heading_order_and_levels": [level for _index, level in headings],
            "fenced_code_blocks": fence_lines // 2,
            "section_nonblank_and_bullet_counts": section_counts,
        }

    @unittest.skipIf(REPO_ROOT is None, "README contract requires a source checkout")
    def test_translations_preserve_english_structure(self) -> None:
        english = self.structure_profile(REPO_ROOT / "README.md")
        for translation in ("README.zh-CN.md", "README.zh-TW.md", "README.es.md"):
            with self.subTest(translation=translation):
                self.assertEqual(
                    self.structure_profile(REPO_ROOT / translation),
                    english,
                )

    @unittest.skipIf(REPO_ROOT is None, "README contract requires a source checkout")
    def test_ui_design_prompts_use_the_ui_design_2_flow(self) -> None:
        for filename in ("README.md", "README.zh-CN.md", "README.zh-TW.md", "README.es.md"):
            content = (REPO_ROOT / filename).read_text(encoding="utf-8")
            with self.subTest(readme=filename):
                self.assertEqual(ui_design_prompt_problems(content), [])

    def test_ui_design_prompt_check_rejects_the_wireframe_flow(self) -> None:
        legacy = (
            "```text\nThe Product Definition is approved. Use $ui-design-builder and "
            "mandatory $frontend-design for wireframes/5, direction selection and full "
            "HiFi. Validate the wireframe internally.\n```\n\n"
            "```text\nThe wireframes/5 structure and sourced copy passed internal "
            "validation. Continue $ui-design-builder with $frontend-design Style "
            "Integration, run separately authorized $impeccable critique and audit plus "
            "H1-H9 grading, obtain one full Visual Approval, and invoke "
            "$design-system-compiler only when required.\n```\n"
        )
        problems = ui_design_prompt_problems(legacy)
        self.assertTrue(any("Wireframe stage" in problem for problem in problems))
        self.assertIn("missing `ui-design/2`", problems)
        self.assertIn(
            "expected 2 ui-design-builder prompts, found 0",
            ui_design_prompt_problems("no prompts"),
        )

    @unittest.skipIf(REPO_ROOT is None, "README contract requires a source checkout")
    def test_readme_outputs_have_no_standalone_run_and_mermaid_braces_close(self) -> None:
        for filename in ("README.md", "README.zh-CN.md", "README.zh-TW.md", "README.es.md"):
            content = (REPO_ROOT / filename).read_text(encoding="utf-8")
            with self.subTest(readme=filename):
                for line in content.splitlines():
                    if line.startswith("|") and line.count("|") >= 4:
                        output_cell = line.split("|")[-2]
                        self.assertNotRegex(output_cell, r"(?:^|,\s*)`RUN\.md`(?:\s*,|$)")
                for block in re.findall(r"```mermaid\n(.*?)```", content, flags=re.DOTALL):
                    self.assertEqual(block.count("{"), block.count("}"), "unbalanced Mermaid braces")

    @unittest.skipIf(REPO_ROOT is None, "README contract requires a source checkout")
    def test_runtime_handoff_graph_profiles_and_zero_to_one_are_aligned(self) -> None:
        for filename in ("README.md", "README.zh-CN.md", "README.zh-TW.md", "README.es.md"):
            content = (REPO_ROOT / filename).read_text(encoding="utf-8")
            with self.subTest(readme=filename):
                for required in (
                    "Zero-to-one",
                    "PLAN/RUN",
                    "same-repository",
                    "cross-machine",
                    "active host",
                    "RUN.active_wave.status",
                    "Host A",
                    "Host B",
                    "exact SHA",
                    "`runtime_unavailable`",
                    "permission-level tool removal",
                ):
                    self.assertIn(required, content)
                self.assertIn("fresh reviewers", content)
                self.assertRegex(content, r"(?i)(never delegate|不能再次分派|nunca delegan)")
                self.assertRegex(content, r"(?i)exact-head[^\n]*review")
                self.assertNotIn("omits write-capable tools", content)
                self.assertNotIn("blocked on provider mismatch", content)
                self.assertNotIn("allowlist", content.lower())
                self.assertNotIn("白名单", content)
                self.assertNotIn("允許清單", content)


if __name__ == "__main__":
    unittest.main()
