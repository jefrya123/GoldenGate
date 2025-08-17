"""
PII Detection Engine - Enhanced Presidio Integration
"""

import re
from typing import List, Optional
from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpEngineProvider, NlpArtifacts
from .schema import EntityHit
from .classifier import classify_label

class EnhancedRobustRecognizer(PatternRecognizer):
    """Enhanced recognizer with overlapping result filtering."""
    
    def __init__(self, entity_type: str, patterns: List[Pattern]):
        super().__init__(
            supported_entity=entity_type,
            patterns=patterns,
            supported_language="en"
        )
    
    def analyze(self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts) -> List[RecognizerResult]:
        """Enhanced analysis with overlapping result filtering."""
        results = super().analyze(text, entities, nlp_artifacts)
        
        # Remove duplicates and overlapping results
        filtered_results = self._filter_overlapping_results(results)
        
        return filtered_results
    
    def _filter_overlapping_results(self, results: List[RecognizerResult]) -> List[RecognizerResult]:
        """Remove overlapping results, keeping the highest confidence."""
        if not results:
            return results
        
        sorted_results = sorted(results, key=lambda x: x.score, reverse=True)
        filtered = []
        
        for result in sorted_results:
            overlaps = False
            for accepted in filtered:
                if (result.start < accepted.end and result.end > accepted.start):
                    overlaps = True
                    break
            
            if not overlaps:
                filtered.append(result)
        
        return filtered

def build_analyzer() -> Optional[AnalyzerEngine]:
    """
    Build Presidio analyzer with enhanced recognizers.
    
    Returns:
        Configured AnalyzerEngine or None if Presidio is not available
    """
    try:
        # Try to create NLP engine with fallback configuration
        try:
            nlp_configuration = {
                "nlp_engine_name": "spacy",
                "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}]
            }
            provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
            nlp_engine = provider.create_engine()
        except Exception as e:
            print(f"Warning: Could not load spaCy model, using basic NLP engine: {e}")
            # Fallback to basic configuration
            nlp_configuration = {
                "nlp_engine_name": "spacy",
                "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}]
            }
            provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
            nlp_engine = provider.create_engine()
        
        analyzer = AnalyzerEngine(nlp_engine=nlp_engine, registry=None)
        
        # Add enhanced recognizers with improved patterns
        enhanced_recognizers = [
            EnhancedRobustRecognizer("ID", [
                Pattern("SSN_DASHED", r'\b\d{3}-\d{2}-\d{4}\b', 0.95),
                Pattern("SSN_SPACED", r'\b\d{3}\s\d{2}\s\d{4}\b', 0.95),
                Pattern("SSN_DOTTED", r'\b\d{3}\.\d{2}\.\d{4}\b', 0.95),
                Pattern("SSN_RAW", r'(?<!\d)\d{9}(?!\d)', 0.6)  # Avoid false positives
            ]),
            EnhancedRobustRecognizer("PHONE_NUMBER", [
                Pattern("US_PHONE_FULL", r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b', 0.9),
                Pattern("INTERNATIONAL_PHONE", r'\b\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b', 0.8),
                Pattern("PHONE_WITH_EXT", r'\b\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\s?(?:ext|extension|x)\.?\s?\d+\b', 0.9)
            ]),
            EnhancedRobustRecognizer("ADDRESS", [
                Pattern("FULL_ADDRESS", r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct|Place|Pl|Way|Terrace|Ter|Circle|Cir|Parkway|Pkwy)(?:\s+(?:Apt|Apartment|Unit|Suite|Ste|#)\s*[A-Za-z0-9]+)?,\s+[A-Za-z\s]+,\s+[A-Z]{2}\s+\d{5}(?:-\d{4})?\b', 0.95),
                Pattern("STREET_ADDRESS", r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct|Place|Pl|Way|Terrace|Ter|Circle|Cir|Parkway|Pkwy)\b', 0.85),
                Pattern("CITY_STATE_ZIP", r'\b[A-Za-z\s]+,\s+[A-Z]{2}\s+\d{5}(?:-\d{4})?\b', 0.9),
                Pattern("PO_BOX", r'\bP\.?O\.?\s+Box\s+\d+\b', 0.8)
            ]),
            EnhancedRobustRecognizer("EMAIL_ADDRESS", [
                Pattern("EMAIL", r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 0.99)
            ]),
            EnhancedRobustRecognizer("CREDIT_CARD", [
                Pattern("CREDIT_CARD_FORMATTED", r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', 0.95),
                Pattern("CREDIT_CARD_AMEX", r'\b3[47]\d{2}[-\s]?\d{6}[-\s]?\d{5}\b', 0.95),
                Pattern("CREDIT_CARD_RAW", r'\b(?:4\d{15}|5[1-5]\d{14}|3[47]\d{13}|6(?:011|5\d{2})\d{12})\b', 0.9)
            ]),
            EnhancedRobustRecognizer("EIN", [
                Pattern("EIN_FORMATTED", r'\b\d{2}-\d{7}\b', 0.95),
                Pattern("EIN_RAW", r'(?<!\d)\d{9}(?!\d)', 0.7)
            ]),
            EnhancedRobustRecognizer("ZIP", [
                Pattern("ZIP_EXTENDED", r'\b\d{5}-\d{4}\b', 0.95),
                Pattern("ZIP_BASIC", r'\b\d{5}\b', 0.85)
            ]),
            EnhancedRobustRecognizer("DRIVER_LICENSE", [
                Pattern("DL_PATTERN", r'\b[A-Z]{1,2}\d{6,8}\b', 0.8)
            ]),
            EnhancedRobustRecognizer("SOCIAL_MEDIA_HANDLE", [
                Pattern("TWITTER_X_HANDLE", r'@[A-Za-z0-9_]{1,15}\b', 0.9),
                Pattern("INSTAGRAM_HANDLE", r'@[A-Za-z0-9_.]{1,30}\b', 0.9),
                Pattern("LINKEDIN_HANDLE", r'linkedin\.com/in/[A-Za-z0-9-]+', 0.95),
                Pattern("FACEBOOK_HANDLE", r'facebook\.com/[A-Za-z0-9.]+', 0.9),
                Pattern("GENERIC_SOCIAL_HANDLE", r'@[A-Za-z0-9_.-]{3,30}\b', 0.7)
            ])
        ]
        
        for recognizer in enhanced_recognizers:
            analyzer.registry.add_recognizer(recognizer)
        
        return analyzer
        
    except Exception as e:
        print(f"Warning: Could not build Presidio analyzer: {e}")
        return None

def _chunk(text: str, size: int = 2000, overlap: int = 100) -> List[str]:
    """
    Split text into overlapping chunks for processing.
    
    Args:
        text: Text to chunk
        size: Maximum chunk size
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    if len(text) <= size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + size, len(text))
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
        
        if start >= len(text):
            break
    
    return chunks

def hits_from_text(text: str, chunk_size: int = 2000, overlap: int = 100) -> List[EntityHit]:
    """
    Detect PII entities in text using Presidio or fallback regex.
    
    Args:
        text: Text to analyze
        chunk_size: Maximum chunk size for processing
        overlap: Overlap between chunks
        
    Returns:
        List of detected PII entities
    """
    analyzer = build_analyzer()
    
    if analyzer:
        return _process_with_presidio(analyzer, text, chunk_size, overlap)
    else:
        return _process_with_fallback(text, chunk_size, overlap)

def _process_with_presidio(analyzer: AnalyzerEngine, text: str, chunk_size: int, overlap: int) -> List[EntityHit]:
    """Process text using Presidio analyzer."""
    chunks = _chunk(text, chunk_size, overlap)
    all_hits = []
    
    for i, chunk in enumerate(chunks):
        try:
            results = analyzer.analyze(
                text=chunk,
                entities=["ID", "PHONE_NUMBER", "ADDRESS", "EMAIL_ADDRESS", "CREDIT_CARD", "EIN", "ZIP", "DRIVER_LICENSE", "SOCIAL_MEDIA_HANDLE"],
                language="en"
            )
            
            # Adjust positions for chunk offset
            chunk_offset = i * (chunk_size - overlap)
            
            for result in results:
                entity_text = chunk[result.start:result.end]
                
                # Get context
                context_start = max(0, result.start - 30)
                context_end = min(len(chunk), result.end + 30)
                context_left = chunk[context_start:result.start].strip()
                context_right = chunk[result.end:context_end].strip()
                
                # Classify the entity using only chunk context (memory efficient)
                chunk_context = chunk[max(0, result.start - 100):min(len(chunk), result.end + 100)]
                label = classify_label(
                    result.entity_type,
                    entity_text,
                    chunk_context,  # Use chunk context instead of full text
                    result.start,
                    result.end
                )
                
                hit = EntityHit(
                    entity_type=result.entity_type,
                    value=entity_text,
                    start=chunk_offset + result.start,
                    end=chunk_offset + result.end,
                    score=result.score,
                    label=label,
                    context_left=context_left,
                    context_right=context_right
                )
                
                all_hits.append(hit)
            
            # Memory cleanup - clear chunk after processing
            del chunk
            del results
            
        except Exception as e:
            print(f"Error processing chunk {i}: {e}")
            continue
    
    return all_hits

def _process_with_fallback(text: str, chunk_size: int, overlap: int) -> List[EntityHit]:
    """Process text using fallback regex patterns."""
    from .recognizers import FALLBACK_REGEX
    
    all_hits = []
    
    for entity_type, patterns in FALLBACK_REGEX.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                entity_text = match.group(0)
                
                # Get context
                context_start = max(0, match.start() - 30)
                context_end = min(len(text), match.end() + 30)
                context_left = text[context_start:match.start()].strip()
                context_right = text[match.end():context_end].strip()
                
                # Classify the entity
                label = classify_label(
                    entity_type,
                    entity_text,
                    text,
                    match.start(),
                    match.end()
                )
                
                hit = EntityHit(
                    entity_type=entity_type,
                    value=entity_text,
                    start=match.start(),
                    end=match.end(),
                    score=0.7,  # Default confidence for regex
                    label=label,
                    context_left=context_left,
                    context_right=context_right
                )
                
                all_hits.append(hit)
    
    return all_hits 