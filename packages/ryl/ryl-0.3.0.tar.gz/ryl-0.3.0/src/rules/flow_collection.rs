use std::ops::Range;

use saphyr_parser::{Event, Parser, Span, SpannedEventReceiver};

use crate::config::YamlLintConfig;
use crate::rules::span_utils::ranges_to_char_indices;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Forbid {
    None,
    All,
    NonEmpty,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Config {
    forbid: Forbid,
    min_spaces_inside: i64,
    max_spaces_inside: i64,
    min_spaces_inside_empty: i64,
    max_spaces_inside_empty: i64,
}

impl Config {
    const DEFAULT_MIN_SPACES_INSIDE: i64 = 0;
    const DEFAULT_MAX_SPACES_INSIDE: i64 = 0;
    const DEFAULT_MIN_SPACES_INSIDE_EMPTY: i64 = -1;
    const DEFAULT_MAX_SPACES_INSIDE_EMPTY: i64 = -1;

    #[must_use]
    pub fn resolve_for(cfg: &YamlLintConfig, rule_id: &str) -> Self {
        let forbid = cfg
            .rule_option(rule_id, "forbid")
            .map_or(Forbid::None, |node| match (node.as_bool(), node.as_str()) {
                (Some(true), _) => Forbid::All,
                (None, Some("non-empty")) => Forbid::NonEmpty,
                _ => Forbid::None,
            });

        let min_spaces_inside = cfg
            .rule_option(rule_id, "min-spaces-inside")
            .and_then(saphyr::YamlOwned::as_integer)
            .unwrap_or(Self::DEFAULT_MIN_SPACES_INSIDE);
        let max_spaces_inside = cfg
            .rule_option(rule_id, "max-spaces-inside")
            .and_then(saphyr::YamlOwned::as_integer)
            .unwrap_or(Self::DEFAULT_MAX_SPACES_INSIDE);
        let min_spaces_inside_empty = cfg
            .rule_option(rule_id, "min-spaces-inside-empty")
            .and_then(saphyr::YamlOwned::as_integer)
            .unwrap_or(Self::DEFAULT_MIN_SPACES_INSIDE_EMPTY);
        let max_spaces_inside_empty = cfg
            .rule_option(rule_id, "max-spaces-inside-empty")
            .and_then(saphyr::YamlOwned::as_integer)
            .unwrap_or(Self::DEFAULT_MAX_SPACES_INSIDE_EMPTY);

        Self {
            forbid,
            min_spaces_inside,
            max_spaces_inside,
            min_spaces_inside_empty,
            max_spaces_inside_empty,
        }
    }

    #[must_use]
    pub const fn new_for_tests(
        forbid: Forbid,
        min_spaces_inside: i64,
        max_spaces_inside: i64,
        min_spaces_inside_empty: i64,
        max_spaces_inside_empty: i64,
    ) -> Self {
        Self {
            forbid,
            min_spaces_inside,
            max_spaces_inside,
            min_spaces_inside_empty,
            max_spaces_inside_empty,
        }
    }

    #[must_use]
    pub const fn effective_min_empty(&self) -> i64 {
        if self.min_spaces_inside_empty >= 0 {
            self.min_spaces_inside_empty
        } else {
            self.min_spaces_inside
        }
    }

    #[must_use]
    pub const fn effective_max_empty(&self) -> i64 {
        if self.max_spaces_inside_empty >= 0 {
            self.max_spaces_inside_empty
        } else {
            self.max_spaces_inside
        }
    }

    #[must_use]
    pub const fn forbid(&self) -> Forbid {
        self.forbid
    }

    #[must_use]
    pub const fn min_spaces_inside(&self) -> i64 {
        self.min_spaces_inside
    }

    #[must_use]
    pub const fn max_spaces_inside(&self) -> i64 {
        self.max_spaces_inside
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Violation {
    pub line: usize,
    pub column: usize,
    pub message: String,
}

pub struct FlowCollectionDescriptor {
    pub open: char,
    pub close: char,
    pub forbid_message: &'static str,
    pub min_message: &'static str,
    pub max_message: &'static str,
    pub min_empty_message: &'static str,
    pub max_empty_message: &'static str,
}

struct ScalarRangeCollector {
    ranges: Vec<(usize, usize)>,
}

impl ScalarRangeCollector {
    const fn new() -> Self {
        Self { ranges: Vec::new() }
    }

    fn into_sorted(mut self) -> Vec<Range<usize>> {
        self.ranges.sort_by(|a, b| a.0.cmp(&b.0));
        self.ranges
            .into_iter()
            .filter_map(|(start, end)| (start <= end).then_some(start..end))
            .collect()
    }
}

impl SpannedEventReceiver<'_> for ScalarRangeCollector {
    fn on_event(&mut self, ev: Event<'_>, span: Span) {
        if matches!(ev, Event::Scalar(..)) {
            let start = span.start.index();
            let end = span.end.index();
            self.ranges.push((start, end));
        }
    }
}

#[derive(Debug, Clone, Copy)]
struct CollectionState {
    is_empty: bool,
}

#[derive(Debug, PartialEq, Eq)]
enum AfterResult {
    SameLine { spaces: usize, next_idx: usize },
    Ignored,
}

#[derive(Clone, Copy)]
struct SpacingMessages<'a> {
    min: &'a str,
    max: &'a str,
}

#[must_use]
pub fn check(buffer: &str, cfg: &Config, desc: &FlowCollectionDescriptor) -> Vec<Violation> {
    if buffer.is_empty() {
        return Vec::new();
    }

    let mut parser = Parser::new_from_str(buffer);
    let mut collector = ScalarRangeCollector::new();
    let _ = parser.load(&mut collector, true);
    let scalar_ranges = collector.into_sorted();

    let chars: Vec<(usize, char)> = buffer.char_indices().collect();
    let buffer_len = buffer.len();
    let scalar_ranges = ranges_to_char_indices(scalar_ranges, &chars, buffer_len);
    let line_starts = build_line_starts(buffer);

    let mut range_idx = 0usize;
    let mut idx = 0usize;
    let mut stack: Vec<CollectionState> = Vec::new();
    let mut violations = Vec::new();

    while idx < chars.len() {
        while range_idx < scalar_ranges.len() && scalar_ranges[range_idx].end <= idx {
            range_idx += 1;
        }

        if let Some(range) = scalar_ranges.get(range_idx)
            && idx >= range.start
            && idx < range.end
        {
            if idx == range.start
                && let Some(state) = stack.last_mut()
            {
                state.is_empty = false;
            }
            idx = range.end;
            continue;
        }

        let ch = chars[idx].1;
        if ch == desc.open {
            if let Some(state) = stack.last_mut() {
                state.is_empty = false;
            }
            handle_open(
                cfg,
                desc,
                &chars,
                idx,
                &line_starts,
                &mut stack,
                &mut violations,
            );
        } else if ch == desc.close {
            handle_close(
                cfg,
                desc,
                &chars,
                idx,
                &line_starts,
                &mut stack,
                &mut violations,
            );
        } else {
            match ch {
                '#' => {
                    idx = skip_comment(&chars, idx);
                    continue;
                }
                ',' | ' ' | '\t' | '\n' => {}
                '\r' => {
                    if idx + 1 < chars.len() && chars[idx + 1].1 == '\n' {
                        idx += 1;
                    }
                }
                _ => {
                    if let Some(state) = stack.last_mut() {
                        state.is_empty = false;
                    }
                }
            }
        }

        idx += 1;
    }

    violations
}

fn handle_open(
    cfg: &Config,
    desc: &FlowCollectionDescriptor,
    chars: &[(usize, char)],
    idx: usize,
    line_starts: &[usize],
    stack: &mut Vec<CollectionState>,
    violations: &mut Vec<Violation>,
) {
    let open_byte = chars[idx].0;
    let (line, column) = line_and_column(line_starts, open_byte);
    let next_significant = next_significant_index(chars, idx);

    let mut skip_open_check = false;
    match cfg.forbid() {
        Forbid::All => {
            violations.push(Violation {
                line,
                column: column + 1,
                message: desc.forbid_message.to_string(),
            });
            skip_open_check = true;
        }
        Forbid::NonEmpty => {
            let is_empty =
                matches!(next_significant.map(|j| chars[j].1), Some(close) if close == desc.close);
            if !is_empty {
                violations.push(Violation {
                    line,
                    column: column + 1,
                    message: desc.forbid_message.to_string(),
                });
                skip_open_check = true;
            }
        }
        Forbid::None => {}
    }

    let mut state = CollectionState {
        is_empty: matches!(next_significant.map(|j| chars[j].1), Some(close) if close == desc.close),
    };

    if !skip_open_check
        && let AfterResult::SameLine { spaces, next_idx } = compute_spaces_after_open(chars, idx)
    {
        let next_byte = chars[next_idx].0;
        let (line, next_column) = line_and_column(line_starts, next_byte);
        if state.is_empty && chars[next_idx].1 == desc.close {
            record_after_spacing(
                cfg.effective_min_empty(),
                cfg.effective_max_empty(),
                spaces,
                line,
                next_column,
                SpacingMessages {
                    min: desc.min_empty_message,
                    max: desc.max_empty_message,
                },
                violations,
            );
        } else {
            state.is_empty = false;
            record_after_spacing(
                cfg.min_spaces_inside(),
                cfg.max_spaces_inside(),
                spaces,
                line,
                next_column,
                SpacingMessages {
                    min: desc.min_message,
                    max: desc.max_message,
                },
                violations,
            );
        }
    }

    stack.push(state);
}

fn handle_close(
    cfg: &Config,
    desc: &FlowCollectionDescriptor,
    chars: &[(usize, char)],
    idx: usize,
    line_starts: &[usize],
    stack: &mut Vec<CollectionState>,
    violations: &mut Vec<Violation>,
) {
    let Some(state) = stack.pop() else {
        return;
    };

    if state.is_empty {
        return;
    }

    if let Some(spaces) = compute_spaces_before_close(chars, idx) {
        let spaces_i64 = i64::try_from(spaces).unwrap_or(i64::MAX);
        let close_byte = chars[idx].0;
        let (line, close_column) = line_and_column(line_starts, close_byte);
        if cfg.max_spaces_inside() >= 0 && spaces_i64 > cfg.max_spaces_inside() {
            let highlight = close_column.saturating_sub(1).max(1);
            violations.push(Violation {
                line,
                column: highlight,
                message: desc.max_message.to_string(),
            });
        }
        if cfg.min_spaces_inside() >= 0 && spaces_i64 < cfg.min_spaces_inside() {
            violations.push(Violation {
                line,
                column: close_column,
                message: desc.min_message.to_string(),
            });
        }
    }
}

fn record_after_spacing(
    min: i64,
    max: i64,
    spaces: usize,
    line: usize,
    next_column: usize,
    messages: SpacingMessages<'_>,
    violations: &mut Vec<Violation>,
) {
    let spaces_i64 = i64::try_from(spaces).unwrap_or(i64::MAX);
    if max >= 0 && spaces_i64 > max {
        let highlight = next_column.saturating_sub(1).max(1);
        violations.push(Violation {
            line,
            column: highlight,
            message: messages.max.to_string(),
        });
    }
    if min >= 0 && spaces_i64 < min {
        violations.push(Violation {
            line,
            column: next_column,
            message: messages.min.to_string(),
        });
    }
}

fn compute_spaces_after_open(chars: &[(usize, char)], open_idx: usize) -> AfterResult {
    let mut spaces = 0usize;
    let mut idx = open_idx + 1;
    while idx < chars.len() {
        match chars[idx].1 {
            ' ' | '\t' => {
                spaces += 1;
                idx += 1;
            }
            '\n' | '\r' | '#' => return AfterResult::Ignored,
            _ => {
                return AfterResult::SameLine {
                    spaces,
                    next_idx: idx,
                };
            }
        }
    }
    AfterResult::Ignored
}

fn compute_spaces_before_close(chars: &[(usize, char)], close_idx: usize) -> Option<usize> {
    let mut spaces = 0usize;
    let mut idx = close_idx;
    loop {
        idx = idx
            .checked_sub(1)
            .expect("closing delimiter should have a preceding opening delimiter");
        match chars[idx].1 {
            ' ' | '\t' => spaces += 1,
            '\n' | '\r' | '#' => return None,
            _ => return Some(spaces),
        }
    }
}

fn next_significant_index(chars: &[(usize, char)], open_idx: usize) -> Option<usize> {
    let mut idx = open_idx + 1;
    while idx < chars.len() {
        match chars[idx].1 {
            ' ' | '\t' | '\n' => idx += 1,
            '\r' => {
                if idx + 1 < chars.len() && chars[idx + 1].1 == '\n' {
                    idx += 2;
                } else {
                    idx += 1;
                }
            }
            '#' => {
                idx = skip_comment(chars, idx);
                if idx >= chars.len() {
                    continue;
                }
                idx += 1;
            }
            _ => return Some(idx),
        }
    }
    None
}

fn skip_comment(chars: &[(usize, char)], mut idx: usize) -> usize {
    idx += 1;
    while idx < chars.len() {
        let ch = chars[idx].1;
        if ch == '\n' {
            break;
        }
        if ch == '\r' {
            if idx + 1 < chars.len() && chars[idx + 1].1 == '\n' {
                idx += 1;
            }
            break;
        }
        idx += 1;
    }
    idx
}

fn build_line_starts(buffer: &str) -> Vec<usize> {
    let mut starts = Vec::new();
    starts.push(0);
    let bytes = buffer.as_bytes();
    let mut idx = 0usize;
    while idx < bytes.len() {
        match bytes[idx] {
            b'\n' => {
                starts.push(idx + 1);
                idx += 1;
            }
            b'\r' => {
                if idx + 1 < bytes.len() && bytes[idx + 1] == b'\n' {
                    starts.push(idx + 2);
                    idx += 2;
                } else {
                    starts.push(idx + 1);
                    idx += 1;
                }
            }
            _ => idx += 1,
        }
    }
    starts
}

fn line_and_column(line_starts: &[usize], byte_idx: usize) -> (usize, usize) {
    let mut left = 0usize;
    let mut right = line_starts.len();
    while left + 1 < right {
        let mid = usize::midpoint(left, right);
        if line_starts[mid] <= byte_idx {
            left = mid;
        } else {
            right = mid;
        }
    }
    let line_start = line_starts[left];
    (left + 1, byte_idx - line_start + 1)
}
