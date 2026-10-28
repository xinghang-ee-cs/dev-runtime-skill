from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/planning-layer-runtime/scripts/validate_discovery_entry.py'
spec = importlib.util.spec_from_file_location('discovery_entry', SCRIPT)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def first_checkpoint():
    timestamp = '2026-10-28T08:00:00+00:00'
    return {
        'current_phase': 'discovery_start', 'planning_status': 'planning_in_progress',
        'discovery_checkpoint': {
            'status': 'in_progress', 'revision': 1, 'updated_at': timestamp,
            'initial_intake_summary': 'User requested an offline CSV tool.', 'last_applied_round_id': None,
            'active_question': {'question_id': 'DQ-001', 'topic': 'primary workflow',
                                'prompt_summary': 'What outcome do you need?', 'asked_at': timestamp,
                                'answer_status': 'awaiting_answer'},
            'facts': [{'fact_id': 'DF-001', 'topic': 'goal', 'summary': 'Work offline',
                       'confirmation_status': 'confirmed', 'source_round_id': None}],
            'unresolved_items': [{'item_id': 'DU-001', 'summary': 'Desired result', 'blocking': True,
                                  'resolution_route': 'user_confirmation', 'next_question': 'DQ-001'}],
            'research_findings': [], 'relevant_requirement_pool_refs': [],
        },
        'active_interaction': {'target_type': 'discovery_question', 'target_id': 'DQ-001',
                               'stage': 'discovery_answer', 'version': 1, 'scope': 'initial workflow',
                               'expected_user_action': 'Describe expected output', 'next_step': 'Apply real answer'},
        'explanation_adaptation': {'mode': 'plain_language', 'terminology_policy': 'explain_first_use',
                                   'source': 'safe_default', 'source_refs': [], 'last_reconciled_at': timestamp},
    }


class DiscoveryEntryTests(unittest.TestCase):
    def test_valid_initial_checkpoint_and_cli(self):
        value = first_checkpoint()
        self.assertEqual(validator.validate(value), [])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'current-interaction.yaml'
            path.write_text(json.dumps(value))
            result = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn('passed', result.stdout)

    def test_rejects_first_use_observed_enum_and_id_drift(self):
        value = first_checkpoint()
        value['planning_status'] = 'discovery_in_progress'
        value['discovery_checkpoint']['status'] = 'awaiting_user_answer'
        value['discovery_checkpoint']['active_question']['answer_status'] = 'pending'
        value['discovery_checkpoint']['active_question']['question_id'] = 'discovery-q001'
        value['discovery_checkpoint']['unresolved_items'][0]['resolution_route'] = 'user_answer'
        value['active_interaction']['stage'] = 'awaiting_user_answer'
        errors = validator.validate(value)
        self.assertGreaterEqual(len(errors), 6)
        self.assertTrue(any('DQ-' in error for error in errors))
        self.assertTrue(any('resolution_route' in error for error in errors))

    def test_does_not_accept_future_or_answered_state_as_initial(self):
        value = first_checkpoint()
        value['discovery_checkpoint']['last_applied_round_id'] = 'DR-001'
        value['latest_feedback'] = {'apply_status': 'applied'}
        self.assertTrue(any('answered round' in error for error in validator.validate(value)))
        self.assertTrue(any('feedback' in error for error in validator.validate(value)))

    def test_question_binding_and_revision_must_match(self):
        value = first_checkpoint()
        value['active_interaction']['version'] = 2
        value['active_interaction']['target_id'] = 'DQ-002'
        self.assertEqual(len(validator.validate(value)), 2)

    def test_rejects_missing_or_wrongly_typed_required_fields(self):
        value = first_checkpoint()
        value['discovery_checkpoint']['facts'] = {}
        value['discovery_checkpoint']['revision'] = True
        value['discovery_checkpoint']['updated_at'] = 'yesterday'
        self.assertGreaterEqual(len(validator.validate(value)), 3)
        self.assertEqual(validator.validate(None), ['checkpoint must be a mapping'])

    def test_projection_ids_and_enums_match_existing_format_contract(self):
        profile = (SCRIPT.parent.parent / 'references/discovery-entry.md').read_text()
        canonical = (SCRIPT.parent.parent / 'references/04-planning-format-spec.md').read_text()
        for term in ('planning_in_progress', 'in_progress', 'awaiting_answer', 'discovery_answer',
                     'DQ-<SEQ>', 'DF-<SEQ>', 'DU-<SEQ>', 'RF-<SEQ>', 'DR-<SEQ>',
                     'project_evidence', 'web_research', 'user_confirmation'):
            self.assertIn(term, canonical)
            self.assertIn(term, profile)


if __name__ == '__main__':
    unittest.main()
