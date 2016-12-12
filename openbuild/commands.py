# -*- coding: utf-8 -*-

from openbuild import config, docker, git
from openbuild.db import get_session, Build
from sqlalchemy.exc import IntegrityError
from subprocess import Popen, PIPE
import smtplib
import yaml
import glob
import shutil
import os
import logging


def getcfg():
    '''Load the build configuration from disk.
    Try loading the configuration from the repository first. If there is none,
    use the default configuration instead.
    '''
    try:
        with open(os.path.join(config.repodir, '.ci.yaml')) as f:
            data = yaml.load(f)
    except IOError:
        with open(config.defaultbuildcfg) as f:
            data = yaml.load(f)
    return data


def getauthoremail():
    '''Get mail address of the author of the last commit
    '''
    out, _ = git.log(['--pretty=%aE', '-n1'])
    return out.strip()


def add(rev):
    '''Add a new build to the queue.

    :param rev: Git revision to build
    '''
    hash = git.hash(rev)
    db = get_session()
    db.add(Build(what=rev, hash=hash))
    db.commit()
    return 'Added build %s' % hash


def listbuilds(state):
    '''Return a list of schedules builds

    :param state: Return builds in a given state only
    :returns: List of all builds as string
    '''
    q = get_session().query(Build)
    if state:
        q = q.filter(Build.state == state)
    result = ''
    for build in q:
        result += '%4i  %s  %8s  %s\n' % \
                (build.id, build.hash, build.state, build.what)
    return result.rstrip()


def nextbuild():
    '''Returns the next build in line to ru
    n'''
    db = get_session()

    # Get no build if a build is already running
    q = db.query(Build).filter(Build.active)
    if q.count():
        logging.info('Build already running')
        return

    # get next wainting build
    q = db.query(Build).filter(Build.state == 'waiting')\
          .order_by(Build.id.asc()).limit(1)
    if q.count():
        logging.info('Next build: ' + q[0].what)
        return q[0]


def publish(build, buildcfg, log):
    '''Publish files from build to output directory.

    :param build: Build to publish
    :param buildcfg: Build specific configuration
    :param log: Build log to publish
    '''
    # Create output dir
    dirname = '%05i-%s-%s' % (build.id,
                              build.created.strftime('%Y%m%d%H%M%S'),
                              build.hash)
    path = os.path.join(config.outputdir, dirname)
    os.makedirs(path)

    # Save log file
    with open(os.path.join(path, 'build.log'), 'w') as f:
        f.write(u'\n'.join(log))

    # Copy files
    for file_glob in buildcfg.get('files', []):
        for f in glob.glob(os.path.join(build.path(), file_glob)):
            shutil.copy(f, path)

    # Add a shortlink
    linkname = build.what.replace('/', '')
    try:
        os.unlink(os.path.join(config.outputdir, linkname))
    except OSError:
        pass
    os.symlink(os.path.abspath(path), os.path.join(config.outputdir, linkname))

    # Run global commands
    if buildcfg.get('createrepo'):
        p = Popen(['createrepo', config.outputdir], stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if p.returncode:
        raise OSError('command exited abnormally', err.decode('utf-8'))


def run():
    '''Run the next build.
    '''
    build = nextbuild()
    if not build:
        return

    db = get_session()
    query = db.query(Build).filter(Build.id == build.id)

    # Set build to running
    try:
        query.update({'active': True, 'state': u'running'})
        db.commit()
        logging.info('Starting build ' + build.what)
    except IntegrityError:
        # There is a build going on already
        return

    # Log the output
    log = []
    finished = False

    try:
        logging.info('Cleaning git repository')
        git.clean()

        logging.info('Checking out git commit ' + build.hash)
        log.append('Checking out git commit ' + build.hash)
        git.checkout(build.hash)

        logging.info('Reading configuration')
        log.append('Reading configuration')
        buildcfg = getcfg()

        log += docker.prepare(build, buildcfg)

        # Run build script
        for cmd in buildcfg.get('script', []):
            logging.info('Running: ' + cmd)
            log.append(cmd)
            log += docker.execute(build, cmd)

        publish(build, buildcfg, log)
        docker.destroy(build)

        '''
        # Send success mail
        for emailaddr in config.emailreceiver:
            try_email(emailaddr, 'SWITCHCast Build Success',
                      'http://prunus.switch.ch/builds/%05i-%s-%s/' %
                      (build.id, build.created.strftime('%Y%m%d%H%M%S'),
                          build.hash))
        '''
        finished = True
    except:
        logging.error(u'\n'.join(log))
        raise
    finally:
        if finished:
            query.update({'state': u'success', 'active': None})
        else:
            query.update({'state': u'failed', 'active': None})
        db.commit()

        '''
        # Send failure mail
        for emailaddr in config.emailreceiver:
            try_email(emailaddr, 'SWITCHCast Build Failure',
                      'http://prunus.switch.ch/builds/%05i-%s-%s/' %
                      (build.id, build.created.strftime('%Y%m%d%H%M%S'),
                          build.hash))
        '''


def try_email(h_to, h_subject, body, h_from=config.emailsender):
    header = 'From: %s\n' % h_from
    header += 'To: %s\n' % h_to
    header += 'Subject: %s\n\n' % h_subject
    message = header + body

    try:
        server = smtplib.SMTP('localhost')
        server.sendmail(h_from, h_to, message)
        server.quit()
    except smtplib.SMTPSenderRefused:
        pass
