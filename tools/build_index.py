"""Semantic metadata indexing only; never import or execute skill scripts.

Original indexing code by Carlos Felipe (ofelipepeixoto), Apache-2.0.
Skill attribution is preserved verbatim; indexing is not content approval.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

import yaml


class UniqueLoader(yaml.SafeLoader):
    """Reject ambiguous duplicate metadata keys instead of silently overriding."""


def unique_mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if not isinstance(key, str) or key in result:
            raise ValueError('duplicate or non-string metadata key')
        if key == 'tags' and isinstance(value_node, yaml.SequenceNode):
            # Tags are textual labels, not YAML 1.1 booleans/numbers (off, 802.11).
            permitted = {'tag:yaml.org,2002:' + kind for kind in ('str', 'bool', 'int', 'float')}
            if any(not isinstance(n, yaml.ScalarNode) or n.tag not in permitted for n in value_node.value):
                raise ValueError('tags must be scalar labels')
            result[key] = [loader.construct_scalar(n) for n in value_node.value]
        else:
            result[key] = loader.construct_object(value_node, deep=True)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def metadata(text):
    if not text.startswith('---\n'):
        raise ValueError('missing frontmatter')
    parts = text.split('\n---', 1)
    if len(parts) != 2:
        raise ValueError('unterminated frontmatter')
    frontmatter = parts[0][4:]
    if len(frontmatter.encode()) > 65536:
        raise ValueError('oversize frontmatter')
    # Metadata does not need aliases; reject alias expansion, including cycles.
    if any(isinstance(t, (yaml.tokens.AliasToken, yaml.tokens.AnchorToken)) for t in yaml.scan(frontmatter)):
        raise ValueError('aliases forbidden')
    data = yaml.load(frontmatter, Loader=UniqueLoader)
    if not isinstance(data, dict):
        raise ValueError('mapping required')
    for field in ('name', 'description', 'domain', 'subdomain', 'version', 'author', 'license'):
        if not isinstance(data.get(field), str) or not data[field].strip():
            raise ValueError(f'invalid {field}')
        data[field] = data[field].strip()
    if not re.fullmatch(r'[a-z0-9-]{1,64}', data['name']):
        raise ValueError('invalid name')
    if not isinstance(data.get('tags'), list) or not all(isinstance(t, str) and t.strip() for t in data['tags']):
        raise ValueError('invalid tags')
    return {k: data[k] for k in ('name', 'description', 'domain', 'subdomain', 'tags', 'version', 'author', 'license')}


def build(root, generated_at):
    skills, names = [], set()
    for path in sorted((root / 'skills').glob('*/SKILL.md')):
        entry = metadata(path.read_text(encoding='utf-8'))
        if entry['name'] in names:
            raise ValueError(f'duplicate name: {path.parent.name}')
        names.add(entry['name'])
        entry['path'] = path.parent.relative_to(root).as_posix()
        skills.append(entry)
    domains = Counter(s['domain'] for s in skills)
    subdomains = Counter(s['subdomain'] for s in skills)
    tags = Counter(t for s in skills for t in s['tags'])
    return {
        'version': '1.0.0', 'generated_at': generated_at,
        'repository': 'https://github.com/liptonj-eng/anthropic-cybersecurity-skills',
        'total_skills': len(skills), 'total_domains': len(domains),
        'total_subdomains': len(subdomains), 'domain_stats': dict(domains),
        'subdomain_stats': dict(subdomains),
        'top_tags': [{'tag': t, 'count': c} for t, c in tags.most_common(20)],
        'skills': skills,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--generated-at', required=True, help='Explicit UTC timestamp for reproducible generation')
    args = parser.parse_args()
    result = build(args.root, args.generated_at)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
