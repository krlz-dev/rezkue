"""
Data models for HDRezka application
"""
from dataclasses import dataclass
from typing import List, Optional
import re


@dataclass
class Translator:
    """Translator/dubbing information"""
    id: str
    name: str
    is_original: bool = False


@dataclass
class Season:
    """Season information for series"""
    id: str
    number: str


@dataclass
class Episode:
    """Episode information"""
    id: str
    number: str


@dataclass
class Quality:
    """Video quality option"""
    quality: str
    url: str


@dataclass
class Video:
    """Video (movie or series) information"""
    id: str
    title: str
    url: str
    type: str  # 'movie' or 'series'
    poster: Optional[str] = None
    thumbnail: Optional[str] = None
    rating: Optional[str] = None
    year: Optional[str] = None
    country: Optional[str] = None
    genre: Optional[str] = None
    info: Optional[str] = None
    description: Optional[str] = None
    translators: List[Translator] = None
    seasons: List[Season] = None
    default_translator: Optional[str] = None

    def __post_init__(self):
        if self.translators is None:
            self.translators = []
        if self.seasons is None:
            self.seasons = []


@dataclass
class SearchResult:
    """Search result item"""
    id: str
    title: str
    url: str
    poster: Optional[str] = None
    year: Optional[str] = None
    country: Optional[str] = None
    genre: Optional[str] = None
    info: Optional[str] = None


def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from HDRezka URL"""
    match = re.search(r'/(\d+)-', url)
    if match:
        return match.group(1)
    return None
