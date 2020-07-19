import logging
from asyncio import (
    CancelledError, create_subprocess_exec, sleep, subprocess, wait_for)

log = logging.getLogger(__name__)


async def stop_polling_previews(app):
    for task in app['preview_pollers'].values():
        task.cancel()


async def poll_previews(app, source, port):
    """Update previews for source, every second"""
    host = app['config']['host']
    while True:
        try:
            preview = preview_source(host, source, port)
            app['previews'][source] = await wait_for(preview, timeout=10)
        except CancelledError:
            return
        except Exception:
            log.exception('Exception previewing source %s', source)
        await sleep(1)


async def preview_source(host, source, port):
    """Generate and return a single preview image"""
    log.debug('Previewing %s', source)
    proc = await create_subprocess_exec(
        'ffmpeg', '-v', 'quiet', '-y',
        '-i', f'tcp://{host}:{port}?timeout=1000000',
        '-map', '0:v', '-an',
        '-s', '320x180',
        '-q', '5',
        '-vframes', '1',
        '-f', 'singlejpeg',
        '-',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise Exception(f'ffmpeg exited {proc.returncode}: {stderr}')
    return stdout
