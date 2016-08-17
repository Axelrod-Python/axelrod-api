from distutils.util import strtobool


def passes_boolean_filter(strategy, filterset, filter):
    filter_value = strtobool(filterset[filter])
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
    filter_map = {
        'stochastic': 'boolean',
        'manipulates_state': 'boolean',
        'manipulates_source': 'boolean',
        'inspects_source': 'boolean'
    }
    passes_filters = []

    for filter in filterset:
        if filter_map[filter] == 'boolean':
            passes_filters.append(
                passes_boolean_filter(strategy, filterset, filter))

    return all(passes_filters)
