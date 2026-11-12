"""Offline regression for PI requests; never contacts a historian or scans ports."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

SOURCE = Path(__file__).resolve().parents[1] / 'skills/detecting-attacks-on-historian-servers/scripts/agent.py'


class HistorianTLS(unittest.TestCase):
    def test_authenticated_requests_validate_server_certificates(self):
        tree = ast.parse(SOURCE.read_text())
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'check_pi_web_api')
        get = Mock(return_value=SimpleNamespace(status_code=200, json=lambda: {'Items': []}))
        namespace = {'requests': SimpleNamespace(get=get, exceptions=SimpleNamespace(ConnectionError=ConnectionError))}
        exec(compile(ast.Module(body=[function], type_ignores=[]), str(SOURCE), 'exec'), namespace)
        result = namespace['check_pi_web_api']('historian.invalid', 'synthetic-user', 'synthetic-password')
        self.assertEqual(get.call_count, 2)
        self.assertEqual(result['exposed_points'], 0)
        for call in get.call_args_list:
            self.assertTrue(call.kwargs.get('verify', True))
            self.assertEqual(call.kwargs['timeout'], 10)
            self.assertEqual(call.kwargs['auth'], ('synthetic-user', 'synthetic-password'))


if __name__ == '__main__':
    unittest.main()
