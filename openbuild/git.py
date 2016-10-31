# -*- coding: utf-8 -*-

import subprocess
import config


def fetch():
    '''Fetch from remote git'''

    p = subprocess.Popen(['git', 'fetch'], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, cwd=config.repodir)
    out, err = p.communicate()
    if p.returncode:
        raise OSError('git rev-parse exited abnormally', err)
    return out, err


def log(args=[]):
    # Fetch from remote git
    p = subprocess.Popen(['git', 'log'] + (args or []),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         cwd=config.repodir)
    out, err = p.communicate()
    if p.returncode:
        raise OSError('git log exited abnormally', err)
    return out, err


def checkout(rev):
    # Check out git commit
    p = subprocess.Popen(['git', 'checkout', rev],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         cwd=config.repodir)
    out, err = p.communicate()
    if p.returncode:
        raise OSError('Could not check out commit hash', err)
    return out, err


def clean():
    # Check out git commit
    p = subprocess.Popen(['git', 'clean', '-fdx'], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, cwd=config.repodir)
    out, err = p.communicate()
    if p.returncode:
        raise OSError('Could not check out commit hash', err)
    return out, err
