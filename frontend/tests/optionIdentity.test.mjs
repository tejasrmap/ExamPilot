import test from "node:test";
import assert from "node:assert/strict";
import {
  formatClipboardAnswer,
  formatAnswerBadge,
  handleOptionTextChange,
  addOptionItem,
  removeOptionItem,
  resolveAnswerOnShuffle
} from "../lib/optionIdentity.js";

test("Option Identity — Lettered Clipboard Output", () => {
  const result = formatClipboardAnswer({
    suggested_answer: "B",
    answer_text: "TCP",
    original_label: "B",
    source_position: 2,
    explanation: "TCP guarantees reliable byte-stream delivery."
  });

  assert.equal(
    result,
    "Correct Answer: Option B: TCP\n\nExplanation:\nTCP guarantees reliable byte-stream delivery."
  );
  assert.ok(result.startsWith("Correct Answer: Option B: TCP"));
});

test("Option Identity — Unlettered Clipboard Output", () => {
  const result = formatClipboardAnswer({
    suggested_answer: "B",
    answer_text: "Database",
    original_label: null,
    source_position: 2,
    explanation: "A computer software system used to securely store and query data."
  });

  assert.equal(
    result,
    "Correct Answer: Database (Item #2)\n\nExplanation:\nA computer software system used to securely store and query data."
  );
  // Guarantee no invented "Option " string in the header
  const headerLine = result.split("\n")[0];
  assert.equal(headerLine, "Correct Answer: Database (Item #2)");
  assert.ok(!headerLine.includes("Option"));
});

test("Option Identity — No Invented Visible Labels on UI Badge", () => {
  const unletteredBadge = formatAnswerBadge({
    suggested_answer: "A",
    answer_text: "Database",
    original_label: null,
    source_position: 1,
    explanation: "..."
  });
  assert.equal(unletteredBadge, "Suggested Answer: Database (Item #1)");
  assert.ok(!unletteredBadge.includes("Option"));

  const letteredBadge = formatAnswerBadge({
    suggested_answer: "C",
    answer_text: "Cache",
    original_label: "C",
    source_position: 3,
    explanation: "..."
  });
  assert.equal(letteredBadge, "Suggested Answer: Option C");
});

test("Option Identity — Manual Option Editing Preserves Identity & Position", () => {
  const initial = [
    { id: "opt_1", text: "Cache", original_label: null, internal_label: "A", source_order: 1, is_user_edited: false },
    { id: "opt_2", text: "Datbase", original_label: null, internal_label: "B", source_order: 2, is_user_edited: false },
  ];

  const updated = handleOptionTextChange(initial, "B", "Database");

  assert.equal(updated.length, 2);
  assert.equal(updated[1].id, "opt_2");
  assert.equal(updated[1].text, "Database");
  assert.equal(updated[1].original_label, null);
  assert.equal(updated[1].internal_label, "B");
  assert.equal(updated[1].source_order, 2);
  assert.equal(updated[1].is_user_edited, true);

  // Unedited option remains unchanged
  assert.equal(updated[0].is_user_edited, false);
});

test("Option Identity — Adding and Removing Options with Source-Order Updates", () => {
  const initial = [
    { id: "opt_1", text: "Alpha", original_label: null, internal_label: "A", source_order: 1 },
    { id: "opt_2", text: "Beta", original_label: null, internal_label: "B", source_order: 2 },
    { id: "opt_3", text: "Gamma", original_label: null, internal_label: "C", source_order: 3 },
  ];

  // 1. Add new option
  const { nextKey, updated: withAdded } = addOptionItem(initial, ["A", "B", "C"]);
  assert.equal(nextKey, "D");
  assert.equal(withAdded.length, 4);
  assert.equal(withAdded[3].internal_label, "D");
  assert.equal(withAdded[3].source_order, 4);
  assert.equal(withAdded[3].is_user_edited, true);

  // 2. Remove intermediate option "B"
  const afterRemoval = removeOptionItem(withAdded, "B");
  assert.equal(afterRemoval.length, 3);
  assert.equal(afterRemoval[0].internal_label, "A");
  assert.equal(afterRemoval[0].source_order, 1);
  assert.equal(afterRemoval[1].internal_label, "C");
  assert.equal(afterRemoval[1].source_order, 2); // Re-indexed from 3 to 2
  assert.equal(afterRemoval[2].internal_label, "D");
  assert.equal(afterRemoval[2].source_order, 3); // Re-indexed from 4 to 3
});

test("Option Identity — Correct Answer Display After Option Shuffling", () => {
  // Coursera randomizes option orders between attempts
  const attempt1 = [
    { id: "opt_1", text: "Database", original_label: null, internal_label: "A", source_order: 1 },
    { id: "opt_2", text: "Data ecosystem", original_label: null, internal_label: "B", source_order: 2 },
    { id: "opt_3", text: "Cache", original_label: null, internal_label: "C", source_order: 3 },
  ];

  const attempt2 = [
    { id: "opt_1", text: "Data ecosystem", original_label: null, internal_label: "A", source_order: 1 },
    { id: "opt_2", text: "Cache", original_label: null, internal_label: "B", source_order: 2 },
    { id: "opt_3", text: "Database", original_label: null, internal_label: "C", source_order: 3 },
  ];

  const resolved1 = resolveAnswerOnShuffle(attempt1, "Database");
  assert.notEqual(resolved1, null);
  assert.equal(resolved1.source_position, 1);
  assert.equal(resolved1.original_label, null);

  const display1 = formatClipboardAnswer({
    suggested_answer: "A",
    answer_text: resolved1.answer_text,
    original_label: resolved1.original_label,
    source_position: resolved1.source_position,
    explanation: "Standard definition."
  });
  assert.ok(display1.startsWith("Correct Answer: Database (Item #1)"));

  const resolved2 = resolveAnswerOnShuffle(attempt2, "Database");
  assert.notEqual(resolved2, null);
  assert.equal(resolved2.source_position, 3);
  assert.equal(resolved2.original_label, null);

  const display2 = formatClipboardAnswer({
    suggested_answer: "C",
    answer_text: resolved2.answer_text,
    original_label: resolved2.original_label,
    source_position: resolved2.source_position,
    explanation: "Standard definition."
  });
  assert.ok(display2.startsWith("Correct Answer: Database (Item #3)"));
  assert.ok(!display2.includes("Option A"));
});

