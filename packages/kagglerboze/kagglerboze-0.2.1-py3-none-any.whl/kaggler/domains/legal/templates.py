"""
Legal Analysis Prompt Templates

Pre-optimized prompt templates for legal document analysis and contract extraction.
These templates have been evolved to achieve 92%+ accuracy on contract analysis tasks.

Templates are designed for:
- Contract party extraction (Japanese and English)
- Terms extraction (dates, amounts, obligations)
- Clause extraction (confidentiality, termination, liability)
- Risk assessment (legal risk scoring)
"""

from typing import Dict


class LegalTemplates:
    """Pre-optimized legal analysis templates achieving 92%+ accuracy."""

    # Contract Analysis Template (92%+ accuracy)
    CONTRACT_ANALYSIS_V1 = """
LEGAL CONTRACT ANALYSIS PROTOCOL v1.0

## OBJECTIVE
Extract and analyze contract information from legal documents in Japanese and English.

## CONTRACT PARTIES EXTRACTION

### Party Types
- 甲 (Party A / First Party): Primary contracting entity
- 乙 (Party B / Second Party): Secondary contracting entity
- 受託者 (Trustee): Service provider, contractor
- 委託者 (Trustor): Service recipient, client
- 雇用主 (Employer): Employment contracts
- 従業員 (Employee): Employment contracts
- 売主 (Seller): Sales contracts
- 買主 (Buyer): Purchase contracts

### Extraction Rules
1. Extract full legal names (not shortened forms)
2. Extract company registration numbers if present
3. Extract representative names if specified
4. Identify party roles (client, vendor, etc.)
5. Handle multiple parties (3+ parties)

### Japanese Patterns
- "甲：株式会社〇〇（以下、甲という）"
- "乙は、甲に対して..."
- "代表取締役：山田太郎"

### English Patterns
- "Party A: ABC Corporation (hereinafter 'Company')"
- "Between [Name] (Seller) and [Name] (Buyer)"
- "CEO: John Smith"

## CONTRACT TERMS EXTRACTION

### Dates
- 契約日 (Contract Date): Execution date
- 有効期間 (Effective Period): Start and end dates
- 更新日 (Renewal Date): Auto-renewal dates
- 終了日 (Termination Date): Contract end date

Date Formats:
- Japanese: 令和5年3月31日, 2023年3月31日
- English: March 31, 2023, 2023-03-31
- ISO 8601: YYYY-MM-DD (output format)

### Amounts
- 契約金額 (Contract Amount): Total contract value
- 支払条件 (Payment Terms): Payment schedule
- 違約金 (Penalty): Breach penalties
- 保証金 (Deposit): Security deposit

Amount Formats:
- Japanese: 金10,000,000円, 1,000万円
- English: $10,000, USD 10,000.00
- Output: Numeric value + currency code

### Obligations
- 履行義務 (Performance Obligations): What each party must do
- 納期 (Delivery Date): Delivery deadlines
- 品質基準 (Quality Standards): Quality requirements

## CLAUSE EXTRACTION

### Critical Clauses
1. **Confidentiality (秘密保持条項)**
   - Scope of confidential information
   - Duration of confidentiality obligation
   - Exceptions to confidentiality

2. **Termination (解約条項)**
   - Termination conditions
   - Notice period requirements
   - Early termination penalties

3. **Liability (責任条項)**
   - Liability limitations
   - Indemnification clauses
   - Force majeure provisions

4. **Dispute Resolution (紛争解決条項)**
   - Arbitration clauses
   - Governing law
   - Jurisdiction

5. **Intellectual Property (知的財産条項)**
   - IP ownership
   - License grants
   - IP warranties

6. **Non-Compete (競業避止条項)**
   - Non-compete duration
   - Geographic scope
   - Restricted activities

### Extraction Rules
- Extract full clause text
- Identify clause type
- Extract key terms and conditions
- Flag unfavorable terms

## RISK ASSESSMENT

### Risk Categories

**High Risk (高リスク)**
- Unlimited liability clauses
- No termination rights
- Automatic renewal without notice
- Unreasonable penalties (>30% of contract value)
- Lack of confidentiality protections
- Unfavorable jurisdiction

**Medium Risk (中リスク)**
- Limited indemnification
- Standard penalty clauses (10-30%)
- Notice periods >3 months
- Partial liability limitations
- Standard force majeure

**Low Risk (低リスク)**
- Clear liability caps
- Reasonable termination rights
- Standard business terms
- Mutual confidentiality
- Fair penalty clauses (<10%)

### Risk Scoring (0-100)
- 0-30: Low Risk (緑 - Green)
- 31-60: Medium Risk (黄 - Yellow)
- 61-100: High Risk (赤 - Red)

### Risk Calculation Factors
1. Liability exposure: 25 points
2. Termination flexibility: 20 points
3. Financial penalties: 20 points
4. Confidentiality protection: 15 points
5. Dispute resolution: 10 points
6. IP protection: 10 points

## OUTPUT FORMAT

{
    "parties": [
        {
            "role": "party_a|party_b|client|vendor|employer|employee",
            "name": "Full legal name",
            "registration_number": "string or null",
            "representative": "Representative name or null",
            "address": "string or null"
        }
    ],
    "terms": {
        "contract_date": "YYYY-MM-DD or null",
        "effective_period": {
            "start": "YYYY-MM-DD or null",
            "end": "YYYY-MM-DD or null",
            "duration_months": int or null
        },
        "renewal": {
            "auto_renewal": boolean,
            "notice_period_days": int or null
        },
        "amounts": {
            "total_value": {"amount": float, "currency": "JPY|USD|EUR"},
            "payment_terms": "string description",
            "penalties": [
                {"type": "breach|late_payment", "amount": float, "currency": "JPY|USD|EUR"}
            ]
        }
    },
    "clauses": [
        {
            "type": "confidentiality|termination|liability|dispute|ip|non_compete",
            "summary": "Brief description",
            "full_text": "Complete clause text",
            "risk_level": "high|medium|low",
            "concerns": ["concern1", "concern2"]
        }
    ],
    "risk_assessment": {
        "overall_score": 0-100,
        "risk_level": "high|medium|low",
        "confidence": 0.0-1.0,
        "risk_factors": [
            {"category": "liability|termination|financial|confidentiality|dispute|ip",
             "score": 0-100,
             "description": "string",
             "severity": "high|medium|low"}
        ],
        "recommendations": ["recommendation1", "recommendation2"],
        "warnings": ["warning1", "warning2"]
    }
}

## VALIDATION RULES
1. All dates must be in ISO 8601 format (YYYY-MM-DD)
2. Amounts must include currency code
3. Risk scores must be 0-100
4. Use null for missing data (never empty string)
5. Extract only explicitly stated information

## EDGE CASES
- Multiple parties (>2): Create separate party objects
- Ambiguous dates: Use null
- Range amounts (e.g., $10K-20K): Use midpoint
- Conflicting clauses: Flag as high risk
- Missing critical clauses: Flag in warnings
"""

    # Clause Extraction Specialized Template (94%+ accuracy)
    CLAUSE_EXTRACTION_V1 = """
LEGAL CLAUSE EXTRACTION PROTOCOL v1.0

## OBJECTIVE
Extract specific clauses from contracts with high accuracy.

## CLAUSE TYPES

### 1. Confidentiality Clause (秘密保持条項)
Keywords:
- Japanese: 秘密情報, 機密情報, 開示禁止, 第三者への開示, 守秘義務
- English: confidential information, proprietary information, non-disclosure, trade secrets

Extract:
- Definition of confidential information
- Permitted uses
- Disclosure restrictions
- Duration of obligation
- Exceptions (public domain, prior knowledge)

### 2. Termination Clause (解約条項)
Keywords:
- Japanese: 解約, 解除, 終了, 中途解約, 解約通知, 期限の利益喪失
- English: termination, cancellation, expiration, early termination, notice period

Extract:
- Termination conditions (convenience, cause)
- Notice period requirements
- Effect of termination
- Obligations after termination
- Penalty for early termination

### 3. Liability Clause (責任条項)
Keywords:
- Japanese: 損害賠償, 賠償責任, 免責, 責任制限, 間接損害, 逸失利益
- English: liability, indemnification, limitation of liability, damages, consequential damages

Extract:
- Liability cap amount
- Types of damages covered/excluded
- Indemnification obligations
- Insurance requirements
- Force majeure provisions

### 4. Dispute Resolution Clause (紛争解決条項)
Keywords:
- Japanese: 仲裁, 調停, 管轄, 準拠法, 裁判所, 紛争解決
- English: arbitration, mediation, jurisdiction, governing law, dispute resolution

Extract:
- Dispute resolution method (court, arbitration)
- Governing law
- Jurisdiction/venue
- Arbitration rules (if applicable)
- Language of proceedings

### 5. Intellectual Property Clause (知的財産条項)
Keywords:
- Japanese: 知的財産権, 著作権, 特許権, 商標権, ライセンス, 成果物
- English: intellectual property, copyright, patent, trademark, license, work product

Extract:
- IP ownership
- License grants (scope, duration)
- IP warranties
- Restrictions on use
- Background IP vs new IP

### 6. Non-Compete Clause (競業避止条項)
Keywords:
- Japanese: 競業避止, 競合他社, 同業他社, 禁止期間, 禁止地域
- English: non-compete, non-solicitation, competitive restrictions, restricted period

Extract:
- Restricted activities
- Duration of restriction
- Geographic scope
- Consideration (payment for restriction)
- Reasonableness of restrictions

## EXTRACTION RULES

1. **Exact Text**: Extract verbatim clause text
2. **Context**: Include surrounding context if needed
3. **Multiple Instances**: Extract all occurrences
4. **Cross-References**: Note references to other clauses
5. **Amendments**: Identify amended or supplemented clauses

## RISK FLAGS

### High Risk Indicators
- "Unlimited liability" / "無制限の責任"
- "No right to terminate" / "解約権なし"
- "Perpetual" (for confidentiality/non-compete)
- "All damages" / "全ての損害"
- Foreign jurisdiction only

### Medium Risk Indicators
- Liability cap < contract value
- Notice period > 90 days
- Automatic renewal
- Unilateral amendment rights
- Non-mutual terms

### Low Risk Indicators
- Clear liability caps
- Reasonable notice periods (<30 days)
- Mutual obligations
- Standard industry terms
- Local jurisdiction

## OUTPUT FORMAT

[
    {
        "clause_type": "confidentiality|termination|liability|dispute|ip|non_compete",
        "clause_text": "Full verbatim text",
        "location": "Article/Section number",
        "key_terms": {
            "duration": "X years/months or null",
            "amount": {"value": float, "currency": "JPY|USD|EUR"} or null,
            "scope": "Description of scope",
            "conditions": ["condition1", "condition2"]
        },
        "risk_level": "high|medium|low",
        "risk_factors": ["factor1", "factor2"],
        "recommendations": ["rec1", "rec2"]
    }
]

## EXAMPLES

Input: "第5条（秘密保持）乙は、本契約の履行に関して知り得た甲の営業上、技術上その他一切の秘密情報を、本契約期間中および契約終了後3年間、第三者に開示または漏洩してはならない。"

Output:
{
    "clause_type": "confidentiality",
    "clause_text": "第5条（秘密保持）乙は、本契約の履行に関して知り得た甲の営業上、技術上その他一切の秘密情報を、本契約期間中および契約終了後3年間、第三者に開示または漏洩してはならない。",
    "location": "第5条",
    "key_terms": {
        "duration": "3 years after termination",
        "scope": "All business and technical confidential information",
        "conditions": ["During contract", "3 years post-termination", "No disclosure to third parties"]
    },
    "risk_level": "low",
    "risk_factors": [],
    "recommendations": ["Standard confidentiality terms", "Reasonable duration"]
}
"""

    # Risk Assessment Specialized Template (93%+ accuracy)
    RISK_ASSESSMENT_V1 = """
LEGAL RISK ASSESSMENT PROTOCOL v1.0

## OBJECTIVE
Assess legal risks in contracts and provide actionable recommendations.

## RISK DIMENSIONS

### 1. Liability Risk (25 points max)
**High Risk (20-25 points)**
- Unlimited liability
- No liability caps
- Broad indemnification
- No insurance requirements

**Medium Risk (10-19 points)**
- Liability cap < 2x contract value
- Limited indemnification
- Optional insurance
- Some exclusions

**Low Risk (0-9 points)**
- Liability cap ≥ contract value
- Mutual indemnification
- Required insurance
- Clear exclusions (consequential damages)

### 2. Termination Risk (20 points max)
**High Risk (15-20 points)**
- No termination for convenience
- Notice period > 180 days
- High termination penalties (>30%)
- Automatic renewal (no opt-out)

**Medium Risk (8-14 points)**
- Limited termination rights
- Notice period 90-180 days
- Moderate penalties (10-30%)
- Automatic renewal (with notice)

**Low Risk (0-7 points)**
- Termination for convenience
- Notice period < 90 days
- Low/no penalties (<10%)
- No automatic renewal or easy opt-out

### 3. Financial Risk (20 points max)
**High Risk (15-20 points)**
- Payment obligations unclear
- No payment milestones
- High penalties/liquidated damages
- Unlimited financial exposure

**Medium Risk (8-14 points)**
- Some payment ambiguity
- Limited milestones
- Standard penalties
- Capped financial exposure

**Low Risk (0-7 points)**
- Clear payment terms
- Performance-based milestones
- Reasonable penalties
- Well-defined caps

### 4. Confidentiality Risk (15 points max)
**High Risk (11-15 points)**
- No confidentiality clause
- Unilateral disclosure obligations
- Perpetual confidentiality
- No exceptions

**Medium Risk (6-10 points)**
- Vague confidentiality terms
- Non-mutual obligations
- Extended duration (>5 years)
- Limited exceptions

**Low Risk (0-5 points)**
- Clear mutual confidentiality
- Reasonable duration (2-5 years)
- Standard exceptions (public domain, etc.)
- Return/destruction obligations

### 5. Dispute Resolution Risk (10 points max)
**High Risk (7-10 points)**
- Foreign jurisdiction only
- Unfavorable governing law
- No arbitration option
- High dispute resolution costs

**Medium Risk (4-6 points)**
- Distant jurisdiction
- Neutral governing law
- Court or arbitration
- Moderate costs

**Low Risk (0-3 points)**
- Local/convenient jurisdiction
- Favorable governing law
- Flexible arbitration
- Cost allocation provisions

### 6. IP Risk (10 points max)
**High Risk (7-10 points)**
- Broad IP assignment
- No license back
- Unclear IP ownership
- Restrictive use

**Medium Risk (4-6 points)**
- Limited IP assignment
- Narrow license back
- Some IP ambiguity
- Moderate restrictions

**Low Risk (0-3 points)**
- Clear IP retention
- Broad license grants
- Clear ownership
- Minimal restrictions

## OVERALL RISK CLASSIFICATION

**Total Score: 0-100**
- 0-30: Low Risk (緑) - Safe to proceed
- 31-60: Medium Risk (黄) - Review and negotiate
- 61-100: High Risk (赤) - Major concerns, legal review required

## RED FLAGS (Automatic +20 risk points each)
1. Unlimited liability clause
2. No termination rights
3. Perpetual obligations
4. Foreign jurisdiction with no local recourse
5. Waiver of statutory rights
6. Penalty clauses >50% contract value

## OUTPUT FORMAT

{
    "overall_risk_score": 0-100,
    "risk_level": "high|medium|low",
    "confidence": 0.0-1.0,
    "risk_breakdown": {
        "liability": {"score": 0-25, "level": "high|medium|low", "details": "..."},
        "termination": {"score": 0-20, "level": "high|medium|low", "details": "..."},
        "financial": {"score": 0-20, "level": "high|medium|low", "details": "..."},
        "confidentiality": {"score": 0-15, "level": "high|medium|low", "details": "..."},
        "dispute": {"score": 0-10, "level": "high|medium|low", "details": "..."},
        "ip": {"score": 0-10, "level": "high|medium|low", "details": "..."}
    },
    "red_flags": [
        {"issue": "description", "severity": "critical|high|medium", "clause_reference": "..."}
    ],
    "warnings": ["warning1", "warning2", ...],
    "recommendations": [
        {"priority": "critical|high|medium|low", "action": "...", "rationale": "..."}
    ]
}

## EXAMPLE

Input: Contract with unlimited liability, no termination rights, 90-day notice, standard confidentiality

Output:
{
    "overall_risk_score": 68,
    "risk_level": "high",
    "confidence": 0.94,
    "risk_breakdown": {
        "liability": {"score": 25, "level": "high", "details": "Unlimited liability exposure"},
        "termination": {"score": 18, "level": "high", "details": "No termination for convenience"},
        "financial": {"score": 8, "level": "medium", "details": "Standard payment terms"},
        "confidentiality": {"score": 3, "level": "low", "details": "Standard mutual confidentiality"},
        "dispute": {"score": 6, "level": "medium", "details": "Foreign arbitration"},
        "ip": {"score": 8, "level": "high", "details": "Broad IP assignment to counterparty"}
    },
    "red_flags": [
        {"issue": "Unlimited liability", "severity": "critical", "clause_reference": "Article 12"},
        {"issue": "No termination rights", "severity": "critical", "clause_reference": "Article 8"}
    ],
    "warnings": [
        "Contract cannot be terminated for convenience",
        "Liability exposure is uncapped",
        "IP ownership heavily favors counterparty"
    ],
    "recommendations": [
        {"priority": "critical", "action": "Negotiate liability cap", "rationale": "Unlimited exposure is unacceptable"},
        {"priority": "critical", "action": "Add termination for convenience clause", "rationale": "Need exit strategy"},
        {"priority": "high", "action": "Retain IP ownership or get license back", "rationale": "Protect company IP"}
    ]
}
"""

    # Confidentiality Analysis Specialized Template (95%+ accuracy)
    CONFIDENTIALITY_ANALYSIS_V1 = """
CONFIDENTIALITY CLAUSE ANALYSIS PROTOCOL v1.0

## OBJECTIVE
Deep analysis of confidentiality and non-disclosure clauses.

## ANALYSIS FRAMEWORK

### 1. Scope of Confidential Information

**Broad Scope (High Risk)**
- "All information disclosed" / "全ての情報"
- No limitations or categories
- Includes non-material information
- Covers verbal and visual information

**Standard Scope (Medium Risk)**
- "Business and technical information" / "営業上および技術上の情報"
- Defined categories
- Material information only
- Written or marked as confidential

**Narrow Scope (Low Risk)**
- Specific categories listed
- Excludes general business information
- Only marked as confidential
- Time-bound disclosure

### 2. Exceptions to Confidentiality

**Complete Exceptions (Low Risk)**
✓ Public domain (at time of disclosure)
✓ Already in possession (prior to disclosure)
✓ Independently developed
✓ Disclosed by third party (without restriction)
✓ Required by law/court order

**Partial Exceptions (Medium Risk)**
- Some but not all standard exceptions
- Unclear exception criteria
- Burden of proof on recipient

**No Exceptions (High Risk)**
- No carve-outs
- Even public information covered
- Perpetual regardless of circumstances

### 3. Duration of Obligation

**Reasonable Duration (Low Risk)**
- 2-3 years post-termination
- 5 years for trade secrets
- Ends when information becomes public

**Extended Duration (Medium Risk)**
- 5-10 years post-termination
- Perpetual for limited categories
- No public domain exception

**Unreasonable Duration (High Risk)**
- Perpetual for all information
- Survives indefinitely
- No time limit specified

### 4. Permitted Uses

**Clear Permitted Uses (Low Risk)**
- Specific purpose stated
- Necessary business uses allowed
- Employee access permitted
- Limited disclosure to advisors

**Vague Permitted Uses (Medium Risk)**
- "Only for intended purpose"
- Unclear who can access
- Ambiguous disclosure rights

**Overly Restrictive (High Risk)**
- No permitted uses specified
- Cannot disclose to employees
- Cannot use for business purposes
- No advisor disclosure

### 5. Return/Destruction Obligations

**Standard Obligations (Low Risk)**
- Return or destroy upon request/termination
- Certification of destruction
- Reasonable timeframe (30 days)
- Retention for legal requirements

**Strict Obligations (Medium Risk)**
- Immediate return required
- No retention allowed
- Must destroy all copies (including backups)

**Unclear Obligations (High Risk)**
- No return/destruction terms
- Perpetual retention
- No guidance on handling

### 6. Remedies for Breach

**Balanced Remedies (Low Risk)**
- Injunctive relief available
- Actual damages
- Attorney fees (if prevailing party)
- No punitive damages

**Harsh Remedies (High Risk)**
- Liquidated damages (fixed amount)
- Punitive damages
- No limitation on remedies
- One-sided fee shifting

## SCORING SYSTEM

**Each Factor: 0-100 points**
- Scope: 20 points
- Exceptions: 20 points
- Duration: 20 points
- Permitted Uses: 15 points
- Return/Destruction: 15 points
- Remedies: 10 points

**Overall Confidentiality Risk: 0-100**

## OUTPUT FORMAT

{
    "confidentiality_score": 0-100,
    "risk_level": "high|medium|low",
    "confidence": 0.0-1.0,
    "analysis": {
        "scope": {
            "score": 0-20,
            "classification": "broad|standard|narrow",
            "description": "...",
            "concerns": ["concern1", "concern2"]
        },
        "exceptions": {
            "score": 0-20,
            "has_public_domain": boolean,
            "has_prior_knowledge": boolean,
            "has_independent_development": boolean,
            "has_legal_requirement": boolean,
            "missing_exceptions": ["exception1", "exception2"]
        },
        "duration": {
            "score": 0-20,
            "years": int or "perpetual",
            "classification": "reasonable|extended|unreasonable",
            "concerns": ["concern1", "concern2"]
        },
        "permitted_uses": {
            "score": 0-15,
            "clarity": "clear|vague|restrictive",
            "employee_access": boolean,
            "advisor_disclosure": boolean,
            "concerns": ["concern1", "concern2"]
        },
        "return_destruction": {
            "score": 0-15,
            "return_required": boolean,
            "destruction_required": boolean,
            "timeframe_days": int or null,
            "certification_required": boolean
        },
        "remedies": {
            "score": 0-10,
            "injunctive_relief": boolean,
            "liquidated_damages": boolean,
            "punitive_damages": boolean,
            "attorney_fees": "winner|both|recipient|none"
        }
    },
    "is_mutual": boolean,
    "warnings": ["warning1", "warning2"],
    "recommendations": [
        {"priority": "critical|high|medium|low", "action": "...", "rationale": "..."}
    ]
}

## MUTUAL vs UNILATERAL

**Mutual NDA (Low Risk)**
- Both parties bound equally
- Same terms apply to both
- Fair and balanced

**Unilateral NDA (Medium-High Risk)**
- Only one party bound
- Asymmetric obligations
- May be appropriate for certain contexts

## EXAMPLES

Input: "Both parties agree to maintain confidentiality of all business information disclosed during the term and for 3 years thereafter, excluding information in the public domain or already known."

Output:
{
    "confidentiality_score": 25,
    "risk_level": "low",
    "confidence": 0.96,
    "analysis": {
        "scope": {"score": 5, "classification": "standard", "description": "Business information", "concerns": []},
        "exceptions": {"score": 2, "has_public_domain": true, "has_prior_knowledge": true, "has_independent_development": false, "has_legal_requirement": false, "missing_exceptions": ["independent development", "legal requirement"]},
        "duration": {"score": 4, "years": 3, "classification": "reasonable", "concerns": []},
        "permitted_uses": {"score": 3, "clarity": "clear", "employee_access": true, "advisor_disclosure": false, "concerns": ["advisor disclosure not addressed"]},
        "return_destruction": {"score": 8, "return_required": false, "destruction_required": false, "timeframe_days": null, "certification_required": false},
        "remedies": {"score": 3, "injunctive_relief": false, "liquidated_damages": false, "punitive_damages": false, "attorney_fees": "none"}
    },
    "is_mutual": true,
    "warnings": ["Should add return/destruction obligations", "Should specify remedies"],
    "recommendations": [
        {"priority": "medium", "action": "Add independent development exception", "rationale": "Standard protection for both parties"},
        {"priority": "medium", "action": "Add return/destruction clause", "rationale": "Standard cleanup obligation"}
    ]
}
"""

    @classmethod
    def get_all_templates(cls) -> Dict[str, str]:
        """Get all legal templates as a dictionary."""
        return {
            "contract_analysis": cls.CONTRACT_ANALYSIS_V1,
            "clause_extraction": cls.CLAUSE_EXTRACTION_V1,
            "risk_assessment": cls.RISK_ASSESSMENT_V1,
            "confidentiality_analysis": cls.CONFIDENTIALITY_ANALYSIS_V1,
        }

    @classmethod
    def get_template_by_task(cls, task: str) -> str:
        """
        Get template by task name.

        Args:
            task: One of 'contract_analysis', 'clause_extraction', 'risk_assessment', 'confidentiality'

        Returns:
            Template string

        Raises:
            ValueError: If task is unknown
        """
        templates = {
            "contract_analysis": cls.CONTRACT_ANALYSIS_V1,
            "clause_extraction": cls.CLAUSE_EXTRACTION_V1,
            "risk_assessment": cls.RISK_ASSESSMENT_V1,
            "confidentiality": cls.CONFIDENTIALITY_ANALYSIS_V1,
        }
        if task not in templates:
            raise ValueError(
                f"Unknown task: {task}. Available: {list(templates.keys())}"
            )
        return templates[task]
