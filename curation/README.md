# Defensive, read-only curation

Original selection and indexing work by Carlos Felipe (ofelipepeixoto), under
Apache-2.0. Existing skill authors, repository copyright and licenses remain.
This is a review catalog, not an installed skill pack or executable agent.

Three selections:

1. **building-detection-rules-with-sigma**: study detection-rule metadata and
   conversion prerequisites. No SIEM deployment, conversion execution or claim
   of detection coverage. Follow-up: valid/invalid synthetic rules and explicit
   rejected-input counts.
2. **implementing-cloud-trail-log-analysis**: study audit-event provenance and
   review questions using synthetic JSON only. The source includes AWS setup
   commands: these are NOT approved for execution. No account access, resource
   creation, logging changes or paid queries.
3. **performing-nist-csf-maturity-assessment**: study governance questions and
   evidence gaps. Not a certification or compliance score. Its metadata syntax
   was repaired without changing its instructional body or authorship.

`manifest.json` records the exact source commit, original and reviewed file
hashes, declared authors and license. It does not attest effectiveness or endorse
every source instruction. No scripts are loaded, improved or executed.

## Semantic index correction

`tools/build_index.py` uses PyYAML SafeLoader with duplicate-key and alias
rejection. It preserves multiline descriptions and each declared author rather
than assigning the index maintainer to every entry. Two existing descriptions
contained unquoted colon-space sequences; only those YAML scalar forms changed.
The root index is rebuilt for all 734 entries; inclusion does not authorize use.

With Python and `tools/requirements-index.txt` available, run:

```sh
python tools/build_index.py --output index.json --generated-at 2026-10-14T20:20:00Z
python -m unittest discover -s tests -p 'test_index_semantics.py' -v
```

The update-index workflow source now delegates parsing to this generator; no
workflow is enabled or dispatched by this change. Commits use `[skip ci]` and
validation is local only. Keep the draft unmerged until maintainers review the
new parser dependency and future CI permissions. No offensive scripts changed.
