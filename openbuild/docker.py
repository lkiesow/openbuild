# -*- coding: utf-8 -*-

import config
from subprocess import Popen, PIPE
import shutil
import os.path


def prepare(build, buildcfg):
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
        raise OSError('command exited abnormally', err)
    log.append(out)

    uid, _ = Popen(['id', '-u'], stdout=PIPE).communicate()
    gid, _ = Popen(['id', '-g'], stdout=PIPE).communicate()

    # Create openbuild group
    useradd = ['docker', 'exec', '-i', '-t', build.name(),
               'groupadd', '-g', gid, 'openbuild']
    p = Popen(useradd, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if p.returncode:
        raise OSError('command exited abnormally', err)
    log.append(out)

    # Create openbuild user
    useradd = ['docker', 'exec', '-i', '-t', build.name(),
               'useradd', '-u', uid, '-g', gid, '--home=/openbuild', 'openbuild']
    p = Popen(useradd, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if p.returncode:
        raise OSError('command exited abnormally', err)
    log.append(out)

    return log


def execute(build, cmd):
    log = []

    # Start docker container
    execcmd = ['docker', 'exec', '-i', '-t', '--user=openbuild', build.name(),
               'bash', '-c', cmd]
    p = Popen(execcmd, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if p.returncode:
        raise OSError('command exited abnormally', err)
    log.append(out)

    return log


def destroy(build):
    log = []

    # Start docker container
    rmcmd = ['docker', 'rm', '-f', build.name()]
    p = Popen(rmcmd, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if p.returncode:
        raise OSError('command exited abnormally', err)
    log.append(out)

    # Remove checkout
    shutil.rmtree(build.path())

    return log
