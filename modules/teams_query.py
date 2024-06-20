from typing import Literal, TypedDict


class GetTeamArgs(TypedDict):
    page: int
    count: int
    sort_field: str
    sort_order: Literal["ASC", "DESC"]


team_args: GetTeamArgs = {
    "page": 1,
    "count": 30,
    "sort_field": "abbreviation",
    "sort_order": "ASC",
}


def get_teams_query(**opts) -> str:
    sort_field = opts.get("sort_field", team_args["sort_field"])
    sort_order = opts.get("sort_order", team_args["sort_order"])

    return f"""
        SELECT * FROM team_details
        ORDER BY {sort_field} {sort_order}
    """


def get_teams_count() -> str:
    return """
    SELECT DISTINCT count(team_id) FROM team_details
    """


def get_team_query(name: str) -> str:
    return f"""
    SELECT * FROM team_details
        WHERE LOWER(nickname) = '{name}'
    """


def get_conference() -> str:
    return """
    SELECT jsonb_object_agg(conference, teams)
    FROM (
        SELECT
            conference,
            jsonb_agg(
                jsonb_build_object(
                    'id', team_id,
                    'abbr', abbreviation,
                    'name', nickname,
                    'city', city,
                    'arena', arena,
                    'arena_capacity', arenacapacity,
                    'general_manager', generalmanager,
                    'head_coach', headcoach,
                    'd_league_affiliation', dleagueaffiliation,
                    'facebook', facebook,
                    'twitter', twitter,
                    'instagram', instagram,
                    'conference', conference,
                    'division', division,
                    'founded', yearfounded
                )
            ) AS teams
        FROM team_details
        GROUP BY conference
    ) subquery;
    """


def get_team_info() -> str:
    return """
    """


def get_team_roster() -> str:
    return """
    """


def get_team_games() -> str:
    return """
    """
