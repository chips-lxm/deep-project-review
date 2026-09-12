#!/usr/bin/env python3
"""Read-only Codex skills/list probe; never starts a model turn or review."""
import argparse
import json
import queue
import subprocess
import threading
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cwd', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    cwd = str(Path(args.cwd).resolve(strict=True))
    proc = subprocess.Popen(
        ['codex', 'app-server', '--stdio'], cwd=cwd, stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
    )
    replies = queue.Queue()

    def read():
        for line in proc.stdout:
            try:
                replies.put(json.loads(line))
            except json.JSONDecodeError:
                continue

    threading.Thread(target=read, daemon=True).start()

    def send(message):
        proc.stdin.write(json.dumps(message) + '\n')
        proc.stdin.flush()

    def response(request_id):
        import time
        end = time.monotonic() + 20
        while True:
            remaining = end - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('Codex app-server did not respond in 20 seconds')
            try:
                message = replies.get(timeout=remaining)
            except queue.Empty as exc:
                raise TimeoutError('Codex app-server did not respond in 20 seconds') from exc
            if message.get('id') == request_id:
                if 'error' in message:
                    raise RuntimeError(message['error'])
                return message['result']

    try:
        send({'id': 1, 'method': 'initialize', 'params': {
            'clientInfo': {'name': 'deep_project_review_discovery_test', 'version': '1.0'}
        }})
        response(1)
        send({'method': 'initialized'})
        send({'id': 2, 'method': 'skills/list', 'params': {'cwds': [cwd], 'forceReload': True}})
        result = response(2)
        matches = [skill for entry in result['data'] for skill in entry['skills']
                   if skill['name'] == 'deep-project-review']
        errors = [error for entry in result['data'] for error in entry['errors']
                  if 'deep-project-review' in error.get('path', '')]
        evidence = {
            'test': 'Actual local Codex app-server skills/list, no model turn started',
            'cwd': cwd, 'matches': matches, 'errors': errors,
            'limits': 'Discovery only; does not prove invocation routing or effective implicit policy.',
        }
        Path(args.output).write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
        if errors or len(matches) != 1 or not matches[0]['enabled']:
            raise RuntimeError('Expected exactly one enabled skill without loading errors')
        print('PASS: Codex discovered one enabled deep-project-review skill')
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


if __name__ == '__main__':
    main()
