"""Prepare reviewable analysis configuration from explicit signed decisions.

No files, approvals, protocol status or execution authorization are changed.
"""
from copy import deepcopy
from researcher_approval import ROOT, validate_approval_record


def prepare_analysis_configuration(record, config, evaluation_config, *, root=ROOT):
    """Map signed decision 26 details to inactive configuration copies.

    ``analysis_settings`` is an explicit operational detail in the signed
    resolved_details payload, never inferred from proposal prose. Decisions 12
    and 18 must also be complete. Unsupported Holm/testing plans fail closed.
    """
    errors = validate_approval_record(record, root=root, required_ids={12, 18, 26})
    if errors:
        raise ValueError('; '.join(errors))
    row = next(r for r in record['decisions'] if r['id'] == 26)
    settings = row['resolved_details'].get('analysis_settings')
    if not isinstance(settings, dict):
        raise ValueError('signed analysis_settings mapping required')
    required = {'statistic', 'interval_method', 'confidence_level', 'replicates',
                'seed', 'random_generator_and_version', 'comparisons',
                'missing_policy', 'multiplicity_method', 'analysis_dependency_versions'}
    if set(settings) != required:
        raise ValueError('analysis_settings must contain exactly the documented keys')
    from evaluation import ARMS
    pairs = settings['comparisons']
    if (settings['statistic'] != 'arithmetic_mean'
            or settings['interval_method'] != 'linear_percentile'
            or settings['confidence_level'] != 0.95
            or settings['multiplicity_method'] != 'unadjusted_marginal_intervals'
            or settings['random_generator_and_version'] != 'python.random.Random/MT19937; sha256(seed:replicate) streams'
            or settings['missing_policy'] not in ('block', 'complete_pairs')
            or type(settings['replicates']) is not int or settings['replicates'] < 1
            or type(settings['seed']) is not int
            or not isinstance(pairs, list) or not pairs
            or any(not isinstance(p, list) or len(p) != 2 or p[0] == p[1]
                   or any(a not in ARMS for a in p) for p in pairs)
            or len({tuple(p) for p in pairs}) != len(pairs)
            or not isinstance(settings['analysis_dependency_versions'], str)
            or not settings['analysis_dependency_versions'].strip()):
        raise ValueError('unsupported or incomplete analysis settings; implement replacement before use')
    # Explicit signed scalar settings above bind the plan independently of prose.
    config, evaluation_config = deepcopy(config), deepcopy(evaluation_config)
    config['statistical_analysis'].update(
        comparisons=deepcopy(pairs), statistical_model='paired arithmetic mean differences by input set',
        multiplicity_method=settings['multiplicity_method'], missing_data_rule=settings['missing_policy'],
        analysis_dependency_versions=settings['analysis_dependency_versions'])
    evaluation_config['paired_bootstrap'].update({k: deepcopy(settings[k]) for k in (
        'statistic', 'interval_method', 'confidence_level', 'replicates', 'seed', 'random_generator_and_version')})
    evaluation_config['paired_bootstrap'].update(comparisons=deepcopy(pairs),
        missing_policy=settings['missing_policy'],
        multiplicity_method=settings['multiplicity_method'], analysis_scope='descriptive',
        all_seven_arm_pairwise_comparisons=len({frozenset(p) for p in pairs}) == 21)
    return config, evaluation_config
