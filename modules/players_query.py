from typing import Literal, TypedDict


class GetPlayerArgs(TypedDict):
    active: int
    page: int
    count: int
    sort_field: str
    sort_order: Literal["ASC", "DESC"]


get_players_args: GetPlayerArgs = {
    "active": 1,
    "page": 1,
    "count": 20,
    "sort_field": "draft_year",
    "sort_order": "DESC",
}


def get_players(**opts):
    sort_field = opts.get("sort_field", "draft_year")
    sort_order = opts.get("sort_order", "DESC")

    return f"""
    SELECT * FROM common_player_info
        JOIN player ON common_player_info.person_id = player.id
        WHERE is_active = {opts.get('active', 1)}
        ORDER BY {sort_field} {sort_order}
        OFFSET {opts.get('page', 1)}
        LIMIT {opts.get('count', 20)}
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


def find_player_record(keyword: str, orderby="DESC"):
    return f"""
    SELECT * FROM common_player_info
        WHERE first_name ILIKE '%{keyword}%'
        OR last_name ILIKE '%{keyword}%'
        OR display_first_last ILIKE '%{keyword}%'
        ORDER BY from_year {orderby};
    """
