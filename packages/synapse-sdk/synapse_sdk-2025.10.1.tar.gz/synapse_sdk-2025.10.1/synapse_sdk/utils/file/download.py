import asyncio
import operator
from functools import reduce
from pathlib import Path

import aiohttp
import requests

from synapse_sdk.utils.network import clean_url
from synapse_sdk.utils.string import hash_text

from .io import get_temp_path


def download_file(url, path_download, name=None, coerce=None, use_cached=True):
    chunk_size = 1024 * 1024 * 50
    cleaned_url = clean_url(url)  # remove query params and fragment

    if name:
        use_cached = False
    else:
        name = hash_text(cleaned_url)

    name += Path(cleaned_url).suffix

    path = Path(path_download) / name

    if not use_cached or not path.is_file():
        response = requests.get(url, allow_redirects=True, stream=True)
        response.raise_for_status()

        with path.open('wb') as file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                file.write(chunk)

    if coerce:
        path = coerce(path)

    return path


def files_url_to_path(files, coerce=None, file_field=None):
    path_download = get_temp_path('media')
    path_download.mkdir(parents=True, exist_ok=True)
    if file_field:
        files[file_field] = download_file(files[file_field], path_download, coerce=coerce)
    else:
        for file_name in files:
            if isinstance(files[file_name], str):
                files[file_name] = download_file(files[file_name], path_download, coerce=coerce)
            else:
                files[file_name]['path'] = download_file(files[file_name].pop('url'), path_download, coerce=coerce)


def files_url_to_path_from_objs(objs, files_fields, coerce=None, is_list=False, is_async=False):
    if is_async:
        asyncio.run(afiles_url_to_path_from_objs(objs, files_fields, coerce=coerce, is_list=is_list))
    else:
        if not is_list:
            objs = [objs]

        for obj in objs:
            for files_field in files_fields:
                try:
                    files = reduce(operator.getitem, files_field.split('.'), obj)
                    if isinstance(files, str):
                        files_url_to_path(obj, coerce=coerce, file_field=files_field)
                    else:
                        files_url_to_path(files, coerce=coerce)
                except KeyError:
                    pass


async def adownload_file(url, path_download, name=None, coerce=None, use_cached=True):
    chunk_size = 1024 * 1024 * 50
    cleaned_url = clean_url(url)  # remove query params and fragment

    if name:
        use_cached = False
    else:
        name = hash_text(cleaned_url)

    name += Path(cleaned_url).suffix

    path = Path(path_download) / name

    if not use_cached or not path.is_file():
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                with path.open('wb') as file:
                    while chunk := await response.content.read(chunk_size):
                        file.write(chunk)

    if coerce:
        path = coerce(path)

    return path


async def afiles_url_to_path(files, coerce=None):
    path_download = get_temp_path('media')
    path_download.mkdir(parents=True, exist_ok=True)
    for file_name in files:
        if isinstance(files[file_name], str):
            files[file_name] = await adownload_file(files[file_name], path_download, coerce=coerce)
        else:
            files[file_name]['path'] = await adownload_file(files[file_name].pop('url'), path_download, coerce=coerce)


async def afiles_url_to_path_from_objs(objs, files_fields, coerce=None, is_list=False):
    if not is_list:
        objs = [objs]

    tasks = []

    for obj in objs:
        for files_field in files_fields:
            try:
                files = reduce(operator.getitem, files_field.split('.'), obj)
                tasks.append(afiles_url_to_path(files, coerce=coerce))
            except KeyError:
                pass

    await asyncio.gather(*tasks)
