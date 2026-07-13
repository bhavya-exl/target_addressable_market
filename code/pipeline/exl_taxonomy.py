"""
EXL Official Taxonomy + Product Catalog
========================================
Sourced from `docs/project_plan/Addressable Market Tracker (Project Plan).pptx`:
  - Slides 6, 16, 17  → P&C value chain
  - Slides 8-9, 14-15 → L&A value chain
  - Slide 7           → Service offering pillars
  - Slides 10-11      → Partnering Matrix retention benchmarks
  - All slides        → Product names + outcome metrics

This is the canonical vocabulary the lead engine uses in synthesized briefs.
"""

# ============ Service offering pillars (slide 7) ============
SERVICE_PILLARS = {
    "DTEO":  "Digital/Technology enabled Operations",
    "DAI":   "Data & AI-led Transformation",
    "ETAM":  "Enterprise Tech, Analytics & Data Modernization",
    "PIC":   "Platform Implementation and Conversion",
}

# ============ P&C value chain (slide 6, 16, 17) ============
PC_FUNCTIONS = {
    "Broker Management": [
        "Marketing Analytics", "Indexing", "New Agent/Set-up", "Licensing",
        "Agency Billing", "Renewals", "Debt Management", "Transfers",
        "Maintenance", "Unpaid items and written premiums",
        "Reconciliation of accounts", "Payment receipt and processing",
        "Collections",
    ],
    "Actuarial / New Business / UW": [
        "Actuarial Support", "New Business Intake and Set-up",
        "Monitor Status of pending contracts", "Indexing", "Policy Issuance",
        "Application Entry", "Pre- & Post-Underwriting Support",
        "Customer service", "Pre-Quotes and Quotes", "Book Rolls",
        "Competitor Benchmarking", "Pricing Reviews",
    ],
    "Policy Administration": [
        "State Filing", "Indexing", "Mailroom Ops and Scanning",
        "Policy Conversion", "Policy Processing", "Endorsements intake and setup",
        "Renewals/Cancellations", "Administration", "Mid-term Adjustments",
        "Correspondence", "Coverage Verification", "Exception Processing",
        "Premium Audit", "Coding", "Customer service",
    ],
    "Claims Management": [
        "First Notification of Loss (FNOL)", "Claim Intake and setup",
        "Categorization & Claims Indexing", "Claim Administration",
        "Dispute Handling", "Rental Car",
        "Claim Legal - Medical Record and construction defect summarization",
        "Third Party Claims", "Claims Adjudication", "Eligibility Verification",
        "Long Term Disability Claims", "Subrogation Collections",
        "Utilization Review",
    ],
    "Accounting / Billing": [
        "Broker Collections", "Direct Debit Set-up", "Premium Administration",
        "Research & Reconciliation", "Write-offs, Refunds", "Credit Control",
        "Query Management", "Accounts Payable", "Account Maintenance",
        "Bill Maintenance, Remittance, Reconciliation",
        "Agency Bill Operations", "Loss Sensitive Receivables",
    ],
}

# ============ L&A value chain (slides 8-9, 14-15) ============
LA_FUNCTIONS = {
    "Product Development": [
        "Actuarial support", "Low-code/No-code configuration",
        "Product innovation", "Pricing analytics",
    ],
    "Sales, Marketing, Agency Management": [
        "Agent setup", "Agent licensing and appointment",
        "Agency renewals", "Debt management", "New agency acquisition",
        "Commission",
    ],
    "New Business and Underwriting": [
        "Application pre-screening / completeness review",
        "Policy issuance", "Delivery and correspondence", "Policy administration",
        "Accelerated underwriting", "APS summarization",
    ],
    "Policy Administration & Billing": [
        "Customer service / Contact Center", "Billing and payments / Lockbox",
        "Reconciliation - Daily, Monthly, Quarterly, Annual",
        "Assignments, Riders, Debit authorization (EFT)",
    ],
    "Claims": [
        "First notice of claim", "Electronic data interchange",
        "Disability premium Waivers", "ICD10 diagnosis Codes",
        "Claim Packets Follow Ups", "Claim Adjudication",
        "Support for standard and non-standard Medicare plans",
    ],
}

# ============ EXL product catalog (slides 7, 8-9, 14-17) ============
EXL_PRODUCTS = {
    "EXL XTRAKTO.AI": {
        "what": "Intelligent document processing — automated data extraction from forms, ACORD, mail, email",
        "applies_to_fn": ["Indexing", "Mailroom Ops", "Application Entry",
                          "FNOL", "Claim Intake", "Premium Audit",
                          "Pre- & Post-Underwriting Support"],
        "applies_to_area": ["Claims Management", "Actuarial / New Business / UW",
                            "Policy Administration", "New Business and Underwriting"],
        "outcome": "25-30% reduction in cost of operations, 30% improvement in cycle time",
        "pillar": "DAI",
    },
    "EXL EXELIA.AI": {
        "what": "Conversational AI — voicebot/chatbot for self-service",
        "applies_to_fn": ["Customer service", "Inbound calls", "Policy Servicing", "Query Management"],
        "applies_to_area": ["Policy Administration", "Policy Administration & Billing",
                            "Sales, Marketing, Agency Management"],
        "outcome": "AHT reduction, 5-10 pt NPS increase, increase in First Call Resolution",
        "pillar": "DAI",
    },
    "EXL Engage": {
        "what": "Self-service customer engagement platform — portals, mobile, omnichannel",
        "applies_to_fn": ["Customer service", "Inbound calls", "Self-service"],
        "applies_to_area": ["Policy Administration"],
        "outcome": "5-10 pt NPS increase, increase in First Call Resolution",
        "pillar": "DTEO",
    },
    "EXL LifePRO": {
        "what": "L&A policy admin platform (proprietary)",
        "applies_to_fn": ["Policy Administration"],
        "applies_to_area": ["Policy Administration & Billing"],
        "outcome": "10-15% reduced cost to serve, 15-20% AHT improvement",
        "pillar": "PIC",
        "lob": "L&A",
    },
    "EXL MedConnection": {
        "what": "APS (Attending Physician Statement) summarization, medical record processing",
        "applies_to_fn": ["Medical record summarization", "Claim Legal",
                          "Accelerated underwriting", "APS summarization"],
        "applies_to_area": ["Claims Management", "New Business and Underwriting"],
        "outcome": "25-30% reduction in medical costs through intelligent triage",
        "pillar": "DAI",
    },
    "EXL Subrosource": {
        "what": "End-to-end subrogation handling — demand letters, third-party follow-up, recovery",
        "applies_to_fn": ["Subrogation Collections", "End to end subrogation handling"],
        "applies_to_area": ["Claims Management"],
        "outcome": "Subrogation recovery uplift, 4-5% reduction in claim operational expenses",
        "pillar": "DTEO",
    },
    "EXL Paymentor": {
        "what": "Payment automation — accounts payable, payment processing, leakage detection",
        "applies_to_fn": ["Accounts Payable", "Payments", "Account Maintenance",
                          "Check Issuance and EFTs", "Payment receipt and processing"],
        "applies_to_area": ["Accounting / Billing", "Policy Administration"],
        "outcome": "100% reduction in payment leakage, 40-60% reduction in F&A cost",
        "pillar": "DTEO",
    },
    "EXL Digital Finance Suite": {
        "what": "F&A automation including Reconciliations Accelerator",
        "applies_to_fn": ["Reconciliation", "Bill Maintenance, Remittance, Reconciliation",
                          "Premium Administration", "Research & Reconciliation",
                          "Credit Control"],
        "applies_to_area": ["Accounting / Billing"],
        "outcome": "40-60% reduction in F&A cost, 100% payment-leakage elimination",
        "pillar": "DTEO",
    },
    "EXL Customer 360": {
        "what": "Unified customer view across policy, claims, billing",
        "applies_to_fn": ["Customer service", "Marketing Analytics", "Agent setup"],
        "applies_to_area": ["Sales, Marketing, Agency Management", "Broker Management"],
        "outcome": "24M+ quality leads generated, $518M+ estimated value uplift",
        "pillar": "DAI",
    },
    "EXL NerveHub": {
        "what": "Workflow orchestration — connects intake, decisioning, and ops across the value chain",
        "applies_to_fn": ["Cross-process orchestration"],
        "applies_to_area": ["Broker Management", "Actuarial / New Business / UW",
                            "Policy Administration", "Claims Management"],
        "outcome": "Cross-process efficiency, integrated end-to-end visibility",
        "pillar": "ETAM",
    },
    "EXL Assist": {
        "what": "Underwriter workbench — submission triage, pre/post UW support",
        "applies_to_fn": ["Pre- & Post-Underwriting Support", "Submission prioritization",
                          "Risk selection"],
        "applies_to_area": ["Actuarial / New Business / UW"],
        "outcome": "30% improvement in UW cycle time, 25-30% reduction in cost of operations",
        "pillar": "DAI",
    },
    "EXL DIVA": {
        "what": "Intelligent virtual assistant for ops support",
        "applies_to_fn": ["Customer service", "Agent self-service"],
        "applies_to_area": ["Policy Administration & Billing"],
        "outcome": "Operational efficiency lift",
        "pillar": "DAI",
    },
}

# ============ Partnering Matrix: typical EXL retention by function (slides 10-11) ============
# Each entry: (min_retention, max_retention, headroom_label).
# "Retention" = % of that function EXL typically holds when in an account.
# Low retention = lots of headroom to grow.
RETENTION_BENCHMARKS = {
    # P&C UW (slide 10)
    "Underwriting Info Gathering":    (0.85, 0.90),   # high retention - mature offering
    "Account Set Up & Clearance":     (0.25, 0.35),   # high headroom
    "Underwriting Rating":            (0.25, 0.35),
    "Underwriting Risk Assessment":   (0.10, 0.20),   # very high headroom
    "Policy Issuance":                (0.25, 0.35),
    "Policy Servicing":               (0.30, 0.40),
    # P&C Claims (slide 11)
    "Claims Set up (FNOL)":           (0.10, 0.20),   # very high headroom
    "Coverage verification":          (0.60, 0.70),
    "Investigation":                  (0.65, 0.70),
    "Resolution":                     (0.60, 0.70),
    "Subrogation":                    (0.40, 0.50),
    "Compliance":                     (0.20, 0.30),
}

# ============ Function-to-product mapping (which EXL products fit each function bucket) ============
# Keyed by the function buckets our pipeline already uses (Claims/FNOL, Underwriting, etc.)
# Each value: list of EXL product names (in suggested-pitch priority order).
FUNCTION_TO_PRODUCTS = {
    "Claims / FNOL": [
        "EXL XTRAKTO.AI",        # document intake
        "EXL Subrosource",       # subrogation
        "EXL MedConnection",     # medical record summarization
        "EXL EXELIA.AI",         # customer-facing voice/chat at FNOL
        "EXL Paymentor",         # claim payment automation
    ],
    "Underwriting": [
        "EXL Assist",            # UW workbench
        "EXL XTRAKTO.AI",        # submission/ACORD extraction
        "EXL NerveHub",          # orchestration
        "EXL MedConnection",     # accelerated UW for L&A
    ],
    "Policy Admin": [
        "EXL XTRAKTO.AI",        # endorsement / docs
        "EXL EXELIA.AI",         # servicing voice/chat
        "EXL Engage",            # self-service portal
        "EXL Paymentor",         # premium payment
        "EXL LifePRO",           # L&A only
    ],
    "Premium Audit": [
        "EXL XTRAKTO.AI",
        "EXL Digital Finance Suite",
    ],
    "F&A / Finance": [
        "EXL Paymentor",
        "EXL Digital Finance Suite",
        "EXL XTRAKTO.AI",
    ],
    "Platform / Tech": [
        "EXL LifePRO",           # L&A
        "EXL NerveHub",
    ],
    # New buckets the deck exposes
    "Broker Management": [
        "EXL Customer 360",
        "EXL Digital Finance Suite",
        "EXL XTRAKTO.AI",
    ],
    "Subrogation": [
        "EXL Subrosource",
        "EXL XTRAKTO.AI",
    ],
}

# ============ Legacy code -> EXL product map (replaces the old generic names) ============
# Used to upgrade the existing pipeline's solution-code references.
LEGACY_CODE_TO_PRODUCT = {
    "FNOL":      "EXL XTRAKTO.AI + EXL EXELIA.AI (FNOL stack)",
    "FNOL-aaS":  "EXL XTRAKTO.AI + EXL EXELIA.AI (FNOL stack)",
    "PaaS":      "EXL Paymentor + EXL Digital Finance Suite",
    "DT-WC":     "EXL XTRAKTO.AI + EXL Subrosource + EXL MedConnection (WC stack)",
    "NB-PaaS":   "EXL XTRAKTO.AI + EXL Assist (New Business stack)",
    "NB_PaaS":   "EXL XTRAKTO.AI + EXL Assist (New Business stack)",
    "E-E2E":     "EXL NerveHub + EXL XTRAKTO.AI (Endorsements stack)",
    "E_E2E":     "EXL NerveHub + EXL XTRAKTO.AI (Endorsements stack)",
    "BIE":       "EXL Engage + EXL Customer 360",
    "Int-Col":   "EXL Digital Finance Suite + EXL Paymentor",
    "Int_Col":   "EXL Digital Finance Suite + EXL Paymentor",
    "Audit-ATC": "EXL XTRAKTO.AI + EXL Digital Finance Suite (Audit Analytics)",
    "PRA":       "EXL NerveHub + EXL Digital Finance Suite (Process Risk Assessment)",
    "Fin-Auto":  "EXL Paymentor + EXL Digital Finance Suite",
    "DT-CUW":    "EXL Assist + EXL XTRAKTO.AI (Commercial UW stack)",
    "TrRFF":     "EXL NerveHub (workflow orchestration)",
}

# ============ Helpers ============

def product_info(name):
    """Returns the catalog dict for a product, or None."""
    return EXL_PRODUCTS.get(name)

def product_outcome(name):
    """Returns the typical outcome metric for a product, or empty."""
    info = EXL_PRODUCTS.get(name)
    return info.get("outcome", "") if info else ""

def products_for_function(func_bucket):
    """Returns the list of EXL products that fit the given function bucket."""
    return FUNCTION_TO_PRODUCTS.get(func_bucket, [])

def retention_headroom(function_label):
    """Returns (max_headroom_pct, label) — fraction not retained by EXL, i.e. where competitors play."""
    bm = RETENTION_BENCHMARKS.get(function_label)
    if not bm: return (None, "")
    avg = (bm[0] + bm[1]) / 2
    headroom = 1 - avg
    if headroom >= 0.70:
        label = "very high headroom"
    elif headroom >= 0.50:
        label = "high headroom"
    elif headroom >= 0.30:
        label = "moderate headroom"
    else:
        label = "low headroom (EXL mature)"
    return (round(headroom * 100, 0), label)

def map_legacy_code(code_or_codes):
    """Maps a legacy solution code (or '; '-separated list) to EXL product names."""
    if not code_or_codes: return ""
    out = []
    for code in str(code_or_codes).split(";"):
        code = code.strip()
        if code in LEGACY_CODE_TO_PRODUCT:
            out.append(LEGACY_CODE_TO_PRODUCT[code])
        elif code:
            out.append(code)
    return "; ".join(out)
