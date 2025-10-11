use dyn_clone::DynClone;
use serde::{Deserialize, Serialize};
use std::fmt::{Debug, Display};

#[cfg(feature = "rayon")]
use rayon::prelude::*;

#[cfg(feature = "mpi")]
use crate::mpi::LadduMPI;
use crate::{
    data::{Dataset, Event},
    utils::{
        enums::{Channel, Frame},
        vectors::Vec3,
    },
    Float, LadduError,
};

use auto_ops::impl_op_ex;

#[cfg(feature = "mpi")]
use mpi::{datatype::PartitionMut, topology::SimpleCommunicator, traits::*};

/// Standard methods for extracting some value out of an [`Event`].
#[typetag::serde(tag = "type")]
pub trait Variable: DynClone + Send + Sync + Debug + Display {
    /// This method takes an [`Event`] and extracts a single value (like the mass of a particle).
    fn value(&self, event: &Event) -> Float;

    /// This method distributes the [`Variable::value`] method over each [`Event`] in a
    /// [`Dataset`] (non-MPI version).
    ///
    /// # Notes
    ///
    /// This method is not intended to be called in analyses but rather in writing methods
    /// that have `mpi`-feature-gated versions. Most users should just call [`Variable::value_on`] instead.
    fn value_on_local(&self, dataset: &Dataset) -> Vec<Float> {
        #[cfg(feature = "rayon")]
        let local_values: Vec<Float> = dataset.events.par_iter().map(|e| self.value(e)).collect();
        #[cfg(not(feature = "rayon"))]
        let local_values: Vec<Float> = dataset.events.iter().map(|e| self.value(e)).collect();
        local_values
    }

    /// This method distributes the [`Variable::value`] method over each [`Event`] in a
    /// [`Dataset`] (MPI-compatible version).
    ///
    /// # Notes
    ///
    /// This method is not intended to be called in analyses but rather in writing methods
    /// that have `mpi`-feature-gated versions. Most users should just call [`Variable::value_on`] instead.
    #[cfg(feature = "mpi")]
    fn value_on_mpi(&self, dataset: &Dataset, world: &SimpleCommunicator) -> Vec<Float> {
        let local_weights = self.value_on_local(dataset);
        let n_events = dataset.n_events();
        let mut buffer: Vec<Float> = vec![0.0; n_events];
        let (counts, displs) = world.get_counts_displs(n_events);
        {
            let mut partitioned_buffer = PartitionMut::new(&mut buffer, counts, displs);
            world.all_gather_varcount_into(&local_weights, &mut partitioned_buffer);
        }
        buffer
    }

    /// This method distributes the [`Variable::value`] method over each [`Event`] in a
    /// [`Dataset`].
    fn value_on(&self, dataset: &Dataset) -> Vec<Float> {
        #[cfg(feature = "mpi")]
        {
            if let Some(world) = crate::mpi::get_world() {
                return self.value_on_mpi(dataset, &world);
            }
        }
        self.value_on_local(dataset)
    }

    /// Create an [`VariableExpression`] that evaluates to `self == val`
    fn eq(&self, val: Float) -> VariableExpression
    where
        Self: std::marker::Sized + 'static,
    {
        VariableExpression::Eq(dyn_clone::clone_box(self), val)
    }

    /// Create an [`VariableExpression`] that evaluates to `self < val`
    fn lt(&self, val: Float) -> VariableExpression
    where
        Self: std::marker::Sized + 'static,
    {
        VariableExpression::Lt(dyn_clone::clone_box(self), val)
    }

    /// Create an [`VariableExpression`] that evaluates to `self > val`
    fn gt(&self, val: Float) -> VariableExpression
    where
        Self: std::marker::Sized + 'static,
    {
        VariableExpression::Gt(dyn_clone::clone_box(self), val)
    }

    /// Create an [`VariableExpression`] that evaluates to `self >= val`
    fn ge(&self, val: Float) -> VariableExpression
    where
        Self: std::marker::Sized + 'static,
    {
        self.gt(val).or(&self.eq(val))
    }

    /// Create an [`VariableExpression`] that evaluates to `self <= val`
    fn le(&self, val: Float) -> VariableExpression
    where
        Self: std::marker::Sized + 'static,
    {
        self.lt(val).or(&self.eq(val))
    }
}
dyn_clone::clone_trait_object!(Variable);

/// Expressions which can be used to compare [`Variable`]s to [`Float`]s.
#[derive(Clone, Debug)]
pub enum VariableExpression {
    /// Expression which is true when the variable is equal to the float.
    Eq(Box<dyn Variable>, Float),
    /// Expression which is true when the variable is less than the float.
    Lt(Box<dyn Variable>, Float),
    /// Expression which is true when the variable is greater than the float.
    Gt(Box<dyn Variable>, Float),
    /// Expression which is true when both inner expressions are true.
    And(Box<VariableExpression>, Box<VariableExpression>),
    /// Expression which is true when either inner expression is true.
    Or(Box<VariableExpression>, Box<VariableExpression>),
    /// Expression which is true when the inner expression is false.
    Not(Box<VariableExpression>),
}

impl VariableExpression {
    /// Construct an [`VariableExpression::And`] from the current expression and another.
    pub fn and(&self, rhs: &VariableExpression) -> VariableExpression {
        VariableExpression::And(Box::new(self.clone()), Box::new(rhs.clone()))
    }

    /// Construct an [`VariableExpression::Or`] from the current expression and another.
    pub fn or(&self, rhs: &VariableExpression) -> VariableExpression {
        VariableExpression::Or(Box::new(self.clone()), Box::new(rhs.clone()))
    }

    /// Comple the [`VariableExpression`] into a [`CompiledExpression`].
    pub(crate) fn compile(&self) -> CompiledExpression {
        compile_expression(self.clone())
    }
}
impl Display for VariableExpression {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            VariableExpression::Eq(var, val) => {
                write!(f, "({} == {})", var, val)
            }
            VariableExpression::Lt(var, val) => {
                write!(f, "({} < {})", var, val)
            }
            VariableExpression::Gt(var, val) => {
                write!(f, "({} > {})", var, val)
            }
            VariableExpression::And(lhs, rhs) => {
                write!(f, "({} & {})", lhs, rhs)
            }
            VariableExpression::Or(lhs, rhs) => {
                write!(f, "({} | {})", lhs, rhs)
            }
            VariableExpression::Not(inner) => {
                write!(f, "!({})", inner)
            }
        }
    }
}

/// A method which negates the given expression.
pub fn not(expr: &VariableExpression) -> VariableExpression {
    VariableExpression::Not(Box::new(expr.clone()))
}

#[rustfmt::skip]
impl_op_ex!(& |lhs: &VariableExpression, rhs: &VariableExpression| -> VariableExpression{ lhs.and(rhs) });
#[rustfmt::skip]
impl_op_ex!(| |lhs: &VariableExpression, rhs: &VariableExpression| -> VariableExpression{ lhs.or(rhs) });
#[rustfmt::skip]
impl_op_ex!(! |exp: &VariableExpression| -> VariableExpression{ not(exp) });

#[derive(Debug)]
enum Opcode {
    PushEq(usize, Float),
    PushLt(usize, Float),
    PushGt(usize, Float),
    And,
    Or,
    Not,
}

pub(crate) struct CompiledExpression {
    bytecode: Vec<Opcode>,
    variables: Vec<Box<dyn Variable>>,
}

impl CompiledExpression {
    /// Evaluate the [`CompiledExpression`] on a given [`Event`].
    pub fn evaluate(&self, event: &Event) -> bool {
        let mut stack = Vec::with_capacity(self.bytecode.len());

        for op in &self.bytecode {
            match op {
                Opcode::PushEq(i, val) => stack.push(self.variables[*i].value(event) == *val),
                Opcode::PushLt(i, val) => stack.push(self.variables[*i].value(event) < *val),
                Opcode::PushGt(i, val) => stack.push(self.variables[*i].value(event) > *val),
                Opcode::Not => {
                    let a = stack.pop().unwrap();
                    stack.push(!a);
                }
                Opcode::And => {
                    let b = stack.pop().unwrap();
                    let a = stack.pop().unwrap();
                    stack.push(a && b);
                }
                Opcode::Or => {
                    let b = stack.pop().unwrap();
                    let a = stack.pop().unwrap();
                    stack.push(a || b);
                }
            }
        }

        stack.pop().unwrap()
    }
}

pub(crate) fn compile_expression(expr: VariableExpression) -> CompiledExpression {
    let mut bytecode = Vec::new();
    let mut variables: Vec<Box<dyn Variable>> = Vec::new();

    fn compile(
        expr: VariableExpression,
        bytecode: &mut Vec<Opcode>,
        variables: &mut Vec<Box<dyn Variable>>,
    ) {
        match expr {
            VariableExpression::Eq(var, val) => {
                variables.push(var);
                bytecode.push(Opcode::PushEq(variables.len() - 1, val));
            }
            VariableExpression::Lt(var, val) => {
                variables.push(var);
                bytecode.push(Opcode::PushLt(variables.len() - 1, val));
            }
            VariableExpression::Gt(var, val) => {
                variables.push(var);
                bytecode.push(Opcode::PushGt(variables.len() - 1, val));
            }
            VariableExpression::And(lhs, rhs) => {
                compile(*lhs, bytecode, variables);
                compile(*rhs, bytecode, variables);
                bytecode.push(Opcode::And);
            }
            VariableExpression::Or(lhs, rhs) => {
                compile(*lhs, bytecode, variables);
                compile(*rhs, bytecode, variables);
                bytecode.push(Opcode::Or);
            }
            VariableExpression::Not(inner) => {
                compile(*inner, bytecode, variables);
                bytecode.push(Opcode::Not);
            }
        }
    }

    compile(expr, &mut bytecode, &mut variables);

    CompiledExpression {
        bytecode,
        variables,
    }
}

fn sort_indices<T: AsRef<[usize]>>(indices: T) -> Vec<usize> {
    let mut indices = indices.as_ref().to_vec();
    indices.sort();
    indices
}

fn indices_to_string<T: AsRef<[usize]>>(indices: T) -> String {
    indices
        .as_ref()
        .iter()
        .map(|n| n.to_string())
        .collect::<Vec<_>>()
        .join(", ")
}

/// A struct for obtaining the mass of a particle by indexing the four-momenta of an event, adding
/// together multiple four-momenta if more than one index is given.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Mass(Vec<usize>);
impl Mass {
    /// Create a new [`Mass`] from the sum of the four-momenta at the given indices in the
    /// [`Event`]'s `p4s` field.
    pub fn new<T: AsRef<[usize]>>(constituents: T) -> Self {
        Self(sort_indices(constituents))
    }
}
impl Display for Mass {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Mass(constituents=[{}])", indices_to_string(&self.0))
    }
}
#[typetag::serde]
impl Variable for Mass {
    fn value(&self, event: &Event) -> Float {
        event.get_p4_sum(&self.0).m()
    }
}

/// A struct for obtaining the $`\cos\theta`$ (cosine of the polar angle) of a decay product in
/// a given reference frame of its parent resonance.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CosTheta {
    beam: usize,
    recoil: Vec<usize>,
    daughter: Vec<usize>,
    resonance: Vec<usize>,
    frame: Frame,
}
impl Display for CosTheta {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "CosTheta(beam={}, recoil=[{}], daughter=[{}], resonance=[{}], frame={})",
            self.beam,
            indices_to_string(&self.recoil),
            indices_to_string(&self.daughter),
            indices_to_string(&self.resonance),
            self.frame
        )
    }
}
impl CosTheta {
    /// Construct the angle given the four-momentum indices for each specified particle. Fields
    /// which can take lists of more than one index will add the relevant four-momenta to make a
    /// new particle from the constituents. See [`Frame`] for options regarding the reference
    /// frame.
    pub fn new<T: AsRef<[usize]>, U: AsRef<[usize]>, V: AsRef<[usize]>>(
        beam: usize,
        recoil: T,
        daughter: U,
        resonance: V,
        frame: Frame,
    ) -> Self {
        Self {
            beam,
            recoil: recoil.as_ref().into(),
            daughter: daughter.as_ref().into(),
            resonance: resonance.as_ref().into(),
            frame,
        }
    }
}
impl Default for CosTheta {
    fn default() -> Self {
        Self {
            beam: 0,
            recoil: vec![1],
            daughter: vec![2],
            resonance: vec![2, 3],
            frame: Frame::Helicity,
        }
    }
}
#[typetag::serde]
impl Variable for CosTheta {
    fn value(&self, event: &Event) -> Float {
        let beam = event.p4s[self.beam];
        let recoil = event.get_p4_sum(&self.recoil);
        let daughter = event.get_p4_sum(&self.daughter);
        let resonance = event.get_p4_sum(&self.resonance);
        let daughter_res = daughter.boost(&-resonance.beta());
        match self.frame {
            Frame::Helicity => {
                let recoil_res = recoil.boost(&-resonance.beta());
                let z = -recoil_res.vec3().unit();
                let y = beam.vec3().cross(&-recoil.vec3()).unit();
                let x = y.cross(&z);
                let angles = Vec3::new(
                    daughter_res.vec3().dot(&x),
                    daughter_res.vec3().dot(&y),
                    daughter_res.vec3().dot(&z),
                );
                angles.costheta()
            }
            Frame::GottfriedJackson => {
                let beam_res = beam.boost(&-resonance.beta());
                let z = beam_res.vec3().unit();
                let y = beam.vec3().cross(&-recoil.vec3()).unit();
                let x = y.cross(&z);
                let angles = Vec3::new(
                    daughter_res.vec3().dot(&x),
                    daughter_res.vec3().dot(&y),
                    daughter_res.vec3().dot(&z),
                );
                angles.costheta()
            }
        }
    }
}

/// A struct for obtaining the $`\phi`$ angle (azimuthal angle) of a decay product in a given
/// reference frame of its parent resonance.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Phi {
    beam: usize,
    recoil: Vec<usize>,
    daughter: Vec<usize>,
    resonance: Vec<usize>,
    frame: Frame,
}
impl Display for Phi {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "Phi(beam={}, recoil=[{}], daughter=[{}], resonance=[{}], frame={})",
            self.beam,
            indices_to_string(&self.recoil),
            indices_to_string(&self.daughter),
            indices_to_string(&self.resonance),
            self.frame
        )
    }
}
impl Phi {
    /// Construct the angle given the four-momentum indices for each specified particle. Fields
    /// which can take lists of more than one index will add the relevant four-momenta to make a
    /// new particle from the constituents. See [`Frame`] for options regarding the reference
    /// frame.
    pub fn new<T: AsRef<[usize]>, U: AsRef<[usize]>, V: AsRef<[usize]>>(
        beam: usize,
        recoil: T,
        daughter: U,
        resonance: V,
        frame: Frame,
    ) -> Self {
        Self {
            beam,
            recoil: recoil.as_ref().into(),
            daughter: daughter.as_ref().into(),
            resonance: resonance.as_ref().into(),
            frame,
        }
    }
}
impl Default for Phi {
    fn default() -> Self {
        Self {
            beam: 0,
            recoil: vec![1],
            daughter: vec![2],
            resonance: vec![2, 3],
            frame: Frame::Helicity,
        }
    }
}
#[typetag::serde]
impl Variable for Phi {
    fn value(&self, event: &Event) -> Float {
        let beam = event.p4s[self.beam];
        let recoil = event.get_p4_sum(&self.recoil);
        let daughter = event.get_p4_sum(&self.daughter);
        let resonance = event.get_p4_sum(&self.resonance);
        let daughter_res = daughter.boost(&-resonance.beta());
        match self.frame {
            Frame::Helicity => {
                let recoil_res = recoil.boost(&-resonance.beta());
                let z = -recoil_res.vec3().unit();
                let y = beam.vec3().cross(&-recoil.vec3()).unit();
                let x = y.cross(&z);
                let angles = Vec3::new(
                    daughter_res.vec3().dot(&x),
                    daughter_res.vec3().dot(&y),
                    daughter_res.vec3().dot(&z),
                );
                angles.phi()
            }
            Frame::GottfriedJackson => {
                let beam_res = beam.boost(&-resonance.beta());
                let z = beam_res.vec3().unit();
                let y = beam.vec3().cross(&-recoil.vec3()).unit();
                let x = y.cross(&z);
                let angles = Vec3::new(
                    daughter_res.vec3().dot(&x),
                    daughter_res.vec3().dot(&y),
                    daughter_res.vec3().dot(&z),
                );
                angles.phi()
            }
        }
    }
}

/// A struct for obtaining both spherical angles at the same time.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Angles {
    /// See [`CosTheta`].
    pub costheta: CosTheta,
    /// See [`Phi`].
    pub phi: Phi,
}

impl Display for Angles {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "Angles(beam={}, recoil=[{}], daughter=[{}], resonance=[{}], frame={})",
            self.costheta.beam,
            indices_to_string(&self.costheta.recoil),
            indices_to_string(&self.costheta.daughter),
            indices_to_string(&self.costheta.resonance),
            self.costheta.frame
        )
    }
}
impl Angles {
    /// Construct the angles given the four-momentum indices for each specified particle. Fields
    /// which can take lists of more than one index will add the relevant four-momenta to make a
    /// new particle from the constituents. See [`Frame`] for options regarding the reference
    /// frame.
    pub fn new<T: AsRef<[usize]>, U: AsRef<[usize]>, V: AsRef<[usize]>>(
        beam: usize,
        recoil: T,
        daughter: U,
        resonance: V,
        frame: Frame,
    ) -> Self {
        Self {
            costheta: CosTheta::new(beam, &recoil, &daughter, &resonance, frame),
            phi: Phi {
                beam,
                recoil: recoil.as_ref().into(),
                daughter: daughter.as_ref().into(),
                resonance: resonance.as_ref().into(),
                frame,
            },
        }
    }
}

/// A struct defining the polarization angle for a beam relative to the production plane.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct PolAngle {
    beam: usize,
    recoil: Vec<usize>,
    beam_polarization: usize,
}
impl Display for PolAngle {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "PolAngle(beam={}, recoil=[{}], beam_polarization={})",
            self.beam,
            indices_to_string(&self.recoil),
            self.beam_polarization,
        )
    }
}
impl PolAngle {
    /// Constructs the polarization angle given the four-momentum indices for each specified
    /// particle. Fields which can take lists of more than one index will add the relevant
    /// four-momenta to make a new particle from the constituents.
    pub fn new<T: AsRef<[usize]>>(beam: usize, recoil: T, beam_polarization: usize) -> Self {
        Self {
            beam,
            recoil: recoil.as_ref().into(),
            beam_polarization,
        }
    }
}
#[typetag::serde]
impl Variable for PolAngle {
    fn value(&self, event: &Event) -> Float {
        let beam = event.p4s[self.beam];
        let recoil = event.get_p4_sum(&self.recoil);
        let y = beam.vec3().cross(&-recoil.vec3()).unit();
        Float::atan2(
            y.dot(&event.aux[self.beam_polarization]),
            beam.vec3()
                .unit()
                .dot(&event.aux[self.beam_polarization].cross(&y)),
        )
    }
}

/// A struct defining the polarization magnitude for a beam relative to the production plane.
#[derive(Copy, Clone, Default, Debug, Serialize, Deserialize)]
pub struct PolMagnitude {
    beam_polarization: usize,
}
impl Display for PolMagnitude {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "PolMagnitude(beam_polarization={})",
            self.beam_polarization,
        )
    }
}
impl PolMagnitude {
    /// Constructs the polarization magnitude given the four-momentum index for the beam.
    pub fn new(beam_polarization: usize) -> Self {
        Self { beam_polarization }
    }
}
#[typetag::serde]
impl Variable for PolMagnitude {
    fn value(&self, event: &Event) -> Float {
        event.aux[self.beam_polarization].mag()
    }
}

/// A struct for obtaining both the polarization angle and magnitude at the same time.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Polarization {
    /// See [`PolMagnitude`].
    pub pol_magnitude: PolMagnitude,
    /// See [`PolAngle`].
    pub pol_angle: PolAngle,
}
impl Display for Polarization {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "Polarization(beam={}, recoil=[{}], beam_polarization={})",
            self.pol_angle.beam,
            indices_to_string(&self.pol_angle.recoil),
            self.pol_angle.beam_polarization,
        )
    }
}
impl Polarization {
    /// Constructs the polarization angle and magnitude given the four-momentum indices for
    /// the beam and target (recoil) particle. Fields which can take lists of more than one index will add
    /// the relevant four-momenta to make a new particle from the constituents.
    pub fn new<T: AsRef<[usize]>>(beam: usize, recoil: T, beam_polarization: usize) -> Self {
        Self {
            pol_magnitude: PolMagnitude::new(beam_polarization),
            pol_angle: PolAngle::new(beam, recoil, beam_polarization),
        }
    }
}

/// A struct used to calculate Mandelstam variables ($`s`$, $`t`$, or $`u`$).
///
/// By convention, the metric is chosen to be $`(+---)`$ and the variables are defined as follows
/// (ignoring factors of $`c`$):
///
/// $`s = (p_1 + p_2)^2 = (p_3 + p_4)^2`$
///
/// $`t = (p_1 - p_3)^2 = (p_4 - p_2)^2`$
///
/// $`u = (p_1 - p_4)^2 = (p_3 - p_2)^2`$
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Mandelstam {
    p1: Vec<usize>,
    p2: Vec<usize>,
    p3: Vec<usize>,
    p4: Vec<usize>,
    missing: Option<u8>,
    channel: Channel,
}
impl Display for Mandelstam {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "Mandelstam(p1=[{}], p2=[{}], p3=[{}], p4=[{}], channel={})",
            indices_to_string(&self.p1),
            indices_to_string(&self.p2),
            indices_to_string(&self.p3),
            indices_to_string(&self.p4),
            self.channel,
        )
    }
}
impl Mandelstam {
    /// Constructs the Mandelstam variable for the given `channel` and particles.
    /// Fields which can take lists of more than one index will add
    /// the relevant four-momenta to make a new particle from the constituents.
    pub fn new<T, U, V, W>(p1: T, p2: U, p3: V, p4: W, channel: Channel) -> Result<Self, LadduError>
    where
        T: AsRef<[usize]>,
        U: AsRef<[usize]>,
        V: AsRef<[usize]>,
        W: AsRef<[usize]>,
    {
        let mut missing = None;
        if p1.as_ref().is_empty() {
            missing = Some(1)
        }
        if p2.as_ref().is_empty() {
            if missing.is_none() {
                missing = Some(2)
            } else {
                return Err(LadduError::Custom("A maximum of one particle may be ommitted while constructing a Mandelstam variable!".to_string()));
            }
        }
        if p3.as_ref().is_empty() {
            if missing.is_none() {
                missing = Some(3)
            } else {
                return Err(LadduError::Custom("A maximum of one particle may be ommitted while constructing a Mandelstam variable!".to_string()));
            }
        }
        if p4.as_ref().is_empty() {
            if missing.is_none() {
                missing = Some(4)
            } else {
                return Err(LadduError::Custom("A maximum of one particle may be ommitted while constructing a Mandelstam variable!".to_string()));
            }
        }
        Ok(Self {
            p1: p1.as_ref().into(),
            p2: p2.as_ref().into(),
            p3: p3.as_ref().into(),
            p4: p4.as_ref().into(),
            missing,
            channel,
        })
    }
}

#[typetag::serde]
impl Variable for Mandelstam {
    fn value(&self, event: &Event) -> Float {
        match self.channel {
            Channel::S => match self.missing {
                None | Some(3) | Some(4) => {
                    let p1 = event.get_p4_sum(&self.p1);
                    let p2 = event.get_p4_sum(&self.p2);
                    (p1 + p2).mag2()
                }
                Some(1) | Some(2) => {
                    let p3 = event.get_p4_sum(&self.p3);
                    let p4 = event.get_p4_sum(&self.p4);
                    (p3 + p4).mag2()
                }
                _ => unreachable!(),
            },
            Channel::T => match self.missing {
                None | Some(2) | Some(4) => {
                    let p1 = event.get_p4_sum(&self.p1);
                    let p3 = event.get_p4_sum(&self.p3);
                    (p1 - p3).mag2()
                }
                Some(1) | Some(3) => {
                    let p2 = event.get_p4_sum(&self.p2);
                    let p4 = event.get_p4_sum(&self.p4);
                    (p4 - p2).mag2()
                }
                _ => unreachable!(),
            },
            Channel::U => match self.missing {
                None | Some(2) | Some(3) => {
                    let p1 = event.get_p4_sum(&self.p1);
                    let p4 = event.get_p4_sum(&self.p4);
                    (p1 - p4).mag2()
                }
                Some(1) | Some(4) => {
                    let p2 = event.get_p4_sum(&self.p2);
                    let p3 = event.get_p4_sum(&self.p3);
                    (p3 - p2).mag2()
                }
                _ => unreachable!(),
            },
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::data::{test_dataset, test_event};
    use approx::assert_relative_eq;

    #[test]
    fn test_mass_single_particle() {
        let event = test_event();
        let mass = Mass::new([1]);
        assert_relative_eq!(mass.value(&event), 1.007);
    }

    #[test]
    fn test_mass_multiple_particles() {
        let event = test_event();
        let mass = Mass::new([2, 3]);
        assert_relative_eq!(
            mass.value(&event),
            1.37437863,
            epsilon = Float::EPSILON.sqrt()
        );
    }

    #[test]
    fn test_mass_display() {
        let mass = Mass::new([2, 3]);
        assert_eq!(mass.to_string(), "Mass(constituents=[2, 3])");
    }

    #[test]
    fn test_costheta_helicity() {
        let event = test_event();
        let costheta = CosTheta::new(0, [1], [2], [2, 3], Frame::Helicity);
        assert_relative_eq!(
            costheta.value(&event),
            -0.4611175,
            epsilon = Float::EPSILON.sqrt()
        );
    }

    #[test]
    fn test_costheta_display() {
        let costheta = CosTheta::new(0, [1], [2], [2, 3], Frame::Helicity);
        assert_eq!(
            costheta.to_string(),
            "CosTheta(beam=0, recoil=[1], daughter=[2], resonance=[2, 3], frame=Helicity)"
        );
    }

    #[test]
    fn test_phi_helicity() {
        let event = test_event();
        let phi = Phi::new(0, [1], [2], [2, 3], Frame::Helicity);
        assert_relative_eq!(
            phi.value(&event),
            -2.65746258,
            epsilon = Float::EPSILON.sqrt()
        );
    }

    #[test]
    fn test_phi_display() {
        let phi = Phi::new(0, [1], [2], [2, 3], Frame::Helicity);
        assert_eq!(
            phi.to_string(),
            "Phi(beam=0, recoil=[1], daughter=[2], resonance=[2, 3], frame=Helicity)"
        );
    }

    #[test]
    fn test_costheta_gottfried_jackson() {
        let event = test_event();
        let costheta = CosTheta::new(0, [1], [2], [2, 3], Frame::GottfriedJackson);
        assert_relative_eq!(
            costheta.value(&event),
            0.09198832,
            epsilon = Float::EPSILON.sqrt()
        );
    }

    #[test]
    fn test_phi_gottfried_jackson() {
        let event = test_event();
        let phi = Phi::new(0, [1], [2], [2, 3], Frame::GottfriedJackson);
        assert_relative_eq!(
            phi.value(&event),
            -2.71391319,
            epsilon = Float::EPSILON.sqrt()
        );
    }

    #[test]
    fn test_angles() {
        let event = test_event();
        let angles = Angles::new(0, [1], [2], [2, 3], Frame::Helicity);
        assert_relative_eq!(
            angles.costheta.value(&event),
            -0.4611175,
            epsilon = Float::EPSILON.sqrt()
        );
        assert_relative_eq!(
            angles.phi.value(&event),
            -2.65746258,
            epsilon = Float::EPSILON.sqrt()
        );
    }

    #[test]
    fn test_angles_display() {
        let angles = Angles::new(0, [1], [2], [2, 3], Frame::Helicity);
        assert_eq!(
            angles.to_string(),
            "Angles(beam=0, recoil=[1], daughter=[2], resonance=[2, 3], frame=Helicity)"
        );
    }

    #[test]
    fn test_pol_angle() {
        let event = test_event();
        let pol_angle = PolAngle::new(0, vec![1], 0);
        assert_relative_eq!(
            pol_angle.value(&event),
            1.93592989,
            epsilon = Float::EPSILON.sqrt()
        );
    }

    #[test]
    fn test_pol_angle_display() {
        let pol_angle = PolAngle::new(0, vec![1], 0);
        assert_eq!(
            pol_angle.to_string(),
            "PolAngle(beam=0, recoil=[1], beam_polarization=0)"
        );
    }

    #[test]
    fn test_pol_magnitude() {
        let event = test_event();
        let pol_magnitude = PolMagnitude::new(0);
        assert_relative_eq!(
            pol_magnitude.value(&event),
            0.38562805,
            epsilon = Float::EPSILON.sqrt()
        );
    }

    #[test]
    fn test_pol_magnitude_display() {
        let pol_magnitude = PolMagnitude::new(0);
        assert_eq!(
            pol_magnitude.to_string(),
            "PolMagnitude(beam_polarization=0)"
        );
    }

    #[test]
    fn test_polarization() {
        let event = test_event();
        let polarization = Polarization::new(0, vec![1], 0);
        assert_relative_eq!(
            polarization.pol_angle.value(&event),
            1.93592989,
            epsilon = Float::EPSILON.sqrt()
        );
        assert_relative_eq!(
            polarization.pol_magnitude.value(&event),
            0.38562805,
            epsilon = Float::EPSILON.sqrt()
        );
    }

    #[test]
    fn test_polarization_display() {
        let polarization = Polarization::new(0, vec![1], 0);
        assert_eq!(
            polarization.to_string(),
            "Polarization(beam=0, recoil=[1], beam_polarization=0)"
        );
    }

    #[test]
    fn test_mandelstam() {
        let event = test_event();
        let s = Mandelstam::new([0], [], [2, 3], [1], Channel::S).unwrap();
        let t = Mandelstam::new([0], [], [2, 3], [1], Channel::T).unwrap();
        let u = Mandelstam::new([0], [], [2, 3], [1], Channel::U).unwrap();
        let sp = Mandelstam::new([], [0], [1], [2, 3], Channel::S).unwrap();
        let tp = Mandelstam::new([], [0], [1], [2, 3], Channel::T).unwrap();
        let up = Mandelstam::new([], [0], [1], [2, 3], Channel::U).unwrap();
        assert_relative_eq!(
            s.value(&event),
            18.50401105,
            epsilon = Float::EPSILON.sqrt()
        );
        assert_relative_eq!(s.value(&event), sp.value(&event),);
        assert_relative_eq!(
            t.value(&event),
            -0.19222859,
            epsilon = Float::EPSILON.sqrt()
        );
        assert_relative_eq!(t.value(&event), tp.value(&event),);
        assert_relative_eq!(
            u.value(&event),
            -14.40419893,
            epsilon = Float::EPSILON.sqrt()
        );
        assert_relative_eq!(u.value(&event), up.value(&event),);
        let m2_beam = test_event().get_p4_sum([0]).m2();
        let m2_recoil = test_event().get_p4_sum([1]).m2();
        let m2_res = test_event().get_p4_sum([2, 3]).m2();
        assert_relative_eq!(
            s.value(&event) + t.value(&event) + u.value(&event) - m2_beam - m2_recoil - m2_res,
            1.00,
            epsilon = 1e-2
        );
        // Note: not very accurate, but considering the values in test_event only go to about 3
        // decimal places, this is probably okay
    }

    #[test]
    fn test_mandelstam_display() {
        let s = Mandelstam::new([0], [], [2, 3], [1], Channel::S).unwrap();
        assert_eq!(
            s.to_string(),
            "Mandelstam(p1=[0], p2=[], p3=[2, 3], p4=[1], channel=s)"
        );
    }

    #[test]
    fn test_variable_value_on() {
        let dataset = test_dataset();
        let mass = Mass::new(vec![2, 3]);

        let values = mass.value_on(&dataset);
        assert_eq!(values.len(), 1);
        assert_relative_eq!(values[0], 1.37437863, epsilon = Float::EPSILON.sqrt());
    }
}
