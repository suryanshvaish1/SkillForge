from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Difficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class SkillLevel(str, Enum):
    NONE = "none"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class Domain(str, Enum):
    TECHNICAL = "technical"
    MANAGEMENT = "management"
    SOFT_SKILLS = "soft_skills"
    OPERATIONAL = "operational"
    BUSINESS = "business"


class ExtractedSkill(BaseModel):
    """A single skill extracted from a document."""
    name: str
    level: SkillLevel = SkillLevel.NONE
    years_experience: Optional[float] = None
    context: Optional[str] = None 


class SkillGap(BaseModel):
    """Difference between required and current proficiency."""
    skill: str
    current_level: SkillLevel
    required_level: SkillLevel
    gap_score: float = Field(ge=0.0, le=1.0, description="0 = no gap, 1 = maximum gap")
    priority: str = "medium"  # low / medium / high / critical


class Course(BaseModel):
    id: str
    title: str
    description: str
    skills_covered: list[str]
    difficulty: Difficulty
    duration_hours: int
    prerequisites: list[str]
    domain: Domain
    relevance_score: float = 0.0
    reason: str = ""


class PathwayPhase(BaseModel):
    """A phase in the learning pathway (e.g. Foundation → Core → Advanced)."""
    phase_name: str
    phase_number: int
    description: str
    courses: list[Course]
    total_hours: int
    skills_addressed: list[str]


class ReasoningStep(BaseModel):
    step: int
    action: str
    detail: str
    data: Optional[dict] = None


class PathwaySummary(BaseModel):
    total_courses: int
    total_hours: int
    estimated_weeks: float
    phases: int
    top_gaps: list[str]
    skills_already_met: list[str]
    domain_coverage: dict[str, int] 



class AnalysisRequest(BaseModel):
    resume_text: Optional[str] = None
    jd_text: Optional[str] = None


class AnalysisResponse(BaseModel):
    resume_skills: list[ExtractedSkill]
    jd_skills: list[ExtractedSkill]
    skill_gaps: list[SkillGap]
    pathway: list[PathwayPhase]
    summary: PathwaySummary      
    reasoning_trace: list[ReasoningStep]