/**
 * Option Identity and Clipboard Formatting Utilities
 * GT InnoX LLP - ExamPilot 2.0
 */

/**
 * Format answer and pedagogical explanation for clipboard copying.
 * Guarantees never inventing letters for unlettered questions.
 */
export function formatClipboardAnswer(analysis) {
  if (!analysis) return "";
  const header = analysis.original_label
    ? `Correct Answer: Option ${analysis.original_label}: ${analysis.answer_text}`
    : `Correct Answer: ${analysis.answer_text} (Item #${analysis.source_position || 1})`;
  return `${header}\n\nExplanation:\n${analysis.explanation || ""}`;
}

/**
 * Format answer badge label for visual UI display.
 */
export function formatAnswerBadge(analysis) {
  if (!analysis) return "";
  return analysis.original_label
    ? `Suggested Answer: Option ${analysis.original_label}`
    : `Suggested Answer: ${analysis.answer_text} (Item #${analysis.source_position || 1})`;
}

/**
 * Update text of a structured option while preserving its stable identity,
 * source order, and marking is_user_edited: true.
 */
export function handleOptionTextChange(current, internalLabel, newText) {
  const idx = current.findIndex(o => o.internal_label === internalLabel);
  if (idx !== -1) {
    const updated = [...current];
    updated[idx] = {
      ...updated[idx],
      text: newText,
      is_user_edited: true,
    };
    return updated;
  }
  return [
    ...current,
    {
      id: `opt_${Date.now()}_${internalLabel}`,
      text: newText,
      original_label: null,
      internal_label: internalLabel,
      source_order: current.length + 1,
      confidence: 1.0,
      is_user_edited: true,
    },
  ];
}

/**
 * Add a new option slot with next available alphabet key,
 * assigning sequential source order.
 */
export function addOptionItem(current, existingKeys) {
  const candidateKeys = ["A", "B", "C", "D", "E", "F", "G", "H"];
  const nextKey = candidateKeys.find(k => !existingKeys.includes(k)) || null;
  if (!nextKey) return { nextKey: null, updated: current };

  const newOpt = {
    id: `opt_${Date.now()}_${nextKey}`,
    text: "",
    original_label: null,
    internal_label: nextKey,
    source_order: current.length + 1,
    confidence: 1.0,
    is_user_edited: true,
  };
  return { nextKey, updated: [...current, newOpt] };
}

/**
 * Remove an option slot and re-index remaining source orders from 1 to N.
 */
export function removeOptionItem(current, internalLabelToRemove) {
  const filtered = current.filter(o => o.internal_label !== internalLabelToRemove);
  return filtered.map((o, idx) => ({ ...o, source_order: idx + 1 }));
}

/**
 * Resolve answer position after options are shuffled by an exam platform.
 */
export function resolveAnswerOnShuffle(structuredOptions, correctText) {
  const match = structuredOptions.find(
    o => o.text.trim().toLowerCase() === correctText.trim().toLowerCase()
  );
  if (!match) return null;
  return {
    source_position: match.source_order,
    original_label: match.original_label || null,
    answer_text: match.text,
  };
}

