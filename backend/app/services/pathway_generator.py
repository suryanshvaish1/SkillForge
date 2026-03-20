from __future__ import annotations

import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Optional

import networkx as nx
from loguru import logger
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import get_settings
from app.models.schemas import (
    Course,
    Difficulty,
    Domain,
    ExtractedSkill,
    PathwayPhase,
    PathwaySummary,
    ReasoningStep,
    SkillGap,
    SkillLevel,
)


class CourseRecommender:
    """Graph-based adaptive pathway generator grounded in the course catalog."""

    def __init__(self) -> None:
        self.catalog: dict[str, dict] = {}   # id → raw course dict
        self.graph = nx.DiGraph()
        self._tfidf: Optional[TfidfVectorizer] = None
        self._course_vectors = None
        self._course_ids_ordered: list[str] = []
        self._load_catalog()


    def _load_catalog(self) -> None:
        """Load and index the course catalog + build the prerequisite DAG."""
        settings = get_settings()
        catalog_path = settings.catalog_abs_path
        logger.info("Loading course catalog from {}", catalog_path)

        if not catalog_path.exists():
            raise FileNotFoundError(f"Course catalog not found: {catalog_path}")

        with open(catalog_path, "r") as f:
            raw = json.load(f)

        # Flatten categories into a single dict
        for cat_key, cat_data in raw.get("categories", {}).items():
            for course in cat_data.get("courses", []):
                cid = course["id"]
                self.catalog[cid] = course
                self.graph.add_node(cid, **course)

        # Build prerequisite edges
        for cid, course in self.catalog.items():
            for prereq in course.get("prerequisites", []):
                if prereq in self.catalog:
                    self.graph.add_edge(prereq, cid)  # prereq → course

        logger.info(
            "Catalog loaded: {} courses, {} prerequisite edges",
            len(self.catalog), self.graph.number_of_edges(),
        )

        # Build TF-IDF vectors for relevance scoring
        self._build_tfidf()

    def _build_tfidf(self) -> None:
        """Build TF-IDF vectors from course skills + descriptions."""
        self._course_ids_ordered = list(self.catalog.keys())
        corpus = []
        for cid in self._course_ids_ordered:
            c = self.catalog[cid]
            text = " ".join(c.get("skills_covered", [])) + " " + c.get("description", "")
            corpus.append(text.lower())

        self._tfidf = TfidfVectorizer(stop_words="english", max_features=500)
        self._course_vectors = self._tfidf.fit_transform(corpus)
        logger.debug("TF-IDF index built: {} courses × {} features", len(corpus), self._course_vectors.shape[1])

    # Public API

    def generate_pathway(
        self,
        skill_gaps: list[SkillGap],
        resume_skills: list[ExtractedSkill],
        already_met: list[str],
    ) -> tuple[list[PathwayPhase], PathwaySummary, list[ReasoningStep]]:
        """
        Generate a personalised learning pathway.

        Args:
            skill_gaps: Prioritised skill gaps from GapAnalyser.
            resume_skills: Skills the candidate already has.
            already_met: Skill names with no gap.

        Returns:
            (phases, summary, reasoning_trace)
        """
        trace: list[ReasoningStep] = []
        resume_skill_names = {s.name.lower() for s in resume_skills}

        # Step 1: Score courses against gaps
        trace.append(ReasoningStep(
            step=1,
            action="Score catalog courses against skill gaps",
            detail=f"Evaluating {len(self.catalog)} courses against {len(skill_gaps)} gaps",
            data={"total_courses": len(self.catalog), "total_gaps": len(skill_gaps)},
        ))
        scored_courses = self._score_courses(skill_gaps)
        logger.info("Scored {} courses, {} have relevance > 0", len(scored_courses), sum(1 for _, s in scored_courses if s > 0))

        # Step 2: Select courses via weighted set cover
        trace.append(ReasoningStep(
            step=2,
            action="Select minimal course set (weighted set cover)",
            detail="Choosing courses that cover all gaps with minimum redundancy",
        ))
        selected_ids = self._select_courses(scored_courses, skill_gaps, resume_skill_names)
        logger.info("Selected {} courses before prerequisite resolution", len(selected_ids))

        # Step 3: Resolve prerequisites
        trace.append(ReasoningStep(
            step=3,
            action="Resolve prerequisites transitively",
            detail=f"Expanding {len(selected_ids)} selected courses with their prerequisite chains",
        ))
        full_set = self._resolve_prerequisites(selected_ids, resume_skill_names)
        logger.info("After prerequisite resolution: {} courses", len(full_set))

        # Step 4: Filter already-mastered courses
        trace.append(ReasoningStep(
            step=4,
            action="Filter courses whose content is already mastered",
            detail=f"Checking {len(full_set)} courses against {len(resume_skill_names)} known skills",
        ))
        filtered = self._filter_mastered(full_set, resume_skill_names, already_met)
        logger.info("After mastery filter: {} courses", len(filtered))

        # Step 5: Build phased pathway via topological sort
        trace.append(ReasoningStep(
            step=5,
            action="Build phased pathway (topological sort)",
            detail="Organising courses into Foundation → Core → Advanced phases",
        ))
        phases = self._build_phases(filtered, skill_gaps)

        # Step 6: Generate summary
        summary = self._build_summary(phases, skill_gaps, already_met)
        trace.append(ReasoningStep(
            step=6,
            action="Generate pathway summary",
            detail=f"{summary.total_courses} courses, {summary.total_hours}h, ~{summary.estimated_weeks:.1f} weeks",
            data={
                "total_courses": summary.total_courses,
                "total_hours": summary.total_hours,
                "estimated_weeks": summary.estimated_weeks,
                "phases": summary.phases,
            },
        ))

        return phases, summary, trace


    def _score_courses(self, skill_gaps: list[SkillGap]) -> list[tuple[str, float]]:
        """Score each catalog course by relevance to the set of skill gaps."""
        if not skill_gaps:
            return [(cid, 0.0) for cid in self.catalog]

        # Build a query string from all gaps
        gap_text = " ".join(g.skill.lower() for g in skill_gaps)
        gap_vector = self._tfidf.transform([gap_text])
        similarities = cosine_similarity(gap_vector, self._course_vectors).flatten()

        scored = []
        for i, cid in enumerate(self._course_ids_ordered):
            course = self.catalog[cid]
            base_score = float(similarities[i])

            # Boost for direct skill match
            course_skills = {s.lower() for s in course.get("skills_covered", [])}
            gap_skills = {g.skill.lower() for g in skill_gaps}
            direct_overlap = len(course_skills & gap_skills)
            if direct_overlap > 0:
                base_score += 0.3 * direct_overlap  # Boost per matching skill

            # Boost for high-priority gaps
            for gap in skill_gaps:
                if gap.skill.lower() in course_skills:
                    if gap.priority == "critical":
                        base_score += 0.2
                    elif gap.priority == "high":
                        base_score += 0.1

            scored.append((cid, base_score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

    def _select_courses(
        self,
        scored_courses: list[tuple[str, float]],
        skill_gaps: list[SkillGap],
        resume_skills: set[str],
    ) -> set[str]:
        """Weighted set cover: pick courses that cover all gap skills."""
        uncovered_gaps = {g.skill.lower() for g in skill_gaps}
        selected: set[str] = set()

        for cid, score in scored_courses:
            if not uncovered_gaps:
                break
            if score <= 0.01:
                continue

            course = self.catalog[cid]
            course_skills = {s.lower() for s in course.get("skills_covered", [])}
            coverage = course_skills & uncovered_gaps

            if coverage:
                selected.add(cid)
                uncovered_gaps -= coverage
                logger.debug(
                    "  Selected '{}' (score={:.3f}) covering: {}",
                    cid, score, coverage,
                )

        # If gaps remain uncovered, log them
        if uncovered_gaps:
            logger.warning("Uncovered gaps (no matching courses): {}", uncovered_gaps)

        return selected

    def _resolve_prerequisites(self, selected: set[str], resume_skills: set[str]) -> set[str]:
        """Transitively include all prerequisite courses."""
        full_set = set(selected)
        queue = deque(selected)

        while queue:
            cid = queue.popleft()
            for prereq in self.catalog.get(cid, {}).get("prerequisites", []):
                if prereq not in full_set and prereq in self.catalog:
                    # Check if the candidate already masters the prereq's content
                    prereq_skills = {s.lower() for s in self.catalog[prereq].get("skills_covered", [])}
                    mastered_ratio = len(prereq_skills & resume_skills) / max(len(prereq_skills), 1)

                    if mastered_ratio < 0.8:  # If they don't already know 80%+ of the prereq
                        full_set.add(prereq)
                        queue.append(prereq)
                        logger.debug("  Added prerequisite '{}' (mastered ratio={:.2f})", prereq, mastered_ratio)
                    else:
                        logger.debug("  Skipping prereq '{}' — already mastered ({:.0%})", prereq, mastered_ratio)

        return full_set

    def _filter_mastered(
        self, course_set: set[str], resume_skills: set[str], already_met: list[str]
    ) -> set[str]:
        """Remove courses whose skill content is substantially covered by the candidate."""
        already_met_set = {s.lower() for s in already_met}
        filtered = set()

        for cid in course_set:
            course = self.catalog[cid]
            course_skills = {s.lower() for s in course.get("skills_covered", [])}

            # What fraction of this course's skills does the candidate already have?
            overlap = course_skills & (resume_skills | already_met_set)
            if len(course_skills) == 0:
                filtered.add(cid)
                continue

            mastery_ratio = len(overlap) / len(course_skills)
            if mastery_ratio < 0.9:  # Keep if they haven't mastered 90%+ of the course
                filtered.add(cid)
            else:
                logger.debug(
                    "  Filtered out '{}' — candidate already knows {:.0%} of content",
                    cid, mastery_ratio,
                )

        return filtered

    def _build_phases(
        self, course_set: set[str], skill_gaps: list[SkillGap]
    ) -> list[PathwayPhase]:
        """Organise courses into sequential phases using topological sort + difficulty."""
        if not course_set:
            return []

        # Sub-graph of selected courses
        subgraph = self.graph.subgraph(course_set).copy()

        # Remove any cycles (shouldn't happen with valid catalog, but safety net)
        if not nx.is_directed_acyclic_graph(subgraph):
            logger.warning("Cycle detected in course subgraph, removing back-edges")
            cycles = list(nx.simple_cycles(subgraph))
            for cycle in cycles:
                subgraph.remove_edge(cycle[-1], cycle[0])

        # Topological generations = natural phase groupings
        try:
            generations = list(nx.topological_generations(subgraph))
        except nx.NetworkXUnfeasible:
            # Fallback: group by difficulty
            logger.warning("Topological sort failed, falling back to difficulty grouping")
            generations = self._fallback_grouping(course_set)

        # Map to phases
        gap_skills = {g.skill.lower(): g for g in skill_gaps}
        phases: list[PathwayPhase] = []
        phase_names = ["Foundation", "Core Development", "Advanced Specialisation", "Capstone"]

        for gen_idx, gen_courses in enumerate(generations):
            if not gen_courses:
                continue

            phase_num = gen_idx + 1
            phase_name = phase_names[min(gen_idx, len(phase_names) - 1)]

            # Build Course objects
            courses: list[Course] = []
            all_skills: set[str] = set()

            for cid in sorted(gen_courses):
                raw = self.catalog[cid]
                skills = raw.get("skills_covered", [])
                all_skills.update(s.lower() for s in skills)

                # Compute relevance
                relevance = 0.0
                reasons = []
                for s in skills:
                    if s.lower() in gap_skills:
                        gap = gap_skills[s.lower()]
                        relevance += gap.gap_score
                        reasons.append(f"Addresses '{gap.skill}' gap ({gap.priority} priority)")

                courses.append(Course(
                    id=cid,
                    title=raw["title"],
                    description=raw["description"],
                    skills_covered=skills,
                    difficulty=Difficulty(raw["difficulty"]),
                    duration_hours=raw["duration_hours"],
                    prerequisites=raw.get("prerequisites", []),
                    domain=Domain(raw.get("domain", "technical")),
                    relevance_score=round(min(relevance, 1.0), 3),
                    reason="; ".join(reasons) if reasons else "Prerequisite for required courses",
                ))

            # Sort courses within phase by relevance
            courses.sort(key=lambda c: c.relevance_score, reverse=True)

            total_hours = sum(c.duration_hours for c in courses)
            description = self._phase_description(phase_name, courses)

            phases.append(PathwayPhase(
                phase_name=phase_name,
                phase_number=phase_num,
                description=description,
                courses=courses,
                total_hours=total_hours,
                skills_addressed=sorted(all_skills),
            ))

        return phases

    def _fallback_grouping(self, course_set: set[str]) -> list[set[str]]:
        """Group courses by difficulty level as a fallback."""
        groups: dict[str, set[str]] = defaultdict(set)
        for cid in course_set:
            diff = self.catalog[cid].get("difficulty", "intermediate")
            groups[diff].add(cid)

        ordered = []
        for level in ["beginner", "intermediate", "advanced"]:
            if level in groups:
                ordered.append(groups[level])
        return ordered

    @staticmethod
    def _phase_description(name: str, courses: list[Course]) -> str:
        if not courses:
            return ""
        skills = set()
        for c in courses:
            skills.update(c.skills_covered[:3])
        skill_list = ", ".join(sorted(skills)[:5])
        return f"{name} phase covering {skill_list} across {len(courses)} course(s)."

    def _build_summary(
        self, phases: list[PathwayPhase], gaps: list[SkillGap], already_met: list[str]
    ) -> PathwaySummary:
        total_courses = sum(len(p.courses) for p in phases)
        total_hours = sum(p.total_hours for p in phases)
        # Assume 10 hours/week of study
        estimated_weeks = round(total_hours / 10, 1) if total_hours > 0 else 0.0

        domain_counts: dict[str, int] = defaultdict(int)
        for phase in phases:
            for course in phase.courses:
                domain_counts[course.domain.value] += 1

        top_gaps = [g.skill for g in sorted(gaps, key=lambda x: x.gap_score, reverse=True)[:5]]

        return PathwaySummary(
            total_courses=total_courses,
            total_hours=total_hours,
            estimated_weeks=estimated_weeks,
            phases=len(phases),
            top_gaps=top_gaps,
            skills_already_met=already_met,
            domain_coverage=dict(domain_counts),
        )


# Singleton
_recommender: CourseRecommender | None = None


def get_recommender() -> CourseRecommender:
    global _recommender
    if _recommender is None:
        _recommender = CourseRecommender()
    return _recommender
