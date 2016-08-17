from distutils.util import strtobool
import operator


def passes_boolean_filter(strategy, classifier, value):
    if isinstance(value, str):
        filter_value = strtobool(value)
    else:
        filter_value = value

    return strategy.classifier[classifier] == filter_value


def passes_operator_filter(strategy, classifier, value, operator):
    if isinstance(value, str):
        filter_value = int(value)
    else:
        filter_value = value

    classifier_value = strategy.classifier[classifier]
    if (isinstance(classifier_value, str) and
            classifier_value.lower() == 'infinity'):
        classifier_value = float('inf')

    return operator(classifier_value, filter_value)


def passes_in_list_filter(strategy, classifier, value):
    return value in strategy.classifier[classifier]


def passes_filterset(strategy, filterset):
    """
    Parameters
    ----------
        strategy : a descendant class of axelrod.Player
        filterset : dictionary

    Returns
    -------
        boolean
    """
    filter_types = {
        'stochastic': ('boolean', 'stochastic'),
        'long_run_time': ('boolean', 'long_run_time'),
        'manipulates_state': ('boolean', 'manipulates_state'),
        'manipulates_source': ('boolean', 'manipulates_source'),
        'inspects_source': ('boolean', 'inspects_source'),
        'min_memory_depth': ('gte', 'memory_depth'),
        'max_memory_depth': ('lte', 'memory_depth'),
        'makes_use_of': ('list', 'makes_use_of')
    }
    passes_filters = []

    for filter in filterset:
        if filter_types[filter][0] == 'boolean':
            passes_filters.append(
                passes_boolean_filter(
                    strategy, filter_types[filter][1], filterset[filter]))
        elif filter_types[filter][0] == 'gte':
            passes_filters.append(
                passes_operator_filter(
                    strategy, filter_types[filter][1], filterset[filter],
                    operator.ge))
        elif filter_types[filter][0] == 'lte':
            passes_filters.append(
                passes_operator_filter(
                    strategy, filter_types[filter][1], filterset[filter],
                    operator.le))
        elif filter_types[filter][0] == 'list':
            passes_filters.append(
                passes_in_list_filter(
                    strategy, filter_types[filter][1], filterset[filter]))

    return all(passes_filters)
