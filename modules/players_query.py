from typing import Literal, TypedDict


class GetPlayerArgs(TypedDict):
    active: int
    page: int
    count: int
    orderby: Literal["ASC", "DESC"]
    field: str


get_players_args: GetPlayerArgs = {
    "active": 1,
    "page": 1,
    "count": 20,
    "orderby": "DESC",
    "field": "draft_year",
}


def get_players(**kwargs):
    orderby = kwargs.get("orderby", "DESC")
    return f"""
        SELECT * FROM common_player_info
        JOIN player ON common_player_info.person_id = player.id
        WHERE is_active = {kwargs.get('active', 1)}
        ORDER BY {kwargs.get('field', 'draft_year')} {orderby}
        OFFSET {kwargs.get('page', 1)}
        LIMIT {kwargs.get('count', 20)}
    """


def get_players_count(active: int):
    return f"""
    SELECT COUNT(person_id) FROM common_player_info
        JOIN player ON common_player_info.person_id = player.id
        WHERE is_active = {active};
    """


def get_player(player_slug: str):
    return f"""
    SELECT * FROM common_player_info
        JOIN player ON common_player_info.person_id = player.id
        WHERE player_slug = '{player_slug}'
        LIMIT 1;
    """


def find_player(keyword: str, orderby="DESC"):
    return f"""
    SELECT * FROM common_player_info
        WHERE first_name ILIKE '%{keyword}%'
        OR last_name ILIKE '%{keyword}%'
        OR display_first_last ILIKE '%{keyword}%'
        ORDER BY from_year {orderby};
    """
