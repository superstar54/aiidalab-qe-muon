from aiida.common.exceptions import NotExistent
from subprocess import run
from aiida.orm import load_code
from aiida import load_profile
from pathlib import Path


QE_VERSION = "7.2"

CONDA_ENV_PREFIX = Path.home().joinpath(
    ".conda", "envs", f"quantum-espresso-{QE_VERSION}"
)

def InstallCodes(code_name="pp", computer_name="localhost"):
    load_profile()
    try:
        load_code(f"{code_name}-{QE_VERSION}@{computer_name}")
    except NotExistent:
        run(
            [
                "verdi",
                "code",
                "create",
                "core.code.installed",
                "--non-interactive",
                "--label",
                f"{code_name}-{QE_VERSION}",
                "--description",
                f"{code_name}.x ({QE_VERSION}) setup by AiiDAlab.",
                "--default-calc-job-plugin",
                f"quantumespresso.{code_name}",
                "--computer",
                computer_name,
                "--prepend-text",
                f'eval "$(conda shell.posix hook)"\nconda activate {CONDA_ENV_PREFIX}\nexport OMP_NUM_THREADS=1',
                "--filepath-executable",
                CONDA_ENV_PREFIX.joinpath("bin", f"{code_name}.x"),
            ],
            check=True,
            capture_output=True,
        )
    else:
        raise ValueError(f"Code {code_name}-{QE_VERSION}@{computer_name} already set up")

if __name__ == "__main__":
    InstallCodes(code_name="pp")