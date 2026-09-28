"""Versioned frozen source joins cannot silently skip missing design authority."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import test_harness_strict_authority as legacy
sys.path.insert(0, str(legacy.UI_TESTS_DIR))
from test_wireframe_free_publication import current_publication
from harness_contract_join import validate_frozen_contract_joins
from harness_manifest import mission_has_ui_authoring_action


class WireframeFreeJoinTests(unittest.TestCase):
    def test_ui_contract_authoring_requires_authoring_admission(self):
        self.assertTrue(mission_has_ui_authoring_action({'sources': []},
            {'write_scope': ['docs/design/ui-design.md'], 'deny_scope': []}))
        self.assertFalse(mission_has_ui_authoring_action({'sources': []},
            {'write_scope': ['docs/design/ui-design.md'], 'deny_scope': ['docs/design/**']}))

    def fixture(self, root):
        plan, run, _ = legacy.StrictAuthorityJoinTests._ui_fixture(root, required=False)
        ui, prd, hifi = current_publication(root)
        paths = {'prd': prd, 'architecture': root/'docs/product/architecture.md',
                 'stack decisions': root/'docs/product/stack-decisions.md',
                 'ui design': ui, 'approved ui target': hifi}
        plan['sources'] = [legacy.StrictAuthorityJoinTests._row('SRC-'+str(index), kind, path, root)
                           for index, (kind, path) in enumerate(paths.items())]
        for trace in plan['traces']:
            trace['source_ids'] = ['SRC-0']
        run['runtime_capabilities']['runtime_adapter']['version_gate']['required_harness_version'] = '0.56.0'
        return plan, run, ui

    def test_current_freeze_has_no_wireframe(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            plan, run, _ = self.fixture(root)
            self.assertEqual([], validate_frozen_contract_joins(plan, root, run=run))

    def test_current_freeze_requires_explicit_marker_and_rejects_extra_wireframe(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            plan, run, ui = self.fixture(root)
            text=ui.read_text(encoding='utf-8').replace('UI contract: ui-design/2', '')
            ui.write_text(text,encoding='utf-8')
            plan['sources'][3] = legacy.StrictAuthorityJoinTests._row('SRC-3','ui design',ui,root)
            findings=validate_frozen_contract_joins(plan, root, run=run)
            self.assertIn('requires UI contract: ui-design/2','\n'.join(findings))
            plan['sources'].append(dict(plan['sources'][3], id='SRC-WF',kind='wireframe', location='docs/design/wireframes.html'))
            self.assertIn('must not freeze a wireframe', '\n'.join(validate_frozen_contract_joins(plan,root,run=run)))

    def test_current_maintenance_needs_no_wireframe_row(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            plan, run, _ = self.fixture(root)
            record = root/'docs/epics/EPIC-maintenance.md'
            record.parent.mkdir(parents=True, exist_ok=True)
            record.write_text('Design workflow: maintenance\nUI impact: style\n'
                              f"Plan ID: {plan['plan_id']}\nPlan objective: {plan['objective']}\n"
                              'Requirement refs: REQ-001\nUI scope: UI-001\n', encoding='utf-8')
            for arguments in (('init', '-q'), ('config', 'core.autocrlf', 'false'),
                              ('add', 'docs/epics/EPIC-maintenance.md'),
                              ('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test',
                               'commit', '-qm', 'Freeze maintenance task')):
                subprocess.run(['git', *arguments], cwd=root, check=True, capture_output=True, timeout=15)
            revision = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=root, check=True,
                                      capture_output=True, text=True, timeout=15).stdout.strip()
            row = legacy.StrictAuthorityJoinTests._row('SRC-TASK', 'task record', record, root)
            row['source_revision'] = revision
            plan['sources'].append(row)
            next(trace for trace in plan['traces'] if trace['id'] == 'REQ-001')['source_ids'].append('SRC-TASK')
            self.assertEqual([], validate_frozen_contract_joins(plan, root, run=run))

    def test_legacy_pin_cannot_skip_wireframe_by_using_new_ui(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            plan,run,_=self.fixture(root)
            run['runtime_capabilities']['runtime_adapter']['version_gate']['required_harness_version']='0.55.0'
            self.assertIn('exactly one frozen wireframes', '\n'.join(validate_frozen_contract_joins(plan,root,run=run)))


if __name__=='__main__':
    unittest.main()
