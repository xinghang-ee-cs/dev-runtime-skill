#!/usr/bin/env python3
"""Validate a new first-question checkpoint using the existing Discovery contract.

JSON syntax is valid YAML and permits dependency-free validation of new checkpoints.
Existing YAML Runtime recovery is handled by the regular Planning recovery workflow.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path


def validate(value: object) -> list[str]:
    errors: list[str] = []
    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)
    def mapping(parent: dict, key: str) -> dict:
        child = parent.get(key)
        require(isinstance(child, dict), f'{key} must be a mapping')
        return child if isinstance(child, dict) else {}
    def text(parent: dict, key: str) -> bool:
        return isinstance(parent.get(key), str) and bool(parent[key].strip())
    def timestamp(value: object) -> bool:
        if not isinstance(value, str):
            return False
        try:
            return dt.datetime.fromisoformat(value.replace('Z', '+00:00')).tzinfo is not None
        except ValueError:
            return False
    if not isinstance(value, dict):
        return ['checkpoint must be a mapping']
    require(text(value, 'current_phase'), 'current_phase is required')
    require(value.get('planning_status') == 'planning_in_progress', 'first entry planning_status must be planning_in_progress')
    checkpoint = mapping(value, 'discovery_checkpoint')
    require(checkpoint.get('status') == 'in_progress', 'first entry discovery_checkpoint.status must be in_progress')
    require(type(checkpoint.get('revision')) is int and checkpoint['revision'] >= 0, 'revision must be a nonnegative integer')
    require(timestamp(checkpoint.get('updated_at')), 'updated_at requires a timestamp with timezone')
    require(text(checkpoint, 'initial_intake_summary'), 'initial_intake_summary is required before the question')
    require('last_applied_round_id' in checkpoint and checkpoint['last_applied_round_id'] is None, 'no answered round may be invented at first entry')
    question = mapping(checkpoint, 'active_question')
    question_id = question.get('question_id')
    require(isinstance(question_id, str) and bool(re.fullmatch(r'DQ-\d+', question_id)), 'question_id must use DQ-<SEQ>')
    require(question.get('answer_status') == 'awaiting_answer', 'question answer_status must be awaiting_answer')
    for key in ('topic', 'prompt_summary'):
        require(text(question, key), f'active_question.{key} is required')
    require(timestamp(question.get('asked_at')), 'asked_at requires a timestamp with timezone')
    interaction = mapping(value, 'active_interaction')
    require(interaction.get('target_type') == 'discovery_question', 'target_type must be discovery_question')
    require(interaction.get('target_id') == question_id, 'interaction must reference the current question')
    require(interaction.get('stage') == 'discovery_answer', 'interaction stage must be discovery_answer')
    require(interaction.get('version') == checkpoint.get('revision'), 'interaction version must match checkpoint revision')
    for key in ('scope', 'expected_user_action', 'next_step'):
        require(text(interaction, key), f'active_interaction.{key} is required')
    specs = {
        'facts': ('fact_id', r'DF-\d+'),
        'unresolved_items': ('item_id', r'DU-\d+'),
        'research_findings': ('research_id', r'RF-\d+'),
    }
    for collection, (key, pattern) in specs.items():
        items = checkpoint.get(collection)
        require(isinstance(items, list), f'{collection} must be a list')
        seen: set[str] = set()
        for item in items if isinstance(items, list) else []:
            if not isinstance(item, dict):
                require(False, f'{collection} entries must be mappings')
                continue
            identifier = item.get(key)
            valid = isinstance(identifier, str) and bool(re.fullmatch(pattern, identifier))
            require(valid, f'{collection}.{key} has an invalid Discovery ID')
            require(not valid or identifier not in seen, f'{collection} IDs must be unique')
            if valid:
                seen.add(identifier)
            if collection == 'facts':
                require(item.get('confirmation_status') in {'candidate', 'confirmed', 'superseded'}, 'invalid fact confirmation_status')
                for field in ('topic', 'summary'):
                    require(text(item, field), f'fact.{field} is required')
            elif collection == 'unresolved_items':
                require(item.get('resolution_route') in {'project_evidence', 'web_research', 'user_confirmation'}, 'invalid unresolved resolution_route')
                require(text(item, 'summary') and text(item, 'next_question'), 'unresolved summary and next_question are required')
                require(type(item.get('blocking')) is bool, 'unresolved blocking must be boolean')
            else:
                require(item.get('evidence_scope') in {'project_local', 'external_public'}, 'invalid research evidence_scope')
                require(item.get('evidence_status') in {'verified', 'conflicting', 'insufficient', 'stale'}, 'invalid research evidence_status')
                require(item.get('planning_relevance') in {'evidence_only', 'candidate', 'confirmed_applicable', 'not_applicable'}, 'invalid research planning_relevance')
                require(timestamp(item.get('checked_at')) and text(item, 'finding_summary'), 'research summary and checked_at are required')
                require(isinstance(item.get('sources'), list) and bool(item.get('sources')), 'research sources are required')
    require(isinstance(checkpoint.get('relevant_requirement_pool_refs'), list), 'requirement pool references must be a list')
    adaptation = mapping(value, 'explanation_adaptation')
    require(adaptation.get('mode') in {'plain_language', 'adaptive', 'technical_concise'}, 'invalid explanation mode')
    require(adaptation.get('terminology_policy') in {'explain_first_use', 'explain_when_ambiguous', 'concise'}, 'invalid terminology policy')
    require(adaptation.get('source') in {'safe_default', 'user_profile', 'current_discovery', 'combined'}, 'invalid explanation source')
    require(isinstance(adaptation.get('source_refs'), list), 'explanation source_refs must be a list')
    require(timestamp(adaptation.get('last_reconciled_at')), 'last_reconciled_at requires a timestamp with timezone')
    require(not value.get('latest_feedback'), 'do not invent user feedback before the first question')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('checkpoint', type=Path)
    args = parser.parse_args()
    try:
        value = json.loads(args.checkpoint.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        print(f'Cannot validate new entry: {exc}. Use JSON syntax (valid YAML); do not install a parser or rewrite existing Runtime for this check.')
        return 1
    errors = validate(value)
    for error in errors[:20]:
        print(f'- {error}')
    print('Discovery entry validation ' + ('failed.' if errors else 'passed.'))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
