import shlex

commands = {
  'start a new git repo': 'git init',
  'add everything': 'git add .',
  'check status': 'git status',
  'commit with message': lambda args: ['git', 'commit', '-m', shlex.quote(args)],
  'push changes': 'git push',
  'pull latest changes': 'git pull',
  # ... add more mappings as needed
}
