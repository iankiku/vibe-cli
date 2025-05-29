import shlex

commands = {
  'create a node project': 'npm init -y',
  'add': lambda args: ['npm', 'install', shlex.quote(args)],
  'remove': lambda args: ['npm', 'uninstall', shlex.quote(args)],
  'run': lambda args: ['npm', 'run', shlex.quote(args)],
  'check updates': 'npm outdated',
}
