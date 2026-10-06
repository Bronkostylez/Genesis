"""Regressionstests ohne GUI oder laufendes Ollama."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import commands
import config
import interfaces
import ollama_client
import state
import world


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'genesis_instance'
        for module in (world, interfaces, state):
            patcher = patch.object(module, 'GENESIS_DIR', self.root)
            patcher.start()
            self.addCleanup(patcher.stop)
        world.reset_instance()

    def test_initial_world_preserves_original_program(self):
        expected = config.BASE_DIR / 'templates' / 'world_main.py.txt'
        self.assertEqual(list(self.root.iterdir()), [self.root / 'main.py'])
        self.assertEqual((self.root / 'main.py').read_bytes(), expected.read_bytes())
        (self.root / 'extra.txt').write_text('old')
        world.reset_instance()
        self.assertFalse((self.root / 'extra.txt').exists())

    def test_path_restrictions(self):
        for invalid in (None, '', ' ', '../outside.txt', str(self.root.parent / 'outside')):
            with self.subTest(path=invalid), self.assertRaises(ValueError):
                world.safe_path(invalid)
        self.assertEqual(world.safe_path('folder/file.txt'), self.root / 'folder/file.txt')
        self.assertFalse(interfaces.interface_delete('.')['ok'])

    def test_file_operations_and_dispatch(self):
        create = {'operation': 'create', 'path': 'notes/test.txt', 'kind': 'file',
                  'content': 'Hallo', 'reason': 'Test'}
        self.assertEqual(commands.validate_command(create), (True, None))
        self.assertTrue(commands.execute_interface(create)['ok'])
        self.assertFalse(commands.execute_interface(create)['ok'])
        self.assertEqual(interfaces.interface_view('notes/test.txt')['content'], 'Hallo')
        self.assertTrue(interfaces.interface_edit('notes/test.txt', 'Neu')['ok'])
        self.assertEqual(interfaces.interface_view('notes/test.txt')['content'], 'Neu')
        self.assertTrue(interfaces.interface_delete('notes')['ok'])
        self.assertFalse(interfaces.interface_view('notes')['ok'])
        self.assertTrue(commands.execute_interface({'operation': 'none'})['ok'])

    def test_view_limit_and_directory(self):
        interfaces.interface_create('long.txt', content='a' * (config.MAX_VIEW_CHARS + 1))
        content = interfaces.interface_view('long.txt')['content']
        self.assertEqual(content, 'a' * config.MAX_VIEW_CHARS + '\n...[abgeschnitten]...')
        self.assertEqual(interfaces.interface_view('.')['type'], 'directory')

    def test_execute_success_error_and_limits(self):
        interfaces.interface_create('test.py', content='print("Hallo")')
        result = interfaces.interface_execute('test.py')
        self.assertTrue(result['ok'])
        self.assertEqual(result['stdout'], 'Hallo\n')
        interfaces.interface_edit('test.py', 'raise ValueError("Testfehler")')
        self.assertFalse(interfaces.interface_execute('test.py')['ok'])
        self.assertFalse(interfaces.interface_execute('missing.py')['ok'])
        self.assertFalse(interfaces.interface_execute('.')['ok'])
        interfaces.interface_create('note.txt', content='not python')
        self.assertFalse(interfaces.interface_execute('note.txt')['ok'])
        interfaces.interface_edit('test.py', 'print("x" * 6000)')
        self.assertEqual(interfaces.interface_execute('test.py')['stdout'],
                         'x' * config.MAX_EXECUTION_OUTPUT + '\n...[stdout abgeschnitten]...')
        interfaces.interface_edit('test.py', 'import time; time.sleep(2)')
        with patch.object(interfaces, 'EXECUTION_TIMEOUT', 0.01):
            self.assertIn('beendet', interfaces.interface_execute('test.py')['error'])

    def test_parsing_and_validation(self):
        cmd = {'operation': 'none', 'reason': 'Warten'}
        self.assertEqual(commands.parse_command(json.dumps(cmd)), cmd)
        self.assertEqual(commands.parse_command('```json\n' + json.dumps(cmd) + '\n```'), cmd)
        with self.assertRaises(ValueError):
            commands.parse_command('kein JSON')
        for invalid in ([], {}, {'operation': 'wrong'}, {'operation': 'none'},
                        {'operation': 'view', 'reason': 'test'},
                        {'operation': 'execute', 'path': 'a.txt', 'reason': 'test'},
                        {'operation': 'create', 'path': 'x', 'kind': 'file', 'reason': 'test'},
                        {'operation': 'edit', 'path': 'x', 'content': 5, 'reason': 'test'}):
            with self.subTest(command=invalid):
                self.assertFalse(commands.validate_command(invalid)[0])

    def test_state_and_history(self):
        history = []
        self.assertEqual(state.format_action_history(history), 'Noch keine vorherigen Schritte.')
        for i in range(20):
            state.add_action_history(history, i, {'operation': 'none'}, {'ok': True})
        self.assertEqual(len(history), config.MAX_ACTION_HISTORY)
        self.assertEqual(history[0]['turn'], 8)
        self.assertIn('[FILE] main.py', state.get_world_tree())
        summary = state.world_summary({'ok': True, 'interface': 'create'}, history)
        self.assertIn('WELT VERÄNDERT DURCH LETZTEN SCHRITT:\nJA', summary)

    def test_ollama_payload_and_errors(self):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = b'{"message":{"content":"ok"}}'
        with patch.object(ollama_client.urllib.request, 'urlopen', return_value=response) as urlopen:
            self.assertEqual(ollama_client.ask_genesis([]), 'ok')
            request = urlopen.call_args.args[0]
            payload = json.loads(request.data)
            self.assertEqual(payload['model'], config.MODEL)
            self.assertFalse(payload['stream'])
            self.assertEqual(payload['options']['temperature'], 0.8)
            self.assertEqual(urlopen.call_args.kwargs['timeout'], 120)
            response.__enter__.return_value.read.return_value = b'bad json'
            with self.assertRaisesRegex(RuntimeError, 'gültiges JSON'):
                ollama_client.ask_genesis([])
            response.__enter__.return_value.read.return_value = b'{}'
            with self.assertRaisesRegex(RuntimeError, 'keine Entscheidung'):
                ollama_client.ask_genesis([])


if __name__ == '__main__':
    unittest.main()

