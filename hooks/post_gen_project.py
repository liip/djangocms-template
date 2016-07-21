#!/usr/bin/env python

import os
import subprocess


def install_drifter():
    os.system('git init .')
    os.system('curl -sS https://raw.githubusercontent.com/liip/drifter/master/install.sh | /bin/bash')


def set_parameter(path, key, value):
    patched_lines = []
    parameter_exists = False

    with open(path) as f:
        lines = f.readlines()

    for line in lines:
        if line.startswith('{}:'.format(key)):
            line = '{key}: "{value}"\n'.format(key=key, value=value)
            parameter_exists = True
        patched_lines.append(line)

    if not parameter_exists:
        patched_lines.append('{key}: "{value}"\n'.format(key=key, value=value))

    with open(path, 'w') as f:
        f.write(''.join(patched_lines))


def patch_parameters(path):
    set_parameter(path, 'django_pip_requirements', 'requirements/dev.txt')
    set_parameter(path, 'project_name', '{{ cookiecutter.project_slug }}')
    set_parameter(path, 'database_name', '{{ cookiecutter.project_slug }}')
    set_parameter(path, 'hostname', "{{ cookiecutter.project_slug.replace('_', '-') }}.lo")
    set_parameter(path, 'python_version', '3')


def patch_playbook(path):
    patched_lines = []

    with open(path) as f:
        lines = f.readlines()

    for line in lines:
        if 'role: django' in line or 'role: postgresql' in line:
            line = line.replace('# -', '-')

        patched_lines.append(line)

    with open(path, 'w') as f:
        f.write(''.join(patched_lines))


def install_kanbasu():
    base_directory = 'static/sass'
    base_kanbasu_directory = 'vendors/kanbasu'
    kanbasu_directory = '%s/src/assets/scss' % base_kanbasu_directory

    os.system('git submodule add git@github.com:liip/kanbasu.git %s/%s' % (base_directory, base_kanbasu_directory))

    main_file_path = '%s/kanbasu.scss' % base_directory
    os.system('cp %s/%s/kanbasu.scss %s' % (base_directory, kanbasu_directory, main_file_path))
    os.system('echo "@import \'kanbasu\';\n" > static/sass/main.scss')
    patch_kanbasu(main_file_path, kanbasu_directory)

    settings_directory = '%s/settings' % base_directory
    os.system('mkdir -p %s' % settings_directory)
    os.system('cp %s/%s/settings/_settings.scss %s/_kanbasu.scss' % (base_directory, kanbasu_directory, settings_directory))


def patch_kanbasu(path, kanbasu_directory):
    patched_lines = []

    with open(path) as f:
        lines = f.readlines()

    for line in lines:
        if '@import' in line and not 'settings/settings' in line:
            line = line.replace("@import '", "@import '%s/" % kanbasu_directory)

        patched_lines.append(line)

    with open(path, 'w') as f:
        f.write(''.join(patched_lines))


def pip_compile(path):
    with open('/dev/null', 'wb') as f:
        subprocess.call(['pip-compile', path], stdout=f)


if __name__ == '__main__':
    use_drifter = '{{ cookiecutter.use_drifter }}' == 'y'
    use_kanbasu = '{{ cookiecutter.use_kanbasu }}' == 'y'

    if use_drifter:
        install_drifter()
        patch_parameters('virtualization/parameters.yml')
        patch_playbook('virtualization/playbook.yml')

    if use_kanbasu:
        install_kanbasu()

    pip_compile('requirements/dev.in')
    pip_compile('requirements/base.in')
    pip_compile('requirements/deploy.in')
