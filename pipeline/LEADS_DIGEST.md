# Leads Digest

Generated: 2026-05-27

Top 10 leads from 236 ranked accounts. Full briefs in `pipeline/leads/`.

## Top 10 ranked

| Rank | Client | Score | Confidence | Triggers | Recommended Solutions |
|---:|---|---:|---|---:|---|
| **1** | [Travelers Group](leads/01_travelers_group.md) | **89.3** | Very High | 17 | EXL XTRAKTO.AI (5); EXL Paymentor (4); EXL EXELIA.AI (4); EXL Subrosource (3); EXL MedConnection (3) |
| **2** | [Allstate](leads/02_allstate.md) | **64.5** | High | 5 | EXL NerveHub (1); EXL XTRAKTO.AI (1); EXL EXELIA.AI (1); EXL Paymentor (1) |
| **3** | [Liberty Mutual](leads/03_liberty_mutual.md) | **56.3** | High | 3 | EXL Paymentor (1); EXL Digital Finance Suite (1); EXL XTRAKTO.AI (1); EXL NerveHub (1) |
| **4** | [State Farm](leads/04_state_farm.md) | **54.4** | Medium | 1 | EXL XTRAKTO.AI (1); EXL NerveHub (1) |
| **5** | [Hanover Insurance Group](leads/05_hanover_insurance_group.md) | **54.0** | Medium | 2 | EXL NerveHub (1); EXL XTRAKTO.AI (1); EXL EXELIA.AI (1); EXL Paymentor (1) |
| **6** | [Munich-Amer Hldg Corp Cos](leads/06_munich_amer_hldg_corp_cos.md) | **53.2** | Medium | 2 | EXL XTRAKTO.AI (2); EXL NerveHub (2); EXL Paymentor (1); EXL Digital Finance Suite (1) |
| **7** | [Swiss Re](leads/07_swiss_re.md) | **51.8** | Medium | 3 | EXL Paymentor (1); EXL Digital Finance Suite (1); EXL XTRAKTO.AI (1); EXL NerveHub (1) |
| **8** | [Amer Family Ins Group](leads/08_amer_family_ins_group.md) | **51.3** | Medium | 1 | EXL Paymentor (1); EXL Digital Finance Suite (1); EXL XTRAKTO.AI (1); EXL NerveHub (1) |
| **9** | [Hartford](leads/09_hartford.md) | **51.0** | Medium | 2 | EXL NerveHub (1); EXL XTRAKTO.AI (1); EXL EXELIA.AI (1); EXL Paymentor (1) |
| **10** | [Nationwide](leads/10_nationwide.md) | **50.5** | Medium | 3 | EXL XTRAKTO.AI (1); EXL NerveHub (1) |


## Scoring weights (V1 defaults — tunable)

| Component | Weight |
|---|---:|
| Account fit (NWP rank, Strategic/Named status, growth %) | 30% |
| Signal strength (Σ trigger strength + diversity) | 40% |
| Solution match (triggers mapped to EXL packaged solutions) | 20% |
| Relationship warmth (EXL CE / Growth Leader / Owner) | 10% |

## Trigger library (13 rules)

See `pipeline/TRIGGERS_REPORT.md` for the full catalog. All rules are deterministic and source-cited.

## Full lead briefs

- [01. Travelers Group (89.3)](leads/01_travelers_group.md)
- [02. Allstate (64.5)](leads/02_allstate.md)
- [03. Liberty Mutual (56.3)](leads/03_liberty_mutual.md)
- [04. State Farm (54.4)](leads/04_state_farm.md)
- [05. Hanover Insurance Group (54.0)](leads/05_hanover_insurance_group.md)
- [06. Munich-Amer Hldg Corp Cos (53.2)](leads/06_munich_amer_hldg_corp_cos.md)
- [07. Swiss Re (51.8)](leads/07_swiss_re.md)
- [08. Amer Family Ins Group (51.3)](leads/08_amer_family_ins_group.md)
- [09. Hartford (51.0)](leads/09_hartford.md)
- [10. Nationwide (50.5)](leads/10_nationwide.md)
- [11. Great Amer P&C Ins Group (49.9)](leads/11_great_amer_p_c_ins_group.md)
- [12. Marsh (48.4)](leads/12_marsh.md)
- [13. AXIS US Operations (46.8)](leads/13_axis_us_operations.md)
- [14. American Family (44.2)](leads/14_american_family.md)
- [15. Axis (44.2)](leads/15_axis.md)
- [16. QBE (42.4)](leads/16_qbe.md)
- [17. Aviva (42.4)](leads/17_aviva.md)
- [18. MAPFRE (42.4)](leads/18_mapfre.md)
- [19. Suncorp (42.4)](leads/19_suncorp.md)
- [20. IAG (42.4)](leads/20_iag.md)


---

## All artifacts (end-to-end)

```
pipeline/
├── ingest.py          → 18 typed CSVs + audit log
├── audit.py           → row-by-row coverage reconciliation (PASS)
├── profiles.py        → per-account profiles + engagement summary
├── triggers.py        → 13-rule trigger library + firings with citations
├── score.py           → solution matching + 4-component weighted scoring
├── synthesize.py      → polished lead briefs (THIS STAGE)
├── data/*.csv         → all the structured outputs
└── leads/*.md         → top-20 briefs (one .md per lead)
```

Re-run from scratch:
```
python3 pipeline/ingest.py && python3 pipeline/audit.py && \
python3 pipeline/profiles.py && python3 pipeline/triggers.py && \
python3 pipeline/score.py && python3 pipeline/synthesize.py
```

Total runtime: ~5 seconds for 236 accounts.
