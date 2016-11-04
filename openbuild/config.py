# -*- coding: utf-8 -*-

# Defaults:
builddir = 'data/build'
database = 'sqlite:///data/ci.db'
defaultbuildcfg = 'data/default.ci.yaml'
emailsender = 'no-reply@build.opencast.org'
outputdir = 'data/output/'
repodir = 'data/repository/'


def _module():
    import sys
    return sys.modules[__name__]


def _keys():
    return [i for i in _module().__dict__.keys() if not i.startswith('_')]


def _load():
    import yaml, logging, os
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
            mod[key] = config[key]

_load()
