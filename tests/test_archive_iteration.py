"""Stdlib fixture tests; no project documents are archived."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/wrap-up/scripts/archive_iteration.py'
SPEC = importlib.util.spec_from_file_location('archive_iteration', SCRIPT)
helper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(helper)


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR'))
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / 'repo'
        self.root.mkdir()
        self.summary = self.base / 'summary.md'
        self.summary.write_text('# Result\nAccepted with known limits.\n', encoding='utf-8')
        self.put('docs/plans/x.md', '---\nplan: docs/plans/x.md\n---\nFAIL and BLOCKED remain.\n[review](../reviews/x.md#check)\n[b](../brainstorm/x.md)\n[asset](../../assets/a.png)\n[web](https://example.com/a)\n')
        self.put('docs/reviews/x.md', 'plan: docs/plans/x.md\n[plan][p]\n[p]: ../plans/x.md#goal "Title"\n**Source brainstorm:** docs/brainstorm/x.md\n')
        self.put('docs/brainstorm/x.md', '[plan](../plans/x.md)\n')
        self.put('README.md', '[plan](docs/plans/x.md#goal)\n[p]: <docs/reviews/x.md#check>\nnotdocs/plans/x.md docs/plans/x.md.extra\n')
        self.put('docs/backlog/active.md', 'Still active\n')
        self.put('config.py', 'plan = "docs/plans/x.md"\n')

    def put(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')

    def run_archive(self, **kwargs):
        args = dict(root=self.root, plan='docs/plans/x.md', review='docs/reviews/x.md',
                    brainstorm=['docs/brainstorm/x.md'], summary_file=self.summary, iteration='iteration-1', apply=True)
        args.update(kwargs)
        return helper.archive(**args)

    def snapshot(self, root=None):
        root = self.root if root is None else root
        return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*') if p.is_file()}

    def test_cli_dry_run_no_writes(self):
        before = self.snapshot()
        result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(self.root), '--plan', 'docs/plans/x.md', '--review', 'docs/reviews/x.md', '--brainstorm', 'docs/brainstorm/x.md', '--summary-file', str(self.summary), '--id', 'iteration-1'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['status'], 'dry run')
        self.assertIn('README.md', report['affected_markdown'])
        self.assertEqual(before, self.snapshot())
        self.assertFalse((self.root / 'docs/workflow').exists())

    def test_multiple_inline_links_archive_without_crossing_destinations(self):
        external = '[first](https://example.com/a) and [second](https://example.com/b)\n'
        self.put('docs/plans/x.md', external + '[review](../reviews/x.md) and [asset](../../assets/a.png)\n')
        self.put('README.md', '[plan](docs/plans/x.md#goal) and [review](docs/reviews/x.md)\n')
        before = self.snapshot()
        self.assertEqual(self.run_archive(apply=False)['status'], 'dry run')
        self.assertEqual(before, self.snapshot())
        self.run_archive()
        archived = self.root / 'docs/workflow/archive/iteration-1/plans/x.md'
        self.assertEqual(archived.read_text(),
                         external + '[review](../reviews/x.md) and [asset](../../../../../assets/a.png)\n')
        self.assertEqual((self.root / 'README.md').read_text(),
                         '[plan](docs/workflow/archive/iteration-1/plans/x.md#goal) and '
                         '[review](docs/workflow/archive/iteration-1/reviews/x.md)\n')

    def test_archive_links_metadata_and_evidence(self):
        self.assertEqual(self.run_archive()['status'], 'applied')
        archive = self.root / 'docs/workflow/archive/iteration-1'
        plan = (archive / 'plans/x.md').read_text()
        self.assertIn('FAIL and BLOCKED remain.', plan)
        self.assertIn('[review](../reviews/x.md#check)', plan)
        self.assertIn('[asset](../../../../../assets/a.png)', plan)
        self.assertIn('[web](https://example.com/a)', plan)
        self.assertIn('plan: docs/workflow/archive/iteration-1/plans/x.md', plan)
        review = (archive / 'reviews/x.md').read_text()
        self.assertIn('[p]: ../plans/x.md#goal "Title"', review)
        self.assertIn('**Source brainstorm:** docs/workflow/archive/iteration-1/brainstorm/x.md', review)
        readme = (self.root / 'README.md').read_text()
        self.assertIn('[plan](docs/workflow/archive/iteration-1/plans/x.md#goal)', readme)
        self.assertIn('[p]: <docs/workflow/archive/iteration-1/reviews/x.md#check>', readme)
        self.assertIn('notdocs/plans/x.md docs/plans/x.md.extra', readme)
        self.assertFalse((self.root / 'docs/plans/x.md').exists())
        self.assertEqual((self.root / 'docs/changes/iteration-1.md').read_bytes(), self.summary.read_bytes())
        self.assertEqual((self.root / 'config.py').read_text(), 'plan = "docs/plans/x.md"\n')
        self.assertEqual((self.root / 'docs/backlog/active.md').read_text(), 'Still active\n')

    def test_idempotent_and_mismatched_summary_rejected(self):
        self.run_archive()
        before = self.snapshot()
        self.assertEqual(self.run_archive()['status'], 'already archived')
        self.assertEqual(before, self.snapshot())
        self.summary.write_text('Different summary')
        with self.assertRaises(helper.ArchiveError):
            self.run_archive()
        self.assertEqual(before, self.snapshot())

    def test_idempotent_detects_tamper_source_and_selection_conflict(self):
        self.run_archive()
        self.put('docs/plans/x.md', 'conflict')
        with self.assertRaises(helper.ArchiveError):
            self.run_archive()
        (self.root / 'docs/plans/x.md').unlink()
        with self.assertRaises(helper.ArchiveError):
            self.run_archive(brainstorm=[])
        self.put('docs/workflow/archive/iteration-1/plans/x.md', 'tampered')
        with self.assertRaises(helper.ArchiveError):
            self.run_archive()

    def test_collisions_preserve_sources(self):
        for collision in ['docs/changes/iteration-1.md', 'docs/workflow/archive/iteration-1/plans/x.md']:
            self.put(collision, 'unrelated')
            before = self.snapshot()
            with self.assertRaises(helper.ArchiveError):
                self.run_archive()
            self.assertEqual(before, self.snapshot())
            (self.root / collision).unlink()

    def test_symlink_traversal_duplicate_and_bad_id(self):
        for options in [dict(plan='docs/plans/../plans/x.md'), dict(plan='/docs/plans/x.md'), dict(iteration='../escape'), dict(brainstorm=['docs/brainstorm/x.md'] * 2)]:
            with self.assertRaises(helper.ArchiveError):
                self.run_archive(**options)
        source = self.root / 'docs/plans/x.md'
        data = source.read_bytes()
        source.unlink()
        source.symlink_to(self.summary)
        with self.assertRaises(helper.ArchiveError):
            self.run_archive()
        source.unlink()
        source.write_bytes(data)
        (self.root / 'docs/changes').symlink_to(self.base, target_is_directory=True)
        with self.assertRaises(helper.ArchiveError):
            self.run_archive()

    @unittest.skipUnless(os.name == 'nt', 'NTFS junctions require Windows')
    def test_junction_source_ancestors_preserve_files(self):
        for rel in ['docs/plans', 'docs']:
            for outside_root in [False, True]:
                with self.subTest(ancestor=rel, outside_root=outside_root), tempfile.TemporaryDirectory(dir=self.base) as directory:
                    root = Path(directory) / 'repo'
                    shutil.copytree(self.root, root)
                    link = root / rel
                    target = (Path(directory) if outside_root else root) / 'junction-target'
                    link.rename(target)
                    try:
                        subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(target)],
                                       check=True, capture_output=True)
                        self.assertFalse(link.is_symlink())
                        self.assertTrue(link.is_junction())
                        before = self.snapshot(root)
                        originals = {p.relative_to(target): p.read_bytes()
                                     for p in target.rglob('*') if p.is_file()}
                        with self.assertRaises(helper.ArchiveError):
                            self.run_archive(root=root)
                        self.assertEqual(before, self.snapshot(root))
                        self.assertEqual(originals, {p.relative_to(target): p.read_bytes()
                                                    for p in target.rglob('*') if p.is_file()})
                    finally:
                        link.rmdir()
                        target.rename(link)

    @unittest.skipUnless(os.name == 'nt', 'NTFS junctions require Windows')
    def test_junction_destination_ancestors_preserve_files(self):
        for rel in ['docs/workflow', 'docs/workflow/archive',
                    'docs/workflow/archive/iteration-1',
                    'docs/workflow/archive/iteration-1/plans', 'docs/changes']:
            with self.subTest(ancestor=rel), tempfile.TemporaryDirectory(dir=self.base) as directory:
                root = Path(directory) / 'repo'
                shutil.copytree(self.root, root)
                link = root / rel
                link.parent.mkdir(parents=True, exist_ok=True)
                with tempfile.TemporaryDirectory(dir=directory) as outside:
                    target = Path(outside)
                    sentinel = target / 'untouched.txt'
                    sentinel.write_bytes(b'outside root')
                    subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(target)],
                                   check=True, capture_output=True)
                    try:
                        before = self.snapshot(root)
                        with self.assertRaises(helper.ArchiveError):
                            self.run_archive(root=root)
                        self.assertEqual(before, self.snapshot(root))
                        self.assertEqual({p.name: p.read_bytes() for p in target.rglob('*') if p.is_file()},
                                         {'untouched.txt': b'outside root'})
                    finally:
                        link.rmdir()

    @unittest.skipUnless(os.name == 'nt', 'Windows drive paths require Windows')
    def test_windows_drive_paths_cannot_escape_root(self):
        outside = self.base / 'outside.md'
        outside.write_bytes(b'outside root')
        relative_to_drive = outside.as_posix().replace(outside.drive + '/', outside.drive, 1)
        before = self.snapshot()
        for rel in [outside.as_posix(), relative_to_drive,
                    (self.base / 'new.md').as_posix()]:
            with self.subTest(path=rel):
                with self.assertRaises(helper.ArchiveError):
                    helper.safe(self.root.resolve(), rel)
        self.assertEqual(before, self.snapshot())
        self.assertEqual(outside.read_bytes(), b'outside root')
        self.assertFalse((self.base / 'new.md').exists())

    def test_invalid_utf8_and_summary_collision(self):
        self.put('bad.md', 'x')
        (self.root / 'bad.md').write_bytes(b'\xff')
        before = self.snapshot()
        with self.assertRaises(UnicodeError):
            self.run_archive()
        self.assertEqual(before, self.snapshot())
        (self.root / 'bad.md').unlink()
        with self.assertRaises(helper.ArchiveError):
            self.run_archive(summary_file=self.root / 'docs/plans/x.md')

    def test_write_failure_rolls_back_partial_inbound(self):
        before = self.snapshot()
        def fail(path, data):
            path.write_bytes(b'partial')
            raise OSError('injected write failure')
        with patch.object(helper, 'replace_file', side_effect=fail):
            with self.assertRaisesRegex(helper.ArchiveError, 'rolled back'):
                self.run_archive()
        self.assertEqual(before, self.snapshot())

    def test_copy_failure_preserves_sources(self):
        before = self.snapshot()
        def fail(path, data):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'partial')
            raise OSError('injected copy failure')
        with patch.object(helper, 'write_new', side_effect=fail):
            with self.assertRaisesRegex(helper.ArchiveError, 'rolled back'):
                self.run_archive()
        self.assertEqual(before, self.snapshot())

    def test_remove_failure_recovers_originals(self):
        before = self.snapshot()
        original = Path.unlink
        def fail(path, *args, **kwargs):
            if path == self.root / 'docs/reviews/x.md':
                raise OSError('injected remove failure')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'unlink', fail):
            with self.assertRaisesRegex(helper.ArchiveError, 'rolled back'):
                self.run_archive()
        self.assertEqual(before, self.snapshot())

    def test_explicit_selection_does_not_discover_shared_brainstorm(self):
        self.put('docs/brainstorm/shared.md', 'Shared active document\n')
        self.run_archive(brainstorm=[])
        self.assertTrue((self.root / 'docs/brainstorm/x.md').is_file())
        self.assertEqual((self.root / 'docs/brainstorm/shared.md').read_text(), 'Shared active document\n')

    def test_summary_input_in_repo_is_readonly(self):
        self.put('summary-input.md', '[plan](docs/plans/x.md)\n')
        before = self.snapshot()
        with self.assertRaisesRegex(helper.ArchiveError, 'readonly summary'):
            self.run_archive(summary_file=self.root / 'summary-input.md')
        self.assertEqual(before, self.snapshot())

    def test_source_change_during_initial_planning_detected(self):
        original = helper.rewrite
        altered = False
        def mutate(*args):
            nonlocal altered
            result = original(*args)
            if not altered:
                self.put('docs/plans/x.md', 'Changed before apply\n')
                altered = True
            return result
        with patch.object(helper, 'rewrite', side_effect=mutate):
            with self.assertRaisesRegex(helper.ArchiveError, 'source changed during preflight'):
                self.run_archive()
        self.assertEqual((self.root / 'docs/plans/x.md').read_text(), 'Changed before apply\n')
        self.assertFalse((self.root / 'docs/workflow').exists())

    def test_external_urls_are_not_metadata(self):
        text = '[web](https://example.com?file=docs/plans/x.md)\nhttps://example.com?file=docs/plans/x.md\n'
        self.put('README.md', text)
        self.run_archive()
        self.assertEqual((self.root / 'README.md').read_text(), text)

    def test_cli_apply_and_repeat(self):
        args = [sys.executable, str(SCRIPT), '--root', str(self.root), '--plan', 'docs/plans/x.md', '--review', 'docs/reviews/x.md', '--summary-file', str(self.summary), '--id', 'cli-test', '--apply']
        for status in ['applied', 'already archived']:
            result = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['status'], status)
        self.assertTrue((self.root / 'docs/changes/cli-test.md').is_file())

    def test_source_change_during_copy_detected(self):
        original = helper.write_new
        altered = False
        def mutate(path, data):
            nonlocal altered
            original(path, data)
            if not altered:
                self.put('docs/plans/x.md', 'Changed by another writer\n')
                altered = True
        with patch.object(helper, 'write_new', side_effect=mutate):
            with self.assertRaisesRegex(helper.ArchiveError, 'source changed'):
                self.run_archive()
        self.assertEqual((self.root / 'docs/plans/x.md').read_text(), 'Changed by another writer\n')
        self.assertTrue((self.root / 'docs/reviews/x.md').is_file())
        self.assertFalse((self.root / 'docs/changes/iteration-1.md').exists())

    def test_exclusive_create_race_preserves_unrelated_destination(self):
        original = helper.write_new
        raced = []
        def collide(path, data):
            raced.append(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'unrelated race winner')
            original(path, data)
        with patch.object(helper, 'write_new', side_effect=collide):
            with self.assertRaises(helper.ArchiveError):
                self.run_archive()
        self.assertEqual(raced[0].read_bytes(), b'unrelated race winner')
        self.assertTrue((self.root / 'docs/plans/x.md').is_file())

    def test_nested_and_multiline_relevant_links_fail_closed(self):
        for text in ['[a [b]](docs/plans/x.md)\n', '[plan](\n docs/plans/x.md)\n', '<a href="docs/plans/x.md">plan</a>\n']:
            self.put('README.md', text)
            before = self.snapshot()
            with self.assertRaises(helper.ArchiveError):
                self.run_archive()
            self.assertEqual(before, self.snapshot())

    def test_multiline_links_fail_closed_with_lf_and_crlf(self):
        for newline in [b'\n', b'\r\n']:
            for text in [b'[plan](' + newline + b' docs/plans/x.md)' + newline,
                         b'[plan][p]' + newline + b'[p]: ' + newline + b' docs/plans/x.md' + newline]:
                for rel in ['README.md', 'docs/plans/x.md']:
                    with self.subTest(newline=newline, text=text, document=rel), tempfile.TemporaryDirectory(dir=self.base) as directory:
                        root = Path(directory) / 'repo'
                        shutil.copytree(self.root, root)
                        (root / rel).write_bytes(text)
                        before = self.snapshot(root)
                        with self.assertRaises(helper.ArchiveError):
                            self.run_archive(root=root)
                        self.assertEqual(before, self.snapshot(root))

    def test_url_escaped_paths_query_fragment_and_reference_only(self):
        self.put('docs/plans/space name.md', '# Space\n[here](../reviews/x.md?q=one#check)\n')
        self.put('README.md', '[space](docs/plans/space%20name.md#frag)\n[p]: docs/plans/space%20name.md#frag\n')
        self.run_archive(plan='docs/plans/space name.md')
        text = (self.root / 'README.md').read_text()
        self.assertIn('docs/workflow/archive/iteration-1/plans/space%20name.md#frag', text)
        archived = (self.root / 'docs/workflow/archive/iteration-1/plans/space name.md').read_text()
        self.assertIn('../reviews/x.md?q=one#check', archived)

    def prepare_sequential_archives(self):
        self.put('docs/plans/b.md', '# B\n')
        self.put('docs/reviews/b.md', '[B](../plans/b.md)\n')
        with (self.root / 'docs/plans/x.md').open('a') as stream:
            stream.write('[B](b.md#goal)\n')
        self.summary.write_text('# A\n[B](../plans/b.md#goal)\n')
        self.run_archive()
        self.summary_b = self.base / 'summary-b.md'
        self.summary_b.write_text('# B result\n')
        self.prior_manifest = 'docs/workflow/archive/iteration-1/.archive.json'
        self.prior_plan = 'docs/workflow/archive/iteration-1/plans/x.md'
        self.prior_summary = 'docs/changes/iteration-1.md'

    def archive_b(self, **options):
        return self.run_archive(plan='docs/plans/b.md', review='docs/reviews/b.md',
                                brainstorm=[], summary_file=self.summary_b, iteration='B', **options)

    def test_sequential_archives_update_content_and_summary_and_repeat_a(self):
        self.prepare_sequential_archives()
        before = self.snapshot()
        dry = self.archive_b(apply=False)
        self.assertEqual(before, self.snapshot())
        self.assertEqual(dry['updated_manifests'], [self.prior_manifest])
        self.archive_b()
        manifest = json.loads((self.root / self.prior_manifest).read_text())
        self.assertIn('[B](../../B/plans/b.md#goal)', (self.root / self.prior_plan).read_text())
        self.assertIn('[B](../workflow/archive/B/plans/b.md#goal)', (self.root / self.prior_summary).read_text())
        self.assertEqual(manifest['archived'][self.prior_plan], helper.digest((self.root / self.prior_plan).read_bytes()))
        self.assertEqual(manifest['summary'], helper.digest((self.root / self.prior_summary).read_bytes()))
        self.assertEqual(manifest['summary_input'], helper.digest(self.summary.read_bytes()))
        before_repeat = self.snapshot()
        self.assertEqual(self.run_archive()['status'], 'already archived')
        self.assertEqual(self.archive_b()['status'], 'already archived')
        self.assertEqual(before_repeat, self.snapshot())

    def test_sequential_archive_rejects_tampered_entire_old_bundle(self):
        self.prepare_sequential_archives()
        # Both affected documents and an unaffected member must be verified.
        for rel in [self.prior_plan, self.prior_summary,
                    'docs/workflow/archive/iteration-1/reviews/x.md']:
            with self.subTest(rel=rel):
                path = self.root / rel
                original = path.read_bytes()
                path.write_bytes(original + b'\nUnauthorized edit\n')
                before = self.snapshot()
                for apply in [False, True]:
                    with self.assertRaisesRegex(helper.ArchiveError, 'archive verification failed'):
                        self.archive_b(apply=apply)
                    self.assertEqual(before, self.snapshot())
                path.write_bytes(original)

    def test_prior_manifest_partial_write_failure_rolls_back_everything(self):
        self.prepare_sequential_archives()
        before = self.snapshot()
        original = helper.replace_file
        reached = []
        def fail(path, data):
            if path == self.root / self.prior_manifest:
                reached.append(path)
                path.write_bytes(b'partial manifest')
                raise OSError('injected manifest failure')
            original(path, data)
        with patch.object(helper, 'replace_file', side_effect=fail):
            with self.assertRaisesRegex(helper.ArchiveError, 'manifest failure; rolled back'):
                self.archive_b()
        self.assertEqual(len(reached), 1)
        self.assertEqual(before, self.snapshot())
        self.assertEqual(self.run_archive()['status'], 'already archived')

    def test_blockquoted_reference_definitions_rewritten(self):
        self.put('docs/reviews/active.md', '> [plan][p]\n> [p]: ../plans/x.md#goal "Title"\n> > [q]: <../plans/x.md?q=one#two>\n')
        self.run_archive()
        text = (self.root / 'docs/reviews/active.md').read_text()
        self.assertIn('> [p]: ../workflow/archive/iteration-1/plans/x.md#goal "Title"', text)
        self.assertIn('> > [q]: <../workflow/archive/iteration-1/plans/x.md?q=one#two>', text)

    def test_network_path_urls_are_not_metadata(self):
        text = ('source: //example.com/?file=docs/plans/x.md\n'
                '//example.com/docs/plans/x.md\n'
                '[web](//example.com/?file=docs/plans/x.md)\n'
                '[p]: //example.com/?file=docs/plans/x.md\n')
        self.put('README.md', text + 'source: docs/plans/x.md\n')
        self.run_archive()
        self.assertEqual((self.root / 'README.md').read_text(),
                         text + 'source: docs/workflow/archive/iteration-1/plans/x.md\n')

    def test_nongit_scan_skips_dependency_and_unrelated_symlink_dirs(self):
        outside = self.base / 'dependency'
        outside.mkdir()
        (outside / 'bad.md').write_bytes(b'\xff')
        (self.root / 'node_modules').mkdir()
        (self.root / 'node_modules/pkg').symlink_to(outside, target_is_directory=True)
        (self.root / 'external').symlink_to(outside, target_is_directory=True)
        self.put('build/generated.md', '[plan](docs/plans/x.md)\n')
        report = self.run_archive()
        self.assertTrue(any('Skipped symlink directory: external' in s for s in report['limitations']))
        self.assertEqual((outside / 'bad.md').read_bytes(), b'\xff')
        self.assertEqual((self.root / 'build/generated.md').read_text(), '[plan](docs/plans/x.md)\n')
        self.assertIn('docs/workflow/archive/iteration-1/plans/x.md', (self.root / 'README.md').read_text())

    def test_git_scan_tracks_ignored_files_and_skips_untracked_ignored(self):
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True, capture_output=True)
        self.put('.gitignore', 'node_modules/\nignored/\ndocs/plans/x.md\n')
        self.put('ignored/tracked.md', '[plan](../docs/plans/x.md)\n')
        subprocess.run(['git', '-C', str(self.root), 'add', '-f', 'ignored/tracked.md'], check=True, capture_output=True)
        self.put('ignored/bad.md', 'placeholder')
        (self.root / 'ignored/bad.md').write_bytes(b'\xff')
        outside = self.base / 'dependency'
        outside.mkdir()
        (outside / 'bad.md').write_bytes(b'\xff')
        (self.root / 'node_modules').mkdir()
        (self.root / 'node_modules/pkg').symlink_to(outside, target_is_directory=True)
        report = self.run_archive()
        self.assertTrue(any('Git tracked' in s for s in report['limitations']))
        self.assertIn('../docs/workflow/archive/iteration-1/plans/x.md', (self.root / 'ignored/tracked.md').read_text())
        self.assertEqual((self.root / 'ignored/bad.md').read_bytes(), b'\xff')
        self.assertIn('docs/workflow/archive/iteration-1/plans/x.md', (self.root / 'README.md').read_text())
        self.assertFalse((self.root / 'docs/plans/x.md').exists())

    def test_scanned_markdown_symlink_still_rejected(self):
        (self.root / 'inbound.md').symlink_to(self.summary)
        with self.assertRaisesRegex(helper.ArchiveError, 'symlink'):
            self.run_archive()

    def test_fenced_examples_preserved_while_live_links_rewritten(self):
        for prefix in ['', '> ', '> > ']:
            for fence in ['```', '~~~~']:
                for newline in ['\n', '\r\n']:
                    for rel, link in [('README.md', 'docs/plans/x.md'),
                                      ('docs/plans/x.md', '../reviews/x.md')]:
                        with self.subTest(prefix=prefix, fence=fence, newline=newline, document=rel), tempfile.TemporaryDirectory(dir=self.base) as directory:
                            root = Path(directory) / 'repo'
                            shutil.copytree(self.root, root)
                            example = newline.join([
                                prefix + fence + 'md',
                                prefix + '[example](' + link + ')',
                                prefix + '[multiline](',
                                prefix + ' ' + link + ')',
                                prefix + '[reference]:',
                                prefix + ' ' + link,
                                prefix + fence,
                                '',
                            ])
                            live = '[live](' + link + ')' + newline
                            (root / rel).write_bytes((example + live).encode('utf-8'))
                            before = self.snapshot(root)
                            self.run_archive(root=root, apply=False)
                            self.assertEqual(before, self.snapshot(root))
                            self.run_archive(root=root)
                            if rel == 'README.md':
                                output = root / rel
                                expected_link = 'docs/workflow/archive/iteration-1/plans/x.md'
                            else:
                                output = root / 'docs/workflow/archive/iteration-1/plans/x.md'
                                expected_link = '../reviews/x.md'
                            self.assertEqual(output.read_bytes(),
                                             (example + '[live](' + expected_link + ')' + newline).encode('utf-8'))

    def test_fence_closes_only_with_matching_bare_marker(self):
        for false_close in ['```', '~~~~', '````not-a-close', '> ````']:
            with self.subTest(false_close=false_close), tempfile.TemporaryDirectory(dir=self.base) as directory:
                root = Path(directory) / 'repo'
                shutil.copytree(self.root, root)
                example = '````md\n' + false_close + '\n[example](docs/plans/x.md)\n`````\n'
                (root / 'README.md').write_text(example + '[live](docs/plans/x.md)\n', encoding='utf-8')
                self.run_archive(root=root)
                self.assertEqual((root / 'README.md').read_text(encoding='utf-8'),
                                 example + '[live](docs/workflow/archive/iteration-1/plans/x.md)\n')

    def test_unclosed_quoted_fence_ends_at_quote_boundary(self):
        example = '> ```md\n> [example](docs/plans/x.md)\n'
        self.put('README.md', example + '\n[plan](docs/plans/x.md)\n')
        self.run_archive()
        self.assertEqual((self.root / 'README.md').read_text(encoding='utf-8'),
                         example + '\n[plan](docs/workflow/archive/iteration-1/plans/x.md)\n')

    def test_unsupported_ambiguous_link_rejected_and_fences_opaque(self):
        for text in [
            '[plan](docs/plans/x.md(foo))\n',
            '[valid](https://example.com/a) and [plan](docs/plans/x.md(foo))\n',
            '[plan](docs/plans/x.md(foo)) and [valid](https://example.com/b)\n',
        ]:
            with self.subTest(text=text):
                self.put('README.md', text)
                before = self.snapshot()
                with self.assertRaises(helper.ArchiveError):
                    self.run_archive()
                self.assertEqual(before, self.snapshot())
        self.put('README.md', '```md\n[plan](docs/plans/x.md)\n```\n')
        self.run_archive()
        self.assertEqual((self.root / 'README.md').read_text(), '```md\n[plan](docs/plans/x.md)\n```\n')


if __name__ == '__main__':
    unittest.main()
