import os
import platform
import shutil
import signal
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

import psutil
import wget

jdk_path = Path.home().joinpath('ThetaData').joinpath('ThetaTerminal') \
    .joinpath('jdk-19.0.1').joinpath('bin')

to_extract = Path.home().joinpath('ThetaData').joinpath('ThetaTerminal')

_thetadata_jar = "ThetaTerminal.jar"


def bar_progress(current, total, width=80):
    progress_message = "Downloading open-jdk 19.0.1  -->  %d%% Complete" % (current / total * 100)
    sys.stdout.write("\r" + progress_message)
    sys.stdout.flush()


def _install_jdk() -> bool:
    url_windows = 'https://download.java.net/java/GA/jdk19.0.1/afdd2e245b014143b62ccb916125e3ce/10/GPL/openjdk-19.0.1_windows-x64_bin.zip'
    if jdk_path.exists():
        return True
    try:
        if platform.system() == 'Windows':
            print('--------------------------------------------------------------\n')
            print('Initiated first time setup, do not terminate the program!')
            print('\n--------------------------------------------------------------')
            download = wget.download(url_windows, bar=bar_progress)

            with zipfile.ZipFile(download, 'r') as zip_ref:
                zip_ref.extractall(to_extract)
            os.remove(download)
            print()
            return True
    except:
        pass
    return False


def _verify_java():
    if not shutil.which("java"):
        print('Java 11 or higher is required to use this API. Please install Java on this machine.')
        exit(1)
    # version = subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT)
    # pattern = r'\"(\d+\.\d+).*\"'
    # version = float(re.search(pattern, version.decode('utf8')).groups()[0])

    # if version < 11:
    #    print('Java 11 or higher is required to use this API. You are using Java '
    #          + str(version) + '. Please upgrade to a newer version.')
    #    exit(1)


def launch_terminal(username: str = None, passwd: str = None, use_bundle: bool = True, jvm_mem: int = 0, move_jar: bool = True):
    cwd = None
    use_it = False

    if use_bundle:
        use_it = _install_jdk()

    if use_it:
        cwd = jdk_path
        if move_jar:
            shutil.move("ThetaTerminal.jar", str(cwd.joinpath('ThetaTerminal.jar')))
    else:
        _verify_java()

    if jvm_mem > 0:
        if os.name != 'nt':
            process = subprocess.Popen([f"java -Xmx{jvm_mem}G -jar ThetaTerminal.jar {username} {passwd}"],
                                       stdout=subprocess.PIPE, shell=True)
        else:
            process = subprocess.Popen(["java", f"-Xmx{jvm_mem}G", "-jar", "ThetaTerminal.jar", username, passwd],
                                       stdout=subprocess.PIPE, shell=True, cwd=cwd)
    else:
        if os.name != 'nt':
            process = subprocess.Popen([f"java -jar ThetaTerminal.jar {username} {passwd}"],
                                       stdout=subprocess.PIPE, shell=True)
        else:
            process = subprocess.Popen(["java", "-jar", "ThetaTerminal.jar", username, passwd],
                                       stdout=subprocess.PIPE, shell=True, cwd=cwd)
    for line in process.stdout:
        print(line.decode('utf-8').rstrip("\n"))


def check_download(auto_update: bool) -> bool:
    try:
        if os.path.exists('ThetaTerminal.jar') or auto_update:
            jar = urllib.request.urlopen("https://download-latest.thetadata.us")
            with open('ThetaTerminal.jar', 'wb') as output:
                output.write(jar.read())
                output.close()
        return True
    except:
        print('Unable to fetch the latest terminal version.')
    return False


def kill_existing_terminal() -> None:
    """
    Utility function to kill any ThetaData terminal processes by scanning all running proceeses
    and killing such process
    """
    for pid in psutil.pids():
        try:
            cmdline_args = psutil.Process(pid=pid).cmdline()
            for arg in cmdline_args:
                if _thetadata_jar in arg:
                    os.kill(pid, signal.SIGTERM)
        except:
            pass


def is_terminal_instance_running() -> bool:
    """
    Checks if thetadata terminal is running or not
    Returns:
        bool: True if running else False
    """
    running = False
    for pid in psutil.pids():
        try:
            cmdline_args = psutil.Process(pid=pid).cmdline()
            for arg in cmdline_args:
                if _thetadata_jar in arg:
                    running = True
                    break
        except:
            pass
    return running

