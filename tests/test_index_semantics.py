"""Offline metadata regression tests, never skill execution."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_index import build, metadata


class IndexTests(unittest.TestCase):
    def setUp(self):
        self.path = ROOT / 'skills/building-detection-rules-with-sigma/SKILL.md'
        self.text = self.path.read_text()

    def test_multiline_and_author_preserved(self):
        item = metadata(self.text)
        self.assertIn('Builds vendor-agnostic', item['description'])
        self.assertIn('SIEM platforms', item['description'])
        self.assertEqual(item['author'], 'mahipal')
        self.assertEqual(item['license'], 'Apache-2.0')

    def test_tags_preserve_lexical_labels(self):
        text = self.text.replace('tags: [soc, sigma, detection-rules, siem, mitre-attack, splunk, elastic, sentinel]',
                                 'tags: [off, 802.11]')
        self.assertEqual(metadata(text)['tags'], ['off', '802.11'])

    def test_invalid_yaml_and_missing_fields_fail(self):
        for text in ('---\ndescription: a: b\n---', self.text.replace('author: mahipal\n', '')):
            with self.assertRaises((ValueError, yaml.YAMLError)):
                metadata(text)

    def test_duplicate_and_unsafe_yaml_fail(self):
        for text in (self.text.replace('author: mahipal', 'author: first\nauthor: second'),
                     self.text.replace('author: mahipal', 'author: !!python/object:builtins.str {}'),
                     self.text.replace('author: mahipal', 'author: &a [*a]')):
            with self.assertRaises((ValueError, yaml.YAMLError)):
                metadata(text)

    def test_entire_index_semantics_and_reproducibility(self):
        saved = json.loads((ROOT / 'index.json').read_text())
        actual = build(ROOT, saved['generated_at'])
        self.assertEqual(actual, saved)
        self.assertEqual(actual['total_skills'], 734)
        for entry in actual['skills']:
            source = metadata((ROOT / entry['path'] / 'SKILL.md').read_text())
            self.assertEqual(entry['author'], source['author'])
            self.assertEqual(entry['description'], source['description'])
            self.assertNotIn(entry['description'], ('>', '|'))

    def test_curated_manifest_matches_files(self):
        manifest = json.loads((ROOT / 'curation/manifest.json').read_text())
        self.assertLessEqual(len(manifest['items']), 5)
        self.assertEqual(manifest['execution'], 'disabled')
        for item in manifest['items']:
            content = (ROOT / item['path']).read_bytes()
            self.assertEqual(hashlib.sha256(content).hexdigest(), item['reviewed_sha256'])
            self.assertEqual(metadata(content.decode())['author'], item['declared_author'])
            self.assertEqual(item['allowed_use'], 'read-only defensive study')


if __name__ == '__main__':
    unittest.main()
