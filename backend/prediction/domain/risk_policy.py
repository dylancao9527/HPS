INFERENCE_BP_MEDS_POLICY = "neutralized_for_conservative_inference"


def resolve_inference_bp_meds(bp_meds):
    return 0, {
        "bp_meds_input": bp_meds,
        "bp_meds_model_value": 0,
        "bp_meds_policy": INFERENCE_BP_MEDS_POLICY,
    }
