#!/usr/bin/env python3
"""Archive explicitly selected workflow documents; never decides acceptance.

Supported links: single-line inline Markdown destinations (bare or <angle>,
optional quoted title), and single-line reference definitions (including blockquotes).
Relative URLs are URL-decoded/re-encoded; fragments and queries are retained. Fenced code is
opaque. Relevant HTML links and ambiguous/nested Markdown destinations fail
closed. This is not a CommonMark parser. Inbound scanning is bounded by Git
visibility or non-Git dependency exclusions; reports state these limitations.
Older bundles touched by link rewriting are verified before their manifests
are updated. No concurrency/crash-atomic guarantee;
caught write errors roll back, and inputs are rechecked before mutation.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import sys
import subprocess
from urllib.parse import quote, unquote, urlsplit


class ArchiveError(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe(root, rel):
    p = PurePosixPath(rel)
    if p.is_absolute() or not p.parts or '..' in p.parts or '\\' in rel:
        raise ArchiveError('unsafe repository path: ' + rel)
    target = root.joinpath(*p.parts)
    for part in [target, *target.parents]:
        if part == root:
            break
        if part.is_symlink():
            raise ArchiveError('symlink: ' + str(part))
    if target.exists() and not target.is_file():
        raise ArchiveError('not a regular file: ' + rel)
    return target


INLINE = re.compile(r'(!?\[[^\]\n]*\]\()(?P<url><[^>\n]*>|[^\s()]+)(?P<tail>\s+[\"\'][^\n]*?[\"\'])?\)')
REFERENCE = re.compile(r'^( {0,3}(?:> ? {0,3})*\[[^\]\n]+\]:\s*)(?P<url><[^>\n]*>|[^\s]+)(?P<tail>[^\n]*)$', re.M)


def rewrite(text, old, new, moves):
    def url(value):
        angle = value.startswith('<') and value.endswith('>')
        raw = value[1:-1] if angle else value
        parsed = urlsplit(raw)
        if parsed.scheme or parsed.netloc or raw.startswith(('/', '#', '?')):
            return value
        if '\\' in raw:
            raise ArchiveError('unsupported escaped link destination in ' + old)
        target = posixpath.normpath(posixpath.join(posixpath.dirname(old), unquote(parsed.path)))
        if target not in moves and old == new:
            return value
        if not parsed.path:
            return value
        dest = moves.get(target, target)
        result = quote(posixpath.relpath(dest, posixpath.dirname(new)), safe='/@:+~!$&*,;=-._')
        if parsed.query:
            result += '?' + parsed.query
        if parsed.fragment:
            result += '#' + parsed.fragment
        return '<' + result + '>' if angle else result

    relevant_document = old != new or any(posixpath.basename(p) in text for p in moves)
    if relevant_document and re.search(r'\]\([ \t]*\n|\]:[ \t]*\n[ \t]*\S', text):
        raise ArchiveError('unsupported multiline link in ' + old)
    result = []
    fence = None
    for line in text.splitlines(keepends=True):
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            result.append(line)
            continue
        if fence:
            result.append(line)
            continue
        # Refuse unsupported relevant constructs rather than silently breaking them.
        relevant = old != new or any(p in line or posixpath.basename(p) in line for p in moves)
        remainder = REFERENCE.sub('', INLINE.sub('', line))
        if relevant and (re.search(r'<(?:a|img)\b', line, re.I)
                         or re.search(r'\]\([^\n]*\([^\n]*\)', line)
                         or '](' in remainder
                         or re.search(r'<(?:\.\.?/|docs/)[^>]+>', remainder)):
            raise ArchiveError('unsupported ambiguous/HTML link in ' + old)
        def sub(match):
            start, end = match.span('url')
            return match.group(0)[:start-match.start()] + url(match.group('url')) + match.group(0)[end-match.start():]
        line = INLINE.sub(sub, line)
        line = REFERENCE.sub(sub, line)
        # Plain repository paths are metadata, not arbitrary URL substrings.
        # Protect parsed destinations and bare external URLs from this pass.
        spans = [m.span('url') for pattern in (INLINE, REFERENCE) for m in pattern.finditer(line)]
        spans += [m.span() for m in re.finditer(r'(?:[A-Za-z][A-Za-z0-9+.-]*:|(?<![\w/])//)[^\s<>]+', line)]
        def metadata(chunk):
            for source, dest in moves.items():
                chunk = re.sub(r'(?<![\w/.-])' + re.escape(source) + r'(?![\w/.-])', lambda _: dest, chunk)
            return chunk
        cursor, pieces = 0, []
        for start, end in sorted(spans):
            if end <= cursor:
                continue
            pieces.append(metadata(line[cursor:start]) if start >= cursor else '')
            pieces.append(line[max(cursor, start):end])
            cursor = end
        pieces.append(metadata(line[cursor:]))
        result.append(''.join(pieces))
    return ''.join(result)


def write_new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(data)


def replace_file(path, data):
    with path.open('wb') as stream:
        stream.write(data)


def markdown_paths(root):
    """Bound inbound scanning; never follow unrelated symlink directories."""
    limitations = []
    try:
        probe = subprocess.run(['git', '-C', str(root), 'rev-parse', '--show-toplevel'],
                               capture_output=True, check=False)
    except FileNotFoundError:
        probe = None
    if probe and probe.returncode == 0 and Path(os.fsdecode(probe.stdout).strip()).resolve() == root:
        result = subprocess.run(['git', '-C', str(root), 'ls-files', '--cached', '--others',
                                 '--exclude-standard', '-z'], capture_output=True, check=True)
        candidates = sorted(set(os.fsdecode(p) for p in result.stdout.split(b'\0') if p))
        limitations.append('Inbound scan covers Git tracked and non-ignored untracked Markdown only; ignored files and submodules are not scanned.')
        paths = []
        for rel in candidates:
            if not rel.lower().endswith('.md'):
                continue
            path = root / rel
            # Tracked deletions are not live inbound documents.
            if not path.exists() and not path.is_symlink():
                continue
            if any(p.is_symlink() for p in path.parents if p != root and root in p.parents):
                limitations.append('Skipped symlink directory containing: ' + rel)
                continue
            paths.append(rel)
        return paths, limitations
    limitations.append('Non-Git inbound scan excludes .git, node_modules, .venv, venv, __pycache__, vendor, dist, and build; symlink directories are not followed.')
    paths = []
    excluded = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', 'vendor', 'dist', 'build'}
    for directory, dirs, files in os.walk(root, followlinks=False):
        kept = []
        for name in sorted(dirs):
            path = Path(directory) / name
            if path.is_symlink():
                limitations.append('Skipped symlink directory: ' + path.relative_to(root).as_posix())
            elif name not in excluded:
                kept.append(name)
        dirs[:] = kept
        paths.extend((Path(directory) / name).relative_to(root).as_posix()
                     for name in sorted(files) if name.lower().endswith('.md'))
    return paths, limitations


def verified_bundle(root, manifest_rel):
    """Validate the entire old bundle before authorizing any digest updates."""
    raw = safe(root, manifest_rel).read_bytes()
    manifest = json.loads(raw)
    bundle = str(PurePosixPath(manifest_rel).parent)
    iteration = PurePosixPath(bundle).name
    moves = manifest.get('moves')
    if not isinstance(moves, dict) or not moves:
        raise ArchiveError('invalid archive manifest: ' + manifest_rel)
    for source, destination in moves.items():
        if not isinstance(source, str) or not source.startswith('docs/') or destination != bundle + '/' + source[len('docs/'):]:
            raise ArchiveError('invalid archive manifest: ' + manifest_rel)
        safe(root, source)
        safe(root, destination)
    expected = manifest.get('archived', {})
    if not isinstance(expected, dict) or set(expected) != set(moves.values()):
        raise ArchiveError('invalid archive manifest: ' + manifest_rel)
    contents = {manifest_rel: raw}
    for rel, checksum in {**expected, 'docs/changes/' + iteration + '.md': manifest.get('summary')}.items():
        data = safe(root, rel).read_bytes()
        if digest(data) != checksum:
            raise ArchiveError('archive verification failed: ' + rel)
        contents[rel] = data
    return manifest, contents


def archive(root, plan, review, brainstorm, summary_file, iteration, apply=False):
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ArchiveError('root is not a directory')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,99}', iteration):
        raise ArchiveError('unsafe iteration id')
    selected = [plan, review, *brainstorm]
    if len(set(selected)) != len(selected):
        raise ArchiveError('duplicate selected document')
    for rel, category in zip(selected, ['plans', 'reviews'] + ['brainstorm'] * len(brainstorm)):
        p = PurePosixPath(rel)
        if len(p.parts) < 3 or p.parts[:2] != ('docs', category) or p.suffix.lower() != '.md' or str(p) != rel:
            raise ArchiveError('document outside allowed directory: ' + rel)
        safe(root, rel)
    moves = {p: 'docs/workflow/archive/' + iteration + '/' + p[len('docs/'):] for p in selected}
    summary_rel = 'docs/changes/' + iteration + '.md'
    manifest_rel = 'docs/workflow/archive/' + iteration + '/.archive.json'
    for rel in [*moves.values(), summary_rel, manifest_rel]:
        safe(root, rel)
    summary_path = Path(summary_file)
    if any(p.is_symlink() for p in [summary_path, *summary_path.absolute().parents]) or not summary_path.is_file():
        raise ArchiveError('summary input must be a regular nonsymlink file')
    # Input may live outside root, but must never alias a source or output.
    if summary_path.resolve() in {root / p for p in [*selected, *moves.values(), summary_rel, manifest_rel]}:
        raise ArchiveError('summary input collides with bundle')
    summary = summary_path.read_bytes()
    summary.decode('utf-8')
    if not summary.strip():
        raise ArchiveError('empty summary')
    manifest_path = root / manifest_rel
    if manifest_path.exists():
        manifest, _ = verified_bundle(root, manifest_rel)
        if manifest.get('moves') != moves or manifest.get('summary_input', manifest.get('summary')) != digest(summary):
            raise ArchiveError('existing bundle does not match request')
        if any((root / p).exists() for p in selected):
            raise ArchiveError('source conflict with existing archive')
        return {'status': 'already archived', 'moves': moves, 'summary': summary_rel,
                'affected_markdown': [], 'limitations': ['Repeat verifies this bundle only; no inbound scan performed.']}
    for rel in [*moves.values(), summary_rel]:
        if (root / rel).exists():
            raise ArchiveError('destination exists: ' + rel)
    snapshots = {}
    paths, limitations = markdown_paths(root)
    # Explicit inputs are always included, even when Git-ignored. Their paths
    # were checked above; scanning exclusions never waive explicit path safety.
    for rel in sorted(set(paths) | set(selected)):
        path = safe(root, rel)
        if not path.is_file():
            raise ArchiveError('missing source: ' + rel)
        snapshots[rel] = path.read_bytes()
        snapshots[rel].decode('utf-8')
    for rel in selected:
        if rel not in snapshots:
            raise ArchiveError('missing source: ' + rel)
    changed = {}
    archived = {}
    for rel, data in snapshots.items():
        rewritten = rewrite(data.decode('utf-8'), rel, moves.get(rel, rel), moves).encode('utf-8')
        if rel in moves:
            archived[moves[rel]] = rewritten
        elif rewritten != data:
            if (root / rel).resolve() == summary_path.resolve():
                raise ArchiveError('readonly summary input would require link rewriting')
            changed[rel] = rewritten
    prior_manifests = set()
    for rel in changed:
        parts = PurePosixPath(rel).parts
        if parts[:3] == ('docs', 'workflow', 'archive') and len(parts) >= 5:
            prior_manifests.add('/'.join(parts[:4]) + '/.archive.json')
        elif parts[:2] == ('docs', 'changes') and len(parts) == 3:
            candidate = 'docs/workflow/archive/' + PurePosixPath(rel).stem + '/.archive.json'
            if safe(root, candidate).exists():
                prior_manifests.add(candidate)
    for rel in sorted(prior_manifests):
        manifest, originals = verified_bundle(root, rel)
        bundle_prefix = str(PurePosixPath(rel).parent) + '/'
        if any(path.startswith(bundle_prefix) and path not in originals for path in changed):
            raise ArchiveError('unmanifested archive document: ' + rel)
        for path, data in originals.items():
            if path in snapshots and snapshots[path] != data:
                raise ArchiveError('source changed during preflight: ' + path)
            snapshots[path] = data
        # Keep the original request digest stable when the stored summary is
        # legitimately rewritten by a later archive (also upgrades old manifests).
        manifest.setdefault('summary_input', manifest['summary'])
        manifest['archived'] = {path: digest(changed.get(path, originals[path]))
                                for path in manifest['archived']}
        prior_summary = 'docs/changes/' + PurePosixPath(rel).parent.name + '.md'
        manifest['summary'] = digest(changed.get(prior_summary, originals[prior_summary]))
        changed[rel] = (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode()
    report = {'status': 'applied' if apply else 'dry run', 'moves': moves, 'summary': summary_rel,
              'affected_markdown': sorted(set(p for p in changed if p.endswith('.md')) | set(selected)),
              'updated_manifests': sorted(prior_manifests), 'limitations': limitations}
    if not apply:
        return report
    outputs = {**archived, summary_rel: summary}
    outputs[manifest_rel] = (json.dumps({'moves': moves, 'summary': digest(summary),
                                       'archived': {p: digest(b) for p, b in archived.items()}}, sort_keys=True, indent=2) + '\n').encode()
    # Recheck all inputs and absence of outputs immediately before writing.
    if summary_path.read_bytes() != summary:
        raise ArchiveError('summary changed during preflight')
    for rel, data in snapshots.items():
        if safe(root, rel).read_bytes() != data:
            raise ArchiveError('source changed during preflight: ' + rel)
    for rel in outputs:
        if safe(root, rel).exists():
            raise ArchiveError('destination appeared during preflight: ' + rel)
    created, touched, removed = [], [], []
    try:
        for rel, data in outputs.items():
            # Track before writing so a partial write is also cleaned up.
            safe(root, rel)
            created.append(rel)
            try:
                write_new(root / rel, data)
            except FileExistsError:
                # An exclusive-create collision is never ours to remove.
                created.pop()
                raise
            if (root / rel).read_bytes() != data:
                raise ArchiveError('copy verification failed: ' + rel)
        for rel, data in changed.items():
            if safe(root, rel).read_bytes() != snapshots[rel]:
                raise ArchiveError('markdown changed during apply: ' + rel)
            touched.append(rel)
            replace_file(root / rel, data)
            if (root / rel).read_bytes() != data:
                raise ArchiveError('write verification failed: ' + rel)
        for rel in selected:
            if safe(root, rel).read_bytes() != snapshots[rel]:
                raise ArchiveError('source changed during apply: ' + rel)
        for rel in selected:
            (root / rel).unlink()
            removed.append(rel)
    except Exception as error:
        failures = []
        for rel in removed + touched:
            try:
                (root / rel).write_bytes(snapshots[rel])
            except Exception as rollback_error:
                failures.append(str(rollback_error))
        # Keep verified archive copies if source restoration fails.
        if not failures:
            for rel in reversed(created):
                try:
                    (root / rel).unlink(missing_ok=True)
                except Exception as rollback_error:
                    failures.append(str(rollback_error))
        raise ArchiveError('archive failed: ' + str(error) + ('; rollback errors: ' + '; '.join(failures) if failures else '; rolled back')) from error
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('root', 'plan', 'review', 'summary-file', 'id'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--brainstorm', action='append', default=[])
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        print(json.dumps(archive(args.root, args.plan, args.review, args.brainstorm,
                                 args.summary_file, args.id, args.apply), indent=2, sort_keys=True))
    except (OSError, ValueError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
