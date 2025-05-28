import subprocess
from colorama import Fore


def run_cmd(cmd, do_not_fail=False, error=''):
    print(f"{Fore.CYAN}$ {' '.join(cmd)}{Fore.RESET}")
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    print(result.stdout)
    if not do_not_fail and result.returncode != 0:
        raise RuntimeError(f'{result.stderr} | {error}')
    return result
