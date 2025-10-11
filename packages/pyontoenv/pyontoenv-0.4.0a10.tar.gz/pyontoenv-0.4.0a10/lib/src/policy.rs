//! Defines traits and implementations for ontology resolution policies.
//! Policies determine which ontology version to use when multiple ontologies share the same name.

// define a trait for a resolution policy. Given an ontology name and a set of possible ontologies,
// the policy should return the ontology that should be used.

use crate::consts::ONTOLOGY_VERSION_IRIS;
use crate::ontology::Ontology;
use oxigraph::model::NamedNode;
use serde::{Deserialize, Serialize};
use std::fmt::Debug;

pub trait ResolutionPolicy: Debug + Send + Sync {
    fn resolve<'a>(&self, name: &str, ontologies: &'a [&'a Ontology]) -> Option<&'a Ontology>;
    fn policy_name(&self) -> &'static str;
}

pub fn policy_from_name(name: &str) -> Option<Box<dyn ResolutionPolicy>> {
    match name {
        "default" => Some(Box::new(DefaultPolicy)),
        "latest" => Some(Box::new(LatestPolicy)),
        "version" => Some(Box::new(VersionPolicy)),
        _ => None,
    }
}

pub fn policy_to_name(policy: &dyn ResolutionPolicy) -> &'static str {
    policy.policy_name()
}

// custom derives for the resolution policies
pub fn policy_serialize<S>(
    policy: &Box<dyn ResolutionPolicy>,
    serializer: S,
) -> Result<S::Ok, S::Error>
where
    S: serde::Serializer,
{
    serializer.serialize_str(policy.policy_name())
}

pub fn policy_deserialize<'de, D>(deserializer: D) -> Result<Box<dyn ResolutionPolicy>, D::Error>
where
    D: serde::Deserializer<'de>,
{
    let policy_name = String::deserialize(deserializer)?;
    policy_from_name(&policy_name)
        .ok_or_else(|| serde::de::Error::custom(format!("Unknown policy name: {policy_name}")))
}

/// A resolution policy that always returns the first ontology with the given name.
#[derive(Debug, Serialize, Deserialize, Default)]
pub struct DefaultPolicy;

impl ResolutionPolicy for DefaultPolicy {
    fn resolve<'a>(&self, name: &str, ontologies: &'a [&'a Ontology]) -> Option<&'a Ontology> {
        ontologies.iter().find(|o| o.name() == name).copied()
    }

    fn policy_name(&self) -> &'static str {
        "default"
    }
}

/// A resolution policy that returns the ontology which was most recently updated in the
/// environment
#[derive(Debug, Serialize, Deserialize, Default)]
pub struct LatestPolicy;

impl ResolutionPolicy for LatestPolicy {
    fn resolve<'a>(&self, name: &str, ontologies: &'a [&'a Ontology]) -> Option<&'a Ontology> {
        ontologies
            .iter()
            .filter(|o| o.name() == name)
            .max_by_key(|o| o.last_updated)
            .copied()
    }

    fn policy_name(&self) -> &'static str {
        "latest"
    }
}

/// A resolution policy that returns the ontology which has the most recent version, using
/// the various versioning information in the ontology.
#[derive(Debug, Serialize, Deserialize, Default)]
pub struct VersionPolicy;

impl ResolutionPolicy for VersionPolicy {
    fn resolve<'a>(&self, name: &str, ontologies: &'a [&'a Ontology]) -> Option<&'a Ontology> {
        ontologies
            .iter()
            .filter(|o| o.name() == name)
            .max_by_key(|o| {
                ONTOLOGY_VERSION_IRIS
                    .iter()
                    .map(|iri| {
                        let iri_nn: NamedNode = (*iri).into();
                        o.version_properties()
                            .get(&iri_nn)
                            .cloned()
                            .unwrap_or_else(|| "0".to_string())
                    })
                    .collect::<Vec<String>>()
            })
            .copied()
    }

    fn policy_name(&self) -> &'static str {
        "version"
    }
}
