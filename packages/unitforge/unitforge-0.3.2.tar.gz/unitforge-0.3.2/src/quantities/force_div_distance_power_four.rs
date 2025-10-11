use crate::impl_macros::macros::*;
use crate::prelude::*;
use ndarray::{Array1, Array2, ArrayView1, ArrayView2};
use num_traits::identities::Zero;
use num_traits::FromPrimitive;
#[cfg(feature = "pyo3")]
use pyo3::pyclass;
#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};
use std::cmp::Ordering;
use std::fmt;
use std::ops::{Add, AddAssign, Div, DivAssign, Mul, MulAssign, Neg, Sub, SubAssign};
#[cfg(feature = "strum")]
use strum_macros::EnumIter;

#[cfg_attr(feature = "strum", derive(EnumIter))]
#[cfg_attr(feature = "serde", derive(Serialize, Deserialize))]
#[derive(Copy, Clone, PartialEq, Debug)]
#[cfg_attr(feature = "pyo3", pyclass(eq, eq_int))]
pub enum ForcePerDistancePowerFourUnit {
    N_mmhc,
    N_mhc,
}

impl PhysicsUnit for ForcePerDistancePowerFourUnit {
    fn name(&self) -> &str {
        match &self {
            ForcePerDistancePowerFourUnit::N_mmhc => "N/mm⁴",
            ForcePerDistancePowerFourUnit::N_mhc => "N/m⁴",
        }
    }

    fn base_per_x(&self) -> (f64, i32) {
        match self {
            ForcePerDistancePowerFourUnit::N_mmhc => (1., 12),
            ForcePerDistancePowerFourUnit::N_mhc => (1., 0),
        }
    }
}

impl_quantity!(
    ForcePerDistancePowerFour,
    ForcePerDistancePowerFourUnit,
    [ForcePerDistancePowerFourUnit::N_mmhc]
);
impl_div_with_self_to_f64!(ForcePerDistancePowerFour);
