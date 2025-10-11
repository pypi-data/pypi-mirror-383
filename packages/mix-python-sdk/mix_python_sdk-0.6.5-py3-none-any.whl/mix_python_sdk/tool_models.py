"""Tool input/output models for Mix agent tools.

This module provides Pydantic models for interacting with Mix agent tools.
These models provide type safety, validation, and IDE autocomplete support.

Example:
    from mix_python_sdk.tool_models import MediaOutput, MediaType

    output = MediaOutput(
        path="http://localhost:8088/files/video.mp4",
        type=MediaType.VIDEO,
        title="Analysis Results",
        description="Portfolio performance analysis"
    )
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ===== Core Tool Names =====


class CoreToolName(str, Enum):
    """Core built-in tool names."""

    BASH = "bash"
    READ_TEXT = "ReadText"
    GLOB = "glob"
    READ_MEDIA = "ReadMedia"
    GREP = "grep"
    WRITE = "write"
    EDIT = "edit"
    PYTHON_EXECUTION = "python_execution"
    SEARCH = "search"
    TODO_WRITE = "todo_write"
    EXIT_PLAN_MODE = "exit_plan_mode"
    SHOW_MEDIA = "show_media"
    TASK = "task"


# ===== show_media Tool =====


class MediaType(str, Enum):
    """Supported media types for show_media tool."""

    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    GSAP_ANIMATION = "gsap_animation"
    PDF = "pdf"
    CSV = "csv"


class MediaOutput(BaseModel):
    """Single media output for show_media tool.

    Attributes:
        path: Absolute path or URL to the media file (required except for gsap_animation)
        type: Type of media (image, video, audio, gsap_animation, pdf, csv)
        title: Title or name for the media output
        description: Optional description or context
        config: Configuration data for gsap_animation type (JSON object with animation settings)
        start_time: Optional start time in seconds for video/audio segments
        duration: Optional duration in seconds for video/audio segments
    """

    path: Optional[str] = None
    type: MediaType
    title: str
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    start_time: Optional[int] = Field(None, alias="startTime", ge=0)
    duration: Optional[int] = Field(None, ge=1)

    class Config:
        populate_by_name = True  # Allow both snake_case and camelCase


class MediaShowcaseParams(BaseModel):
    """Parameters for show_media tool.

    Attributes:
        outputs: Array of media outputs to showcase
    """

    outputs: List[MediaOutput]


# ===== ReadMedia Tool =====


class MediaAnalysisType(str, Enum):
    """Supported media types for ReadMedia tool."""

    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    PDF = "pdf"


class ReadMediaParams(BaseModel):
    """Parameters for ReadMedia tool.

    Attributes:
        file_path: Path to file or URL for analysis
        media_type: Type of media analysis to perform
        prompt: Analysis prompt for the media content
        pdf_pages: PDF page selection (e.g., '5' or '1-3,7,10-12') - PDF only
        video_interval: Video time interval (e.g., '00:20:50-00:26:10') - video only
    """

    file_path: str
    media_type: MediaAnalysisType
    prompt: str
    pdf_pages: Optional[str] = None
    video_interval: Optional[str] = None


class ReadMediaResult(BaseModel):
    """Single result from ReadMedia tool.

    Attributes:
        file_path: Path to the analyzed file
        media_type: Type of media that was analyzed
        analysis: Analysis results from the AI
        error: Error message if analysis failed
    """

    file_path: str
    media_type: str
    analysis: str
    error: Optional[str] = None


class ReadMediaResponse(BaseModel):
    """Response from ReadMedia tool.

    Attributes:
        results: List of analysis results
        summary: Overall summary of the analysis
    """

    results: List[ReadMediaResult]
    summary: str


# ===== TodoWrite Tool =====


class TodoStatus(str, Enum):
    """Todo item status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TodoPriority(str, Enum):
    """Todo item priority."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Todo(BaseModel):
    """Single todo item.
    Attributes:
        id: Unique identifier for the todo item
        content: The todo task description
        status: Current status (pending, in_progress, completed)
        priority: Priority level (low, medium, high)
    """

    id: str
    content: str
    status: TodoStatus
    priority: TodoPriority


class TodoWriteParams(BaseModel):
    """Parameters for TodoWrite tool.

    Attributes:
        todos: Array of todo items to manage
    """

    todos: List[Todo]


# ===== Bash Tool =====


class BashParams(BaseModel):
    """Parameters for bash tool.

    Attributes:
        command: The bash command to execute (required)
        timeout: Timeout in milliseconds (optional, default: 60000, max: 600000)
    """

    command: str
    timeout: Optional[int] = None


# ===== ReadText Tool =====


class ReadTextParams(BaseModel):
    """Parameters for ReadText tool.

    Attributes:
        file_path: Absolute path or URL (http/https) to read
        offset: Line number to start reading (0-based, optional)
        limit: Number of lines to read (optional, default: 2000)
    """

    file_path: str
    offset: Optional[int] = None
    limit: Optional[int] = None


# ===== Glob Tool =====


class GlobParams(BaseModel):
    """Parameters for glob tool.

    Attributes:
        pattern: The glob pattern to match files against (required)
        path: Directory to search in (optional, defaults to session storage)
    """

    pattern: str
    path: Optional[str] = None


# ===== Grep Tool =====


class GrepParams(BaseModel):
    """Parameters for grep tool.

    Attributes:
        pattern: The regex pattern to search for (required)
        path: Directory to search (optional, defaults to session storage)
        include: File pattern to include, e.g., "*.js", "*.{ts,tsx}" (optional)
        literal_text: If true, pattern is treated as literal text (default: false)
    """

    pattern: str
    path: Optional[str] = None
    include: Optional[str] = None
    literal_text: Optional[bool] = False


# ===== Write Tool =====


class WriteParams(BaseModel):
    """Parameters for write tool.

    Attributes:
        file_path: Path to the file to write (required)
        content: Content to write to the file (required)
    """

    file_path: str
    content: str


# ===== Edit Tool =====


class EditParams(BaseModel):
    """Parameters for edit tool.

    Attributes:
        file_path: Absolute path to the file to modify (required)
        old_string: Text to replace (required)
        new_string: Text to replace it with (required)
    """

    file_path: str
    old_string: str
    new_string: str


# ===== ExitPlanMode Tool =====


class ExitPlanModeParams(BaseModel):
    """Parameters for exit_plan_mode tool.

    Attributes:
        plan: The plan to present (required, supports markdown)
    """

    plan: str


# ===== Search (web_search) Tool =====


class SearchType(str, Enum):
    """Type of search to perform."""

    WEB = "web"
    IMAGES = "images"
    VIDEOS = "videos"


class Safesearch(str, Enum):
    """Safe search level."""

    STRICT = "strict"
    MODERATE = "moderate"
    OFF = "off"


class SearchParams(BaseModel):
    """Parameters for search (web_search) tool.

    Attributes:
        query: Search query (required, minLength: 2)
        search_type: Type of search: "web", "images", "videos" (default: "web")
        allowed_domains: Only include results from these domains
        blocked_domains: Never include results from these domains
        safesearch: Safe search level: "strict", "moderate", "off" (default: "strict")
        spellcheck: Enable spellcheck (default: true)
    """

    query: str = Field(..., min_length=2)
    search_type: Optional[SearchType] = SearchType.WEB
    allowed_domains: Optional[List[str]] = None
    blocked_domains: Optional[List[str]] = None
    safesearch: Optional[Safesearch] = Safesearch.STRICT
    spellcheck: Optional[bool] = True


class SearchResult(BaseModel):
    """Single web search result.

    Attributes:
        title: Result title
        url: Result URL
        description: Result description
    """

    title: str
    url: str
    description: str


class WebResults(BaseModel):
    """Web search results container.

    Attributes:
        type: Result type
        results: List of search results
    """

    type: str
    results: List[SearchResult]


class BraveSearchResponse(BaseModel):
    """Response from Brave web search.

    Attributes:
        type: Response type
        web: Web search results
    """

    type: str
    web: WebResults


class ImageResultThumbnail(BaseModel):
    """Thumbnail information for image search results.

    Attributes:
        src: Thumbnail URL
    """

    src: str


class ImageResultProperties(BaseModel):
    """Properties for image search results.

    Attributes:
        url: Actual image URL
        placeholder: Placeholder data
    """

    url: str
    placeholder: str


class ImageResultMetaURL(BaseModel):
    """Metadata about the source URL.

    Attributes:
        scheme: URL scheme
        netloc: Network location
        hostname: Hostname
        favicon: Favicon URL
        path: URL path
    """

    scheme: str
    netloc: str
    hostname: str
    favicon: str
    path: str


class ImageResult(BaseModel):
    """Single image search result.

    Attributes:
        type: Result type
        title: Result title
        url: Source page URL
        source: Source domain
        page_fetched: Timestamp
        thumbnail: Thumbnail information
        properties: Image properties
        meta_url: Source URL metadata (optional)
        confidence: Confidence score
    """

    type: str
    title: str
    url: str
    source: str
    page_fetched: str
    thumbnail: ImageResultThumbnail
    properties: ImageResultProperties
    meta_url: Optional[ImageResultMetaURL] = None
    confidence: str


class ImageSearchResponse(BaseModel):
    """Response from image search.

    Attributes:
        type: Response type
        results: List of image results
    """

    type: str
    results: List[ImageResult]


class VideoResultThumbnail(BaseModel):
    """Thumbnail information for video search results.

    Attributes:
        src: Thumbnail URL
    """

    src: str


class VideoResultProperties(BaseModel):
    """Properties for video search results.

    Attributes:
        url: Actual video URL
        duration: Video duration
        views: View count
        upload_date: Upload date
        placeholder: Placeholder data
    """

    url: str
    duration: str
    views: str
    upload_date: str
    placeholder: str


class VideoResultMetaURL(BaseModel):
    """Metadata about the source URL.

    Attributes:
        scheme: URL scheme
        netloc: Network location
        hostname: Hostname
        favicon: Favicon URL
        path: URL path
    """

    scheme: str
    netloc: str
    hostname: str
    favicon: str
    path: str


class VideoResult(BaseModel):
    """Single video search result.

    Attributes:
        type: Result type
        title: Result title
        url: Source page URL
        source: Source domain
        page_fetched: Timestamp
        thumbnail: Thumbnail information
        properties: Video properties
        meta_url: Source URL metadata (optional)
        confidence: Confidence score
    """

    type: str
    title: str
    url: str
    source: str
    page_fetched: str
    thumbnail: VideoResultThumbnail
    properties: VideoResultProperties
    meta_url: Optional[VideoResultMetaURL] = None
    confidence: str


class VideoSearchResponse(BaseModel):
    """Response from video search.

    Attributes:
        type: Response type
        results: List of video results
    """

    type: str
    results: List[VideoResult]


# ===== Task Tool =====


class SubagentType(str, Enum):
    """Type of specialized agent to use."""

    GENERAL_PURPOSE = "general-purpose"


class TaskParams(BaseModel):
    """Parameters for task tool.

    Attributes:
        description: Short 3-5 word task description (required)
        prompt: The task for the agent to perform (required)
        subagent_type: Type of specialized agent to use (required)
    """

    description: str
    prompt: str
    subagent_type: str


# ===== PythonExecution Tool =====


class PythonExecutionParams(BaseModel):
    """Parameters for python_execution tool.

    Attributes:
        code: The Python code to execute (required)
    """

    code: str


class PythonExecutionResult(BaseModel):
    """Response from python_execution tool.

    Attributes:
        type: Always "code_execution_result"
        stdout: Standard output from Python execution
        stderr: Standard error from Python execution
        return_code: Exit code (0 for success, non-zero for failure)
    """

    type: str
    stdout: str
    stderr: str
    return_code: int


# ===== Tool Response Metadata Types =====


class BashResponseMetadata(BaseModel):
    """Metadata for bash tool responses.

    Attributes:
        start_time: Unix timestamp in milliseconds when command started
        end_time: Unix timestamp in milliseconds when command completed
    """

    start_time: int
    end_time: int


class ReadTextResponseMetadata(BaseModel):
    """Metadata for ReadText tool responses.

    Attributes:
        file_path: The path/URL that was read
        content: The raw content without line numbers
    """

    file_path: str
    content: str


class GlobResponseMetadata(BaseModel):
    """Metadata for glob tool responses.

    Attributes:
        number_of_files: Count of files returned
        truncated: Whether results were limited to 100 files
    """

    number_of_files: int
    truncated: bool


class GrepResponseMetadata(BaseModel):
    """Metadata for grep tool responses.

    Attributes:
        number_of_matches: Total number of matches found
        truncated: True if results were limited to 100 matches
    """

    number_of_matches: int
    truncated: bool


class WriteResponseMetadata(BaseModel):
    """Metadata for write tool responses.

    Attributes:
        diff: Diff text showing changes
        additions: Number of lines added
        removals: Number of lines removed
    """

    diff: str
    additions: int
    removals: int


class EditResponseMetadata(BaseModel):
    """Metadata for edit tool responses.

    Attributes:
        diff: Diff text showing changes
        additions: Number of lines added
        removals: Number of lines removed
    """

    diff: str
    additions: int
    removals: int
