import os
import sys
import urllib.request


def launch_terminal(username: str = None, passwd: str = None, use_bundle: bool = False):

    cmd = 'java -jar ThetaTerminal.jar'

    if use_bundle:
        jre = os.path.join(str(sys.path[1]), 'resources', 'corretto-11.0.16.1-win', 'bin', 'java')
        jar = os.path.join(str(sys.path[1]), 'resources', 'ThetaTerminal.jar')
        cmd = jre + ' -jar ' + jar

    if username is None or passwd is None:
        os.system(cmd)
    else:
        os.system(cmd + ' ' + username + ' ' + passwd)


def check_download(auto_update: bool):
    if os.path.exists('ThetaTerminal.jar') or auto_update:
        jar = urllib.request.urlopen("https://download-latest.thetadata.us")
        with open('ThetaTerminal.jar', 'wb') as output:
            output.write(jar.read())
            output.close()


