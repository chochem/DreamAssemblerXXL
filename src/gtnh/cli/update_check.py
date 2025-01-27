#!/usr/bin/env python3
import asyncclick as click
import httpx
from colorama import Fore, Style, init
from structlog import get_logger

from gtnh.modpack_manager import GTNHModpackManager

log = get_logger(__name__)

init(autoreset=True)


class NoReleasesException(Exception):
    pass


@click.option("--mods", is_flag=False, metavar="<mods>", type=click.types.STRING)
@click.command()
async def update_check(mods: str | None = None) -> None:
    async with httpx.AsyncClient(http2=True) as client:
        mods_to_update = [m.strip() for m in mods.split(",")] if mods else None
        if mods_to_update:
            log.info(f"Attemting to update mod(s): `{mods_to_update}`")

        m = GTNHModpackManager(client)

        log.info("Grabbing all repository information...")
        # Things get cached here
        await m.get_all_repos()
        log.info("Updating things...")
        await m.update_all(mods_to_update)

        missing_repos = await m.get_missing_repos()
        if len(missing_repos):
            log.info(f"{Fore.RED}****** Missing Mods:{Style.RESET_ALL} {', '.join(sorted(missing_repos))}")

        missing_maven = m.get_missing_mavens()
        if len(missing_maven):
            log.info(f"{Fore.RED}****** Missing Maven:{Style.RESET_ALL} {', '.join(sorted(missing_maven))}")


if __name__ == "__main__":
    update_check()
