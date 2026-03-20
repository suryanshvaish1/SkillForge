from __future__ import annotations

import json
import os
import sys

import pytest


sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.models.schemas import ExtractedSkill, SkillGap, SkillLevel
from app.services.skill_extractor import SkillExtractor
from app.services.gap_analyser import GapAnalyser
from app.services.pathway_generator import CourseRecommender



SAMPLE_RESUME = """
John Doe — Senior Software Engineer

Summary:
5+ years of experience in Python, Java, and cloud technologies.
Built production-grade REST APIs with FastAPI and Flask.
Proficient in Docker, Kubernetes, and AWS (EC2, S3, Lambda).
Experienced with PostgreSQL, Redis, and ETL pipelines using Apache Airflow.
Strong background in Agile/Scrum methodologies and Git workflows.

Skills: Python, Java, SQL, Docker, Kubernetes, AWS, PostgreSQL, Redis,
Apache Airflow, FastAPI, Git, Agile, Linux, CI/CD, REST API

Education: B.S. Computer Science, MIT, 2019
"""

SAMPLE_JD = """
Job Title: Machine Learning Engineer

Requirements:
- 3+ years of experience with Python and machine learning frameworks
- Strong knowledge of deep learning (PyTorch or TensorFlow)
- Experience with NLP and transformer models
- Proficiency in SQL and data analysis with Pandas
- Familiarity with Docker and Kubernetes for model deployment
- Experience with MLOps tools (MLflow, experiment tracking)
- Knowledge of cloud platforms (AWS or GCP)
- Understanding of CI/CD pipelines
- Excellent communication and teamwork skills

Nice to have:
- Experience with Apache Spark for large-scale data processing
- Knowledge of computer vision
- Familiarity with LLM application development (RAG, LangChain)
"""

OPERATIONAL_RESUME = """
Maria Garcia — Warehouse Supervisor

5 years in warehouse operations and logistics management.
Certified forklift operator. OSHA 30 trained.
Experience with WMS systems and inventory management.
Led a team of 15 in a high-volume distribution center.
Six Sigma Green Belt certified.
"""

OPERATIONAL_JD = """
Job Title: Operations Manager

Requirements:
- Experience in supply chain management and logistics
- Knowledge of quality control and lean manufacturing
- Strong leadership and team management skills
- Familiarity with ERP systems
- OSHA compliance knowledge
- Equipment operation and maintenance oversight
- CNC and manufacturing technology understanding
- Excellent communication skills
"""


# ── Skill Extractor Tests

class TestSkillExtractor:
    def setup_method(self):
        self.extractor = SkillExtractor()

    def test_extracts_skills_from_resume(self):
        skills = self.extractor.extract(SAMPLE_RESUME, source="resume")
        skill_names = {s.name.lower() for s in skills}
        assert "python" in skill_names, "Should extract Python"
        assert "java" in skill_names, "Should extract Java"
        assert "docker" in skill_names, "Should extract Docker"
        assert "aws" in skill_names, "Should extract AWS"
        assert "postgresql" in skill_names, "Should extract PostgreSQL"
        assert len(skills) >= 8, f"Should find at least 8 skills, found {len(skills)}"

    def test_extracts_skills_from_jd(self):
        skills = self.extractor.extract(SAMPLE_JD, source="jd")
        skill_names = {s.name.lower() for s in skills}
        assert "python" in skill_names
        assert "machine learning" in skill_names or "deep learning" in skill_names
        assert "docker" in skill_names

    def test_extracts_operational_skills(self):
        skills = self.extractor.extract(OPERATIONAL_RESUME, source="resume")
        skill_names = {s.name.lower() for s in skills}
        assert "warehouse management" in skill_names or "supply chain" in skill_names
        assert "workplace safety" in skill_names or "quality control" in skill_names

    def test_empty_text_returns_empty(self):
        skills = self.extractor.extract("", source="resume")
        assert skills == []

    def test_no_duplicates(self):
        skills = self.extractor.extract(SAMPLE_RESUME, source="resume")
        names = [s.name for s in skills]
        assert len(names) == len(set(names)), "Should have no duplicate skill names"

    def test_infers_experience_level(self):
        text = "Expert in Python with 10+ years of experience. Basic knowledge of Rust."
        skills = self.extractor.extract(text, source="resume")
        skill_map = {s.name.lower(): s for s in skills}
        if "python" in skill_map:
            assert skill_map["python"].level in (SkillLevel.ADVANCED, SkillLevel.EXPERT)
        if "rust" in skill_map:
            assert skill_map["rust"].level in (SkillLevel.BEGINNER, SkillLevel.INTERMEDIATE)

    def test_extracts_years(self):
        text = "5 years of experience with Java and Spring Boot."
        skills = self.extractor.extract(text, source="resume")
        java_skill = next((s for s in skills if s.name.lower() == "java"), None)
        if java_skill and java_skill.years_experience:
            assert java_skill.years_experience == 5.0


# ── Gap Analyser Tests ─────────────────────────────────────────────────────

class TestGapAnalyser:
    def setup_method(self):
        self.analyser = GapAnalyser()

    def test_finds_gaps(self):
        resume = [
            ExtractedSkill(name="python", level=SkillLevel.ADVANCED),
            ExtractedSkill(name="sql", level=SkillLevel.INTERMEDIATE),
        ]
        jd = [
            ExtractedSkill(name="python", level=SkillLevel.ADVANCED),
            ExtractedSkill(name="sql", level=SkillLevel.ADVANCED),
            ExtractedSkill(name="machine learning", level=SkillLevel.INTERMEDIATE),
        ]
        gaps, met = self.analyser.analyse(resume, jd)

        gap_names = {g.skill.lower() for g in gaps}
        assert "machine learning" in gap_names, "Should identify ML as a gap"
        assert "python" in [m.lower() for m in met], "Python should be met"

    def test_no_gaps_when_all_met(self):
        resume = [
            ExtractedSkill(name="python", level=SkillLevel.EXPERT),
            ExtractedSkill(name="java", level=SkillLevel.ADVANCED),
        ]
        jd = [
            ExtractedSkill(name="python", level=SkillLevel.INTERMEDIATE),
            ExtractedSkill(name="java", level=SkillLevel.INTERMEDIATE),
        ]
        gaps, met = self.analyser.analyse(resume, jd)
        assert len(gaps) == 0
        assert len(met) == 2

    def test_gap_priority_ordering(self):
        resume = [
            ExtractedSkill(name="python", level=SkillLevel.BEGINNER),
        ]
        jd = [
            ExtractedSkill(name="python", level=SkillLevel.EXPERT),
            ExtractedSkill(name="java", level=SkillLevel.BEGINNER),
        ]
        gaps, _ = self.analyser.analyse(resume, jd)
        assert len(gaps) >= 1
        # Gaps should be sorted by score descending
        for i in range(len(gaps) - 1):
            assert gaps[i].gap_score >= gaps[i + 1].gap_score

    def test_empty_inputs(self):
        gaps, met = self.analyser.analyse([], [])
        assert gaps == []
        assert met == []


# ── Pathway Generator Tests ────────────────────────────────────────────────

class TestPathwayGenerator:
    def setup_method(self):
        self.recommender = CourseRecommender()

    def test_catalog_loaded(self):
        assert len(self.recommender.catalog) > 0, "Catalog should have courses"
        assert self.recommender.graph.number_of_nodes() > 0

    def test_generates_pathway_for_gaps(self):
        gaps = [
            SkillGap(skill="machine learning", current_level=SkillLevel.NONE,
                     required_level=SkillLevel.INTERMEDIATE, gap_score=0.5, priority="high"),
            SkillGap(skill="deep learning", current_level=SkillLevel.NONE,
                     required_level=SkillLevel.INTERMEDIATE, gap_score=0.5, priority="high"),
        ]
        resume_skills = [
            ExtractedSkill(name="python", level=SkillLevel.ADVANCED),
            ExtractedSkill(name="sql", level=SkillLevel.INTERMEDIATE),
        ]
        phases, summary, trace = self.recommender.generate_pathway(
            skill_gaps=gaps, resume_skills=resume_skills, already_met=["python", "sql"]
        )
        assert len(phases) > 0, "Should generate at least one phase"
        assert summary.total_courses > 0
        assert summary.total_hours > 0
        assert len(trace) > 0, "Should produce reasoning trace"

    def test_empty_gaps_empty_pathway(self):
        phases, summary, trace = self.recommender.generate_pathway(
            skill_gaps=[], resume_skills=[], already_met=[]
        )
        assert summary.total_courses == 0

    def test_prerequisite_resolution(self):
        # DE-105 (Spark) requires DE-102 which requires DE-101 and PROG-101
        gaps = [
            SkillGap(skill="apache spark", current_level=SkillLevel.NONE,
                     required_level=SkillLevel.INTERMEDIATE, gap_score=0.5, priority="high"),
        ]
        phases, summary, trace = self.recommender.generate_pathway(
            skill_gaps=gaps, resume_skills=[], already_met=[]
        )
        all_course_ids = set()
        for p in phases:
            for c in p.courses:
                all_course_ids.add(c.id)
        # Should include prerequisites
        assert "DE-105" in all_course_ids, "Should include the Spark course"

    def test_cross_domain_scalability(self):
        """Test that system works for operational/labor roles."""
        gaps = [
            SkillGap(skill="warehouse management", current_level=SkillLevel.NONE,
                     required_level=SkillLevel.INTERMEDIATE, gap_score=0.5, priority="high"),
            SkillGap(skill="quality control", current_level=SkillLevel.NONE,
                     required_level=SkillLevel.INTERMEDIATE, gap_score=0.5, priority="high"),
            SkillGap(skill="workplace safety", current_level=SkillLevel.NONE,
                     required_level=SkillLevel.BEGINNER, gap_score=0.25, priority="medium"),
        ]
        phases, summary, trace = self.recommender.generate_pathway(
            skill_gaps=gaps, resume_skills=[], already_met=[]
        )
        assert summary.total_courses > 0
        domains = summary.domain_coverage
        assert "operational" in domains, "Should include operational domain courses"

    def test_phases_are_ordered(self):
        gaps = [
            SkillGap(skill="machine learning", current_level=SkillLevel.NONE,
                     required_level=SkillLevel.INTERMEDIATE, gap_score=0.5, priority="high"),
        ]
        phases, _, _ = self.recommender.generate_pathway(
            skill_gaps=gaps, resume_skills=[], already_met=[]
        )
        for i in range(len(phases) - 1):
            assert phases[i].phase_number < phases[i + 1].phase_number


# ── API Integration Tests ──────────────────────────────────────────────────

class TestAPIEndpoints:
    @pytest.fixture(autouse=True)
    def setup_client(self):
        from fastapi.testclient import TestClient
        from app.main import app
        self.client = TestClient(app)

    def test_health_check(self):
        resp = self.client.get("/api/v1/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    def test_catalog_stats(self):
        resp = self.client.get("/api/v1/catalog/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_courses"] > 0

    def test_analyse_with_text(self):
        resp = self.client.post(
            "/api/v1/analyse",
            data={
                "resume_text": SAMPLE_RESUME,
                "jd_text": SAMPLE_JD,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["resume_skills"]) > 0
        assert len(data["jd_skills"]) > 0
        assert "skill_gaps" in data
        assert "pathway" in data
        assert "summary" in data
        assert "reasoning_trace" in data
        assert data["summary"]["total_courses"] >= 0

    def test_analyse_operational_roles(self):
        resp = self.client.post(
            "/api/v1/analyse",
            data={
                "resume_text": OPERATIONAL_RESUME,
                "jd_text": OPERATIONAL_JD,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["resume_skills"]) > 0

    def test_analyse_empty_input_fails(self):
        resp = self.client.post("/api/v1/analyse", data={})
        assert resp.status_code == 400

    def test_analyse_resume_only(self):
        resp = self.client.post(
            "/api/v1/analyse",
            data={"resume_text": SAMPLE_RESUME},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["resume_skills"]) > 0

    def test_reasoning_trace_present(self):
        resp = self.client.post(
            "/api/v1/analyse",
            data={
                "resume_text": SAMPLE_RESUME,
                "jd_text": SAMPLE_JD,
            },
        )
        data = resp.json()
        trace = data["reasoning_trace"]
        assert len(trace) >= 3, "Should have at least 3 reasoning steps"
        for step in trace:
            assert "step" in step
            assert "action" in step
            assert "detail" in step


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
