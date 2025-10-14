from datetime import datetime

from pydantic import BaseModel


class FileLoaderInfo(BaseModel):
    id: str = None
    original_file_name: str = None
    convert_file_name: str = None
    original_file_url: str = None
    convert_file_url: str = None
    content: str = None
    file_size: int = None
    file_source: str = None
    load_flag: int = None
    create_time: datetime = None


class FileTitleInfo(BaseModel):
    id: str = None
    title: str = None
    all_title: str = None
    parent_id: str = None
    source_type: str = None
    file_load_id: str = None
    title_level: int = None
    sn: int = None


class FileParagraphInfo(BaseModel):
    id: str = None
    paragraph: str = None
    start_page: int = None
    end_page: int = None
    source_type: str = None
    title_id: str = None
    file_load_id: str = None
    sn: int = None
