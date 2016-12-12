# -*- coding: utf-8 -*-

import subprocess
from openbuild import config


def fetch():
    '''Fetch from remote git repository'''

    p = subprocess.Popen(['git', 'fetch'], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, cwd=config.repodir)
    out, err = p.communicate()
    if p.returncode:
        raise OSError('git rev-parse exited abnormally', err)
    return out.decode('utf-8'), err.decode('utf-8')


def log(args=[]):
    '''Run `git log` with the given arguments
    '''
    p = subprocess.Popen(['git', 'log'] + (args or []),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         cwd=config.repodir)
    out, err = p.communicate()
    if p.returncode:
        raise OSError('git log exited abnormally', err)
    return out.decode('utf-8'), err.decode('utf-8')


def checkout(rev):
    '''Check out a specific git rebision
    '''
    p = subprocess.Popen(['git', 'checkout', rev],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         cwd=config.repodir)
    out, err = p.communicate()
    if p.returncode:
        raise OSError('Could not check out commit hash', err)
    return out.decode('utf-8'), err.decode('utf-8')


def clean():
    '''Force a clean-up of the git repository, ignoring the .gitignore file..
    '''
    p = subprocess.Popen(['git', 'clean', '-fdx'], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, cwd=config.repodir)
    out, err = p.communicate()
    if p.returncode:
        raise OSError('Could not check out commit hash', err)
    return out.decode('utf-8'), err.decode('utf-8')


def hash(rev):
    '''Resolve the git hash for a specific revision.

    :param rev: Git revision
    :returns: Git hash
    '''
    fetch()

    # Get build hash
    p = subprocess.Popen(['git', 'rev-parse', rev], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, cwd=config.repodir)
    out, err = p.communicate()
    if p.returncode:
        raise OSError('git rev-parse exited abnormally', err)
    return out.decode('utf-8').strip()
