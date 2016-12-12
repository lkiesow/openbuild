Openbuild
=========

Openbuild is a build server for git repositories it allows automatic execution
of arbitrary build commands like Travis but is completely build around using
docker container.


Getting started
---------------

1. Install necessary requirements and ensure the Openbuild user may use them:
    - Docker
    - Git
    - Python

2. Clone the repository you want to build:

        cd data
        git clone https://… repository

3. Add the first build:

        ./openbuild-add origin/master

4. Check if the build is in queue:

        ./openbuild-list

5. Run the build:

        ./openbuild-run


SELinux
-------

If you are running SELinux, it may prevent Docker from accessing data on its
host machine unless specifically tagged as content for the virtual environment.

That is why you need to mark the Git repository and build directory as such
content. You can do that by running:

    chcon -Rt svirt_sandbox_file_t …/data/repository
    chcon -Rt svirt_sandbox_file_t …/data/build


Global Configuration
--------------------

Openbuild will try to load the configuration files in the following order:

    localconf = ./etc/openbuild.yaml
    globalcfg = /etc/openbuild/openbuild.yaml

Note that only one file may be loaded. If configuration keys are not specified,
defaults will be used.


Build Configuration
-------------------

Openbuild will try to load the build instructions from a file `.ci.yaml` in the
root of the Git repository. If no such file exists, the global build
instructions are used if specified.

Example configuration:

    container: lkiesow/testcontainer

    script:
        - python setup.py sdist

    files:
        - dist/test-*.tar.gz


Possible keys to use:

- `container` specifies a Docker container to use for the build.
- `script` specifies a command or a list of commands to use when building the
  project.
- `files` specifies the files to copy to the output directory after a build has
  successfully finished.
- `createrepo` specifies if createrepo should be executed after a build has been
  published.
