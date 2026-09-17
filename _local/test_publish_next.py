"""Failure/retry regression tests; all writes use temporary repositories."""
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import publish_next as p

SOURCE = Path(__file__).resolve().parent

class PublishingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / '_local/drafts').mkdir(parents=True)
        (self.root / 'blog').mkdir()
        self.draft = self.root / '_local/drafts/03-example.html'
        self.draft.write_text('reviewed source — 日本語', encoding='utf8')
        for key, value in dict(ROOT=str(self.root), DRAFTS=str(self.draft.parent),
                               STATE=self.root/'_local/state.json',
                               RECEIPT=self.root/'_local/receipt.json').items():
            patcher = patch.object(p, key, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.calls = []

    def state(self, phase='push', **kwargs):
        state = dict(draft=self.draft.name, slug='example', date='2026-09-17', phase=phase)
        state.update(kwargs)
        p.save_state(state)

    def git(self, *args, **kwargs):
        self.calls.append(args)
        if args[0] == 'branch': return 'main'
        if args[0] == 'rev-list': return '0'
        if args[0] == 'rev-parse': return 'same-commit'
        return ''

    def invoke(self, git=None, dgit=None, argv=None):
        with patch.object(p, 'git', side_effect=git or self.git), \
             patch.object(p, 'draft_git', side_effect=dgit or (lambda *a: '')), \
             patch.object(sys, 'argv', argv or ['publish_next.py', '--write']):
            return p.main()

    def test_push_failure_keeps_draft_and_pending_state(self):
        self.state()
        def fail(*args, **kwargs):
            if args[0] == 'push': raise RuntimeError('offline')
            return self.git(*args, **kwargs)
        with self.assertRaisesRegex(RuntimeError, 'offline'):
            self.invoke(git=fail)
        self.assertTrue(self.draft.exists())
        self.assertEqual(json.loads(p.STATE.read_text())['phase'], 'push')
        self.assertEqual(self.invoke(), 0)
        self.assertFalse(self.draft.exists())
        self.assertFalse(p.STATE.exists())
        self.assertEqual(json.loads(p.RECEIPT.read_text())['slug'], 'example')

    def test_private_push_failure_can_resume_after_deleted_draft(self):
        self.state()
        def fail(*args):
            if args[0] == 'push': raise RuntimeError('private offline')
            return ''
        with self.assertRaisesRegex(RuntimeError, 'private offline'):
            self.invoke(dgit=fail)
        self.assertEqual(json.loads(p.STATE.read_text())['phase'], 'archive')
        self.assertFalse(self.draft.exists())
        self.assertEqual(self.invoke(), 0)

    def test_no_push_does_not_retire_source(self):
        self.state()
        self.invoke(argv=['publish_next.py', '--write', '--no-push'])
        self.assertTrue(self.draft.exists())
        self.assertFalse(any(a[0] == 'push' for a in self.calls))

    def test_unrelated_worktree_is_not_published(self):
        def dirty(*args, **kwargs):
            return ' M about.html' if args[0] == 'status' else self.git(*args, **kwargs)
        with self.assertRaisesRegex(RuntimeError, 'Uncommitted'):
            self.invoke(git=dirty)
        self.assertTrue(self.draft.exists())
        self.assertFalse(p.STATE.exists())

    def test_daily_receipt_prevents_second_article(self):
        p.RECEIPT.write_text(json.dumps({'date':'2026-09-17'}))
        self.assertEqual(self.invoke(argv=['publish_next.py','--write','--date=2026-09-17']), 0)
        self.assertTrue(self.draft.exists())
        self.assertFalse(p.STATE.exists())

    def test_commit_failure_retries_its_own_staged_files(self):
        article = self.root/'blog/example.html'
        article.write_text('published body')
        self.state('commit', title='日本語 — title', files={
            'blog/example.html':hashlib.sha256(article.read_bytes()).hexdigest()})
        attempts = 0
        def commit_git(*args, **kwargs):
            nonlocal attempts
            if args[:3] == ('diff','--cached','--name-only'): return 'blog/example.html'
            if args[0] == 'commit':
                attempts += 1
                if attempts == 1: raise RuntimeError('commit failed')
            return self.git(*args, **kwargs)
        with self.assertRaisesRegex(RuntimeError, 'commit failed'):
            self.invoke(git=commit_git)
        self.assertEqual(json.loads(p.STATE.read_text())['phase'], 'commit')
        self.assertEqual(self.invoke(git=commit_git), 0)
        self.assertEqual(attempts, 2)

    def test_edited_output_is_not_committed_on_retry(self):
        article = self.root/'blog/example.html'
        article.write_text('changed')
        self.state('commit', title='title', files={'blog/example.html':'not-the-same'})
        with self.assertRaisesRegex(RuntimeError, 'Generated file changed'):
            self.invoke()
        self.assertTrue(self.draft.exists())

    def test_registration_is_idempotent(self):
        for name in ['build_blog.py','build_log.py','make_og.py']:
            shutil.copyfile(SOURCE/name, self.root/'_local'/name)
        shutil.copyfile(SOURCE.parent/'sitemap.xml', self.root/'sitemap.xml')
        m = dict(slug='example', title='日本語 — test', cat='ブラウザ', lead='説明。',
                 tags=['test'], icon='<circle cx="1" cy="1" r="1"/>',
                 eyebrow='Browser', ogl1='a', ogl2='b', ogsub='c')
        p.register(m, '2026-09-17')
        before = {f:f.read_bytes() for f in self.root.rglob('*') if f.is_file()}
        p.register(m, '2026-09-17')
        for f,data in before.items(): self.assertEqual(f.read_bytes(), data, str(f))

    def test_cp932_parent_produces_utf8_child_logs(self):
        script = self.root/'_local/unicode.py'
        script.write_text("print('日本語 — ✅')", encoding='utf8')
        env = dict(os.environ, PYTHONIOENCODING='cp932')
        code = "import sys; sys.path.insert(0, %r); import publish_next as p; p.ROOT=%r; print(p.run('unicode.py'))" % (str(SOURCE), str(self.root))
        result = subprocess.run([sys.executable,'-c',code],env=env,capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('日本語 — ✅', result.stdout.decode('utf8'))

if __name__ == '__main__':
    unittest.main()
