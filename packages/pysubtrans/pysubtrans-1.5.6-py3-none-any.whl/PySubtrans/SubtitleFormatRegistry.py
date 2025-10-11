import logging
import os

import pysubs2

from PySubtrans.Helpers.Localization import _
from PySubtrans.SubtitleFileHandler import (
    SubtitleFileHandler,
    default_encoding,
    fallback_encoding,
)
from PySubtrans.SubtitleData import SubtitleData
from PySubtrans.SubtitleError import SubtitleParseError


class SubtitleFormatRegistry:
    """
    Manages discovery and lookup of subtitle file handlers.

    Uses lazy loading to find all subclasses of SubtitleFileHandler in the Formats package.
    Handlers are registered by their supported file extensions and priorities.

    Provides methods to create handler instances based on file extensions or filenames.
    """
    _handlers : dict[str, type[SubtitleFileHandler]] = {}
    _priorities : dict[str, int] = {}
    _discovered : bool = False

    @classmethod
    def register_handler(cls, handler_class : type[SubtitleFileHandler]) -> None:
        """
        Register a subtitle file handler class for its supported extensions.
        """
        instance = handler_class()
        priorities = instance.get_extension_priorities()
        for ext, priority in priorities.items():
            ext = ext.lower()
            if ext not in cls._handlers or priority >= cls._priorities[ext]:
                cls._handlers[ext] = handler_class
                cls._priorities[ext] = priority

    @classmethod
    def get_handler_by_extension(cls, extension : str) -> type[SubtitleFileHandler]:
        """
        Get the subtitle file handler class for the given extension.
        """
        cls._ensure_discovered()
        ext = extension.lower()
        if ext not in cls._handlers:
            raise ValueError(_("Unknown subtitle format: {extension}. Available formats: {available}").format(extension=extension, available=cls.list_available_formats()))
        return cls._handlers[ext]

    @classmethod
    def create_handler(cls, extension: str|None = None, filename: str|None = None) -> SubtitleFileHandler:
        """
        Instantiate a subtitle file handler for the given extension.
        """
        if extension is None and filename is not None:
            extension = cls.get_format_from_filename(filename)

        if extension is None or not extension:
            raise ValueError(
                _("Format cannot be deduced from filename or extension '{name}'. Available formats: {formats}").format(
                    name=filename or extension or "None", formats=cls.list_available_formats()))

        handler_cls = cls.get_handler_by_extension(extension)
        return handler_cls()

    @classmethod
    def enumerate_formats(cls) -> list[str]:
        """
        List all supported subtitle formats (file extensions).
        """
        cls._ensure_discovered()
        return sorted(cls._handlers.keys())

    @classmethod
    def list_available_formats(cls) -> str:
        """
        Get a comma-separated string of all supported subtitle formats.
        """
        formats = cls.enumerate_formats()
        return _("None") if not formats else ", ".join(formats)

    @classmethod
    def disable_autodiscovery(cls) -> None:
        """ Disable automatic loading of subtitle formats (for testing) """
        cls.clear()
        cls._discovered = True

    @classmethod
    def enable_autodiscovery(cls) -> None:
        """ Enable automatic loading of subtitle formats (for testing) """
        cls._discovered = False

    @classmethod
    def discover(cls) -> None:
        """
        Load and register all subtitle file handlers using reflection.
        """
        # Import the formats package, which will trigger explicit imports
        from . import Formats  # type: ignore[ignore-unused]

        for handler_class in SubtitleFileHandler.__subclasses__():
            cls.register_handler(handler_class)

        cls._discovered = True
        logging.debug(f"Supported formats: {sorted(cls._handlers.keys())}")

    @classmethod
    def clear(cls) -> None:
        """
        Clear all registered handlers
        """
        cls._handlers.clear()
        cls._priorities.clear()
        cls._discovered = False

    @classmethod
    def get_format_from_filename(cls, filename):
        """
        Deduce subtitle format from file extension
        """
        base, extension = os.path.splitext(filename) # type: ignore[ignore-unused]
        return extension.lower() if extension else None

    @classmethod
    def detect_format_from_content(cls, content: str) -> str|None:
        """
        Detect subtitle format from content using pysubs2.
        """
        cls._ensure_discovered()
        try:
            detected_format = pysubs2.formats.autodetect_format(content)

            detected_extension = pysubs2.formats.get_file_extension(detected_format)

            logging.info(_("Detected subtitle format '{format}' from content").format(format=detected_extension))

            if detected_extension not in cls._handlers:
                return None

            return detected_extension

        except Exception as e:
            raise SubtitleParseError(_("Failed to detect subtitle format: {}" ).format(str(e)), e)

    @classmethod
    def detect_format_and_load_file(cls, path: str) -> SubtitleData:
        """
        Detect subtitle format using content and load file accordingly.
        """
        cls._ensure_discovered()
        try:
            try:
                subs = pysubs2.load(path, encoding=default_encoding)
            except UnicodeDecodeError:
                subs = pysubs2.load(path, encoding=fallback_encoding)
        except Exception as e:
            raise SubtitleParseError(_("Failed to detect subtitle format: {}" ).format(str(e)), e)

        if not subs.format:
            raise SubtitleParseError(_("Could not detect subtitle format for file: {}" ).format(path))

        detected_extension = pysubs2.formats.get_file_extension(subs.format)

        logging.info(_("Detected subtitle format '{format}'").format(format=detected_extension))

        if detected_extension not in cls._handlers:
            raise SubtitleParseError(_("Detected subtitle format '{format}' is not supported.").format(format=detected_extension))

        handler = cls.create_handler(detected_extension)
        
        data = handler.load_file(path)
        
        data.metadata['detected_format'] = detected_extension
        return data

    @classmethod
    def _ensure_discovered(cls) -> None:
        if not cls._discovered:
            cls.discover()

