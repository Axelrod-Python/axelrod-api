from distutils.util import strtobool


def passes_boolean_filter(strategy, filterset, filter):
    if isinstance(filterset[filter], str):
        filter_value = strtobool(filterset[filter])
    else:
        filter_value = filterset[filter]
    return strategy.classifier[filter] == filter_value


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
        'stochastic': 'boolean',
        'manipulates_state': 'boolean',
        'manipulates_source': 'boolean',
        'inspects_source': 'boolean'
    }
    passes_filters = []

    for filter in filterset:
        if filter_types[filter] == 'boolean':
            passes_filters.append(
                passes_boolean_filter(strategy, filterset, filter))

    return all(passes_filters)
