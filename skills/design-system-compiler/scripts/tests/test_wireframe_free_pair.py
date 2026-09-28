"""A current reusable system binds the approved HiFi without a wireframe."""
import copy
from pathlib import Path
import re
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]/'ui-design-builder/scripts/tests'))
from test_wireframe_free_publication import current_publication
from test_structure_publication import digest
from test_check_design_system_pair import registry, checker


class WireframeFreePairTests(unittest.TestCase):
    def test_schema_three_pair_validates_current_sources_and_rejects_mixing(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            ui, prd, hifi=current_publication(root)
            text=ui.read_text(encoding='utf-8').replace('Decision: not_required','Decision: required')
            text=re.sub(r'^Replacement visual contract when_not_required:.*$',
                        'Compiled design system pair: pending — design-system-compiler',text,flags=re.M)
            ui.write_text(text,encoding='utf-8')
            data=registry(schema='design-system/3', stylingMechanism='Tailwind CSS', stateMatrix=['ready','updated'])
            data['stackSemantics']={'platform':'web','renderingModel':'SPA',
                                    'componentFoundation':'shadcn/ui owned source','stylingMechanism':'Tailwind CSS'}
            data['sourceBindings']={key:{'path':path.relative_to(root).as_posix(),'sha256':digest(path)}
                for key,path in {'prd':prd,'architecture':root/'docs/product/architecture.md',
                                 'stack':root/'docs/product/stack-decisions.md','uiDesign':ui,'hifi':hifi}.items()}
            data['sourceBindings']['uiDesign']['sha256']=checker.canonical_ui_approval_sha256(text)
            markdown=checker.replace_generated_contract('# Pair\n',data)
            self.assertEqual([],checker.compare(markdown,data,repo_root=root,require_filled=True))
            bad=copy.deepcopy(data); bad['sourceBindings']['wireframe']={'path':'docs/design/wireframes.html','sha256':'0'*64}
            self.assertTrue(checker.compare(checker.replace_generated_contract('# Pair\n',bad),bad,repo_root=root,require_filled=True))
            bad['schema']='design-system/2'
            self.assertIn('requires a legacy UI contract','\n'.join(checker.compare(
                checker.replace_generated_contract('# Pair\n',bad),bad,repo_root=root,require_filled=True)))
            # Changed sibling/entry bytes cannot be hidden behind an old binding.
            hifi.write_text(hifi.read_text(encoding='utf-8')+'\n',encoding='utf-8')
            self.assertIn('sha256 does not match','\n'.join(checker.compare(markdown,data,repo_root=root,require_filled=True)))


if __name__=='__main__':
    unittest.main()
