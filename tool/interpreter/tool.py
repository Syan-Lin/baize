import subprocess
def exec_code(code: str) -> dict:
    result = subprocess.run(['python', '-c', code], capture_output=True, text=True)
    return {
        'stdout': result.stdout,
        'stderr': result.stderr
    }