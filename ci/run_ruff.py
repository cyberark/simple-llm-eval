import subprocess


def run_command(cmd, description=None):
    if description:
        print(description)
    try:
        subprocess.run(cmd, shell=True, check=True)
        print()
    except subprocess.CalledProcessError as e:
        print(f'Command failed: {cmd}')
        return e.returncode

def main():
    rc_diff = run_command(cmd='ruff format simpleval --diff', description='Run ruff format diff - fails if changed')

    rc_format = 0
    if rc_diff:
        rc_format = run_command(cmd='ruff format simpleval', description='Run ruff format - update files')

    if rc_diff or rc_format:
        print('Ruff format failed, stopping')
        return 1

    rc_check = run_command(cmd='ruff check simpleval', description='Run ruff check - fails if issues found')
    rc_fix = 0
    if rc_check:
        rc_fix = run_command(cmd='ruff check simpleval --fix', description='Run ruff check --fix - update files')

    if rc_check or rc_fix:
        print('Ruff check failed, stopping')
        return 1

if __name__ == '__main__':
    main()
