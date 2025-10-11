import asyncio
import csv
import json
import logging
import os
import urllib
import xml.etree.ElementTree as ET
from contextlib import asynccontextmanager
from copy import copy
from typing import Final

import aiohttp
import click
from pymongo import MongoClient
import wool

from dcc2cvh.mongo import PIPELINE


BATCH_SIZE: Final = 25
POOL_BREADTH: Final = 1

__client__ = None

logging.basicConfig(level=logging.INFO)


# import signal


# def sigint_handler(signum, frame):
#     pass


# old_sigint = signal.signal(signal.SIGINT, sigint_handler)


class TTLSemaphore(asyncio.BoundedSemaphore):
    def __init__(self, limit: int, interval: float):
        super().__init__(limit)
        self._interval = interval

    async def __aexit__(self, *args, **kwargs):
        pass

    async def acquire(self):
        await super().acquire()
        asyncio.get_event_loop().call_later(self._interval, self.release)
        return True


_request_semaphore = TTLSemaphore(50, 1)


@wool.routine
async def _acquire_request_semaphore():
    return await _request_semaphore.acquire()


@asynccontextmanager
async def rate_limit():
    await _acquire_request_semaphore()
    yield


def debug(ctx, param, value):
    """
    Enable debugging with debugpy.

    Args:
        ctx (click.Context): Click context.
        param (click.Parameter): Click parameter.
        value (bool): Flag value indicating whether to enable debugging.
    """
    if not value or ctx.resilient_parsing:
        return

    import debugpy

    debugpy.listen(5678)
    logging.debug("Waiting for debugger to attach...")
    debugpy.wait_for_client()
    logging.debug("Debugger attached")


def get_client(port=27017):
    global __client__
    if not __client__:
        __client__ = MongoClient(f"mongodb://localhost:{port}/")
    return __client__


@click.group()
def cli(): ...


@cli.group("c2m2")
def c2m2(): ...


@c2m2.command("load-dataset")
@click.argument(
    "directory",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
)
@click.option(
    "--debug",
    "-d",
    callback=debug,
    expose_value=False,
    help="Run with debugger listening on the specified port. Execution will block until the debugger is attached.",
    is_eager=True,
    type=int,
)
def load_c2m2_dataset(directory: os.PathLike):
    """
    Reads and processes a CFDE datapackage.

    This command processes all `.csv` and `.tsv` files in the specified directory,
    reads their contents, and pushes the data to a MongoDB database.

    DIRECTORY is the path to the directory containing the CFDE datapackage.
    """
    asyncio.get_event_loop().run_until_complete(_load_c2m2_dataset(directory))


async def _load_c2m2_dataset(directory: os.PathLike):
    logging.debug(f"Loading directory: {directory}")
    async with wool.WorkerPool(size=POOL_BREADTH):
        try:
            tasks = []
            for filename in os.listdir(directory):
                if filename.endswith(".csv") or filename.endswith(".tsv"):
                    delimiter = "," if filename.endswith(".csv") else "\t"
                    filepath = os.path.join(directory, filename)
                    tasks.append(asyncio.create_task(persist(filepath, delimiter)))
            results = await asyncio.gather(*tasks, return_exceptions=True)

            return results
        except KeyboardInterrupt:
            logging.info("unlinking shared memory")
            raise


@wool.routine
async def persist(filepath, delimiter):
    try:
        logging.debug(f"Reading file: {filepath}")
        count = 0
        with open(filepath, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file, delimiter=delimiter)
            *_, directory, filename = os.path.split(filepath)
            directory = os.path.basename(directory)
            table, _ = os.path.splitext(filename)
            logging.debug(f"Persisting table: {table}")
            batch = []
            metadata = []
            tasks = []
            for row in reader:
                count += 1
                record = {**row, "submission": directory, "table": table}
                batch.append(record)
                if table == "file" and record["access_url"]:
                    metadata_task = asyncio.create_task(
                        get_file_metadata(record["access_url"])
                    )
                    metadata.append(metadata_task)
                if len(batch) >= BATCH_SIZE:
                    tasks.append(
                        asyncio.create_task(
                            flush(
                                "c2m2-2",
                                table,
                                copy(batch),
                                [await m for m in metadata],
                            )
                        )
                    )
                    batch.clear()
                    metadata.clear()
                if len(tasks) >= POOL_BREADTH * 10:
                    await asyncio.gather(*tasks)
                    tasks.clear()
            if batch:
                tasks.append(
                    asyncio.create_task(
                        flush("c2m2-2", table, copy(batch), [await m for m in metadata])
                    )
                )
                metadata.clear()
                batch.clear()
            if tasks:
                await asyncio.gather(*tasks)
                tasks.clear()
        logging.debug(f"Persisted {count} records to c2m2.{table}")
    except asyncio.CancelledError:
        logging.warning("Cancelled!")
        raise


@wool.routine
async def flush(db, table, batch, metadata=None):
    if table == "file":
        if metadata:
            get_client()[db]["file_metadata"].insert_many(metadata)
    get_client()[db][table].insert_many(batch)
    logging.debug(f"Flushed {len(batch)} records to {db}.{table}")


def aggregate(db):
    yield from db.file.aggregate(PIPELINE)


@c2m2.command
def create_files_view():
    db = get_client()["c2m2-backup"]
    db.drop_collection("files")
    db.command(
        "create",
        "files",
        viewOn="file",
        pipeline=PIPELINE,
        writeConcern={"w": 1},
    )


@wool.routine
async def get_file_metadata(url):
    if (parsed_url := urllib.parse.urlparse(url)).scheme == "drs":
        url = parsed_url._replace(scheme="https").geturl()
    async with aiohttp.ClientSession() as session:
        logging.debug("getting metadata")
        async with rate_limit():
            async with session.get(url) as response:
                if response.status == 200:
                    body = await response.text()
                    root = ET.fromstring(body)
                    script_element = root.find(
                        ".//script[@data-prop-name='context'][@type='application/json']"
                    )
                    if script_element is not None and script_element.text:
                        return json.loads(script_element.text)
                else:
                    raise RuntimeError(f"Failed to fetch metadata from {url}")


if __name__ == "__main__":
    cli()
