# -*- coding: utf-8 -*-

# Defaults:
builddir = 'data/build'
database = 'sqlite:///data/ci.db'
defaultbuildcfg = 'data/default.ci.yaml'
emailsender = 'no-reply@build.opencast.org'
outputdir = 'data/output/'
repodir = 'data/repository/'


def _module():
    '''Return active config module
    '''
    import sys
    return sys.modules[__name__]


def _keys():
    '''Get all public methods/properties of the configuration module
    '''
    return [i for i in _module().__dict__.keys() if not i.startswith('_')]


def _load():
    '''Load configuration from file.
    '''
    import yaml
    import logging
    import os
    globalcfg = '/etc/openbuild/openbuild.yaml'
    localconf = './etc/openbuild.yaml'
    cfg = localconf if os.path.isfile(localconf) else globalcfg
    if not os.path.isfile(cfg):
        return
    logging.debug('Loading configuration from ' + cfg)
    with open(cfg, 'r') as f:
        config = yaml.load(f) or {}
    mod = _module()
    for key in _keys():
        if key in config:
            setattr(mod, key, config[key])


_load()
