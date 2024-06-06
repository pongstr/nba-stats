def get_players(active=1, orderby="DESC", limit=20, offset=1):
    return f"""
        SELECT * FROM common_player_info
            JOIN player ON common_player_info.person_id = player.id
            WHERE is_active = {active}
            OFFSET {offset}
            ORDER_BY {orderby}
            LIMIT {limit}
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
