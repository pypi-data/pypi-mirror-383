import os

env = os.environ.copy()

VAR_WORKING_DIRECTORY = 'EMCP_WORKING_DIRECTORY'
VAR_SHELL_WHITELIST = 'EMCP_SHELL_ALLOW_ONLY'

# Working directory:
wd = env.get(VAR_WORKING_DIRECTORY) or os.getcwd()

# Shell restrictions:
shell_whitelist = (
    set(name.strip() for name in env.get(VAR_SHELL_WHITELIST, '').split(',') if name.strip())
    if VAR_SHELL_WHITELIST in env
    else None
)
