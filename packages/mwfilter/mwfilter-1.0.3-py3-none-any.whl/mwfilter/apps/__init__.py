# -*- coding: utf-8 -*-

from argparse import Namespace
from asyncio.exceptions import CancelledError
from functools import lru_cache
from typing import Callable, Dict

from mwfilter.apps.build import build_main
from mwfilter.apps.clear import clear_main
from mwfilter.apps.down import down_main
from mwfilter.apps.exclude import exclude_main
from mwfilter.apps.index import index_main
from mwfilter.apps.nav import nav_main
from mwfilter.arguments import (
    CMD_BUILD,
    CMD_CLEAN,
    CMD_DOWN,
    CMD_EXCLUDE,
    CMD_INDEX,
    CMD_NAV,
)
from mwfilter.logging.logging import logger


@lru_cache
def cmd_apps() -> Dict[str, Callable[[Namespace], None]]:
    return {
        CMD_BUILD: build_main,
        CMD_CLEAN: clear_main,
        CMD_DOWN: down_main,
        CMD_EXCLUDE: exclude_main,
        CMD_INDEX: index_main,
        CMD_NAV: nav_main,
    }


def run_app(cmd: str, args: Namespace) -> int:
    apps = cmd_apps()

    app = apps.get(cmd, None)
    if app is None:
        logger.error(f"Unknown app command: {cmd}")
        return 1

    try:
        app(args)
    except CancelledError:
        logger.debug("An cancelled signal was detected")
    except (KeyboardInterrupt, InterruptedError):
        logger.warning("An interrupt signal was detected")
    except SystemExit as e:
        assert isinstance(e.code, int)
        if e.code != 0:
            logger.warning(f"A system shutdown has been detected ({e.code})")
        return e.code
    except BaseException as e:
        logger.exception(e)
        return 1

    return 0
