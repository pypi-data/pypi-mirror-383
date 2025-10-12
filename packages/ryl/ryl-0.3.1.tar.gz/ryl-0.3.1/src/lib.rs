#![forbid(unsafe_code)]
#![deny(clippy::all, clippy::pedantic, clippy::nursery, clippy::cargo)]

pub mod cli_support;
pub mod conf;
pub mod config;
pub mod decoder;
pub mod discover;
pub mod lint;
pub mod rules;

pub use discover::{gather_yaml_from_dir, is_yaml_path};
pub use lint::{LintProblem, Severity, lint_file};
