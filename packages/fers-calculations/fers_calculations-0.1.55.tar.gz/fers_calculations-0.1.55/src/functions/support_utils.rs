// src/functions/support_utils.rs
use std::collections::{BTreeMap, HashMap, HashSet};

use crate::functions::geometry::dof_index;
use crate::models::fers::fers::{ROTATION_AXES, TRANSLATION_AXES};
use crate::models::members::memberset::MemberSet;
use crate::models::supports::nodalsupport::NodalSupport;
use crate::models::supports::supportcondition::SupportCondition;
use crate::models::supports::supportconditiontype::SupportConditionType;
use nalgebra::DMatrix;

pub fn visit_unique_supported_nodes<F>(
    member_sets: &[MemberSet],
    nodal_supports: &[NodalSupport],
    mut visitor: F,
) -> Result<(), String>
where
    F: FnMut(u32, usize, &NodalSupport) -> Result<(), String>,
{
    let support_by_id: HashMap<u32, &NodalSupport> =
        nodal_supports.iter().map(|s| (s.id, s)).collect();

    let mut seen: HashSet<u32> = HashSet::new();

    for member_set in member_sets {
        for member in &member_set.members {
            for node in [&member.start_node, &member.end_node] {
                if !seen.insert(node.id) {
                    continue;
                }
                if let Some(support_id) = node.nodal_support {
                    if let Some(support) = support_by_id.get(&support_id) {
                        let base_index = dof_index(node.id, 0);
                        visitor(node.id, base_index, support)?;
                    }
                }
            }
        }
    }
    Ok(())
}

/// Case-insensitive fetch of a support condition from a per-axis map.
pub fn get_support_condition<'a>(
    map: &'a BTreeMap<String, SupportCondition>,
    axis_label: &str,
) -> Option<&'a SupportCondition> {
    map.get(axis_label)
        .or_else(|| map.get(&axis_label.to_ascii_lowercase()))
}

pub fn add_support_springs_to_operator(
    member_sets: &[MemberSet],
    nodal_supports: &[NodalSupport],
    k_global: &mut DMatrix<f64>,
) -> Result<(), String> {
    visit_unique_supported_nodes(
        member_sets,
        nodal_supports,
        |_node_id, base_index, support| {
            // Translational springs
            for (axis_label, local_dof) in TRANSLATION_AXES {
                if let Some(cond) =
                    get_support_condition(&support.displacement_conditions, axis_label)
                {
                    if let SupportConditionType::Spring = cond.condition_type {
                        let k = spring_stiffness_or_error(
                            support.id,
                            axis_label,
                            "displacement",
                            cond.stiffness,
                        )?;
                        k_global[(base_index + local_dof, base_index + local_dof)] += k;
                    }
                }
            }

            // Rotational springs
            for (axis_label, local_dof) in ROTATION_AXES {
                if let Some(cond) = get_support_condition(&support.rotation_conditions, axis_label)
                {
                    if let SupportConditionType::Spring = cond.condition_type {
                        let k = spring_stiffness_or_error(
                            support.id,
                            axis_label,
                            "rotation",
                            cond.stiffness,
                        )?;
                        k_global[(base_index + local_dof, base_index + local_dof)] += k;
                    }
                }
            }

            Ok(())
        },
    )
}

/// Validate stiffness option and return k > 0 (uniform error text).
pub fn spring_stiffness_or_error(
    owner_id: u32,
    axis_label: &str,
    kind_label: &str,
    stiffness: Option<f64>,
) -> Result<f64, String> {
    let k = stiffness.ok_or_else(|| {
        format!(
            "Support {} {} {} is Spring but stiffness is missing.",
            owner_id, kind_label, axis_label
        )
    })?;
    if k <= 0.0 {
        return Err(format!(
            "Support {} {} {} Spring stiffness must be positive.",
            owner_id, kind_label, axis_label
        ));
    }
    Ok(k)
}

/// Strong Dirichlet on a single DOF.
pub fn constrain_single_dof(
    k: &mut DMatrix<f64>,
    rhs: &mut DMatrix<f64>,
    dof_index: usize,
    prescribed: f64,
) {
    for j in 0..k.ncols() {
        k[(dof_index, j)] = 0.0;
    }
    for i in 0..k.nrows() {
        k[(i, dof_index)] = 0.0;
    }
    k[(dof_index, dof_index)] = 1.0;
    rhs[(dof_index, 0)] = prescribed;
}
