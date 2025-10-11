//! # laddu-amplitudes
//!
//! This is an internal crate used by `laddu`.
#![warn(clippy::perf, clippy::style, missing_docs)]
#![allow(clippy::excessive_precision)]

/// The Breit-Wigner amplitude.
pub mod breit_wigner;
pub use breit_wigner::BreitWigner;

/// Common amplitudes (like a scalar value which just contains a single free parameter).
pub mod common;
pub use common::{ComplexScalar, PolarComplexScalar, Scalar};

/// Amplitudes related to the K-Matrix formalism.
pub mod kmatrix;

/// Piecewise functions as amplitudes.
pub mod piecewise;
pub use piecewise::{PiecewiseComplexScalar, PiecewisePolarComplexScalar, PiecewiseScalar};

/// A spherical harmonic amplitude.
pub mod ylm;
pub use ylm::Ylm;

/// A polarized spherical harmonic amplitude.
pub mod zlm;
pub use zlm::Zlm;

/// A phase space factor for `$a+b\to c+d$` with `$c\to 1+2$`.
pub mod phase_space;
pub use phase_space::PhaseSpaceFactor;
