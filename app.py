from dash import Dash, html, dcc, callback, Output, Input, State, ALL, ctx
import dash_bootstrap_components as dbc

import data


def build_nominee_card(nominee_data, choice):
    """
    Construct a bootstrap card given the nominee data.
    Add voted class if it is selected
    """
    if choice == nominee_data["id"]:
        card_class = "voted mt-2"
    else:
        card_class = "mt-2"

    return dbc.Col(
        dbc.Card(
            [
                dbc.CardHeader(
                    nominee_data["title"], style={"textAlign": "center"}
                ),
                dbc.CardImg(src=nominee_data["photoUrL"]),
                dbc.CardFooter(
                    dbc.Button(
                        "Select",
                        className="select-button",
                        id={"type": "vote-button", "id": nominee_data["id"]},
                    ),
                    style={"textAlign": "center"},
                ),
            ],
            className=card_class,
        ),
        md=True,
    )


def build_category(category_data, choice):
    """
    Returns list including row with category name and
    row with cards for each nominee
    """
    return [
        dbc.Row(dbc.Col(html.H2(category_data["title"])), className="mt-5"),
        dbc.Row(
            [
                build_nominee_card(nominee, choice)
                for nominee in category_data["items"]
            ]
        ),
    ]


def build_display(choices):
    """
    Returns full set of layout data for all nominees
    in all categories
    """
    nominee_data = []
    for category in data.BALLOT_DATA["items"]:
        nominee_data.extend(build_category(category, choices[category["id"]]))
    return nominee_data


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(html.H1("AWARDS 2023", style={"textAlign": "center"}))
        ),
        html.Div(id="categories"),
        dcc.Store("user-votes", data=data.initial_votes),
        dbc.Row(
            dbc.Col(
                dbc.Button(
                    "Submit Ballot",
                    id="submit-ballot",
                    size="lg",
                    className="mt-5",
                ),
                style={"textAlign": "center"},
            ),
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Ballot Submitted")),
                dbc.ModalBody(id="modal-body"),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close", id="close", className="ms-auto", n_clicks=0
                    )
                ),
            ],
            id="voted-modal",
            is_open=False,
        ),
    ],
    id="container",
)


@callback(
    Output("user-votes", "data"),
    Output("categories", "children"),
    Input({"type": "vote-button", "id": ALL}, "n_clicks"),
    Input({"type": "vote-button", "id": ALL}, "id"),
    State("user-votes", "data"),
)
def load_data(_data, _id, current_votes):
    """
    Render nominees and categories accounting for user's votes
    """
    if ctx.triggered_id is not None:
        nominee_id = ctx.triggered_id["id"]
        current_votes[data.id_to_category[nominee_id]] = nominee_id

    return current_votes, build_display(current_votes)


@callback(
    Output("voted-modal", "is_open"),
    Output("modal-body", "children"),
    Input("submit-ballot", "n_clicks"),
    Input("close", "n_clicks"),
    State("voted-modal", "is_open"),
    State("user-votes", "data"),
    prevent_initial_call=True,
)
def submit_ballot(submit_clicks, close_clicks, modal_open, current_votes):
    """
    Render modal to show what user has voted for
    """
    result = []
    for category_id, nominee_id in current_votes.items():
        category_name = data.category_id_to_name[category_id]
        if nominee_id is None:
            nominee_name = "Abstained"
        else:
            nominee_name = data.item_id_to_name[nominee_id]

        result.append(dbc.ListGroupItem(f"{category_name}: {nominee_name}"))

    return not modal_open, dbc.ListGroup(result)


if __name__ == "__main__":
    app.run(debug=True)
