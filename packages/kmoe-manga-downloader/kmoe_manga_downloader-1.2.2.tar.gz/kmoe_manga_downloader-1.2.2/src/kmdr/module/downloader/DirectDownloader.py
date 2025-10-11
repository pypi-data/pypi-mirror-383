from functools import partial

from kmdr.core import Downloader, BookInfo, VolInfo, DOWNLOADER
from kmdr.core.constants import API_ROUTE

from .download_utils import download_file_multipart, readable_safe_filename

@DOWNLOADER.register(
    hasvalues={
        'method': 1
    }
)
class DirectDownloader(Downloader):
    def __init__(self, dest='.', callback=None, retry=3, num_workers=8, proxy=None, *args, **kwargs):
        super().__init__(dest, callback, retry, num_workers, proxy, *args, **kwargs)

    async def _download(self, book: BookInfo, volume: VolInfo):
        sub_dir = readable_safe_filename(book.name)
        download_path = f'{self._dest}/{sub_dir}'

        await download_file_multipart(
            self._session,
            self._semaphore,
            self._progress,
            partial(self.construct_download_url, book, volume),
            download_path,
            readable_safe_filename(f'[Kmoe][{book.name}][{volume.name}].epub'),
            self._retry,
            callback=lambda: self._callback(book, volume) if self._callback else None
        )

    def construct_download_url(self, book: BookInfo, volume: VolInfo) -> str:
        return API_ROUTE.DOWNLOAD.format(
            book_id=book.id,
            volume_id=volume.id,
            is_vip=self._profile.is_vip
        )
