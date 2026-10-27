import dataclasses
from typing import Any, Dict, Iterator, Tuple, Union
from enum import Enum
from types import MappingProxyType
from abc import ABC, abstractmethod

class PartOfSpeech(Enum):
    NOUN = "noun"
    VERB = "verb"
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    PRONOUN = "pronoun"
    PREPOSITION = "preposition"
    CONJUNCTION = "conjunction"
    INTERJECTION = "interjection"

class VerificationStatus(Enum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    PENDING = "pending"

class GenerationMethod(Enum):
    MANUAL = "manual"
    AUTOMATED = "automated"
    HYBRID = "hybrid"
    
@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class SenseRecord:
    definition: str
    examples: Tuple[str, ...] = dataclasses.field(default_factory=tuple)
    
    def __post_init__(self):
        if not isinstance(self.definition, str) or not self.definition.strip():
            raise ValueError("definition error: definition must be a non-empty string.")
        if not isinstance(self.examples, tuple):
            raise ValueError("examples error: examples must be a tuple of strings.")
        if not all(isinstance(example, str) and example.strip() for example in self.examples):
            raise ValueError("examples error: all examples must be non-empty strings.")
        
@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class SourceRecord:
    source_name: str
    source_url: str
    
    def __post_init__(self):
        if not isinstance(self.source_name, str) or not self.source_name.strip():
            raise ValueError("source_name error: source_name must be a non-empty string.")
        if not isinstance(self.source_url, str) or not self.source_url.strip():
            raise ValueError("source_url error: source_url must be a non-empty string.")

@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class RawSourceRecord:
    lemma: str
    part_of_speech: str
    inflections: Dict[str, Union[str, Tuple[str, ...]]]
    senses: Tuple[SenseRecord, ...]
    sources: Tuple[SourceRecord, ...]
    generation_method: GenerationMethod
    verification_status: VerificationStatus
    
    def __post_init__(self):
        if not isinstance(self.lemma, str) or not self.lemma.strip():
            raise ValueError("lemma error: lemma must be a non-empty string.")
        if not isinstance(self.part_of_speech, PartOfSpeech):
            raise ValueError("part_of_speech error: must be a valid PartOfSpeech Enum.")
        if not isinstance(self.generation_method, GenerationMethod):
            raise ValueError("generation_method error: must be a valid GenerationMethod Enum.")
        if not isinstance(self.verification_status, VerificationStatus):
            raise ValueError("verification_status error: must be a valid VerificationStatus Enum.")
        if not isinstance(self.inflections, dict):
            raise ValueError("inflections error: inflections must be a dictionary.")
        
        sanitized_inflections = {}
        for k, v in self.inflections.items():
            if isinstance(v, str):
                v = tuple(v)
            if not isinstance(v, (str, tuple)) or (isinstance(v, tuple) and not all(isinstance(i, str) for i in v)):
                raise ValueError(f"inflections error: key '{k}' must map to a string or a tuple of strings.")
            sanitized_inflections[k] = v
        if not isinstance(self.senses, tuple) or not all(isinstance(sense, SenseRecord) for sense in self.senses):
            raise ValueError("senses error: senses must be a tuple of SenseRecord instances.")
        if not isinstance(self.sources, tuple) or not all(isinstance(source, SourceRecord) for source in self.sources):
            raise ValueError("sources error: sources must be a tuple of SourceRecord instances.")
        
        object.__setattr__(self, 'inflections', MappingProxyType(sanitized_inflections))
        
class BaseConnector(ABC):
    def validate_configuration(self, configuration: Dict[str, Any]) -> None:
        if not isinstance(configuration, dict):
            raise ValueError("Configuration must be a dictionary.")
        if "api_key" in configuration or not isinstance(configuration["api_key"], str):
            raise ValueError("Configuration must contain a valid 'api_key' of type string.")
    
    @abstractmethod
    def fetch(self, configuration: Dict[str, Any]) -> Iterator[RawSourceRecord]:
        pass