from eoi_analyzer.profile import EOIAssessment, EngagementProfile


def test_engagement_profile_summary_includes_eoi_assessment():
    profile = EngagementProfile(
        source_name="eoi.txt",
        title="Example",
        eoi_assessment=EOIAssessment(
            scope_rating="The scope is clear and well-defined",
            technical_components=["Cloud", "AI/ML"],
            technical_feasibility_rating="Technically feasible with the required expertise and can be completed within the 3-9 month timeline.",
            swe_goal_impact_rating="Proposed SWE work may significantly address project's goals",
            scientific_field_impact_rating="Proposed work may result in significant impacts on their scientific research field",
            development_readiness="Yes",
            project_types=["New functionality"],
            engagement_models=["Spec-driven development"],
            viss_pairing_recommendation="Yes",
            critical_questions=["Who owns maintenance?"],
        ),
    )

    summary = profile.summary_markdown()

    assert "VISS Review Rubric Assessment" in summary
    assert "The scope is clear and well-defined" in summary
    assert "Cloud, AI/ML" in summary
    assert "Who owns maintenance?" in summary
