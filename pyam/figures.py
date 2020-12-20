import logging

import pandas as pd
import plotly.graph_objects as go
from pyam.index import get_index_levels

logger = logging.getLogger(__name__)


def sankey(df, mapping):
    """Plot a sankey diagram

    It is currently only possible to create this diagram for single years.

    Parameters
    ----------
    df : :class:`pyam.IamDataFrame`
        Data to be plotted
    mapping : dict
        Assigns the source and target component of a variable

        .. code-block:: python

            {
                variable: (source, target),
            }

        Returns
        -------
        fig : plotly.graph_objs._figure.Figure
    """
    # Check for duplicates
    for col in [name for name in df._data.index.names if name != 'variable']:
        levels = get_index_levels(df._data, col)
        if len(levels) > 1:
            raise ValueError(f'Non-unique values in column {col}: {levels}')

    # Concatenate the data with source and target columns
    _df = pd.DataFrame(columns=['variable', 'source', 'target'])
    _data = []
    for k, dv in mapping.items():
        for v in dv:
            _data.append({'variable': k, 'source': v[0], 'target': v[1]})
    _df = (
        _df.append(_data,True)
        .merge(df._data, left_on='variable', right_on='variable', left_index=True)
    )
    _df.drop(columns='variable', inplace=True)
    _df = _df.groupby(['source', 'target']).sum()
    label_mapping = dict([(label, i) for i, label
                          in enumerate(set(pd.Series(_df.index.get_level_values('source'))
                                           .append(pd.Series(_df.index.get_level_values('target')))))])
    _df.reset_index(level=['source', 'target'], inplace=True)
    _df.replace(label_mapping, inplace=True)
    #region = get_index_levels(_df, 'region')[0]
    #unit = get_index_levels(_df, 'unit')[0]
    #year = get_index_levels(_df, 'year')[0]
    fig = go.Figure(data=[go.Sankey(
    #    valuesuffix=unit,
        node=dict(
            pad=15,
            thickness=10,
            line=dict(color="black", width=0.5),
            label=pd.Series(list(label_mapping)),
            hovertemplate='%{label}: %{value}<extra></extra>',
            color="blue"
        ),
        link=dict(
            source=_df.source,
            target=_df.target,
            value=_df.value,
            hovertemplate='"%{source.label}" to "%{target.label}": \
                %{value}<extra></extra>'
        )
    )])
    #fig.update_layout(title_text=f'region: {region}, year: {year}',
    #                  font_size=10)
    return fig
