#!/usr/bin/env python
# -*- coding: utf-8 -*-

import attr
import os
import fileinput
import sys
import argparse
import logging
import json
import yaml

import provisioner
from provisioner.commands import commands

logger = logging.getLogger(__name__)

DEF_LOGGING_FORMAT = ("%(asctime)s - %(name)s - %(levelname)s - "
                      "[%(filename)s:%(lineno)d]: %(message)s")
DEF_LOGLEVEL = 'INFO'


AuthArgs = attr.make_class("AuthArgs", ('username', 'password', 'eauth'))
LogArgs = attr.make_class(
    "LogArgs", ('output', 'loglevel', 'logformat', 'logstream', 'logmode')
)


def _reset_logging():
    for handler in logging.root.handlers[:]:
        handler.flush()
        logging.root.removeHandler(handler)
        handler.close()


def _set_logging(
    loglevel=DEF_LOGLEVEL,
    logformat=DEF_LOGGING_FORMAT,
    logstream='stderr',
    logmode='a'
):
    _reset_logging()
    root = logging.getLogger()
    root.setLevel(0)

    if logstream in ('stderr', 'stdout'):
        handler = logging.StreamHandler(getattr(sys, logstream))
    else:  # consider path to file
        handler = logging.FileHandler(logstream, mode=logmode)

    handler.setLevel(loglevel)
    handler.setFormatter(logging.Formatter(logformat))

    root.addHandler(handler)
    # logging.basicConfig(level=DEF_LOGLEVEL, format=DEF_LOGGING_FORMAT)


def _parse_args():
    parser_common = argparse.ArgumentParser(add_help=False)
    parser_common.add_argument(
        "--targets", metavar="STR", default="*",
        help="command's host targets"
    )

    auth_group = parser_common.add_argument_group('authentication')
    auth_group.add_argument(
        "--username", metavar="STR", default=None,
        help="username"
    )
    auth_group.add_argument(
        "--password", metavar="STR", default=None,
        help=(
            "password, '-' means read from stdin. "
            "Another option is to use PRVSNR_PASSWORD env variable"
        )
    )
    auth_group.add_argument(
        "--eauth", default='pam', choices=['pam', 'ldap'],
        help="type of external authentication to use"
    )

    log_group = parser_common.add_argument_group('output & logging')
    log_group.add_argument(
        "--output", default="yaml", choices=['json', 'yaml'],
        help="output format"
    )
    log_group.add_argument(
        "--loglevel", default=DEF_LOGLEVEL,
        choices=['DEBUG', 'INFO', 'WARN', 'ERROR'],
        help="logging level"
    )
    log_group.add_argument(
        "--logformat", default=DEF_LOGGING_FORMAT, metavar='STR',
        help="logging level"
    )
    log_group.add_argument(
        "--logstream", default=None, metavar='STR',
        help=(
            "path to log file, 'stderr' and 'stdout' might be passed "
            "as special values to stream logs to console"
        )
    )
    log_group.add_argument(
        "--logmode", default='a', metavar='STR',
        help="the mode to use to open log files"
    )

    parser = argparse.ArgumentParser(
        description="EOS Provisioner CLI",
        parents=[parser_common],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    subparsers = parser.add_subparsers(
        dest='command',
        title='sub commands',
        description='valid subcommands'
    )

    # TODO description and help strings
    for cmd_name, cmd in commands.items():
        subparser = subparsers.add_parser(
            cmd_name, description='{} configuration'.format(cmd_name),
            help='{} help'.format(cmd_name), parents=[parser_common],
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        cmd.params_type.fill_parser(subparser)

    kwargs = vars(parser.parse_args())
    cmd = kwargs.pop('command')
    if cmd is None:
        raise ValueError('command is required')
    cmd = commands[cmd]
    args = kwargs.pop('args', [])
    return cmd, args, kwargs


def main():
    cmd, args, kwargs = _parse_args()

    auth_args = AuthArgs(
        **{
            k: kwargs.pop(k) for k in list(kwargs)
            if k in attr.fields_dict(AuthArgs)
        }
    )
    log_args = LogArgs(
        **{
            k: kwargs.pop(k) for k in list(kwargs)
            if k in attr.fields_dict(LogArgs)
        }
    )

    if auth_args.password == '-':
        auth_args.password = next(fileinput.input(['-'])).rstrip()
    elif auth_args.password is None:
        auth_args.password = os.environ.get('PRVSNR_PASSWORD')

    if auth_args.username:
        provisioner.auth_init(
            username=auth_args.username,
            password=auth_args.password,
            eauth=auth_args.eauth
        )

    if log_args.logstream:
        _set_logging(
            loglevel=log_args.loglevel,
            logformat=log_args.logformat,
            logstream=log_args.logstream,
            logmode=log_args.logmode,
        )
    logger.debug(
        "Parsed arguments: auth={}, log={}, cmd={}, args={}, kwargs={}"
        .format(auth_args, log_args, cmd, args, kwargs)
    )

    res = cmd.run(*args, **kwargs)

    if res:
        if log_args.output == 'yaml':
            print(yaml.dump(res, default_flow_style=False, canonical=False))
        else:  # json
            print(json.dumps(res, sort_keys=True, indent=4))


if __name__ == "__main__":
    main()
