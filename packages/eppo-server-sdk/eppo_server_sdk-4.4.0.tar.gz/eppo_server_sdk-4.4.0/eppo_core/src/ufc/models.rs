use std::collections::HashMap;

use derive_more::From;
use regex::Regex;
use semver::Version;
use serde::{Deserialize, Serialize};

use crate::{Error, EvaluationError, Str};

use super::AssignmentValue;

#[allow(missing_docs)]
pub type Timestamp = crate::timestamp::Timestamp;

/// Universal Flag Configuration. This the response format from the UFC endpoint.
#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(rename_all = "camelCase")]
pub(crate) struct UniversalFlagConfigWire {
    /// When configuration was last updated.
    pub created_at: Timestamp,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub format: Option<ConfigurationFormat>,
    /// Environment this configuration belongs to.
    pub environment: Environment,
    /// Flags configuration.
    ///
    /// Value is wrapped in `TryParse` so that if we fail to parse one flag (e.g., new server
    /// format), we can still serve other flags.
    pub flags: HashMap<Str, TryParse<FlagWire>>,
    /// `bandits` field connects string feature flags to bandits. Actual bandits configuration is
    /// served separately.
    #[serde(default)]
    pub bandits: HashMap<Str, Vec<BanditVariationWire>>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum ConfigurationFormat {
    Client,
    Server,
    Precomputed,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Environment {
    /// Name of the environment.
    pub name: Str,
}

/// `TryParse` allows the subfield to fail parsing without failing the parsing of the whole
/// structure.
///
/// This can be helpful to isolate errors in a subtree. e.g., if configuration for one flag parses,
/// the rest of the flags are still usable.
#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(untagged)]
pub enum TryParse<T> {
    /// Successfully parsed.
    Parsed(T),
    /// Parsing failed.
    ParseFailed(serde_json::Value),
}
impl<T> From<T> for TryParse<T> {
    fn from(value: T) -> TryParse<T> {
        TryParse::Parsed(value)
    }
}
impl<T> From<TryParse<T>> for Option<T> {
    fn from(value: TryParse<T>) -> Self {
        match value {
            TryParse::Parsed(v) => Some(v),
            TryParse::ParseFailed(_) => None,
        }
    }
}
impl<'a, T> From<&'a TryParse<T>> for Option<&'a T> {
    fn from(value: &TryParse<T>) -> Option<&T> {
        match value {
            TryParse::Parsed(v) => Some(v),
            TryParse::ParseFailed(_) => None,
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(rename_all = "camelCase")]
#[allow(missing_docs)]
pub(crate) struct FlagWire {
    pub key: Str,
    pub enabled: bool,
    pub variation_type: VariationType,
    pub variations: HashMap<String, VariationWire>,
    pub allocations: Vec<AllocationWire>,
    pub total_shards: u32,
}

/// Type of the variation.
#[derive(Debug, Serialize, Deserialize, Clone, Copy, PartialEq, Eq)]
#[cfg_attr(feature = "rustler", derive(rustler::NifUnitEnum))]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
#[allow(missing_docs)]
pub enum VariationType {
    String,
    Integer,
    Numeric,
    Boolean,
    Json,
}

/// Subset of [`serde_json::Value`].
///
/// Unlike [`AssignmentValue`], `Value` is untagged, so we don't know the exact type until we
/// combine it with [`VariationType`] from the flag level.
#[derive(Debug, Serialize, Deserialize, PartialEq, From, Clone)]
#[serde(untagged)]
pub(crate) enum ValueWire {
    /// Boolean maps to [`AssignmentValue::Boolean`].
    Boolean(bool),
    /// Number maps to either [`AssignmentValue::Integer`] or [`AssignmentValue::Numeric`].
    Number(f64),
    /// String maps to either [`AssignmentValue::String`] or [`AssignmentValue::Json`].
    String(Str),
}

impl ValueWire {
    /// Try to convert `Value` to [`AssignmentValue`] under the given [`VariationType`].
    pub(crate) fn into_assignment_value(self, ty: VariationType) -> Option<AssignmentValue> {
        Some(match ty {
            VariationType::String => AssignmentValue::String(self.into_string()?),
            VariationType::Integer => AssignmentValue::Integer(self.as_integer()?),
            VariationType::Numeric => AssignmentValue::Numeric(self.as_number()?),
            VariationType::Boolean => AssignmentValue::Boolean(self.as_boolean()?),
            VariationType::Json => {
                let raw = self.into_string()?;
                let parsed = serde_json::from_str(&raw).ok()?;
                AssignmentValue::Json { raw, parsed }
            }
        })
    }

    fn as_boolean(&self) -> Option<bool> {
        match self {
            Self::Boolean(value) => Some(*value),
            _ => None,
        }
    }

    fn as_number(&self) -> Option<f64> {
        match self {
            Self::Number(value) => Some(*value),
            _ => None,
        }
    }

    fn as_integer(&self) -> Option<i64> {
        let f = self.as_number()?;
        let i = f as i64;
        if i as f64 == f {
            Some(i)
        } else {
            None
        }
    }

    fn into_string(self) -> Option<Str> {
        match self {
            Self::String(value) => Some(value),
            _ => None,
        }
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(rename_all = "camelCase")]
#[allow(missing_docs)]
pub(crate) struct VariationWire {
    pub key: Str,
    pub value: ValueWire,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(rename_all = "camelCase")]
#[allow(missing_docs)]
pub(crate) struct AllocationWire {
    pub key: Str,
    #[serde(default)]
    pub rules: Box<[RuleWire]>,
    #[serde(default)]
    pub start_at: Option<Timestamp>,
    #[serde(default)]
    pub end_at: Option<Timestamp>,
    pub splits: Vec<SplitWire>,
    #[serde(default = "default_do_log")]
    pub do_log: bool,
}

fn default_do_log() -> bool {
    true
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
#[allow(missing_docs)]
pub(crate) struct RuleWire {
    pub conditions: Vec<TryParse<Condition>>,
}

/// `Condition` is a check that given user `attribute` matches the condition `value` under the given
/// `operator`.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(try_from = "ConditionWire", into = "ConditionWire")]
pub(crate) struct Condition {
    pub attribute: Box<str>,
    pub check: ConditionCheck,
}

#[derive(Debug, Clone)]
pub(crate) enum ConditionCheck {
    Comparison {
        operator: ComparisonOperator,
        comparand: Comparand,
    },
    Regex {
        expected_match: bool,
        // As regex is supplied by user, we allow regex parse failure to not fail parsing and
        // evaluation. Invalid regexes are simply ignored.
        regex: Regex,
    },
    Membership {
        expected_membership: bool,
        values: Box<[Box<str>]>,
    },
    Null {
        expected_null: bool,
    },
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub(crate) enum ComparisonOperator {
    Gte,
    Gt,
    Lte,
    Lt,
}

impl From<ComparisonOperator> for ConditionOperator {
    fn from(value: ComparisonOperator) -> ConditionOperator {
        match value {
            ComparisonOperator::Gte => ConditionOperator::Gte,
            ComparisonOperator::Gt => ConditionOperator::Gt,
            ComparisonOperator::Lte => ConditionOperator::Lte,
            ComparisonOperator::Lt => ConditionOperator::Lt,
        }
    }
}

#[derive(Debug, Clone, PartialEq, PartialOrd, From)]
pub(crate) enum Comparand {
    Version(Version),
    Number(f64),
}

impl From<Comparand> for ConditionValue {
    fn from(value: Comparand) -> ConditionValue {
        let s = match value {
            Comparand::Version(v) => v.to_string(),
            Comparand::Number(n) => n.to_string(),
        };
        ConditionValue::Single(ValueWire::String(s.into()))
    }
}

/// Wire (JSON) format for the `Condition`.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
#[allow(missing_docs)]
pub(crate) struct ConditionWire {
    pub attribute: Box<str>,
    pub operator: ConditionOperator,
    pub value: ConditionValue,
}

impl From<Condition> for ConditionWire {
    fn from(condition: Condition) -> Self {
        let (operator, value) = match condition.check {
            ConditionCheck::Comparison {
                operator,
                comparand,
            } => (operator.into(), comparand.into()),
            ConditionCheck::Regex {
                expected_match,
                regex,
            } => (
                if expected_match {
                    ConditionOperator::Matches
                } else {
                    ConditionOperator::NotMatches
                },
                ConditionValue::Single(ValueWire::String(Str::from(regex.as_str()))),
            ),
            ConditionCheck::Membership {
                expected_membership,
                values,
            } => (
                if expected_membership {
                    ConditionOperator::OneOf
                } else {
                    ConditionOperator::NotOneOf
                },
                ConditionValue::Multiple(values),
            ),
            ConditionCheck::Null { expected_null } => {
                (ConditionOperator::IsNull, expected_null.into())
            }
        };
        ConditionWire {
            attribute: condition.attribute,
            operator,
            value,
        }
    }
}

impl From<ConditionWire> for Option<Condition> {
    fn from(value: ConditionWire) -> Self {
        Condition::try_from(value).ok()
    }
}

impl TryFrom<ConditionWire> for Condition {
    type Error = Error;

    fn try_from(condition: ConditionWire) -> Result<Self, Self::Error> {
        let attribute = condition.attribute;
        let check = match condition.operator {
            ConditionOperator::Matches | ConditionOperator::NotMatches => {
                let expected_match = condition.operator == ConditionOperator::Matches;

                let regex_string = match condition.value {
                    ConditionValue::Single(ValueWire::String(s)) => s,
                    _ => {
                        log::warn!(
                            "failed to parse condition: {:?} condition with non-string condition value",
                            condition.operator
                        );
                        return Err(Error::EvaluationError(
                            EvaluationError::UnexpectedConfigurationParseError,
                        ));
                    }
                };
                let regex = match Regex::new(&regex_string) {
                    Ok(regex) => regex,
                    Err(err) => {
                        log::warn!("failed to parse condition: failed to compile regex {regex_string:?}: {err:?}");
                        return Err(Error::EvaluationError(
                            EvaluationError::UnexpectedConfigurationParseError,
                        ));
                    }
                };

                ConditionCheck::Regex {
                    expected_match,
                    regex,
                }
            }
            ConditionOperator::Gte
            | ConditionOperator::Gt
            | ConditionOperator::Lte
            | ConditionOperator::Lt => {
                let operator = match condition.operator {
                    ConditionOperator::Gte => ComparisonOperator::Gte,
                    ConditionOperator::Gt => ComparisonOperator::Gt,
                    ConditionOperator::Lte => ComparisonOperator::Lte,
                    ConditionOperator::Lt => ComparisonOperator::Lt,
                    _ => unreachable!(),
                };

                let condition_version = match &condition.value {
                    ConditionValue::Single(ValueWire::String(s)) => Version::parse(s).ok(),
                    _ => None,
                };

                if let Some(condition_version) = condition_version {
                    ConditionCheck::Comparison {
                        operator,
                        comparand: Comparand::Version(condition_version),
                    }
                } else {
                    // numeric comparison
                    let condition_value = match &condition.value {
                        ConditionValue::Single(ValueWire::Number(n)) => Some(*n),
                        ConditionValue::Single(ValueWire::String(s)) => s.parse().ok(),
                        _ => None,
                    };
                    let Some(condition_value) = condition_value else {
                        log::warn!("failed to parse condition: comparision value is neither regex, nor number: {:?}", condition.value);
                        return Err(Error::EvaluationError(
                            EvaluationError::UnexpectedConfigurationParseError,
                        ));
                    };
                    ConditionCheck::Comparison {
                        operator,
                        comparand: Comparand::Number(condition_value),
                    }
                }
            }
            ConditionOperator::OneOf | ConditionOperator::NotOneOf => {
                let expected_membership = condition.operator == ConditionOperator::OneOf;
                let values = match condition.value {
                    ConditionValue::Multiple(v) => v,
                    _ => {
                        log::warn!("failed to parse condition: membership condition with non-array value: {:?}", condition.value);
                        return Err(Error::EvaluationError(
                            EvaluationError::UnexpectedConfigurationParseError,
                        ));
                    }
                };
                ConditionCheck::Membership {
                    expected_membership,
                    values,
                }
            }
            ConditionOperator::IsNull => {
                let ConditionValue::Single(ValueWire::Boolean(expected_null)) = condition.value
                else {
                    log::warn!("failed to parse condition: IS_NULL condition with non-boolean condition value");
                    return Err(Error::EvaluationError(
                        EvaluationError::UnexpectedConfigurationParseError,
                    ));
                };
                ConditionCheck::Null { expected_null }
            }
        };
        Ok(Condition { attribute, check })
    }
}

/// Possible condition types.
#[derive(Debug, Serialize, Deserialize, PartialEq, Eq, Clone, Copy)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub(crate) enum ConditionOperator {
    /// Matches regex. Condition value must be a regex string.
    Matches,
    /// Regex does not match. Condition value must be a regex string.
    NotMatches,
    /// Greater than or equal. Attribute and condition value must either be numbers or semver
    /// string.
    Gte,
    /// Greater than. Attribute and condition value must either be numbers or semver string.
    Gt,
    /// Less than or equal. Attribute and condition value must either be numbers or semver string.
    Lte,
    /// Less than. Attribute and condition value must either be numbers or semver string.
    Lt,
    /// One of values. Condition value must be a list of strings. Match is case-sensitive.
    OneOf,
    /// Not one of values. Condition value must be a list of strings. Match is case-sensitive.
    ///
    /// Null/absent attributes fail this condition automatically. (i.e., `null NOT_ONE_OF ["hello"]`
    /// is `false`)
    NotOneOf,
    /// Null check.
    ///
    /// Condition value must be a boolean. If it's `true`, this is a null check. If it's `false`,
    /// this is a not null check.
    IsNull,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(untagged)]
#[allow(missing_docs)]
pub(crate) enum ConditionValue {
    Single(ValueWire),
    // Only string arrays are currently supported.
    Multiple(Box<[Box<str>]>),
}

impl<T: Into<ValueWire>> From<T> for ConditionValue {
    fn from(value: T) -> Self {
        Self::Single(value.into())
    }
}
impl From<Vec<String>> for ConditionValue {
    fn from(value: Vec<String>) -> Self {
        Self::Multiple(value.into_iter().map(|it| it.into()).collect())
    }
}

#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(rename_all = "camelCase")]
#[allow(missing_docs)]
pub(crate) struct SplitWire {
    pub shards: Vec<ShardWire>,
    pub variation_key: Str,
    #[serde(default)]
    pub extra_logging: HashMap<String, String>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
#[allow(missing_docs)]
pub(crate) struct ShardWire {
    pub salt: String,
    pub ranges: Box<[ShardRange]>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
#[allow(missing_docs)]
pub struct ShardRange {
    pub start: u32,
    pub end: u32,
}
impl ShardRange {
    pub(crate) fn contains(&self, v: u32) -> bool {
        self.start <= v && v < self.end
    }
}

/// `BanditVariation` associates a variation in feature flag with a bandit.
#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(rename_all = "camelCase")]
pub(crate) struct BanditVariationWire {
    pub key: Str,
    /// Key of the flag.
    pub flag_key: Str,
    /// Today it's the same as `variation_value`.
    pub variation_key: Str,
    /// String variation value.
    pub variation_value: Str,
}

#[cfg(test)]
mod tests {
    use std::{fs::File, io::BufReader};

    use super::{TryParse, UniversalFlagConfigWire};

    #[test]
    fn parse_flags_v1() {
        let f = File::open("../sdk-test-data/ufc/flags-v1.json")
            .expect("Failed to open ../sdk-test-data/ufc/flags-v1.json");
        let _ufc: UniversalFlagConfigWire = serde_json::from_reader(BufReader::new(f)).unwrap();
    }

    #[test]
    fn parse_partially_if_unexpected() {
        let ufc: UniversalFlagConfigWire = serde_json::from_str(
            &r#"
              {
                "createdAt": "2024-07-18T00:00:00Z",
                "format": "SERVER",
                "environment": {"name": "test"},
                "flags": {
                  "success": {
                    "key": "success",
                    "enabled": true,
                    "variationType": "BOOLEAN",
                    "variations": {},
                    "allocations": [],
                    "totalShards": 10000
                  },
                  "fail_parsing": {
                    "key": "fail_parsing",
                    "enabled": true,
                    "variationType": "NEW_TYPE",
                    "variations": {},
                    "allocations": [],
                    "totalShards": 10000
                  }
                }
              }
            "#,
        )
        .unwrap();
        assert!(
            matches!(ufc.flags.get("success").unwrap(), TryParse::Parsed(_)),
            "{:?} should match TryParse::Parsed(_)",
            ufc.flags.get("success").unwrap()
        );
        assert!(
            matches!(
                ufc.flags.get("fail_parsing").unwrap(),
                TryParse::ParseFailed(_)
            ),
            "{:?} should match TryParse::ParseFailed(_)",
            ufc.flags.get("fail_parsing").unwrap()
        );
    }
}
