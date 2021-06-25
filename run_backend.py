#!/usr/bin/env python3

import sys
import os

usage = 'Usage: run_backend [dev|test] [--remove-prev]'

options = ['--remove-prev']
modes = {
    'test': {
        'database_url': 'postgresql://postgres:postgres@c_postgresdb_test:5433/ariavt',
        'extra_args': [
            '--abort-on-container-exit'
        ],
        'remove_commands': [
            'docker stop c_postgresdb_test',
            'docker rm c_postgresdb_test'
        ]
    },
    'dev': {
        'database_url': 'postgresql://postgres:postgres@c_postgresdb:5432/ariavt',
        'extra_args': [],
        'remove_commands': [
            'docker stop c_postgresdb',
            'docker rm c_postgresdb',
            'docker volume rm postgres-data app-data'
        ]
    }
}

mode = option = database_url = None


def arguments_error(message):
    print('Error: {}'.format(message))
    print(usage)
    exit(1)


num_arguments = len(sys.argv) - 1

# Argument validation
if num_arguments == 0:
    arguments_error('Bad arguments')
elif 2 >= num_arguments >= 1:
    mode = sys.argv[1]
    if mode not in modes:
        arguments_error('Unknown option: {}'.format(mode))
    if num_arguments == 2:
        option = sys.argv[2]
        if option not in options:
            arguments_error('Unknown option: {}'.format(option))
else:
    arguments_error('Bad arguments')


extra_args = ' '.join([str(v) for v in modes[mode]['extra_args']])

for command in modes[mode]['remove_commands']:
    os.system(command)

# Write database URL
os.system(
    'echo "{}" > app/database'
    .format(modes[mode]['database_url'])
)

# Run docker compose
os.system(
    'docker-compose -f backend.{}.yml up \
    --build --force-recreate {}'
    .format(mode, extra_args)
)
