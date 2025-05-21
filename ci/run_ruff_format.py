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
    rc_diff = run_command(
        cmd='ruff format simpleval --diff',
        description='Run ruff format diff - fails if not formatted correctly'
    )

    rc_format = 0
    if rc_diff:
        rc_format = run_command(
            cmd='ruff format simpleval',
            description='Run ruff format - update files'
        )

    if rc_diff or rc_format:
        print('Ruff format failed, stopping')
        return 1

if __name__ == '__main__':
    main()