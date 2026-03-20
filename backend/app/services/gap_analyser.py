from __future__ import annotations

from loguru import logger

from app.models.schemas import ExtractedSkill, SkillGap, SkillLevel


# Numeric mapping for level comparison
LEVEL_SCORES: dict[SkillLevel, float] = {
    SkillLevel.NONE: 0.0,
    SkillLevel.BEGINNER: 0.25,
    SkillLevel.INTERMEDIATE: 0.5,
    SkillLevel.ADVANCED: 0.75,
    SkillLevel.EXPERT: 1.0,
}

# Default required level when JD mentions a skill without explicit level
JD_DEFAULT_LEVEL = SkillLevel.INTERMEDIATE


class GapAnalyser:
    """Computes the delta between candidate skills and role requirements."""

    def __init__(self) -> None:
        self._model = None
        logger.info("GapAnalyser initialised")

    @property
    def embedder(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer("all-MiniLM-L6-v2")
                logger.info("Sentence-transformer model loaded")
            except Exception as e:
                logger.warning("Sentence-transformer unavailable ({}), using exact matching", e)
        return self._model

    def analyse(
        self,
        resume_skills: list[ExtractedSkill],
        jd_skills: list[ExtractedSkill],
    ) -> tuple[list[SkillGap], list[str]]:
        
        logger.info(
            "Gap analysis: {} resume skills vs {} JD requirements",
            len(resume_skills), len(jd_skills),
        )

        # Build resume lookup
        resume_map: dict[str, ExtractedSkill] = {s.name.lower(): s for s in resume_skills}

        # Build semantic embeddings if model available
        resume_names = [s.name.lower() for s in resume_skills]
        jd_names = [s.name.lower() for s in jd_skills]

        semantic_matches = self._build_semantic_matches(resume_names, jd_names)

        gaps: list[SkillGap] = []
        already_met: list[str] = []

        for jd_skill in jd_skills:
            jd_name = jd_skill.name.lower()
            required_level = jd_skill.level if jd_skill.level != SkillLevel.NONE else JD_DEFAULT_LEVEL

            # Try exact match first
            matched_resume_skill = resume_map.get(jd_name)

            # Try semantic match if no exact match
            if matched_resume_skill is None and jd_name in semantic_matches:
                best_match = semantic_matches[jd_name]
                if best_match:
                    matched_resume_skill = resume_map.get(best_match)
                    if matched_resume_skill:
                        logger.debug(
                            "Semantic match: JD '{}' → Resume '{}' ",
                            jd_name, best_match,
                        )

            if matched_resume_skill is None:
                # Skill not found in resume at all
                gap_score = LEVEL_SCORES[required_level]
                priority = self._compute_priority(gap_score)
                gaps.append(SkillGap(
                    skill=jd_skill.name,
                    current_level=SkillLevel.NONE,
                    required_level=required_level,
                    gap_score=min(gap_score, 1.0),
                    priority=priority,
                ))
                logger.debug(
                    "  Gap: '{}' — missing entirely (score={:.2f}, priority={})",
                    jd_skill.name, gap_score, priority,
                )
            else:
                # Skill found — check level
                current_score = LEVEL_SCORES[matched_resume_skill.level]
                required_score = LEVEL_SCORES[required_level]
                delta = max(0.0, required_score - current_score)

                if delta > 0.05:  # Small threshold to avoid noise
                    priority = self._compute_priority(delta)
                    gaps.append(SkillGap(
                        skill=jd_skill.name,
                        current_level=matched_resume_skill.level,
                        required_level=required_level,
                        gap_score=min(delta, 1.0),
                        priority=priority,
                    ))
                    logger.debug(
                        "  Gap: '{}' — {}.→{} (delta={:.2f})",
                        jd_skill.name,
                        matched_resume_skill.level.value,
                        required_level.value,
                        delta,
                    )
                else:
                    already_met.append(jd_skill.name)
                    logger.debug("  Met: '{}' — no gap", jd_skill.name)

        # Sort by gap_score descending
        gaps.sort(key=lambda g: g.gap_score, reverse=True)

        logger.info(
            "Gap analysis complete: {} gaps, {} already met",
            len(gaps), len(already_met),
        )
        return gaps, already_met

    def _build_semantic_matches(
        self, resume_names: list[str], jd_names: list[str]
    ) -> dict[str, str | None]:
        """Build fuzzy matches from JD skill → closest resume skill via embeddings."""
        matches: dict[str, str | None] = {}

        if not self.embedder or not resume_names or not jd_names:
            return matches

        try:
            import numpy as np
            resume_embs = self.embedder.encode(resume_names, convert_to_numpy=True)
            jd_embs = self.embedder.encode(jd_names, convert_to_numpy=True)

            # Cosine similarity matrix
            from sklearn.metrics.pairwise import cosine_similarity
            sim_matrix = cosine_similarity(jd_embs, resume_embs)

            for i, jd_name in enumerate(jd_names):
                best_idx = int(np.argmax(sim_matrix[i]))
                best_score = float(sim_matrix[i][best_idx])
                if best_score >= 0.65:  # Threshold for semantic match
                    matches[jd_name] = resume_names[best_idx]
                    logger.debug(
                        "Semantic pair: '{}' ↔ '{}' (sim={:.3f})",
                        jd_name, resume_names[best_idx], best_score,
                    )
        except Exception as e:
            logger.warning("Semantic matching failed: {}", e)

        return matches

    @staticmethod
    def _compute_priority(gap_score: float) -> str:
        if gap_score >= 0.7:
            return "critical"
        elif gap_score >= 0.5:
            return "high"
        elif gap_score >= 0.25:
            return "medium"
        return "low"


# Singleton
_analyser: GapAnalyser | None = None


def get_gap_analyser() -> GapAnalyser:
    global _analyser
    if _analyser is None:
        _analyser = GapAnalyser()
    return _analyser
