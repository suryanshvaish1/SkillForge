from __future__ import annotations

import time
import traceback

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from loguru import logger

from app.models.schemas import (
    AnalysisResponse,
    ReasoningStep,
)
from app.services.gap_analyser import get_gap_analyser
from app.services.pathway_generator import get_recommender
from app.services.skill_extractor import get_skill_extractor
from app.utils.text_extraction import extract_text_from_file

router = APIRouter(prefix="/api/v1", tags=["analysis"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/analyse", response_model=AnalysisResponse)
async def analyse_and_generate_pathway(
    resume_file: UploadFile | None = File(None),
    jd_file: UploadFile | None = File(None),
    resume_text: str | None = Form(None),
    jd_text: str | None = Form(None),
):
   
    start_time = time.time()
    reasoning_trace: list[ReasoningStep] = []

    logger.info("=== New analysis request ===")
    logger.info(
        "Inputs: resume_file={}, jd_file={}, resume_text={}, jd_text={}",
        resume_file.filename if resume_file else None,
        jd_file.filename if jd_file else None,
        bool(resume_text),
        bool(jd_text),
    )


    try:
        # Resume text
        final_resume_text = ""
        if resume_file and resume_file.filename:
            content = await resume_file.read()
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(status_code=413, detail="Resume file too large (max 10MB)")
            final_resume_text = extract_text_from_file(resume_file.filename, content)
            logger.info("Resume extracted from file: {} chars", len(final_resume_text))
        elif resume_text:
            final_resume_text = resume_text.strip()
            logger.info("Resume provided as text: {} chars", len(final_resume_text))

        # JD text
        final_jd_text = ""
        if jd_file and jd_file.filename:
            content = await jd_file.read()
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(status_code=413, detail="JD file too large (max 10MB)")
            final_jd_text = extract_text_from_file(jd_file.filename, content)
            logger.info("JD extracted from file: {} chars", len(final_jd_text))
        elif jd_text:
            final_jd_text = jd_text.strip()
            logger.info("JD provided as text: {} chars", len(final_jd_text))

        if not final_resume_text and not final_jd_text:
            raise HTTPException(
                status_code=400,
                detail="At least one of resume or job description must be provided.",
            )

        reasoning_trace.append(ReasoningStep(
            step=0,
            action="Document Parsing",
            detail=f"Extracted {len(final_resume_text)} chars from resume, {len(final_jd_text)} chars from JD",
            data={"resume_chars": len(final_resume_text), "jd_chars": len(final_jd_text)},
        ))

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Text extraction failed: {}\n{}", e, traceback.format_exc())
        raise HTTPException(status_code=422, detail=f"Failed to extract text: {str(e)}")


    try:
        extractor = get_skill_extractor()

        resume_skills = extractor.extract(final_resume_text, source="resume") if final_resume_text else []
        jd_skills = extractor.extract(final_jd_text, source="jd") if final_jd_text else []

        reasoning_trace.append(ReasoningStep(
            step=1,
            action="Skill Extraction (NLP + Taxonomy Matching)",
            detail=f"Found {len(resume_skills)} resume skills and {len(jd_skills)} JD requirements",
            data={
                "resume_skills": [s.name for s in resume_skills],
                "jd_skills": [s.name for s in jd_skills],
            },
        ))

        logger.info("Skills extracted: resume={}, jd={}", len(resume_skills), len(jd_skills))

    except Exception as e:
        logger.error("Skill extraction failed: {}\n{}", e, traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Skill extraction error: {str(e)}")

    try:
        analyser = get_gap_analyser()
        skill_gaps, already_met = analyser.analyse(resume_skills, jd_skills)

        reasoning_trace.append(ReasoningStep(
            step=2,
            action="Skill Gap Analysis (Semantic Similarity + Level Comparison)",
            detail=f"Identified {len(skill_gaps)} gaps; {len(already_met)} skills already met",
            data={
                "gaps": [{"skill": g.skill, "gap_score": g.gap_score, "priority": g.priority} for g in skill_gaps],
                "already_met": already_met,
            },
        ))

        logger.info("Gap analysis: {} gaps, {} met", len(skill_gaps), len(already_met))

    except Exception as e:
        logger.error("Gap analysis failed: {}\n{}", e, traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Gap analysis error: {str(e)}")


    try:
        recommender = get_recommender()
        phases, summary, pathway_trace = recommender.generate_pathway(
            skill_gaps=skill_gaps,
            resume_skills=resume_skills,
            already_met=already_met,
        )

        reasoning_trace.extend(ReasoningStep(
            step=s.step + 3,  # Offset step numbers
            action=s.action,
            detail=s.detail,
            data=s.data,
        ) for s in pathway_trace)

    except Exception as e:
        logger.error("Pathway generation failed: {}\n{}", e, traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Pathway generation error: {str(e)}")

    elapsed = time.time() - start_time
    logger.info("=== Analysis complete in {:.2f}s ===", elapsed)

    reasoning_trace.append(ReasoningStep(
        step=len(reasoning_trace),
        action="Pipeline Complete",
        detail=f"Total processing time: {elapsed:.2f}s",
        data={"elapsed_seconds": round(elapsed, 2)},
    ))

    return AnalysisResponse(
        resume_skills=resume_skills,
        jd_skills=jd_skills,
        skill_gaps=skill_gaps,
        pathway=phases,
        summary=summary,
        reasoning_trace=reasoning_trace,
    )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "adaptive-learning-engine"}


@router.get("/catalog/stats")
async def catalog_stats():
    """Return catalog statistics."""
    recommender = get_recommender()
    categories = {}
    for cid, course in recommender.catalog.items():
        domain = course.get("domain", "unknown")
        if domain not in categories:
            categories[domain] = 0
        categories[domain] += 1

    return {
        "total_courses": len(recommender.catalog),
        "domains": categories,
        "prerequisite_edges": recommender.graph.number_of_edges(),
    }
