# -*- coding: utf-8 -*-

from openbuild import config
from subprocess import Popen, PIPE, STDOUT
import shutil
import os.path


def prepare(build, buildcfg):
    '''Prepare a Docker container to use for a specific build.

    This command will:

    - Create the Docker container
    - Add the openbuild user
    - Set the Bash environment variables

    :param build: Build for which to prepare
    :param buildcfg: Build configuration to use
    :returns: Output of executed command
    '''
    log = []

    # Prepare checkout
    try:
        os.makedirs(config.builddir)
    except OSError:
        pass
    shutil.copytree(config.repodir, build.path())

    # Start docker container
    runcmd = ['docker', 'run', '-d', '-t', '--name=' + build.name(),
              '--workdir=/openbuild', '-v', build.path() + ':/openbuild',
              buildcfg.get('container', 'fedora'), 'bash']
    p = Popen(runcmd, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if p.returncode:
        raise OSError('command exited abnormally', err.decode('utf-8'))
    log.append(out.decode('utf-8'))

    uid, _ = Popen(['id', '-u'], stdout=PIPE).communicate()
    gid, _ = Popen(['id', '-g'], stdout=PIPE).communicate()
    uid = uid.decode('utf-8')
    gid = gid.decode('utf-8')

    # Create openbuild group
    useradd = ['docker', 'exec', '-i', '-t', build.name(),
               'groupadd', '-g', gid.strip(), 'openbuild']
    p = Popen(useradd, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if p.returncode:
        raise OSError('command exited abnormally', err.decode('utf-8'))
    log.append(out.decode('utf-8'))

    # Create openbuild user
    useradd = ['docker', 'exec', '-i', '-t', build.name(),
               'useradd', '-u', uid.strip(), '-g', gid.strip(),
               '--home=/openbuild', 'openbuild']
    p = Popen(useradd, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if p.returncode:
        raise OSError('command exited abnormally', err.decode('utf-8'))
    log.append(out.decode('utf-8'))

    # Add environment variables
    env = 'BUILDNUMBER=%i\nBUILDTARGET="%s"\nBUILDHASH="%s"'
    env = env % (build.id,
                 build.what.replace('"', r'\"'),
                 build.hash.replace('"', r'\"'))
    log += execute(build, 'echo \'%s\' >> ~/.bashrc' % env)

    return log


def execute(build, cmd):
    '''Execute a given command on the build container.

    :param build: Build to specify the container
    :param cmd: Command to execute
    '''
    log = []

    # Start docker container
    execcmd = ['docker', 'exec', '-i', '-t', '--user=openbuild', build.name(),
               'bash', '-i', '-c', cmd]
    p = Popen(execcmd, stdout=PIPE, stderr=STDOUT)
    out, _ = p.communicate()
    if p.returncode:
        raise OSError('command exited abnormally', out.decode('utf-8'))
    log.append(out.decode('utf-8'))

    return log


def destroy(build):
    '''Destroys the container for a given build.

    :param build: Build to specify the container
    '''
    log = []

    # Start docker container
    rmcmd = ['docker', 'rm', '-f', build.name()]
    p = Popen(rmcmd, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if p.returncode:
        raise OSError('command exited abnormally', err.decode('utf-8'))
    log.append(out.decode('utf-8'))

    # Remove checkout
    shutil.rmtree(build.path())

    return log
