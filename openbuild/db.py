# -*- coding: utf-8 -*-
'''
Database specification
'''

import config
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Boolean, Integer, Text, DateTime, create_engine
from sqlalchemy.orm import sessionmaker
import os.path

# Set default encoding to UTF-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

Base = declarative_base()


def init():
    '''Initialize connection to database and create database structure if
    non-existent.
    '''
    global engine
    engine = create_engine(config.database)
    Base.metadata.create_all(engine)


def get_session():
    '''Get a session for database communication. If necessary a new connection
    to the database will be established.

    :return:  Database session
    '''
    if 'engine' not in globals():
        init()
    Session = sessionmaker(bind=engine)
    return Session()


# Database Schema Definition
class Build(Base):
    '''Database definition for builds.'''

    __tablename__ = 'build'

    id = Column('id', Integer(), autoincrement='ignore_fk',
                primary_key=True)
    state = Column('state', Text(), nullable=False, default='waiting')
    hash = Column('hash', Text(), nullable=False)
    what = Column('what', Text(), nullable=False)
    created = Column('created', DateTime(), nullable=False,
                     default=datetime.today())
    active = Column('active', Boolean(), nullable=True, unique=True)

    def name(self):
        return 'openbuild-%06i' % self.id

    def path(self):
        return os.path.abspath(os.path.join(config.builddir, self.name()))

    def __repr__(self):
        '''Return a string representation of this object.

        :return: String representation of object.
        '''
        return '<ID=%i, hash=%s)>' % (self.id, self.hash)

    def serialize(self, expand=0):
        '''Serialize this object as dictionary usable for conversion to JSON.

        :param expand: Defines if sub objects shall be serialized as well.
        :return: Dictionary representing this object.
        '''
        return {
            'id': self.id,
            'hash': self.hash,
            'what': self.what,
            'created': self.created
            }
