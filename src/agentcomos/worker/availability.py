import shutil

def check_hermes_availability() -> tuple[bool, str | None]:
    """Check if the Hermes CLI is available."""
    path = shutil.which("hermes")
    return bool(path), path
