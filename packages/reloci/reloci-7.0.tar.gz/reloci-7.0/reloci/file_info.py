from datetime import UTC, datetime
from os import stat_result
from pathlib import Path

from exiftool.exceptions import ExifToolException
from exiftool.helper import ExifToolHelper

TAGS = [
    'Composite:SubSecDateTimeOriginal',
    'EXIF:DateTimeOriginal',
    'EXIF:Make',
    'EXIF:Model',
    'EXIF:SerialNumber',
    'MakerNotes:DateTimeOriginal',
    'MakerNotes:SerialNumber',
    'MakerNotes:ShutterCount',
    'MakerNotes:Make',
    'MakerNotes:Model',
    'QuickTime:CreationDate',
    'QuickTime:Make',
    'QuickTime:Model',
    'XMP:ImageNumber',
    'XMP:SerialNumber',
]


class FileInfo:
    def __init__(self, path: Path, exiftool: ExifToolHelper) -> None:
        self.file = path
        try:
            self.tags: dict[str, str] = exiftool.get_tags(str(path), TAGS)[0]
        except ExifToolException as error:
            raise RuntimeError(f'An error occured while processing {path}') from error

    @property
    def original_name(self) -> str:
        return self.file.name

    @property
    def extension(self) -> str:
        return self.file.suffix

    @property
    def file_stat(self) -> stat_result:
        return self.file.stat()

    @property
    def camera_make(self) -> str:
        for tag in ('EXIF:Make', 'QuickTime:Make', 'MakerNotes:Make'):
            if tag in self.tags:
                return self.tags[tag]

        raise LookupError(f'Did not find camera make in EXIF of {self.file}')

    @property
    def camera_model(self) -> str:
        for tag in ('EXIF:Model', 'QuickTime:Model', 'MakerNotes:Model'):
            if tag in self.tags:
                return self.tags[tag]

        raise LookupError(f'Did not find camera model in EXIF of {self.file}')

    @property
    def camera_serial(self) -> str:
        for tag in ('MakerNotes:SerialNumber', 'EXIF:SerialNumber', 'XMP:SerialNumber'):
            if tag in self.tags:
                return str(self.tags[tag])

        raise LookupError(f'Did not find camera serial in EXIF of {self.file}')

    @property
    def shutter_count(self) -> str:
        for tag in ('MakerNotes:ShutterCount', 'XMP:ImageNumber'):
            if tag in self.tags:
                return str(self.tags[tag])

        raise LookupError(f'Did not find shutter count in EXIF of {self.file}')

    @property
    def subsecond_datetime(self) -> datetime:
        """Extract subsecond accurate original capture date from EXIF

        Try to get an accurate time by including the subsecond component.
        Raises LookupError if the date is not available in EXIF.

        Assume UTC timezone when not available from EXIF.

        """
        tag = 'Composite:SubSecDateTimeOriginal'
        if tag in self.tags:
            date_time_original = self.tags[tag]
            try:
                return datetime.strptime(date_time_original, '%Y:%m:%d %H:%M:%S.%f%z')
            except ValueError:
                return datetime.strptime(date_time_original, '%Y:%m:%d %H:%M:%S.%f').replace(tzinfo=UTC)

        raise LookupError(f'Did not find accurate date in EXIF of {self.file}')

    @property
    def date_time(self) -> datetime:
        """Extract second accurate original capture date from EXIF

        Try to get the capture time accurate to second.
        Raises LookupError if the date is not available in EXIF.

        Assume UTC timezone when not available from EXIF.

        """
        for tag in (
            'MakerNotes:DateTimeOriginal',
            'EXIF:DateTimeOriginal',
            'QuickTime:CreationDate',
        ):
            if tag in self.tags:
                date_time_original = self.tags[tag]
                try:
                    return datetime.strptime(date_time_original, '%Y:%m:%d %H:%M:%S%z')
                except ValueError:
                    return datetime.strptime(date_time_original, '%Y:%m:%d %H:%M:%S').replace(tzinfo=UTC)

        raise LookupError(f'Did not find original date in EXIF of {self.file}')

    @property
    def creation_datetime(self) -> datetime:
        """Extract file creation date

        These times are not always accurate file created dates.
        Implementation also differ between operating systems.

        """
        timestamp: float = getattr(self.file_stat, 'st_birthtime', self.file_stat.st_ctime)
        return datetime.fromtimestamp(timestamp, tz=UTC)
