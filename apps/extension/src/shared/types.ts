export type AnalysisResponse = {
  analysis_id: string;
  snapshot_hash: string;
  instrument_id: string;
  data_version: number;
  action: string;
  confidence: number;
  summary: string;
  reasons: string[];
};

export type AnalyzeStockResponse = {
  success: boolean;
  data?: AnalysisResponse;
  error?: string;
};
