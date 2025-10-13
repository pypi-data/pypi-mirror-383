from dash import html, dcc
import dash_bootstrap_components as dbc
import inspect
import math
from typing import Callable

from th_helpers.components import deck_label
from th_helpers.utils import colors

win_rate_calc_comp = '''
$$
\% = \\frac{wins + \\frac{ties}{3}}{total}
$$
'''
SIGNIFICANT_MAPPING = {
    'some': '*',
    'all': '**',
    'favored': '*',
    'unfavored': '*'
}


def determine_win_rate(match):
    if 'Win' in match:
        wins = match.get('Win', 0)
        loss = match.get('Loss', 0)
        ties = match.get('Tie', 0)
    elif 'wins' in match:
        wins = match.get('wins', 0)
        loss = match.get('losses', 0)
        ties = match.get('ties', 0)
    elif 'w' in match:
        wins = match.get('w', 0)
        loss = match.get('l', 0)
        ties = match.get('t', 0)
    else:
        wins = 0
        loss = 0
        ties = 0
    total = wins + loss + ties
    if total == 0: return 0
    return round((wins + ties/3) / total * 100, 1)


def create_record_string(match):
    if 'Win' in match and 'Loss' in match:
        tied = f'-{match["Tie"]}' if match.get('Tie', 0) > 0 else ''
        record_string = f'{match["Win"]}-{match["Loss"]}{tied}'
        return record_string
    if 'wins' in match and 'losses' in match:
        tied = f'-{match["ties"]}' if match.get('ties', 0) > 0 else ''
        record_string = f'{match["wins"]}-{match["losses"]}{tied}'
        return record_string
    if 'w' in match or 'l' in match or 't' in match:
        tied = f'-{match["t"]}' if match.get('t', 0) > 0 else ''
        record_string = f'{match.get("w", 0)}-{match.get("l", 0)}{tied}'
        return record_string
    return None


def _call_label_func(func, deck, hide_text=False):
    if func is None:
        return None
    kwargs = {}
    kwargs['hide_text'] = hide_text
    if isinstance(func, Callable):
        return func(deck, **kwargs)
    return None


def create_popover_inside(color='', record='', wr='', decks=None, match=None, player=None, against=None, label_func=None):
    vs_item = html.Div([
        html.Span(
            _call_label_func(label_func, decks.get(match[player]), hide_text=True)
        ),
        html.Span('vs.', className='mx-2'),
        html.Span(
            _call_label_func(label_func, decks.get(match[against]), hide_text=True)
        ),
    ], className='d-flex align-items-center justify-content-around')
    return html.Div([
        vs_item,
        html.Div(f'{wr}%'),
        html.Div(record)
    ], className='text-black text-center p-2 rounded', style={'backgroundColor': color})


def create_record_display(match, className=None):
    wr = match['win_rate']
    record = create_record_string(match)
    color = colors.win_rate_color_bar[math.floor(wr)][1]
    return html.Td([
        f'{wr}%', html.Div(record)
    ], className=f'text-center text-black {className}', style={'backgroundColor': color})


def create_matchup_tile(match, decks, player, against, label_func=None):
    if match is None or match['win_rate'] is None or math.isnan(match['win_rate']):
        return html.Td('-', className='text-center align-middle')
    id = match[player] + match[against]
    wr = match['win_rate']
    record = create_record_string(match)
    color = colors.win_rate_color_bar[math.floor(wr)][1]
    return html.Td([
        html.Div([f'{wr}%', html.Div(record)], id=id, className='text-center'),
        dbc.Popover(
            create_popover_inside(color=color, record=record, wr=wr,
                                  decks=decks, match=match, player=player,
                                  against=against, label_func=label_func),
            target=id,
            trigger='hover',
            placement='bottom'
        ),
    ], style={'backgroundColor': color, 'width': '112px'}, className='text-center text-black align-middle')

def create_matchup_table_row(deck, data, decks, player, against, label_func=None):
    matches = [create_matchup_tile(match, decks, player, against, label_func=label_func) for match in data]
    row = html.Tr([html.Td(
        _call_label_func(label_func, decks[deck]),
        className='text-nowrap align-middle'
    )] + matches)
    return row

def create_matchup_tile_full(match, decks, player, against, label_func=None):
    if match is None or match['win_rate'] is None or math.isnan(match['win_rate']):
        return html.Span(className='d-none')
    id = match[player] + match[against]
    wr = match['win_rate']
    record = create_record_string(match)
    color = colors.win_rate_color_bar[math.floor(wr)][1]
    vs_item = html.Div([
        html.Span('vs.', className='me-1'),
        html.Span(
            _call_label_func(label_func, decks.get(match[against]), hide_text=True)
        ),
    ], className='d-flex align-items-center')
    significant = SIGNIFICANT_MAPPING[match['significant']] if match.get('significant', None) else ''
    return dbc.Card(
        dbc.CardBody([
            vs_item,
            html.Div(f'{match["win_rate"]}%{significant}'),
            html.Div(record)
        ], class_name='text-black text-center p-1'),
        style={'backgroundColor': color},
        className='w-auto',
        id=id
    )    

def create_matchup_tile_row(deck, data, decks, player, against, label_func=None):
    row = html.Div([
        html.H5(_call_label_func(label_func, decks[deck])),
        dbc.Row([create_matchup_tile_full(match, decks, player, against, label_func=label_func) for match in data], class_name='g-1')
    ], className='mb-2')
    return row

def create_matchup_spread(data, decks, player='deck1', against='deck2', small_view=False, label_func=None, sort_matchups=False):
    # Extract unique decks from player and sort them alphabetically
    player_unique_decks = list(set(matchup[player] for matchup in data))
    if len(player_unique_decks) == 0:
        return 'No matchup information found.'
    if 'Plays:' in player_unique_decks[0]:
        player_unique_decks = sorted(player_unique_decks, key=lambda x: int(x.split(':')[1].strip()))
    else:
        player_unique_decks = sorted(player_unique_decks)
    against_unique_decks = sorted(set(matchup[against] for matchup in data))

    rows = []
    small_rows = []
    deck_matchups_lookup = {}

    def _matchup_sort_key(match):
        if match is None:
            return math.inf
        wr = match.get('win_rate')
        if wr is None or math.isnan(wr):
            return math.inf
        return wr

    # Organize the data
    for deck in player_unique_decks:
        if deck not in decks:
            icons = ['substitute'] if 'Plays:' not in deck else []
            decks[deck] = {'id': deck, 'name': deck.title(), 'icons': icons}
        matchups = sorted(
            (matchup for matchup in data if matchup[player] == deck),
            key=lambda x: x[against]
        )
        duplicates = [index for index, d in enumerate(matchups) if d[player] == d[against]]
        if len(duplicates) > 1:
            matchups.pop(duplicates[0])

        ordered_matchups = [None for _ in range(len(against_unique_decks))]
        for m in matchups:
            ordered_matchups[against_unique_decks.index(m[against])] = m
        deck_matchups_lookup[deck] = ordered_matchups

        sorted_matchups = sorted(
            (m for m in ordered_matchups if m is not None),
            key=_matchup_sort_key
        )
        small_rows.append(
            create_matchup_tile_row(
                deck,
                sorted_matchups if sort_matchups else ordered_matchups,
                decks,
                player,
                against,
                label_func=label_func
            )
        )

    if len(player_unique_decks) == 1 and player_unique_decks[0] in deck_matchups_lookup:
        deck = player_unique_decks[0]
        ordered_matchups = deck_matchups_lookup[deck]

        sorted_indexes = sorted(
            range(len(against_unique_decks)),
            key=lambda index: _matchup_sort_key(ordered_matchups[index])
        )
        against_unique_decks = [against_unique_decks[i] for i in sorted_indexes]
        deck_matchups_lookup[deck] = [ordered_matchups[i] for i in sorted_indexes]

    for deck in player_unique_decks:
        if deck in deck_matchups_lookup:
            rows.append(
                create_matchup_table_row(
                    deck,
                    deck_matchups_lookup[deck],
                    decks,
                    player,
                    against,
                    label_func=label_func
                )
            )

    header_labels = [
        html.Div(
            _call_label_func(label_func, decks.get(deck, deck_label.create_default_deck(deck)), hide_text=True),
            className='d-flex justify-content-center')
        for deck in against_unique_decks
    ]
    headers = html.Thead(html.Tr([
        html.Th(deck) for deck in [dcc.Markdown(win_rate_calc_comp, mathjax=True)] + header_labels
    ]), className='sticky-top')
    table = dbc.Table([
        headers,
        html.Tbody(rows)
    ], className='d-none' if small_view else 'd-none d-xl-block')

    small_view = html.Div([
        # win_rate_calc_comp,
        html.Div(small_rows)
    ], className='' if small_view else 'd-xl-none')
    return html.Div([table, small_view])


def create_example(win_rate_mathjax):
    example = html.Div([
        html.Div([
            'Other vs Other',
            create_popover_inside('#fff', 'Wins-Losses-Ties', 'rate', decks={}, match={None: None}),
            'Color based on rate',
            html.Div(style={
                'background': f'linear-gradient(to right, {", ".join(colors.red_to_white_to_blue)})',
                'height': '20px',
                'width': '100%',
                'border': '1px solid #ccc'
            }),
            html.Div([html.Span(c) for c in [0, 100]], className='d-flex justify-content-between')
        ], className='text-center'),
        html.Div([
            'Weighted success rate',
            dcc.Markdown(
                win_rate_mathjax,
                mathjax=True, className='win-rate-calc'
            )
        ]),
    ])
    return example
