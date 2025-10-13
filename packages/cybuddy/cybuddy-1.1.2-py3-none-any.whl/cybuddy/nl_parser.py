"""
Intelligent Natural Language Query Parser for Cybuddy.

Enhanced parser with context-aware understanding, cybersecurity domain knowledge,
and intelligent ambiguity resolution. Handles varied user phrasing and understands
relationships between cybersecurity concepts.

Examples:
- "how do I scan ports?" → ("explain", "port scanning")
- "tips on sql injection" → ("tip", "sql injection")
- "what should I do after getting a shell?" → ("plan", "post-exploitation")
- "i'm stuck on this nmap thing" → ("plan", "nmap troubleshooting")
- "help me understand burp suite" → ("explain", "burp suite")
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import json
from pathlib import Path

# Import thefuzz for enhanced fuzzy matching
try:
    from thefuzz import fuzz, process
    THEFUZZ_AVAILABLE = True
except ImportError:
    THEFUZZ_AVAILABLE = False
    # Fallback functions if thefuzz is not available
    def fuzz_ratio(a, b):
        return 0
    def process_extract(query, choices, limit=5, scorer=None):
        return []


# ============================================================================
# Enhanced Data Structures for Intelligent Parsing
# ============================================================================

class IntentType(Enum):
    """Supported intent types."""
    EXPLAIN = "explain"
    TIP = "tip"
    PLAN = "plan"
    ASSIST = "assist"
    REPORT = "report"
    QUIZ = "quiz"
    CLARIFY = "clarify"


class EntityType(Enum):
    """Types of cybersecurity entities."""
    TOOL = "tool"
    TECHNIQUE = "technique"
    VULNERABILITY = "vulnerability"
    PROTOCOL = "protocol"
    PLATFORM = "platform"
    CONCEPT = "concept"


@dataclass
class Entity:
    """Represents a cybersecurity entity."""
    name: str
    entity_type: EntityType
    aliases: List[str]
    related_entities: List[str]
    confidence: float = 1.0


@dataclass
class IntentResult:
    """Result of intent classification."""
    intent: IntentType
    confidence: float
    entities: List[Entity]
    context: Dict[str, Any]
    clarification_needed: bool = False
    clarification_question: Optional[str] = None


@dataclass
class UnderstandingResult:
    """Complete understanding of user query."""
    intent: IntentType
    entities: List[Entity]
    parameters: Dict[str, Any]
    confidence: float
    original_query: str
    processed_query: str
    clarification_needed: bool = False
    clarification_question: Optional[str] = None


# ============================================================================
# High-Performance Data-Driven Cybersecurity Knowledge Base
# ============================================================================

from typing import Dict, List, Optional, Set, Tuple, Any
from functools import lru_cache
import time
from collections import defaultdict
import re

class TrieNode:
    """Trie node for efficient prefix matching."""
    def __init__(self):
        """Initialize a trie node with empty children, entities, and end flag."""
        self.children: Dict[str, 'TrieNode'] = {}
        self.entities: List[Entity] = []
        self.is_end: bool = False

class FuzzyMatcher:
    """Enhanced fuzzy matching using thefuzz library with trie fallback."""
    
    def __init__(self, high_threshold: float = 0.8, medium_threshold: float = 0.6):
        """Initialize fuzzy matcher with configurable thresholds.
        
        Args:
            high_threshold: Score above which to auto-correct (default: 0.8)
            medium_threshold: Score above which to suggest corrections (default: 0.6)
        """
        self.trie_root = TrieNode()
        self.entity_scores: Dict[str, float] = {}
        self._built = False
        self.high_threshold = high_threshold
        self.medium_threshold = medium_threshold
        self._entity_names: List[str] = []
        self._entity_map: Dict[str, Entity] = {}
    
    def build_trie(self, entities: Dict[str, Entity], alias_index: Dict[str, Entity] = None) -> None:
        """Build trie from entities for fast prefix matching."""
        self._entity_map = entities.copy()
        self._entity_names = []
        self._alias_index = alias_index or {}
        
        for name, entity in entities.items():
            self._insert_entity(name.lower(), entity)
            self._entity_names.append(name.lower())
            # Insert aliases
            for alias in entity.aliases:
                self._insert_entity(alias.lower(), entity)
                self._entity_names.append(alias.lower())
        self._built = True
    
    def _insert_entity(self, text: str, entity: Entity) -> None:
        """Insert entity into trie."""
        node = self.trie_root
        for char in text:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.entities.append(entity)
        node.is_end = True
    
    def find_matches(self, query: str, max_results: int = 5) -> List[Tuple[Entity, float]]:
        """Find fuzzy matches using thefuzz library with early termination optimization."""
        if not self._built:
            return []
        
        query_lower = query.lower().strip()
        
        # Early termination for exact matches
        if query_lower in self._entity_map:
            entity = self._entity_map[query_lower]
            return [(entity, 1.0)]
        
        # Check if we have access to alias index (from knowledge base)
        if hasattr(self, '_alias_index') and query_lower in self._alias_index:
            entity = self._alias_index[query_lower]
            return [(entity, 0.95)]  # High confidence for alias matches
        
        matches = []
        
        # Use thefuzz if available for better scoring
        if THEFUZZ_AVAILABLE and self._entity_names:
            # Optimize limit based on query length and expected matches
            search_limit = min(max_results * 3, len(self._entity_names))
            
            # Get top matches using thefuzz with early termination
            thefuzz_matches = process.extract(
                query_lower, 
                self._entity_names, 
                limit=search_limit,
                scorer=fuzz.ratio
            )
            
            # Early termination: stop if we have high-confidence matches
            high_confidence_found = False
            for match_name, score in thefuzz_matches:
                if score >= self.high_threshold * 100:  # High confidence threshold
                    entity = self._find_entity_by_name(match_name)
                    if entity:
                        matches.append((entity, score / 100.0))
                        high_confidence_found = True
                        # Early termination: if we have enough high-confidence matches, stop
                        if len(matches) >= max_results:
                            break
                
                # If we found high confidence matches, don't process lower confidence ones
                if high_confidence_found and score < self.high_threshold * 100:
                    break
                    
                # Continue with medium confidence matches only if no high confidence found
                if not high_confidence_found and score >= self.medium_threshold * 100:
                    entity = self._find_entity_by_name(match_name)
                    if entity:
                        matches.append((entity, score / 100.0))
        else:
            # Fallback to trie-based matching with early termination
            matches = self._trie_based_matching(query_lower, max_results)
        
        # Sort by score and return top matches (already limited by early termination)
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:max_results]
    
    def _find_entity_by_name(self, name: str) -> Optional[Entity]:
        """Find entity by name (handles aliases)."""
        # Direct lookup first
        # Get all entities
        all_entities = self._get_all_entities()
        
        # Direct lookup first
        if name in all_entities:
            return all_entities[name]
        
        # Search through all entities for aliases
        for entity in all_entities.values():
            if name == entity.name.lower() or name in [alias.lower() for alias in entity.aliases]:
                return entity
        
        return None
    
    def _trie_based_matching(self, query: str, max_results: int) -> List[Tuple[Entity, float]]:
        """Fallback trie-based matching when thefuzz is not available."""
        matches = []
        
        # Try exact prefix match first
        node = self.trie_root
        for char in query:
            if char not in node.children:
                break
            node = node.children[char]
            if node.is_end:
                for entity in node.entities:
                    score = self._calculate_score(query, entity.name.lower())
                    matches.append((entity, score))
        
        return matches
    
    def _calculate_score(self, query: str, entity_name: str) -> float:
        """Calculate similarity score between query and entity name."""
        if query == entity_name:
            return 1.0
        
        if query in entity_name:
            return 0.8
        
        if entity_name in query:
            return 0.6
        
        # Simple character overlap scoring
        query_chars = set(query)
        entity_chars = set(entity_name)
        overlap = len(query_chars & entity_chars)
        total = len(query_chars | entity_chars)
        
        return overlap / total if total > 0 else 0.0
    
    def get_confidence_level(self, score: float) -> str:
        """Get confidence level based on score."""
        if score >= self.high_threshold:
            return "high"
        elif score >= self.medium_threshold:
            return "medium"
        else:
            return "low"
    
    def should_auto_correct(self, score: float) -> bool:
        """Determine if score is high enough for auto-correction."""
        return score >= self.high_threshold
    
    def should_suggest_correction(self, score: float) -> bool:
        """Determine if score is high enough to suggest correction."""
        return score >= self.medium_threshold


class DisambiguationDialogue:
    """Handle disambiguation when multiple fuzzy matches are found."""
    
    def __init__(self, fuzzy_matcher: FuzzyMatcher):
        """Initialize disambiguation dialogue with fuzzy matcher."""
        self.fuzzy_matcher = fuzzy_matcher
    
    def handle_multiple_matches(self, query: str, matches: List[Tuple[Entity, float]]) -> Dict[str, Any]:
        """Handle multiple fuzzy matches by creating disambiguation dialogue.
        
        Args:
            query: Original user query
            matches: List of (entity, score) tuples
            
        Returns:
            Dictionary with disambiguation information
        """
        if len(matches) == 0:
            return {"needs_disambiguation": False}
        elif len(matches) == 1:
            # Single match - auto-select if confidence is high enough
            entity, score = matches[0]
            if score >= self.fuzzy_matcher.high_threshold:
                return {
                    "needs_disambiguation": False,
                    "auto_selected": entity,
                    "confidence": "high"
                }
            else:
                return {"needs_disambiguation": False}
        
        # Filter matches by confidence level
        high_confidence = [m for m in matches if m[1] >= self.fuzzy_matcher.high_threshold]
        medium_confidence = [m for m in matches if m[1] >= self.fuzzy_matcher.medium_threshold]
        
        if len(high_confidence) == 1:
            # Single high confidence match - auto-select
            return {
                "needs_disambiguation": False,
                "auto_selected": high_confidence[0][0],
                "confidence": "high"
            }
        elif len(high_confidence) > 1:
            # Multiple high confidence matches - need disambiguation
            return self._create_disambiguation_options(query, high_confidence, "high")
        elif len(medium_confidence) > 1:
            # Multiple medium confidence matches - need disambiguation
            return self._create_disambiguation_options(query, medium_confidence, "medium")
        else:
            # Low confidence matches - suggest alternatives
            return self._create_suggestion_options(query, matches)
    
    def _create_disambiguation_options(self, query: str, matches: List[Tuple[Entity, float]], confidence_level: str) -> Dict[str, Any]:
        """Create disambiguation options for multiple matches."""
        options = []
        for i, (entity, score) in enumerate(matches[:5]):  # Limit to 5 options
            options.append({
                "index": i + 1,
                "entity": entity.name,
                "aliases": entity.aliases[:2],  # Show first 2 aliases
                "entity_type": entity.entity_type.value,
                "score": score,
                "description": self._get_entity_description(entity)
            })
        
        return {
            "needs_disambiguation": True,
            "confidence_level": confidence_level,
            "query": query,
            "options": options,
            "message": self._generate_disambiguation_message(query, confidence_level, len(options))
        }
    
    def _create_suggestion_options(self, query: str, matches: List[Tuple[Entity, float]]) -> Dict[str, Any]:
        """Create suggestion options for low confidence matches."""
        suggestions = []
        for entity, score in matches[:3]:  # Top 3 suggestions
            suggestions.append({
                "entity": entity.name,
                "aliases": entity.aliases[:1],
                "entity_type": entity.entity_type.value,
                "score": score
            })
        
        return {
            "needs_disambiguation": False,
            "needs_suggestion": True,
            "query": query,
            "suggestions": suggestions,
            "message": f"Did you mean one of these? {', '.join([s['entity'] for s in suggestions])}"
        }
    
    def _get_entity_description(self, entity: Entity) -> str:
        """Get a brief description of the entity for disambiguation."""
        if entity.entity_type == EntityType.TOOL:
            return f"Security tool: {entity.name}"
        elif entity.entity_type == EntityType.TECHNIQUE:
            return f"Attack technique: {entity.name}"
        elif entity.entity_type == EntityType.VULNERABILITY:
            return f"Vulnerability: {entity.name}"
        elif entity.entity_type == EntityType.PROTOCOL:
            return f"Network protocol: {entity.name}"
        elif entity.entity_type == EntityType.PLATFORM:
            return f"Platform: {entity.name}"
        else:
            return f"Security concept: {entity.name}"
    
    def _generate_disambiguation_message(self, query: str, confidence_level: str, num_options: int) -> str:
        """Generate disambiguation message for user."""
        if confidence_level == "high":
            return f"I found multiple high-confidence matches for '{query}'. Which one did you mean?"
        else:
            return f"I found {num_options} possible matches for '{query}'. Which one did you mean?"
    
    def resolve_disambiguation(self, disambiguation_info: Dict[str, Any], user_choice: int) -> Optional[Entity]:
        """Resolve user's disambiguation choice.
        
        Args:
            disambiguation_info: Information from handle_multiple_matches
            user_choice: User's choice (1-based index)
            
        Returns:
            Selected entity or None if invalid choice
        """
        if not disambiguation_info.get("needs_disambiguation", False):
            return None
        
        options = disambiguation_info.get("options", [])
        if 1 <= user_choice <= len(options):
            selected_option = options[user_choice - 1]
            # Find the entity by name
            for entity in self.fuzzy_matcher._entity_map.values():
                if entity.name == selected_option["entity"]:
                    return entity
        
        return None

class PerformanceMonitor:
    """Monitor performance metrics for optimization."""
    
    def __init__(self):
        """Initialize performance monitor with empty metrics."""
        self.timings: Dict[str, List[float]] = defaultdict(list)
        self.cache_hits = 0
        self.cache_misses = 0
        self.entity_lookups = 0
        self.singleton_benefits = 0  # Track singleton pattern benefits
        self.early_terminations = 0  # Track early termination benefits
        self.precompiled_pattern_hits = 0  # Track pre-compiled pattern benefits
    
    def time_operation(self, operation_name: str):
        """Decorator to time operations."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                result = func(*args, **kwargs)
                end_time = time.perf_counter()
                self.timings[operation_name].append(end_time - start_time)
                return result
            return wrapper
        return decorator
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        stats = {}
        for operation, times in self.timings.items():
            if times:
                stats[operation] = {
                    'count': len(times),
                    'total_time': sum(times),
                    'avg_time': sum(times) / len(times),
                    'min_time': min(times),
                    'max_time': max(times)
                }
        
        stats['cache'] = {
            'hits': self.cache_hits,
            'misses': self.cache_misses,
            'hit_rate': self.cache_hits / max(1, self.cache_hits + self.cache_misses)
        }
        
        stats['entity_lookups'] = self.entity_lookups
        
        # Optimization benefits
        stats['optimization_benefits'] = {
            'singleton_benefits': self.singleton_benefits,
            'early_terminations': self.early_terminations,
            'precompiled_pattern_hits': self.precompiled_pattern_hits,
            'total_optimizations': (self.singleton_benefits + 
                                  self.early_terminations + 
                                  self.precompiled_pattern_hits)
        }
        
        return stats

class DataDrivenKnowledgeBase:
    """High-performance cybersecurity knowledge base using data.py with singleton pattern."""
    
    _instance: Optional['DataDrivenKnowledgeBase'] = None
    _initialized: bool = False
    
    def __new__(cls, enable_monitoring: bool = False):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, enable_monitoring: bool = False):
        """Initialize data-driven knowledge base with lazy loading.
        
        Args:
            enable_monitoring: Whether to enable performance monitoring.
        """
        # Only initialize once, even if called multiple times
        if self._initialized:
            return
            
        self.enable_monitoring = enable_monitoring
        self.monitor = PerformanceMonitor() if enable_monitoring else None
        
        # Lazy loading flags
        self._data_loaded = False
        self._indexes_built = False
        
        # High-performance indexes
        self._tool_index: Dict[str, Entity] = {}
        self._technique_index: Dict[str, Entity] = {}
        self._vulnerability_index: Dict[str, Entity] = {}
        self._protocol_index: Dict[str, Entity] = {}
        self._platform_index: Dict[str, Entity] = {}
        
        # Fast lookup structures
        self._alias_index: Dict[str, Entity] = {}
        self._fuzzy_matcher = FuzzyMatcher(high_threshold=0.8, medium_threshold=0.6)
        self._disambiguation_dialogue = DisambiguationDialogue(self._fuzzy_matcher)
        self._entity_cache: Dict[str, Optional[Entity]] = {}
        
        # Data.py integration
        self._explain_db: Optional[Dict] = None
        self._tip_db: Optional[Dict] = None
        self._assist_db: Optional[Dict] = None
        self._report_db: Optional[Dict] = None
        self._quiz_db: Optional[Dict] = None
        self._plan_db: Optional[Dict] = None
        
        # Mark as initialized
        self._initialized = True
    
    @classmethod
    def get_instance(cls, enable_monitoring: bool = False) -> 'DataDrivenKnowledgeBase':
        """Get the singleton instance of the knowledge base."""
        if cls._instance is None:
            cls._instance = cls(enable_monitoring)
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (for testing)."""
        cls._instance = None
        cls._initialized = False
    
    def _lazy_load_data(self) -> None:
        """Lazy load data.py only when needed."""
        if self._data_loaded:
            return
        
        try:
            # Import data.py modules
            from . import data
            
            self._explain_db = data.EXPLAIN_DB
            self._tip_db = data.TIP_DB
            self._assist_db = data.ASSIST_DB
            self._report_db = data.REPORT_DB
            self._quiz_db = data.QUIZ_DB
            self._plan_db = data.PLAN_DB
            
            self._data_loaded = True
            
        except ImportError:
            # Fallback to embedded knowledge if data.py not available
            self._load_fallback_knowledge()
            self._data_loaded = True
    
    def _load_fallback_knowledge(self) -> None:
        """Load fallback knowledge base (original implementation)."""
        # Network Scanning Tools
        self._tool_index.update({
            "nmap": Entity("nmap", EntityType.TOOL, ["network mapper", "port scanner"], ["masscan", "rustscan"]),
            "masscan": Entity("masscan", EntityType.TOOL, ["fast scanner"], ["nmap", "rustscan"]),
            "rustscan": Entity("rustscan", EntityType.TOOL, ["rust scanner"], ["nmap", "masscan"]),
            "burp": Entity("burp", EntityType.TOOL, ["burp suite", "burpsuite"], ["zaproxy", "owasp zap"]),
            "sqlmap": Entity("sqlmap", EntityType.TOOL, ["sql mapper"], ["burp", "havij"]),
            "gobuster": Entity("gobuster", EntityType.TOOL, ["directory buster"], ["dirb", "dirbuster", "ffuf"]),
            "ffuf": Entity("ffuf", EntityType.TOOL, ["fuzz faster u fool"], ["gobuster", "wfuzz"]),
            "nikto": Entity("nikto", EntityType.TOOL, ["web scanner"], ["nmap", "openvas"]),
            "hydra": Entity("hydra", EntityType.TOOL, ["password cracker"], ["john", "hashcat"]),
            "john": Entity("john", EntityType.TOOL, ["john the ripper"], ["hashcat", "hydra"]),
            "hashcat": Entity("hashcat", EntityType.TOOL, ["hash cracker"], ["john", "hydra"]),
            "metasploit": Entity("metasploit", EntityType.TOOL, ["msf", "framework"], ["exploit-db", "searchsploit"]),
            "wireshark": Entity("wireshark", EntityType.TOOL, ["packet analyzer"], ["tcpdump", "tshark"]),
            "tcpdump": Entity("tcpdump", EntityType.TOOL, ["packet capture"], ["wireshark", "tshark"]),
            "tshark": Entity("tshark", EntityType.TOOL, ["wireshark cli"], ["wireshark", "tcpdump"]),
            "netcat": Entity("netcat", EntityType.TOOL, ["nc", "swiss army knife"], ["ncat", "socat"]),
            "nc": Entity("nc", EntityType.TOOL, ["netcat"], ["netcat", "ncat"]),
        })
        
        # Techniques
        self._technique_index.update({
            "sql injection": Entity("sql injection", EntityType.TECHNIQUE, ["sqli", "sql"], ["xss", "csrf"]),
            "xss": Entity("xss", EntityType.TECHNIQUE, ["cross-site scripting"], ["csrf", "sql injection"]),
            "csrf": Entity("csrf", EntityType.TECHNIQUE, ["cross-site request forgery"], ["xss", "sql injection"]),
            "ssrf": Entity("ssrf", EntityType.TECHNIQUE, ["server-side request forgery"], ["xxe", "rce"]),
            "xxe": Entity("xxe", EntityType.TECHNIQUE, ["xml external entity"], ["ssrf", "rce"]),
            "rce": Entity("rce", EntityType.TECHNIQUE, ["remote code execution"], ["xxe", "ssrf"]),
            "lfi": Entity("lfi", EntityType.TECHNIQUE, ["local file inclusion"], ["rfi", "path traversal"]),
            "rfi": Entity("rfi", EntityType.TECHNIQUE, ["remote file inclusion"], ["lfi", "rce"]),
            "ssti": Entity("ssti", EntityType.TECHNIQUE, ["server-side template injection"], ["rce", "xss"]),
            "privilege escalation": Entity("privilege escalation", EntityType.TECHNIQUE, ["privesc", "escalation"], ["buffer overflow", "kernel exploit"]),
            "buffer overflow": Entity("buffer overflow", EntityType.TECHNIQUE, ["bof", "overflow"], ["format string", "heap spray"]),
            "port scanning": Entity("port scanning", EntityType.TECHNIQUE, ["port scan", "scanning"], ["service enumeration", "reconnaissance"]),
            "service enumeration": Entity("service enumeration", EntityType.TECHNIQUE, ["service enum", "enumeration"], ["port scanning", "vulnerability scanning"]),
            "post-exploitation": Entity("post-exploitation", EntityType.TECHNIQUE, ["post-exploit", "post"], ["privilege escalation", "lateral movement"]),
            "lateral movement": Entity("lateral movement", EntityType.TECHNIQUE, ["lateral", "movement"], ["post-exploitation", "credential reuse"]),
        })
        
        # Vulnerabilities
        self._vulnerability_index.update({
            "cve": Entity("cve", EntityType.VULNERABILITY, ["common vulnerabilities"], ["exploit", "patch"]),
            "exploit": Entity("exploit", EntityType.VULNERABILITY, ["exploitation"], ["payload", "shellcode"]),
            "payload": Entity("payload", EntityType.VULNERABILITY, ["malicious code"], ["exploit", "shellcode"]),
            "shellcode": Entity("shellcode", EntityType.VULNERABILITY, ["executable code"], ["payload", "exploit"]),
            "vulnerability": Entity("vulnerability", EntityType.VULNERABILITY, ["vuln", "security issue"], ["exploit", "patch"]),
            "security flaw": Entity("security flaw", EntityType.VULNERABILITY, ["flaw", "weakness"], ["vulnerability", "exploit"]),
        })
        
        # Protocols
        self._protocol_index.update({
            "http": Entity("http", EntityType.PROTOCOL, ["hypertext transfer"], ["https", "web"]),
            "https": Entity("https", EntityType.PROTOCOL, ["secure http"], ["http", "ssl", "tls"]),
            "ssh": Entity("ssh", EntityType.PROTOCOL, ["secure shell"], ["telnet", "rlogin"]),
            "ftp": Entity("ftp", EntityType.PROTOCOL, ["file transfer"], ["sftp", "tftp"]),
            "smb": Entity("smb", EntityType.PROTOCOL, ["server message block"], ["cifs", "netbios"]),
            "ldap": Entity("ldap", EntityType.PROTOCOL, ["lightweight directory"], ["active directory", "kerberos"]),
            "dns": Entity("dns", EntityType.PROTOCOL, ["domain name system"], ["domain", "subdomain"]),
        })
        
        # Platforms
        self._platform_index.update({
            "linux": Entity("linux", EntityType.PLATFORM, ["unix", "gnu/linux"], ["ubuntu", "centos", "debian"]),
            "windows": Entity("windows", EntityType.PLATFORM, ["microsoft windows"], ["win", "microsoft"]),
            "macos": Entity("macos", EntityType.PLATFORM, ["mac os", "apple"], ["mac", "osx"]),
            "android": Entity("android", EntityType.PLATFORM, ["google android"], ["mobile", "phone"]),
            "ios": Entity("ios", EntityType.PLATFORM, ["apple ios"], ["iphone", "ipad"]),
        })
    
    def _build_indexes(self) -> None:
        """Build high-performance indexes from loaded data."""
        if self._indexes_built:
            return
        
        self._lazy_load_data()
        
        # Build indexes from data.py if available
        if self._explain_db:
            self._build_indexes_from_data()
        else:
            # Use fallback data - ensure it's loaded
            if not self._tool_index:
                self._load_fallback_knowledge()
        
        # Build alias index
        self._build_alias_index()
        
        # Build fuzzy matcher
        all_entities = self._get_all_entities()
        self._fuzzy_matcher.build_trie(all_entities, self._alias_index)
        
        self._indexes_built = True
    
    def _build_indexes_from_data(self) -> None:
        """Build indexes from data.py content."""
        if not self._explain_db:
            return
        
        # Extract entities from EXPLAIN_DB (tools)
        self._extract_entities_from_explain_db()
        
        # Extract entities from other databases (techniques)
        self._extract_entities_from_other_dbs()
        
        # Add fallback entities for missing categories
        self._add_fallback_entities()
    
    def _extract_entities_from_explain_db(self) -> None:
        """Extract entities from EXPLAIN_DB."""
        for tool_name in self._explain_db.keys():
            if not self._entity_exists_in_any_index(tool_name):
                entity = self._create_entity_from_name(tool_name)
                self._store_entity_in_index(entity)
    
    def _extract_entities_from_other_dbs(self) -> None:
        """Extract entities from other databases (tip, assist, report, quiz, plan)."""
        databases = [
            ("tip", self._tip_db),
            ("assist", self._assist_db),
            ("report", self._report_db),
            ("quiz", self._quiz_db),
            ("plan", self._plan_db)
        ]
        
        for db_name, db_content in databases:
            if db_content:
                for technique_name in db_content.keys():
                    if not self._entity_exists_in_any_index(technique_name):
                        entity = self._create_entity_from_name(technique_name, EntityType.TECHNIQUE)
                        self._technique_index[technique_name] = entity
    
    def _entity_exists_in_any_index(self, name: str) -> bool:
        """Check if entity exists in any index."""
        return (name in self._tool_index or 
                name in self._technique_index or
                name in self._vulnerability_index or
                name in self._protocol_index or
                name in self._platform_index)
    
    def _create_entity_from_name(self, name: str, entity_type: Optional[EntityType] = None) -> Entity:
        """Create entity from name with classification and relationships."""
        if entity_type is None:
            entity_type = self._classify_entity_type(name)
        
        aliases = self._extract_aliases(name)
        related = self._extract_related_entities(name)
        
        return Entity(name, entity_type, aliases, related)
    
    def _store_entity_in_index(self, entity: Entity) -> None:
        """Store entity in appropriate index based on type."""
        index_map = {
            EntityType.TOOL: self._tool_index,
            EntityType.TECHNIQUE: self._technique_index,
            EntityType.VULNERABILITY: self._vulnerability_index,
            EntityType.PROTOCOL: self._protocol_index,
            EntityType.PLATFORM: self._platform_index,
        }
        
        target_index = index_map.get(entity.entity_type)
        if target_index is not None:
            target_index[entity.name] = entity
    
    def _add_fallback_entities(self) -> None:
        """Add fallback entities for categories not covered by data.py."""
        # Add vulnerabilities if none exist
        if not self._vulnerability_index:
            self._vulnerability_index.update({
                "cve": Entity("cve", EntityType.VULNERABILITY, ["common vulnerabilities"], ["exploit", "patch"]),
                "exploit": Entity("exploit", EntityType.VULNERABILITY, ["exploitation"], ["payload", "shellcode"]),
                "payload": Entity("payload", EntityType.VULNERABILITY, ["malicious code"], ["exploit", "shellcode"]),
                "shellcode": Entity("shellcode", EntityType.VULNERABILITY, ["executable code"], ["payload", "exploit"]),
                "vulnerability": Entity("vulnerability", EntityType.VULNERABILITY, ["vuln", "security issue"], ["exploit", "patch"]),
                "security flaw": Entity("security flaw", EntityType.VULNERABILITY, ["flaw", "weakness"], ["vulnerability", "exploit"]),
            })
        
        # Add protocols if none exist
        if not self._protocol_index:
            self._protocol_index.update({
                "http": Entity("http", EntityType.PROTOCOL, ["hypertext transfer"], ["https", "web"]),
                "https": Entity("https", EntityType.PROTOCOL, ["secure http"], ["http", "ssl", "tls"]),
                "ssh": Entity("ssh", EntityType.PROTOCOL, ["secure shell"], ["telnet", "rlogin"]),
                "ftp": Entity("ftp", EntityType.PROTOCOL, ["file transfer"], ["sftp", "tftp"]),
                "smb": Entity("smb", EntityType.PROTOCOL, ["server message block"], ["cifs", "netbios"]),
                "ldap": Entity("ldap", EntityType.PROTOCOL, ["lightweight directory"], ["active directory", "kerberos"]),
                "dns": Entity("dns", EntityType.PROTOCOL, ["domain name system"], ["domain", "subdomain"]),
            })
        
        # Add platforms if none exist
        if not self._platform_index:
            self._platform_index.update({
                "linux": Entity("linux", EntityType.PLATFORM, ["unix", "gnu/linux"], ["ubuntu", "centos", "debian"]),
                "windows": Entity("windows", EntityType.PLATFORM, ["microsoft windows"], ["win", "microsoft"]),
                "macos": Entity("macos", EntityType.PLATFORM, ["mac os", "apple"], ["mac", "osx"]),
                "android": Entity("android", EntityType.PLATFORM, ["google android"], ["mobile", "phone"]),
                "ios": Entity("ios", EntityType.PLATFORM, ["apple ios"], ["iphone", "ipad"]),
            })
    
    def _classify_entity_type(self, name: str) -> EntityType:
        """Classify entity type based on name patterns."""
        name_lower = name.lower()
        
        # Known tools from data.py (most common first)
        known_tools = {
            'nmap', 'masscan', 'rustscan', 'wireshark', 'tcpdump', 'tshark', 'termshark',
            'unicornscan', 'naabu', 'netcat', 'ncat', 'socat', 'proxychains', 'dig',
            'dnsenum', 'fierce', 'ettercap', 'bettercap', 'arpspoof', 'responder',
            'volatility', 'rekall', 'lime', 'autopsy', 'sleuthkit', 'ftk', 'dd',
            'binwalk', 'exiftool', 'strings', 'foremost', 'networkminer', 'xplico',
            'andriller', 'aleapp', 'ghidra', 'ida', 'radare2', 'binaryninja', 'gdb',
            'pwndbg', 'x64dbg', 'edb', 'objdump', 'readelf', 'nm', 'file', 'ltrace',
            'strace', 'frida', 'burp', 'gobuster', 'ffuf', 'nikto', 'dirb', 'wpscan',
            'sqlmap', 'metasploit', 'msfvenom', 'john', 'hashcat', 'hydra', 'aircrack-ng',
            'hashid', 'hash-identifier', 'openssl', 'linpeas', 'winpeas', 'sudo'
        }
        
        if name_lower in known_tools:
            return EntityType.TOOL
        
        # EXPANDED: Known techniques with acronyms
        known_techniques = {
            # Full names
            'kerberoasting', 'pass-the-hash', 'pass-the-ticket', 'golden-ticket',
            'dcsync', 'ssrf', 'xxe', 'deserialization', 'ssti', 'http-smuggling',
            'suid-exploitation', 'sudo-misconfig', 'kernel-exploits', 'token-impersonation',
            'dll-hijacking', 'arp-spoofing', 'dns-spoofing', 'vlan-hopping', 'ipv6-mitm',
            'smb-relay', 'sql injection', 'xss', 'csrf', 'lfi', 'rfi', 'rce',
            'privilege escalation', 'buffer overflow', 'format string', 'port scanning',
            'service enumeration', 'vulnerability scanning', 'post-exploitation',
            'lateral movement', 'credential reuse',
            
            # NEW: Common acronyms and abbreviations
            'sqli', 'idor', 'cors', 'crlf', 'bof', 'uaf', 'rop', 'jop',
            'mitm', 'dos', 'ddos', 'business logic',
        }
        
        if name_lower in known_techniques:
            return EntityType.TECHNIQUE
        
        # NEW: Acronym expansion mapping
        acronym_expansions = {
            'sqli': 'sql injection',
            'xss': 'cross-site scripting',
            'csrf': 'cross-site request forgery',
            'ssrf': 'server-side request forgery',
            'xxe': 'xml external entities',
            'rce': 'remote code execution',
            'lfi': 'local file inclusion',
            'rfi': 'remote file inclusion',
            'ssti': 'server-side template injection',
        }
        
        if name_lower in acronym_expansions:
            return EntityType.TECHNIQUE
        
        # Tool patterns (fallback)
        if any(pattern in name_lower for pattern in ['scan', 'map', 'dump', 'cat', 'walk', 'enum']):
            return EntityType.TOOL
        
        # Technique patterns (fallback)
        if any(pattern in name_lower for pattern in ['injection', 'overflow', 'escalation', 'movement', 'spoofing']):
            return EntityType.TECHNIQUE
        
        # Vulnerability patterns
        if any(pattern in name_lower for pattern in ['cve', 'exploit', 'vulnerability']):
            return EntityType.VULNERABILITY
        
        # Protocol patterns
        if any(pattern in name_lower for pattern in ['http', 'ssh', 'ftp', 'smb', 'ldap', 'dns']):
            return EntityType.PROTOCOL
        
        # Platform patterns
        if any(pattern in name_lower for pattern in ['linux', 'windows', 'macos', 'android', 'ios']):
            return EntityType.PLATFORM
        
        # Default to tool
        return EntityType.TOOL
    
    def _extract_aliases(self, name: str) -> List[str]:
        """Extract aliases for an entity."""
        aliases = []
        name_lower = name.lower()
        
        # Common alias patterns
        if name_lower == 'nmap':
            aliases.extend(['network mapper', 'port scanner'])
        elif name_lower == 'burp':
            aliases.extend(['burp suite', 'burpsuite'])
        elif name_lower == 'sqlmap':
            aliases.extend(['sql mapper'])
        elif name_lower == 'metasploit':
            aliases.extend(['msf', 'framework'])
        elif name_lower == 'wireshark':
            aliases.extend(['packet analyzer'])
        elif name_lower == 'netcat':
            aliases.extend(['nc', 'swiss army knife'])
        elif 'sql injection' in name_lower:
            aliases.extend(['sqli', 'sql'])
        elif 'cross-site scripting' in name_lower or name_lower == 'xss':
            aliases.extend(['cross-site scripting'])
        elif 'privilege escalation' in name_lower:
            aliases.extend(['privesc', 'escalation'])
        
        return aliases
    
    def _extract_related_entities(self, name: str) -> List[str]:
        """Extract related entities for an entity."""
        name_lower = name.lower()
        
        # Check tool relationships first
        tool_relations = self._get_tool_relationships(name_lower)
        if tool_relations:
            return tool_relations
        
        # Check technique relationships
        technique_relations = self._get_technique_relationships(name_lower)
        if technique_relations:
            return technique_relations
        
        return []
    
    def _get_tool_relationships(self, name_lower: str) -> List[str]:
        """Get tool-specific relationships."""
        tool_relations = {
            'nmap': ['masscan', 'rustscan'],
            'burp': ['zaproxy', 'owasp zap'],
            'sqlmap': ['burp', 'havij'],
            'gobuster': ['dirb', 'dirbuster', 'ffuf'],
            'hydra': ['john', 'hashcat'],
            'metasploit': ['exploit-db', 'searchsploit'],
            'wireshark': ['tcpdump', 'tshark'],
        }
        
        return tool_relations.get(name_lower, [])
    
    def _get_technique_relationships(self, name_lower: str) -> List[str]:
        """Get technique-specific relationships."""
        # Check for specific technique patterns
        if 'sql injection' in name_lower:
            return ['xss', 'csrf']
        elif name_lower == 'xss':
            return ['csrf', 'sql injection']
        elif name_lower == 'csrf':
            return ['xss', 'sql injection']
        elif name_lower == 'ssrf':
            return ['xxe', 'rce']
        elif name_lower == 'xxe':
            return ['ssrf', 'rce']
        elif name_lower == 'rce':
            return ['xxe', 'ssrf']
        
        return []
    
    def _build_alias_index(self) -> None:
        """Build fast alias lookup index."""
        all_entities = self._get_all_entities()
        
        for entity in all_entities.values():
            # Add entity name
            self._alias_index[entity.name.lower()] = entity
            
            # Add aliases
            for alias in entity.aliases:
                self._alias_index[alias.lower()] = entity
    
    def _get_all_entities(self) -> Dict[str, Entity]:
        """Get all entities from all indexes."""
        all_entities = {}
        all_entities.update(self._tool_index)
        all_entities.update(self._technique_index)
        all_entities.update(self._vulnerability_index)
        all_entities.update(self._protocol_index)
        all_entities.update(self._platform_index)
        return all_entities
    
    @lru_cache(maxsize=1000)
    def resolve_entity(self, text: str) -> Optional[Entity]:
        """High-performance entity resolution with enhanced fuzzy matching and early termination."""
        if self.monitor:
            self.monitor.entity_lookups += 1
        
        # Ensure indexes are built
        self._build_indexes()
        
        text_lower = text.lower().strip()
        
        # Check cache first (fastest path)
        if text_lower in self._entity_cache:
            if self.monitor:
                self.monitor.cache_hits += 1
            return self._entity_cache[text_lower]
        
        if self.monitor:
            self.monitor.cache_misses += 1
        
        # Fast hash lookup (O(1) operation)
        entity = self._alias_index.get(text_lower)
        if entity:
            self._entity_cache[text_lower] = entity
            return entity
        
        # Early termination for very short queries (likely not entities)
        if len(text_lower) < 2:
            self._entity_cache[text_lower] = None
            return None
        
        # Enhanced fuzzy matching with early termination
        fuzzy_matches = self._fuzzy_matcher.find_matches(text_lower, max_results=3)  # Reduced from 5
        if fuzzy_matches:
            # Check if we need disambiguation
            disambiguation_info = self._disambiguation_dialogue.handle_multiple_matches(text_lower, fuzzy_matches)
            
            if disambiguation_info.get("needs_disambiguation", False):
                # Return the disambiguation info instead of an entity
                self._entity_cache[text_lower] = disambiguation_info
                return disambiguation_info
            elif disambiguation_info.get("auto_selected"):
                # Auto-selected high confidence match
                entity = disambiguation_info["auto_selected"]
                self._entity_cache[text_lower] = entity
                return entity
            elif fuzzy_matches:
                # Single best match with confidence check
                best_match = fuzzy_matches[0]
                if best_match[1] >= 0.6:  # Only return if confidence is reasonable
                    entity = best_match[0]
                    self._entity_cache[text_lower] = entity
                    return entity
        
        # Cache miss with None result
        self._entity_cache[text_lower] = None
        return None
    
    def get_related_entities(self, entity: Entity) -> List[Entity]:
        """Get entities related to the given entity."""
        related = []
        for related_name in entity.related_entities:
            related_entity = self.resolve_entity(related_name)
            if related_entity:
                related.append(related_entity)
        return related
    
    def _find_entity_by_name(self, name: str) -> Optional[Entity]:
        """Find entity by name (handles aliases)."""
        # Direct lookup first
        # Get all entities
        all_entities = self._get_all_entities()
        
        # Direct lookup first
        if name in all_entities:
            return all_entities[name]
        
        # Search through all entities for aliases
        for entity in all_entities.values():
            if name == entity.name.lower() or name in [alias.lower() for alias in entity.aliases]:
                return entity
        
        return None
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        if not self.monitor:
            return {"monitoring_disabled": True}
        
        stats = self.monitor.get_stats()
        stats.update({
            "entities_loaded": len(self._get_all_entities()),
            "alias_index_size": len(self._alias_index),
            "cache_size": len(self._entity_cache),
            "data_loaded": self._data_loaded,
            "indexes_built": self._indexes_built
        })
        return stats
    
    def clear_cache(self) -> None:
        """Clear entity resolution cache."""
        self._entity_cache.clear()
        self.resolve_entity.cache_clear()
    
    # Legacy compatibility properties
    @property
    def tools(self) -> Dict[str, Entity]:
        """Legacy compatibility: tools property."""
        self._build_indexes()
        return self._tool_index
    
    @property
    def techniques(self) -> Dict[str, Entity]:
        """Legacy compatibility: techniques property."""
        self._build_indexes()
        return self._technique_index
    
    @property
    def vulnerabilities(self) -> Dict[str, Entity]:
        """Legacy compatibility: vulnerabilities property."""
        self._build_indexes()
        return self._vulnerability_index
    
    @property
    def protocols(self) -> Dict[str, Entity]:
        """Legacy compatibility: protocols property."""
        self._build_indexes()
        return self._protocol_index
    
    @property
    def platforms(self) -> Dict[str, Entity]:
        """Legacy compatibility: platforms property."""
        self._build_indexes()
        return self._platform_index
    
    @property
    def all_entities(self) -> Dict[str, Entity]:
        """Legacy compatibility: all_entities property."""
        self._build_indexes()
        return self._get_all_entities()

# Legacy compatibility
CybersecurityKnowledgeBase = DataDrivenKnowledgeBase


# ============================================================================
# Enhanced Intent Classification
# ============================================================================

class IntentClassifier:
    """Multi-layered intent classification with cybersecurity domain knowledge."""
    
    def __init__(self, enable_monitoring: bool = False):
        """Initialize intent classifier with shared knowledge base.
        
        Args:
            enable_monitoring: Whether to enable performance monitoring.
        """
        self.knowledge_base = DataDrivenKnowledgeBase.get_instance(enable_monitoring=enable_monitoring)
        self.confidence_threshold = 0.7
        self.enable_monitoring = enable_monitoring
        
        # Enhanced intent patterns with cybersecurity context
        self.intent_patterns = {
            IntentType.EXPLAIN: [
                r'how (?:do|can) i (.*)',
                r'how to (.*)',
                r'explain (.*)',
                r'what is (.*)',
                r'what\'s (.*)',
                r'tell me about (.*)',
                r'describe (.*)',
                r'show me (.*)',
                r'help me understand (.*)',
                r'learn about (.*)',
                r'teach me (.*)',
                r'what does (.*) do',
                r'how does (.*) work',
            ],
            IntentType.TIP: [
                r'tips? (?:on|for|about) (.*)',
                r'guide (?:for|to|on) (.*)',
                r'(?:how to )?learn (?:about )?(.*)',
                r'techniques? (?:for|on) (.*)',
                r'best practices? (?:for )?(.*)',
                r'methods? (?:for|to) (.*)',
                r'approaches? (?:for|to) (.*)',
                r'strategies? (?:for|to) (.*)',
            ],
            IntentType.PLAN: [
                r'what should i do (?:after|when|if) (.*)',
                r'what(?:\'s| is) (?:the )?next (?:step|after) (.*)',
                r'next steps (?:for|after) (.*)',
                r'i (?:found|got|have|see|discovered) (.*)',
                r'what to do (?:with|about) (.*)',
                r'help (?:me )?(?:with|plan) (.*)',
                r'what\'s next (?:for|after) (.*)',
                r'after (.*) what (?:should|do)',
            ],
            IntentType.ASSIST: [
                r'i\'?m getting (?:an? )?(.*)',
                r'(?:error|problem|issue):? (.*)',
                r'why (?:is|does|am|can\'t) (.*)',
                r'(?:how to )?fix (.*)',
                r'troubleshoot (.*)',
                r'debug (.*)',
                r'help (?:me )?(?:fix|solve) (.*)',
                r'not working (.*)',
                r'failing (.*)',
                r'broken (.*)',
                r'i\'m stuck(?: on| with)? (.*)',
                r'i am stuck(?: on| with)? (.*)',
                r'stuck(?: on| with)? (.*)',
                r'i am having (?:issues|problems|trouble) (?:with|in) (.*)',
                r'having (?:issues|problems|trouble) (?:with|in) (.*)',
                r'network error(?: with| in)? (.*)',
                r'connection (?:refused|failed|error)(?: with| in)? (.*)',
            ],
            IntentType.REPORT: [
                r'document (.*)',
                r'write (?:a )?(?:up |report (?:for|on) )?(.*)',
                r'report (.*)',
                r'create (?:a )?report (?:for )?(.*)',
                r'summarize (.*)',
                r'write up (.*)',
            ],
            IntentType.QUIZ: [
                r'test me (?:on )?(.*)',
                r'quiz (?:me )?(?:on |about )?(.*)',
                r'question(?:s)? (?:on |about )?(.*)',
                r'practice (.*)',
                r'exam (?:on )?(.*)',
                r'challenge (?:me )?(?:on )?(.*)',
            ],
        }
        
        # Pre-compile regex patterns for better performance
        self._compiled_patterns = {}
        for intent_type, patterns in self.intent_patterns.items():
            self._compiled_patterns[intent_type] = [re.compile(pattern) for pattern in patterns]
    
    def classify_intent(self, query: str) -> IntentResult:
        """Classify user intent with confidence scoring."""
        query_lower = query.lower().strip()
        
        # Layer 1: Fast pattern-based classification
        primary_intent = self._fast_classify(query_lower)
        
        # Layer 2: Entity-based classification if confidence is low
        if primary_intent.confidence < self.confidence_threshold:
            entity_intent = self._entity_based_classify(query_lower)
            if entity_intent.confidence > primary_intent.confidence:
                primary_intent = entity_intent
        
        # Layer 3: Context-aware refinement
        refined_intent = self._context_refine(query_lower, primary_intent)
        
        return refined_intent
    
    def _fast_classify(self, query: str) -> IntentResult:
        """Fast pattern-based intent classification with pre-compiled patterns and early termination."""
        entities = []
        
        # Use pre-compiled patterns for better performance
        for intent_type, compiled_patterns in self._compiled_patterns.items():
            for compiled_pattern in compiled_patterns:
                match = compiled_pattern.match(query)
                if match:
                    # Early termination: return immediately on first match
                    entities = self._extract_entities(query)
                    return IntentResult(
                        intent=intent_type,
                        confidence=0.9,  # High confidence for pattern matches
                        entities=entities,
                        context={"pattern": compiled_pattern.pattern, "match": match.group(1)}
                    )
        
        # Default to explain with lower confidence
        entities = self._extract_entities(query)
        return IntentResult(
            intent=IntentType.EXPLAIN,
            confidence=0.3,
            entities=entities,
            context={"method": "default"}
        )
    
    def _entity_based_classify(self, query: str) -> IntentResult:
        """Classify intent based on detected entities."""
        entities = self._extract_entities(query)
        
        if not entities:
            return IntentResult(
                intent=IntentType.EXPLAIN,
                confidence=0.2,
                entities=[],
                context={"method": "no_entities"}
            )
        
        # Analyze entity types to infer intent
        tool_count = sum(1 for e in entities if e.entity_type == EntityType.TOOL)
        technique_count = sum(1 for e in entities if e.entity_type == EntityType.TECHNIQUE)
        
        if tool_count > 0:
            # Tools usually indicate explain intent
            return IntentResult(
                intent=IntentType.EXPLAIN,
                confidence=0.7,
                entities=entities,
                context={"method": "tool_detection", "tool_count": tool_count}
            )
        elif technique_count > 0:
            # Techniques usually indicate tip intent
            return IntentResult(
                intent=IntentType.TIP,
                confidence=0.7,
                entities=entities,
                context={"method": "technique_detection", "technique_count": technique_count}
            )
        
        return IntentResult(
            intent=IntentType.EXPLAIN,
            confidence=0.5,
            entities=entities,
            context={"method": "entity_fallback"}
        )
    
    def _context_refine(self, query: str, intent_result: IntentResult) -> IntentResult:
        """Refine intent based on additional context clues."""
        # Check for scenario indicators that suggest plan intent
        scenario_keywords = [
            'found', 'got', 'have', 'discovered', 'see', 'seeing',
            'stuck', 'after', 'next', 'shell', 'port', 'vulnerability',
            'target', 'enumeration', 'foothold', 'access', 'compromised'
        ]
        
        if any(keyword in query for keyword in scenario_keywords):
            if intent_result.intent != IntentType.PLAN:
                return IntentResult(
                    intent=IntentType.PLAN,
                    confidence=0.8,
                    entities=intent_result.entities,
                    context={**intent_result.context, "refined": "scenario_detection"}
                )
        
        # Check for error/problem indicators that suggest assist intent
        problem_keywords = [
            'error', 'problem', 'issue', 'not working', 'failing',
            'broken', 'trouble', 'stuck', 'help', 'fix', 'debug'
        ]
        
        if any(keyword in query for keyword in problem_keywords):
            if intent_result.intent != IntentType.ASSIST:
                return IntentResult(
                    intent=IntentType.ASSIST,
                    confidence=0.8,
                    entities=intent_result.entities,
                    context={**intent_result.context, "refined": "problem_detection"}
                )
        
        return intent_result
    
    def _extract_entities(self, query: str) -> List[Entity]:
        """Extract cybersecurity entities from query with enhanced fuzzy matching."""
        entities = []
        words = query.split()
        
        # Check for multi-word entities first
        for i in range(len(words)):
            for j in range(i + 1, min(i + 4, len(words) + 1)):  # Check up to 3-word phrases
                phrase = ' '.join(words[i:j])
                result = self.knowledge_base.resolve_entity(phrase)
                
                # Handle disambiguation info
                if isinstance(result, dict) and result.get("needs_disambiguation"):
                    # For now, just use the first option for multi-word phrases
                    # In a full implementation, this would trigger disambiguation dialogue
                    continue
                elif isinstance(result, Entity):
                    if result not in entities:
                        entities.append(result)
        
        # Check for single-word entities with fuzzy matching
        for word in words:
            result = self.knowledge_base.resolve_entity(word)
            
            # Handle disambiguation info
            if isinstance(result, dict) and result.get("needs_disambiguation"):
                # For single words, we can handle disambiguation more gracefully
                # Use the highest confidence match for now
                options = result.get("options", [])
                if options:
                    # Find the entity for the first option
                    first_option = options[0]
                    entity = self.knowledge_base._find_entity_by_name(first_option["entity"])
                    if entity and entity not in entities:
                        entities.append(entity)
            elif isinstance(result, Entity):
                if result not in entities:
                    entities.append(result)
        
        return entities


# ============================================================================
# Context Extraction and Understanding
# ============================================================================

class ContextExtractor:
    """Extract and analyze context from user queries."""
    
    def __init__(self, enable_monitoring: bool = False):
        """Initialize context extractor with shared knowledge base.
        
        Args:
            enable_monitoring: Whether to enable performance monitoring.
        """
        self.knowledge_base = DataDrivenKnowledgeBase.get_instance(enable_monitoring=enable_monitoring)
        self.enable_monitoring = enable_monitoring
    
    def extract_context(self, query: str, session_history: List[str] = None) -> Dict[str, Any]:
        """Extract comprehensive context information."""
        context = {
            "temporal": self._analyze_temporal_context(query, session_history),
            "domain": self._analyze_domain_context(query),
            "skill_level": self._infer_skill_level(query),
            "tools_mentioned": self._extract_tools(query),
            "techniques_mentioned": self._extract_techniques(query),
            "scenario": self._analyze_scenario(query),
            "urgency": self._analyze_urgency(query),
        }
        return context
    
    def _analyze_temporal_context(self, query: str, session_history: List[str]) -> Dict[str, Any]:
        """Analyze temporal context (when in the workflow)."""
        if not session_history:
            return {"stage": "unknown", "previous_commands": []}
        
        # Analyze recent commands to understand workflow stage
        recent_commands = session_history[-5:] if len(session_history) > 5 else session_history
        
        # Look for workflow indicators
        if any("scan" in cmd.lower() for cmd in recent_commands):
            return {"stage": "reconnaissance", "previous_commands": recent_commands}
        elif any("exploit" in cmd.lower() or "payload" in cmd.lower() for cmd in recent_commands):
            return {"stage": "exploitation", "previous_commands": recent_commands}
        elif any("shell" in cmd.lower() or "access" in cmd.lower() for cmd in recent_commands):
            return {"stage": "post-exploitation", "previous_commands": recent_commands}
        
        return {"stage": "unknown", "previous_commands": recent_commands}
    
    def _analyze_domain_context(self, query: str) -> Dict[str, Any]:
        """Analyze domain context (what cybersecurity area)."""
        query_lower = query.lower()
        
        domains = {
            "web": ["web", "http", "https", "xss", "sqli", "csrf", "burp", "nikto", "gobuster"],
            "network": ["network", "port", "scan", "nmap", "masscan", "wireshark", "tcpdump"],
            "forensics": ["forensic", "memory", "disk", "image", "pcap", "timeline"],
            "crypto": ["crypto", "hash", "encrypt", "decrypt", "john", "hashcat"],
            "mobile": ["mobile", "android", "ios", "app", "apk", "ipa"],
            "wireless": ["wireless", "wifi", "bluetooth", "aircrack", "reaver"],
            "reversing": ["reverse", "malware", "binary", "disassembly", "ida", "ghidra"],
        }
        
        detected_domains = []
        for domain, keywords in domains.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_domains.append(domain)
        
        return {
            "domains": detected_domains,
            "primary_domain": detected_domains[0] if detected_domains else "general"
        }
    
    def _infer_skill_level(self, query: str) -> str:
        """Infer user skill level from query language."""
        query_lower = query.lower()
        
        # Beginner indicators
        beginner_indicators = [
            "how do i", "how to", "what is", "explain", "learn", "beginner",
            "new to", "starting", "basics", "simple", "easy"
        ]
        
        # Advanced indicators
        advanced_indicators = [
            "advanced", "expert", "complex", "sophisticated", "optimize",
            "custom", "bypass", "evasion", "polymorphic", "obfuscation"
        ]
        
        if any(indicator in query_lower for indicator in beginner_indicators):
            return "beginner"
        elif any(indicator in query_lower for indicator in advanced_indicators):
            return "advanced"
        else:
            return "intermediate"
    
    def _extract_tools(self, query: str) -> List[str]:
        """Extract mentioned tools."""
        tools = []
        for tool_name, entity in self.knowledge_base.tools.items():
            if tool_name in query.lower() or any(alias in query.lower() for alias in entity.aliases):
                tools.append(tool_name)
        return tools
    
    def _extract_techniques(self, query: str) -> List[str]:
        """Extract mentioned techniques."""
        techniques = []
        for tech_name, entity in self.knowledge_base.techniques.items():
            if tech_name in query.lower() or any(alias in query.lower() for alias in entity.aliases):
                techniques.append(tech_name)
        return techniques
    
    def _analyze_scenario(self, query: str) -> Dict[str, Any]:
        """Analyze the scenario/situation described."""
        query_lower = query.lower()
        
        scenarios = {
            "discovery": ["found", "discovered", "see", "detected"],
            "troubleshooting": ["not working", "error", "problem", "stuck", "failing"],
            "learning": ["learn", "understand", "explain", "teach"],
            "planning": ["next", "after", "should", "plan", "strategy"],
            "reporting": ["document", "report", "write", "summarize"],
        }
        
        detected_scenarios = []
        for scenario, keywords in scenarios.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_scenarios.append(scenario)
        
        return {
            "scenarios": detected_scenarios,
            "primary_scenario": detected_scenarios[0] if detected_scenarios else "general"
        }
    
    def _analyze_urgency(self, query: str) -> str:
        """Analyze urgency level of the query."""
        query_lower = query.lower()
        
        urgent_indicators = ["urgent", "asap", "quickly", "immediately", "emergency", "critical"]
        if any(indicator in query_lower for indicator in urgent_indicators):
            return "high"
        
        moderate_indicators = ["soon", "today", "important", "priority"]
        if any(indicator in query_lower for indicator in moderate_indicators):
            return "medium"
        
        return "low"


# ============================================================================
# Ambiguity Resolution System
# ============================================================================

class AmbiguityResolver:
    """Resolve ambiguities in user queries."""
    
    def __init__(self, enable_monitoring: bool = False):
        """Initialize ambiguity resolver with shared knowledge base.
        
        Args:
            enable_monitoring: Whether to enable performance monitoring.
        """
        self.knowledge_base = DataDrivenKnowledgeBase.get_instance(enable_monitoring=enable_monitoring)
        self.enable_monitoring = enable_monitoring
    
    def detect_ambiguities(self, query: str, entities: List[Entity]) -> List[Dict[str, Any]]:
        """Detect potential ambiguities in the query."""
        ambiguities = []
        
        # Check for multiple possible intents
        if self._has_multiple_intents(query):
            ambiguities.append({
                "type": "multiple_intents",
                "description": "Query could be interpreted multiple ways",
                "options": self._get_intent_options(query)
            })
        
        # Check for ambiguous entities
        for entity in entities:
            if self._is_ambiguous_entity(entity):
                ambiguities.append({
                    "type": "ambiguous_entity",
                    "entity": entity.name,
                    "description": f"'{entity.name}' could refer to multiple concepts",
                    "options": self._get_entity_options(entity)
                })
        
        return ambiguities
    
    def _has_multiple_intents(self, query: str) -> bool:
        """Check if query could have multiple intents."""
        query_lower = query.lower()
        
        # Check for conflicting intent indicators
        explain_indicators = ["what is", "how does", "explain"]
        tip_indicators = ["tips", "techniques", "methods"]
        plan_indicators = ["what should", "next step", "after"]
        
        explain_count = sum(1 for indicator in explain_indicators if indicator in query_lower)
        tip_count = sum(1 for indicator in tip_indicators if indicator in query_lower)
        plan_count = sum(1 for indicator in plan_indicators if indicator in query_lower)
        
        # If multiple intent types are present, it's ambiguous
        intent_counts = [explain_count, tip_count, plan_count]
        return sum(1 for count in intent_counts if count > 0) > 1
    
    def _get_intent_options(self, query: str) -> List[str]:
        """Get possible intent interpretations."""
        return [
            "Explain what it is and how it works",
            "Provide tips and techniques",
            "Create a step-by-step plan"
        ]
    
    def _is_ambiguous_entity(self, entity: Entity) -> bool:
        """Check if entity is ambiguous."""
        # Entities with many aliases or related entities are more likely to be ambiguous
        return len(entity.aliases) > 2 or len(entity.related_entities) > 3
    
    def _get_entity_options(self, entity: Entity) -> List[str]:
        """Get possible entity interpretations."""
        options = [entity.name]
        options.extend(entity.aliases[:2])  # Limit to 2 aliases
        return options
    
    def generate_clarification(self, query: str, ambiguities: List[Dict[str, Any]]) -> Optional[str]:
        """Generate intelligent clarification questions."""
        if not ambiguities:
            return None
        
        # Prioritize ambiguities by impact
        primary_ambiguity = ambiguities[0]  # Take first ambiguity
        
        if primary_ambiguity["type"] == "multiple_intents":
            return f"I can help you with: {', '.join(primary_ambiguity['options'])}. Which one do you need?"
        
        elif primary_ambiguity["type"] == "ambiguous_entity":
            return f"When you say '{primary_ambiguity['entity']}', do you mean: {', '.join(primary_ambiguity['options'])}?"
        
        return None


# ============================================================================
# Performance Optimization and Caching
# ============================================================================

class ParserCache:
    """Cache for parser results to improve performance with memory-aware eviction."""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 50):
        """Initialize parser cache with size and memory limits.
        
        Args:
            max_size: Maximum number of cached results.
            max_memory_mb: Maximum memory usage in MB.
        """
        self.cache: Dict[str, UnderstandingResult] = {}
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.access_count: Dict[str, int] = {}
        self.access_times: Dict[str, float] = {}
        self._current_memory_usage = 0
    
    def get(self, query: str) -> Optional[UnderstandingResult]:
        """Get cached result for query with access tracking."""
        query_key = self._normalize_query(query)
        if query_key in self.cache:
            self.access_count[query_key] = self.access_count.get(query_key, 0) + 1
            self.access_times[query_key] = time.time()
            return self.cache[query_key]
        return None
    
    def put(self, query: str, result: UnderstandingResult) -> None:
        """Cache result for query with memory-aware eviction."""
        query_key = self._normalize_query(query)
        
        # Estimate memory usage of the result
        result_size = self._estimate_result_size(result)
        
        # Check if we need to evict based on size or count
        while (len(self.cache) >= self.max_size or 
               self._current_memory_usage + result_size > self.max_memory_bytes):
            self._evict_optimal()
        
        # Add to cache
        self.cache[query_key] = result
        self.access_count[query_key] = 1
        self.access_times[query_key] = time.time()
        self._current_memory_usage += result_size
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for consistent caching."""
        return query.lower().strip()
    
    def _estimate_result_size(self, result: UnderstandingResult) -> int:
        """Estimate memory usage of a result object."""
        # Rough estimation based on object attributes
        size = 0
        size += len(result.original_query) * 2  # Unicode chars
        size += len(result.processed_query) * 2
        size += len(result.entities) * 100  # Entity objects are complex
        size += len(str(result.parameters)) * 2
        return size
    
    def _evict_optimal(self) -> None:
        """Evict the optimal entry based on access frequency and recency."""
        if not self.cache:
            return
        
        current_time = time.time()
        
        # Calculate score for each entry (lower is better for eviction)
        eviction_scores = {}
        for key in self.cache.keys():
            access_count = self.access_count.get(key, 1)
            last_access = self.access_times.get(key, current_time)
            age = current_time - last_access
            
            # Score based on frequency and recency (lower score = more likely to evict)
            score = access_count / (1 + age / 3600)  # Age in hours
            eviction_scores[key] = score
        
        # Evict the entry with the lowest score
        lru_key = min(eviction_scores.keys(), key=lambda k: eviction_scores[k])
        
        # Update memory usage
        if lru_key in self.cache:
            result_size = self._estimate_result_size(self.cache[lru_key])
            self._current_memory_usage -= result_size
        
        # Remove from all tracking structures
        del self.cache[lru_key]
        if lru_key in self.access_count:
            del self.access_count[lru_key]
        if lru_key in self.access_times:
            del self.access_times[lru_key]
    
    def clear(self) -> None:
        """Clear all cached entries."""
        self.cache.clear()
        self.access_count.clear()
        self.access_times.clear()
        self._current_memory_usage = 0
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics with memory information."""
        total_accesses = sum(self.access_count.values())
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "memory_usage_mb": self._current_memory_usage / (1024 * 1024),
            "max_memory_mb": self.max_memory_bytes / (1024 * 1024),
            "hit_rate": len(self.cache) / max(1, total_accesses),
            "most_accessed": max(self.access_count.items(), key=lambda x: x[1]) if self.access_count else None,
            "memory_efficiency": self._current_memory_usage / max(1, self.max_memory_bytes)
        }


class QueryPreprocessor:
    """Preprocess queries for better parsing performance."""
    
    def __init__(self):
        """Initialize query preprocessor with common stopwords."""
        self.stopwords = {
            'the', 'a', 'an', 'to', 'for', 'with', 'about', 'on',
            'in', 'at', 'by', 'from', 'of', 'and', 'or', 'but',
            'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'can'
        }
    
    def preprocess(self, query: str) -> str:
        """Preprocess query for better parsing."""
        # Normalize whitespace
        query = re.sub(r'\s+', ' ', query.strip())
        
        # Remove excessive punctuation
        query = re.sub(r'[!]{2,}', '!', query)
        query = re.sub(r'[?]{2,}', '?', query)
        
        # Normalize case for better matching
        query = query.lower()
        
        return query
    
    def extract_keywords(self, query: str) -> List[str]:
        """Extract meaningful keywords from query."""
        words = query.split()
        keywords = []
        
        for word in words:
            # Remove punctuation
            word = re.sub(r'[^\w]', '', word)
            if word and word not in self.stopwords and len(word) > 2:
                keywords.append(word)
        
        return keywords


# ============================================================================
# Main Enhanced Parser
# ============================================================================

class IntelligentNLParser:
    """Enhanced natural language parser with context awareness and performance optimization."""
    
    def __init__(self, enable_caching: bool = True, cache_size: int = 1000, enable_monitoring: bool = False):
        """Initialize intelligent NL parser with all components.
        
        Args:
            enable_caching: Whether to enable result caching.
            cache_size: Maximum cache size for results.
            enable_monitoring: Whether to enable performance monitoring.
        """
        self.enable_monitoring = enable_monitoring
        self.intent_classifier = IntentClassifier(enable_monitoring=enable_monitoring)
        self.context_extractor = ContextExtractor(enable_monitoring=enable_monitoring)
        self.ambiguity_resolver = AmbiguityResolver(enable_monitoring=enable_monitoring)
        self.preprocessor = QueryPreprocessor()
        
        # Performance optimizations
        self.enable_caching = enable_caching
        self.cache = ParserCache(cache_size) if enable_caching else None
        
        # Pre-compiled regex patterns for better performance
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """Pre-compile regex patterns for better performance."""
        # This could be expanded to cache compiled patterns
        pass
    
    def parse_query(self, query: str, session_history: List[str] = None) -> UnderstandingResult:
        """Parse query with comprehensive understanding and performance optimization."""
        # Check cache first
        if self.cache:
            cached_result = self.cache.get(query)
            if cached_result:
                return cached_result
        
        # Preprocess query for better performance
        preprocessed_query = self.preprocessor.preprocess(query)
        
        # Extract entities and relationships
        entities = self.intent_classifier._extract_entities(preprocessed_query)
        
        # Classify intent
        intent_result = self.intent_classifier.classify_intent(preprocessed_query)
        
        # Extract context
        context = self.context_extractor.extract_context(preprocessed_query, session_history)
        
        # Check for ambiguities
        ambiguities = self.ambiguity_resolver.detect_ambiguities(preprocessed_query, entities)
        
        # Generate clarification if needed
        clarification_question = None
        if ambiguities:
            clarification_question = self.ambiguity_resolver.generate_clarification(preprocessed_query, ambiguities)
        
        # Build parameters
        parameters = {
            "entities": [e.name for e in entities],
            "context": context,
            "ambiguities": ambiguities,
            "keywords": self.preprocessor.extract_keywords(preprocessed_query),
        }
        
        # Clean and process query
        processed_query = self._clean_query(preprocessed_query)
        
        result = UnderstandingResult(
            intent=intent_result.intent,
            entities=entities,
            parameters=parameters,
            confidence=intent_result.confidence,
            original_query=query,
            processed_query=processed_query,
            clarification_needed=len(ambiguities) > 0,
            clarification_question=clarification_question
        )
        
        # Cache result if caching is enabled
        if self.cache:
            self.cache.put(query, result)
        
        return result
    
    def _clean_query(self, query: str) -> str:
        """Clean and normalize the query for better processing."""
        # For cybersecurity queries, preserve technical flags and parameters
        # Only remove very basic filler words that don't affect meaning
        
        # Preserve technical content - don't modify anything that looks like flags/parameters
        if any(char in query for char in ['-', '/', '\\', ':', '=']):
            # Contains technical syntax, preserve as-is
            return query
        
        # Only remove leading articles for simple queries
        stopwords = ['the', 'a', 'an']
        words = query.split()
        
        # Remove only leading articles, not technical terms
        while words and words[0].lower() in stopwords:
            words.pop(0)

        cleaned = ' '.join(words)
        return cleaned if cleaned else query
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get parser cache statistics."""
        if self.cache:
            return self.cache.stats()
        return {"caching_enabled": False}
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        stats = {
            "cache_stats": self.get_cache_stats(),
            "monitoring_enabled": self.enable_monitoring
        }
        
        if self.enable_monitoring:
            # Get stats from all components
            stats.update({
                "intent_classifier": self.intent_classifier.knowledge_base.get_performance_stats(),
                "context_extractor": self.context_extractor.knowledge_base.get_performance_stats(),
                "ambiguity_resolver": self.ambiguity_resolver.knowledge_base.get_performance_stats(),
            })
        
        return stats
    
    def clear_cache(self) -> None:
        """Clear parser cache."""
        if self.cache:
            self.cache.clear()
        
        # Clear knowledge base caches
        self.intent_classifier.knowledge_base.clear_cache()
        self.context_extractor.knowledge_base.clear_cache()
        self.ambiguity_resolver.knowledge_base.clear_cache()
    
    def parse_query_debug(self, query: str, session_history: List[str] = None) -> Dict[str, Any]:
        """Parse query with detailed debug information."""
        result = self.parse_query(query, session_history)
        
        return {
            "original_query": query,
            "preprocessed_query": self.preprocessor.preprocess(query),
            "intent": result.intent.value,
            "confidence": result.confidence,
            "entities": [{"name": e.name, "type": e.entity_type.value, "aliases": e.aliases} for e in result.entities],
            "parameters": result.parameters,
            "processed_query": result.processed_query,
            "clarification_needed": result.clarification_needed,
            "clarification_question": result.clarification_question,
            "cache_stats": self.get_cache_stats()
        }


# ============================================================================
# Legacy Compatibility Functions
# ============================================================================

def parse_natural_query(text: str) -> tuple[str, str]:
    """
    Parse natural language into (command, query) using enhanced intelligent parser.

    Examples:
        "how do I scan for open ports?" → ("explain", "port scanning")
        "what is burp suite?" → ("explain", "burp suite")
        "tips on sql injection" → ("tip", "sql injection")
        "I found an open port 8080" → ("plan", "post-exploitation")
        "i'm stuck on this nmap thing" → ("plan", "nmap troubleshooting")

    Returns:
        Tuple of (command_name, extracted_query)
    """
    # Use the enhanced parser
    parser = IntelligentNLParser()
    result = parser.parse_query(text)
    
    # If clarification is needed, return a special response
    if result.clarification_needed and result.clarification_question:
        return "clarify", result.clarification_question
    
    # Convert intent to string and get processed query
    command = result.intent.value
    query = result.processed_query
    
    return command, query


def _clean_query(query: str) -> str:
    """Remove filler words and clean up the extracted query."""
    # For cybersecurity queries, preserve technical flags and parameters
    # Only remove very basic filler words that don't affect meaning
    
    # Preserve technical content - don't modify anything that looks like flags/parameters
    if any(char in query for char in ['-', '/', '\\', ':', '=']):
        # Contains technical syntax, preserve as-is
        return query
    
    # Only remove leading articles for simple queries
    stopwords = ['the', 'a', 'an']
    words = query.split()
    
    # Remove only leading articles, not technical terms
    while words and words[0].lower() in stopwords:
        words.pop(0)

    cleaned = ' '.join(words)
    return cleaned if cleaned else query


def extract_topic(text: str) -> str:
    """
    Extract main topic/keywords from natural language query.

    Useful for fuzzy matching against knowledge base.
    """
    # Remove question words and common phrases
    question_patterns = [
        r'^how (?:do|can) i\s+',
        r'^how to\s+',
        r'^what is\s+',
        r'^what\'s\s+',
        r'^tell me about\s+',
        r'^explain\s+',
        r'^tips? on\s+',
        r'^help me\s+',
    ]

    text_lower = text.lower()
    for pattern in question_patterns:
        text_lower = re.sub(pattern, '', text_lower)

    # Remove trailing question marks and punctuation
    text_lower = re.sub(r'[?.!]+$', '', text_lower)

    return text_lower.strip()


def is_natural_language(text: str) -> bool:
    """
    Determine if text is a natural language query vs a direct command using enhanced detection.

    Examples:
        "how do I scan ports?" → True
        "explain nmap" → False (direct command)
        "nmap -sV target" → False (direct command)
        "i'm stuck on this nmap thing" → True
        "what should I do after getting a shell?" → True
    """
    text_lower = text.lower().strip()
    
    # Direct commands start with known command words
    command_words = ['explain', 'tip', 'help', 'report', 'quiz', 'plan', 'assist']
    if any(text_lower.startswith(cmd + ' ') for cmd in command_words):
        return False
    
    # Direct tool usage (tool name followed by flags/args)
    tool_keywords = [
        'nmap', 'burp', 'sqlmap', 'metasploit', 'wireshark',
        'hydra', 'john', 'hashcat', 'gobuster', 'ffuf',
        'nikto', 'dirb', 'wfuzz', 'netcat', 'nc', 'ssh',
        'tcpdump', 'masscan', 'enum4linux', 'smbclient'
    ]
    
    words = text_lower.split()
    if words and words[0] in tool_keywords:
        return False
    
    # Enhanced natural language indicators
    question_words = ['how', 'what', 'why', 'when', 'where', 'which']
    if any(text_lower.startswith(word) for word in question_words):
        return True
    
    # Contains question words anywhere
    if any(word in text_lower for word in question_words):
        return True
    
    # Enhanced natural language patterns
    natural_patterns = [
        'tell me', 'show me', 'help me', 'i need', 'i want',
        'can you', 'could you', 'would you', 'please',
        'tips on', 'guide for', 'learn about', 'best practices',
        'i\'m stuck', 'i\'m getting', 'not working', 'failing',
        'what should i do', 'next step', 'after i', 'when i',
        'how to', 'how do i', 'how can i', 'explain to me',
        'teach me', 'describe', 'understand', 'figure out'
    ]
    
    if any(pattern in text_lower for pattern in natural_patterns):
        return True
    
    # Enhanced scenario/situation language
    scenario_words = [
        'found', 'got', 'have', 'discovered', 'see', 'stuck',
        'after', 'next', 'shell', 'port', 'vulnerability',
        'target', 'enumeration', 'foothold', 'access',
        'compromised', 'exploited', 'injected', 'bypassed'
    ]
    
    if any(word in text_lower for word in scenario_words):
        return True
    
    # Check for conversational language
    conversational_indicators = [
        'i think', 'i believe', 'i guess', 'maybe', 'perhaps',
        'i wonder', 'i\'m confused', 'i don\'t understand',
        'this is', 'that is', 'it seems', 'looks like'
    ]
    
    if any(indicator in text_lower for indicator in conversational_indicators):
        return True
    
    # NEW: Single-word cybersecurity term detection
    if len(words) == 1:
        word = words[0]
        
        # Cybersecurity acronyms and abbreviations
        cybersec_terms = {
            # Techniques
            'ssti', 'sqli', 'xss', 'csrf', 'ssrf', 'xxe', 'rce', 'lfi', 'rfi',
            'idor', 'cors', 'crlf', 'bof', 'uaf', 'rop', 'jop',
            
            # Protocols and technologies
            'sql', 'http', 'https', 'ssh', 'ftp', 'smb', 'ldap', 'dns',
            'tcp', 'udp', 'icmp', 'ssl', 'tls', 'arp', 'dhcp',
            
            # Concepts
            'owasp', 'cve', 'cwe', 'cvss', 'mitm', 'dos', 'ddos',
            'api', 'jwt', 'oauth', 'saml', 'iam', 'rbac', 'mfa',
            
            # Additional common terms
            'authentication', 'authorization', 'encryption', 'hashing',
            'sanitization', 'validation', 'enumeration', 'reconnaissance'
        }
        
        if word in cybersec_terms:
            return True
        
        # Check if word exists in knowledge base
        try:
            from .nl_parser import IntelligentNLParser
            parser = IntelligentNLParser()
            entity = parser.intent_classifier.knowledge_base.resolve_entity(word)
            if entity is not None:
                return True
        except:
            # If knowledge base lookup fails, continue with other checks
            pass
    
    # Default: treat as natural language if it contains multiple words
    # and doesn't look like a direct command
    return len(words) > 1


def suggest_command_format(command: str, query: str) -> str:
    """
    Format the suggested command for display to user.

    Returns formatted string like:
    "🤔 I think you mean: explain 'nmap'"
    """
    return f"🤔 I think you mean: {command} '{query}'"


# Convenience function for testing
def demo():
    """Demo the enhanced natural language parser."""
    import logging
    
    # Configure logging for demo
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[logging.StreamHandler()]
    )
    logger = logging.getLogger(__name__)
    
    test_queries = [
        "how do I scan for open ports?",
        "what is burp suite?",
        "tips on sql injection",
        "I found an open port 22",
        "what should I do after getting a shell?",
        "document xss vulnerability",
        "test me on buffer overflow",
        "why is my scan not working?",
        "how to learn metasploit",
        "i'm stuck on this nmap thing",
        "help me understand privilege escalation",
        "what's the next step after finding XSS?",
        "explain nmap -sV",
        "nmap -sV target.local",
    ]

    logger.info("Enhanced Natural Language Parser Demo")
    logger.info("=" * 60)
    
    # Create parser instance with monitoring enabled
    parser = IntelligentNLParser(enable_monitoring=True)
    
    for query in test_queries:
        logger.info(f"\nQuery: {query}")
        
        # Test natural language detection
        is_nl = is_natural_language(query)
        logger.info(f"  Natural Language: {is_nl}")
        
        if is_nl:
            # Parse with enhanced parser
            result = parser.parse_query(query)
            logger.info(f"  Intent: {result.intent.value}")
            logger.info(f"  Confidence: {result.confidence:.2f}")
            logger.info(f"  Entities: {[e.name for e in result.entities]}")
            logger.info(f"  Processed Query: {result.processed_query}")
            
            if result.clarification_needed:
                logger.info(f"  Clarification: {result.clarification_question}")
        else:
            # Direct command
            command, extracted = parse_natural_query(query)
            suggestion = suggest_command_format(command, extracted)
            logger.info(f"  → {suggestion}")
    
    # Show performance stats
    logger.info(f"\nPerformance Statistics:")
    stats = parser.get_performance_stats()
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")


if __name__ == "__main__":
    demo()
