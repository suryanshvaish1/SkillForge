from __future__ import annotations

import re
from collections import defaultdict
from typing import Optional

from loguru import logger

from app.models.schemas import ExtractedSkill, SkillLevel

SKILL_TAXONOMY: dict[str, set[str]] = {
    # Programming languages
    "python": {"python", "python3", "py", "cpython"},
    "java": {"java", "j2ee", "jdk", "jvm", "core java", "java se", "java ee"},
    "javascript": {"javascript", "js", "ecmascript", "es6", "es2015"},
    "typescript": {"typescript", "ts"},
    "c++": {"c++", "cpp", "c plus plus"},
    "c#": {"c#", "csharp", "c sharp", ".net c#"},
    "go": {"go", "golang"},
    "rust": {"rust", "rust lang"},
    "ruby": {"ruby"},
    "php": {"php"},
    "swift": {"swift"},
    "kotlin": {"kotlin"},
    "scala": {"scala"},
    "r": {"r language", "r programming", "rstudio"},

    # Web development
    "react": {"react", "reactjs", "react.js", "react js"},
    "angular": {"angular", "angularjs", "angular.js"},
    "vue": {"vue", "vuejs", "vue.js"},
    "nextjs": {"next.js", "nextjs", "next js"},
    "nodejs": {"node.js", "nodejs", "node js", "node"},
    "express": {"express", "expressjs", "express.js"},
    "html": {"html", "html5"},
    "css": {"css", "css3", "scss", "sass", "less", "tailwind", "tailwindcss"},
    "graphql": {"graphql", "graph ql"},
    "rest api": {"rest", "rest api", "restful", "restful api"},
    "web development": {"web development", "web dev", "full stack", "fullstack", "full-stack"},

    # Data engineering
    "sql": {"sql", "structured query language", "t-sql", "pl/sql", "plsql"},
    "postgresql": {"postgresql", "postgres", "psql"},
    "mysql": {"mysql", "mariadb"},
    "mongodb": {"mongodb", "mongo"},
    "redis": {"redis"},
    "apache kafka": {"kafka", "apache kafka"},
    "apache spark": {"spark", "apache spark", "pyspark"},
    "apache airflow": {"airflow", "apache airflow"},
    "etl": {"etl", "extract transform load", "data pipeline", "data pipelines"},
    "data warehousing": {"data warehouse", "data warehousing", "dwh", "dimensional modeling"},
    "dbt": {"dbt", "data build tool"},
    "data engineering": {"data engineering", "data engineer"},

    # Data science & ML
    "machine learning": {"machine learning", "ml", "supervised learning", "unsupervised learning"},
    "deep learning": {"deep learning", "dl", "neural network", "neural networks"},
    "natural language processing": {"nlp", "natural language processing", "text mining", "text analytics"},
    "computer vision": {"computer vision", "cv", "image recognition", "object detection"},
    "scikit-learn": {"scikit-learn", "sklearn", "scikit learn"},
    "pytorch": {"pytorch", "torch"},
    "tensorflow": {"tensorflow", "tf", "keras"},
    "pandas": {"pandas"},
    "numpy": {"numpy"},
    "data analysis": {"data analysis", "data analytics", "exploratory data analysis", "eda"},
    "data visualization": {"data visualization", "data viz"},
    "statistics": {"statistics", "statistical analysis", "hypothesis testing"},
    "a/b testing": {"a/b testing", "ab testing", "experimentation", "split testing"},

    # BI tools
    "power bi": {"power bi", "powerbi", "power-bi", "dax"},
    "tableau": {"tableau"},
    "excel": {"excel", "microsoft excel", "ms excel", "spreadsheet"},
    "looker": {"looker"},

    # DevOps & Cloud
    "docker": {"docker", "containerization", "containers", "dockerfile"},
    "kubernetes": {"kubernetes", "k8s"},
    "aws": {"aws", "amazon web services", "ec2", "s3", "lambda", "sagemaker"},
    "azure": {"azure", "microsoft azure"},
    "gcp": {"gcp", "google cloud", "google cloud platform", "bigquery"},
    "terraform": {"terraform", "iac", "infrastructure as code"},
    "ci/cd": {"ci/cd", "cicd", "ci cd", "continuous integration", "continuous deployment",
              "github actions", "jenkins", "gitlab ci"},
    "linux": {"linux", "ubuntu", "centos", "debian", "bash", "shell scripting"},
    "git": {"git", "github", "gitlab", "version control", "bitbucket"},
    "monitoring": {"monitoring", "prometheus", "grafana", "datadog", "observability"},

    # Security
    "cybersecurity": {"cybersecurity", "information security", "infosec", "security"},
    "application security": {"application security", "appsec", "owasp", "secure coding"},
    "cloud security": {"cloud security", "iam", "identity and access management"},

    # PM & Agile
    "agile": {"agile", "scrum", "kanban", "sprint", "jira"},
    "product management": {"product management", "product manager", "product ownership", "roadmap"},
    "project management": {"project management", "pmp", "program management"},

    # Soft skills
    "leadership": {"leadership", "team lead", "tech lead", "team management", "people management"},
    "communication": {"communication", "technical writing", "presentation skills", "public speaking"},

    # Operations
    "warehouse management": {"warehouse management", "wms", "warehouse operations", "inventory management"},
    "supply chain": {"supply chain", "supply chain management", "logistics", "procurement"},
    "quality control": {"quality control", "qc", "quality assurance", "qa", "six sigma", "lean"},
    "manufacturing": {"manufacturing", "cnc", "machining", "production"},
    "equipment operation": {"equipment operation", "heavy equipment", "forklift", "machinery"},
    "workplace safety": {"workplace safety", "osha", "safety compliance", "ppe", "hazard identification"},

    # MLOps / AI Eng
    "mlops": {"mlops", "ml ops", "model deployment", "model serving", "mlflow"},
    "llm": {"llm", "large language model", "gpt", "prompt engineering", "langchain", "rag", "generative ai"},

    # Business analysis
    "business analysis": {"business analysis", "business analyst", "requirements engineering", "brd"},
}

# Experience-level keywords
LEVEL_KEYWORDS: dict[SkillLevel, set[str]] = {
    SkillLevel.BEGINNER: {
        "basic", "fundamentals", "foundation", "intro", "introductory",
        "beginner", "entry level", "entry-level", "familiar", "exposure",
        "learning", "some experience", "0-1 year", "less than 1 year",
    },
    SkillLevel.INTERMEDIATE: {
        "intermediate", "proficient", "working knowledge", "good understanding",
        "2-3 years", "2+ years", "3+ years", "1-3 years", "hands-on",
        "solid", "competent", "practical",
    },
    SkillLevel.ADVANCED: {
        "advanced", "senior", "extensive", "expert-level", "deep knowledge",
        "4-5 years", "5+ years", "4+ years", "3-5 years", "lead",
        "strong", "thorough", "comprehensive",
    },
    SkillLevel.EXPERT: {
        "expert", "master", "authority", "thought leader", "8+ years",
        "10+ years", "7+ years", "decade", "architect", "principal",
        "distinguished", "staff engineer",
    },
}


class SkillExtractor:
    """Extracts skills from text using taxonomy matching and NLP heuristics."""

    def __init__(self) -> None:
        self._nlp = None
        # Build inverted index: alias → canonical name
        self._alias_to_canonical: dict[str, str] = {}
        for canonical, aliases in SKILL_TAXONOMY.items():
            for alias in aliases:
                self._alias_to_canonical[alias.lower()] = canonical
        logger.info(
            "SkillExtractor initialised — {} canonical skills, {} aliases",
            len(SKILL_TAXONOMY),
            len(self._alias_to_canonical),
        )

    @property
    def nlp(self):
        """Lazy-load spaCy model."""
        if self._nlp is None:
            import spacy
            try:
                self._nlp = spacy.load("en_core_web_sm")
                logger.info("spaCy model loaded successfully")
            except OSError:
                logger.warning("spaCy model not found, running download...")
                import subprocess
                subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
                self._nlp = spacy.load("en_core_web_sm")
        return self._nlp

    def extract(self, text: str, source: str = "document") -> list[ExtractedSkill]:
        
        if not text or not text.strip():
            logger.warning("Empty text provided for skill extraction (source={})", source)
            return []

        logger.info("Starting skill extraction from {} — {} chars", source, len(text))
        text_lower = text.lower()

        
        found: dict[str, ExtractedSkill] = {}
        for alias, canonical in self._alias_to_canonical.items():

            if len(alias) <= 2:
                pattern = r'\b' + re.escape(alias) + r'\b'
            else:
                pattern = r'(?<![a-z])' + re.escape(alias) + r'(?![a-z])'

            matches = list(re.finditer(pattern, text_lower))
            if matches:
                if canonical not in found:

                    pos = matches[0].start()
                    ctx_start = max(0, pos - 60)
                    ctx_end = min(len(text), pos + 60)
                    context = text[ctx_start:ctx_end].strip()

                    level = self._infer_level(text_lower, canonical, alias, pos)
                    years = self._infer_years(text_lower, pos)

                    found[canonical] = ExtractedSkill(
                        name=canonical,
                        level=level,
                        years_experience=years,
                        context=context,
                    )
                    logger.debug(
                        "  [{}] Found skill '{}' (via '{}') level={} years={}",
                        source, canonical, alias, level.value, years,
                    )

        try:
            doc = self.nlp(text[:5000])
            for ent in doc.ents:
                if ent.label_ in ("ORG", "PRODUCT") and len(ent.text) > 2:
                    ent_lower = ent.text.lower().strip()
                    if ent_lower in self._alias_to_canonical:
                        canonical = self._alias_to_canonical[ent_lower]
                        if canonical not in found:
                            found[canonical] = ExtractedSkill(
                                name=canonical,
                                level=SkillLevel.NONE,
                                context=ent.sent.text.strip()[:120] if ent.sent else None,
                            )
                            logger.debug("  [{}] NER found skill '{}'", source, canonical)
        except Exception as e:
            logger.warning("SpaCy NER extraction failed: {}", e)

        skills = list(found.values())
        logger.info("Extraction complete for {} — {} unique skills found", source, len(skills))
        return skills

    def _get_sentence_window(self, text_lower: str, match_pos: int, radius: int) -> str:
        """Gets the surrounding text bounded by sentence endings or a maximum radius."""
        start = max(0, match_pos - radius)
        end = min(len(text_lower), match_pos + radius)
        
        # Find nearest preceding sentence boundary (period or newline)
        sent_start = max(text_lower.rfind('.', start, match_pos), text_lower.rfind('\n', start, match_pos))
        if sent_start != -1:
            start = sent_start + 1
            
        # Find nearest succeeding sentence boundary
        end_period = text_lower.find('.', match_pos, end)
        end_newline = text_lower.find('\n', match_pos, end)
        
        ends = [e for e in (end_period, end_newline) if e != -1]
        if ends:
            end = min(ends)
            
        return text_lower[start:end]

    def _infer_level(
        self, text_lower: str, canonical: str, matched_alias: str, match_pos: int
    ) -> SkillLevel:
        """Infer proficiency level from surrounding context bounded by the sentence."""
        window = self._get_sentence_window(text_lower, match_pos, radius=150)

        for level in [SkillLevel.EXPERT, SkillLevel.ADVANCED, SkillLevel.INTERMEDIATE, SkillLevel.BEGINNER]:
            for keyword in LEVEL_KEYWORDS[level]:
                if keyword in window:
                    return level

        return SkillLevel.INTERMEDIATE

    def _infer_years(self, text_lower: str, match_pos: int) -> Optional[float]:
        """Try to extract years of experience from nearby text bounded by the sentence."""
        window = self._get_sentence_window(text_lower, match_pos, radius=200)

        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)?',
            r'(?:experience|exp)\s*(?:of\s*)?(\d+)\+?\s*(?:years?|yrs?)',
        ]
        for pattern in patterns:
            m = re.search(pattern, window)
            if m:
                try:
                    return float(m.group(1))
                except (ValueError, IndexError):
                    pass
        return None


_extractor: Optional[SkillExtractor] = None


def get_skill_extractor() -> SkillExtractor:
    global _extractor
    if _extractor is None:
        _extractor = SkillExtractor()
    return _extractor