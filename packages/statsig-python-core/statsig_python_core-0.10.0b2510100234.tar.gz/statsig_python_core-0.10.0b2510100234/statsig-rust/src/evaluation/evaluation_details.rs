use crate::evaluation::evaluator_result::EvaluatorResult;
use crate::spec_store::SpecStoreData;
use crate::SpecsSource;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone, PartialEq, Debug)]
pub struct EvaluationDetails {
    pub reason: String,
    pub lcut: Option<u64>,
    pub received_at: Option<u64>,
}

impl EvaluationDetails {
    pub fn unrecognized(spec_store_data: &SpecStoreData) -> Self {
        Self::create_from_data(spec_store_data, "Unrecognized", &EvaluatorResult::default())
    }

    pub fn recognized_without_eval_result(spec_store_data: &SpecStoreData) -> Self {
        Self::create_from_data(spec_store_data, "Recognized", &EvaluatorResult::default())
    }

    pub fn recognized(spec_store_data: &SpecStoreData, eval_result: &EvaluatorResult) -> Self {
        Self::create_from_data(spec_store_data, "Recognized", eval_result)
    }

    pub fn recognized_but_overridden(
        spec_store_data: &SpecStoreData,
        override_reason: &str,
    ) -> Self {
        Self {
            reason: format!("{override_reason}:Recognized"),
            lcut: Some(spec_store_data.values.time),
            received_at: spec_store_data.time_received_at,
        }
    }

    #[must_use]
    pub fn unrecognized_no_data() -> Self {
        Self {
            reason: SpecsSource::NoValues.to_string(),
            lcut: None,
            received_at: None,
        }
    }

    #[must_use]
    pub fn error(sub_reason: &str) -> Self {
        Self {
            reason: format!("Error:{sub_reason}"),
            lcut: None,
            received_at: None,
        }
    }

    fn create_from_data(
        data: &SpecStoreData,
        sub_reason: &str,
        eval_result: &EvaluatorResult,
    ) -> Self {
        if data.source == SpecsSource::Uninitialized || data.source == SpecsSource::NoValues {
            return Self {
                reason: data.source.to_string(),
                lcut: None,
                received_at: None,
            };
        }

        if eval_result.unsupported {
            return Self {
                reason: format!("{}:Unsupported", data.source),
                lcut: Some(data.values.time),
                received_at: data.time_received_at,
            };
        }

        Self {
            reason: format!("{}:{}", data.source, sub_reason),
            lcut: Some(data.values.time),
            received_at: data.time_received_at,
        }
    }
}
