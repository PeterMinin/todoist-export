import datetime
import http.client
import logging
import os
import shutil
import subprocess
import zipfile
from pathlib import Path

# Configuration
PORT = 3000
OUTPUT_DIR = Path(R"C:\Backups")
LOG_FILE = Path(__file__).with_suffix(".log")

DOWNLOAD_URL_TEMPLATE = "/todoist-export/download?token={AUTH_TOKEN}&format=json_all"

log = logging.getLogger("main")


def save_backup():
    try:
        token = os.environ["TODOIST_TOKEN"]
    except KeyError:
        log.error("Please set the TODOIST_TOKEN environment variable")
        raise SystemExit(1)
    if not OUTPUT_DIR.is_dir():
        log.error("No dir '%s'", OUTPUT_DIR)
        raise SystemExit(1)
    datetimeStr = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    outputFile = OUTPUT_DIR / f"todoist_{datetimeStr}.zip"
    nodePath = shutil.which("node")
    if not nodePath:
        log.error("'node' not found; Node.JS not installed?")
        raise SystemExit(1)
    indexPath = Path(__file__).parent / "src" / "index.js"
    assert indexPath.is_file()
    childEnv = os.environ.copy()
    childEnv["PORT"] = str(PORT)
    backgroundProcess = subprocess.Popen(
        [nodePath, indexPath],
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
        conn = http.client.HTTPConnection("localhost", port=PORT)
        log.info("Requesting export")
        conn.request("GET", DOWNLOAD_URL_TEMPLATE.format(AUTH_TOKEN=token))
        response = conn.getresponse()
        filename = response.headers.get_filename()
        log.info(f"Saving {filename} to {outputFile}")
        with zipfile.ZipFile(
            outputFile, "x", compression=zipfile.ZIP_DEFLATED
        ) as archive:
            with archive.open(filename, "w") as f:
                while chunk := response.read(1024):
                    f.write(chunk)
    finally:
        if backgroundProcess.poll() is None:
            log.info("Stopping server")
            backgroundProcess.terminate()
            backgroundProcess.wait()
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
