Extract an engagement profile from this document. Include evidence quotes for important facts.

The profile should identify PI team, locations, scientific objective, software objective, existing assets, constraints, data considerations, deadlines, prior working relationships, and open questions.

Return this JSON shape exactly:

{
  "title": "",
  "pi_team": [
    {
      "name": "",
      "role": "",
      "institution": "",
      "location": "",
      "time_zone": "",
      "evidence": ""
    }
  ],
  "institutions": [],
  "locations": [],
  "scientific_domain": "",
  "scientific_objectives": [],
  "software_objectives": [],
  "existing_assets": [],
  "constraints": [],
  "data_considerations": [],
  "deadlines": [],
  "requested_engagement_type": "",
  "prior_relationships": [],
  "open_questions": [],
  "evidence": [
    {
      "claim": "",
      "source": "",
      "quote": "",
      "confidence": "high|medium|low"
    }
  ]
}

Team context for interpretation:
$team_context

Source document name: $source_name

=== Document Text ===
$document_text
