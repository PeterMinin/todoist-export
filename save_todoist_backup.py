import datetime
import http.client
import logging
import os
import shutil
import subprocess
import zipfile
from contextlib import contextmanager
from pathlib import Path

# Configuration: logging
LOG_FILE = Path(__file__).with_suffix(".log")  # Next to this .py

log = logging.getLogger("main")


def get_env_var(name):
    try:
        return os.environ[name]
    except KeyError:
        log.error("Please set the %s environment variable", name)
        raise SystemExit(1)


# Configuration: main part
PORT = 3000
NODEJS_SCRIPT = Path(__file__).parent / "src" / "index.js"
TOKEN = get_env_var("TODOIST_TOKEN")
OUTPUT_DIR = Path(get_env_var("TODOIST_BACKUP_DIR"))


@contextmanager
def run_server():
    nodePath = shutil.which("node")
    if not nodePath:
        log.error("'node' not found; Node.JS not installed?")
        raise SystemExit(1)
    if not NODEJS_SCRIPT.is_file():
        log.error("The Todoist export script wasn't found at '%s'", NODEJS_SCRIPT)
        raise SystemExit(1)
    childEnv = os.environ.copy()
    childEnv["PORT"] = str(PORT)
    backgroundProcess = subprocess.Popen(
        [nodePath, NODEJS_SCRIPT],
        creationflags=subprocess.CREATE_NO_WINDOW,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=childEnv,
    )
    try:
        for line in backgroundProcess.stdout:
            log.info("node: %s", line.rstrip("\n"))
            if line.startswith("Server running at"):
                break
        else:
            log.error("Unsuccessful server start")
            raise SystemExit(1)
        yield
    finally:
        if backgroundProcess.poll() is None:
            log.info("Stopping server")
            backgroundProcess.terminate()
            backgroundProcess.wait()


def save_backup():
    if not OUTPUT_DIR.is_dir():
        log.error("No dir '%s'", OUTPUT_DIR)
        raise SystemExit(1)
    datetimeStr = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    outputFile = OUTPUT_DIR / f"todoist_{datetimeStr}.zip"
    with run_server():
        conn = http.client.HTTPConnection("localhost", port=PORT)
        log.info("Requesting export")
        download_url = f"/todoist-export/download?token={TOKEN}&format=json_all"
        conn.request("GET", download_url)
        response = conn.getresponse()
        filename = response.headers.get_filename()
        log.info(f"Saving {filename} to {outputFile}")
        with zipfile.ZipFile(
            outputFile, "x", compression=zipfile.ZIP_DEFLATED
        ) as archive:
            with archive.open(filename, "w") as f:
                while chunk := response.read(1024):
                    f.write(chunk)
    log.info("Done")


def main():
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(levelname)s %(asctime)s : %(message)s",
        encoding="utf-8",
    )
    try:
        save_backup()
    except Exception:
        log.exception("Error")


if __name__ == "__main__":
    main()
