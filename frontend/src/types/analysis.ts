export type Summary = {
  short_summary: string;
  key_points: string[];
};

export type Clause = {
  clause_id: string;
  heading: string;
  category: string;
  extracted_text: string;
  confidence: number;
  page_reference?: number | null;
};

export type RiskFlag = {
  risk_id: string;
  severity: string;
  title: string;
  description: string;
  recommendation: string;
  impacted_clause_id?: string | null;
};

export type Analysis = {
  document_id: string;
  filename: string;
  document_type: string;
  summary: Summary;
  clauses: Clause[];
  risk_flags: RiskFlag[];
  created_at: string;
};

export type RecentAnalysesResponse = {
  items: Array<{
    document_id: string;
    filename: string;
    document_type: string;
    created_at: string;
  }>;
};
