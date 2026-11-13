export interface StructuredOption {
  id: string;
  text: string;
  original_label?: string | null;
  internal_label: string;
  source_order: number;
  confidence?: number;
  is_user_edited?: boolean;
}

export interface AnalysisDisplayData {
  suggested_answer: string;
  answer_text: string;
  original_label?: string | null;
  source_position?: number | null;
  explanation: string;
}

export function formatClipboardAnswer(analysis: AnalysisDisplayData): string;
export function formatAnswerBadge(analysis: AnalysisDisplayData): string;
export function handleOptionTextChange(
  current: StructuredOption[],
  internalLabel: string,
  newText: string
): StructuredOption[];
export function addOptionItem(
  current: StructuredOption[],
  existingKeys: string[]
): { nextKey: string | null; updated: StructuredOption[] };
export function removeOptionItem(
  current: StructuredOption[],
  internalLabelToRemove: string
): StructuredOption[];
export function resolveAnswerOnShuffle(
  structuredOptions: StructuredOption[],
  correctText: string
): { source_position: number; original_label: string | null; answer_text: string } | null;

