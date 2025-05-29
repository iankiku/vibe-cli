import os
import shlex

commands = {
  'run': lambda args: ['python', shlex.quote(args)],
  'make env': 'python -m venv venv',
  'activate env': 'source venv/bin/activate' if os.name != 'nt' else r'venv\Scripts\activate',
  'install': lambda args: ['pip', 'install', shlex.quote(args)],
  'freeze requirements': 'pip freeze > requirements.txt',
}
