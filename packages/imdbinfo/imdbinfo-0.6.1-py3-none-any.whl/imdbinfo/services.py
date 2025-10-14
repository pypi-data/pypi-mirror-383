# MIT License
# Copyright (c) 2025 tveronesi+imdbinfo@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re
from typing import Optional, Dict, Union, List
from functools import lru_cache
from time import time
import logging
import niquests
import json
from lxml import html

from .models import (
    SearchResult,
    MovieDetail,
    SeasonEpisodesList,
    PersonDetail,
    AkasData,
)
from .parsers import (
    parse_json_movie,
    parse_json_search,
    parse_json_person_detail,
    parse_json_season_episodes,
    parse_json_bulked_episodes,
    parse_json_akas,
    parse_json_trivia,
    parse_json_reviews,
    parse_json_filmography,
)
from .locale import _retrieve_url_lang

logger = logging.getLogger(__name__)


def normalize_imdb_id(imdb_id: str, locale: Optional[str] = None):
    imdb_id = str(imdb_id)
    num = int(re.sub(r"\D", "", imdb_id))
    lang = _retrieve_url_lang(locale)
    imdb_id = f"{num:07d}"
    return imdb_id, lang


@lru_cache(maxsize=128)
def get_movie(imdb_id: str, locale: Optional[str] = None) -> Optional[MovieDetail]:
    """Fetch movie details from IMDb using the provided IMDb ID as string,
    preserve the 'tt' prefix or not, it will be stripped in the function.
    """
    imdb_id, lang = normalize_imdb_id(imdb_id, locale)
    url = f"https://www.imdb.com/{lang}/title/tt{imdb_id}/reference"
    logger.info("Fetching movie %s", imdb_id)
    resp = niquests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if resp.status_code != 200:
        logger.error("Error fetching %s: %s", url, resp.status_code)
        raise Exception(f"Error fetching {url}")
    tree = html.fromstring(resp.content or b"")
    script = tree.xpath('//script[@id="__NEXT_DATA__"]/text()')
    if not script or type(script) is not list:
        logger.error("No script found with id '__NEXT_DATA__'")
        raise Exception("No script found with id '__NEXT_DATA__'")

    raw_json = json.loads(str(script[0]))
    movie = parse_json_movie(raw_json)
    logger.debug("Fetched url %s", url)
    return movie


@lru_cache(maxsize=128)
def search_title(title: str, locale: Optional[str] = None) -> Optional[SearchResult]:
    """Search for a movie by title and return a list of titles and names."""
    lang = _retrieve_url_lang(locale)
    url = f"https://www.imdb.com/{lang}/find?q={title}&ref_=nv_sr_sm"
    logger.info("Searching for title '%s'", title)
    resp = niquests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if resp.status_code != 200:
        logger.warning("Search request failed: %s", resp.status_code)
        return None
    tree = html.fromstring(resp.content or b"")
    script = tree.xpath('//script[@id="__NEXT_DATA__"]/text()')
    if not script or type(script) is not list:  # throw if no script found
        logger.error("No script found with id '__NEXT_DATA__'")
        raise Exception("No script found with id '__NEXT_DATA__'")
    # if script is not indexeable throw
    if len(script) == 0:
        logger.error("No script found with id '__NEXT_DATA__'")
        raise Exception("No script found with id '__NEXT_DATA__'")
    raw_json = json.loads(str(script[0]))

    result = parse_json_search(raw_json)
    logger.debug("Search for '%s' returned %s titles", title, len(result.titles))
    return result


@lru_cache(maxsize=128)
def get_name(person_id: str, locale: Optional[str] = None) -> Optional[PersonDetail]:
    """Fetch person details from IMDb using the provided IMDb ID.
    Preserve the 'nm' prefix or not, it will be stripped in the function.
    """
    person_id, lang = normalize_imdb_id(person_id, locale)
    url = f"https://www.imdb.com/{lang}/name/nm{person_id}/"
    logger.info("Fetching person %s", person_id)
    t0 = time()
    resp = niquests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    t1 = time()
    logger.debug("Fetched person %s in %.2f seconds", person_id, t1 - t0)
    if resp.status_code != 200:
        logger.error("Error fetching %s: %s", url, resp.status_code)
        raise Exception(f"Error fetching {url}")
    tree = html.fromstring(resp.content or b"")
    script = tree.xpath('//script[@id="__NEXT_DATA__"]/text()')
    if not script or type(script) is not list:
        logger.error("No script found with id '__NEXT_DATA__'")
        raise Exception("No script found with id '__NEXT_DATA__'")
    t0 = time()
    raw_json = json.loads(str(script[0]))
    person = parse_json_person_detail(raw_json)
    t1 = time()
    logger.debug("Parsed person %s in %.2f seconds", person_id, t1 - t0)
    return person


@lru_cache(maxsize=128)
def get_season_episodes(
    imdb_id: str, season=1, locale: Optional[str] = None
) -> SeasonEpisodesList:
    """Fetch episodes for a movie or series using the provided IMDb ID."""
    imdb_id, lang = normalize_imdb_id(imdb_id, locale)
    url = f"https://www.imdb.com/{lang}/title/tt{imdb_id}/episodes/?season={season}"
    logger.info("Fetching episodes for movie %s", imdb_id)
    resp = niquests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if resp.status_code != 200:
        logger.error("Error fetching %s: %s", url, resp.status_code)
        raise Exception(f"Error fetching {url}")
    tree = html.fromstring(resp.content or b"")
    script = tree.xpath('//script[@id="__NEXT_DATA__"]/text()')
    if not script or type(script) is not list:
        logger.error("No script found with id '__NEXT_DATA__'")
        raise Exception("No script found with id '__NEXT_DATA__'")
    raw_json = json.loads(str(script[0]))
    episodes = parse_json_season_episodes(raw_json)
    logger.debug("Fetched %d episodes for movie %s", len(episodes.episodes), imdb_id)
    return episodes


@lru_cache(maxsize=128)
def get_all_episodes(imdb_id: str, locale: Optional[str] = None):
    series_id, lang = normalize_imdb_id(imdb_id, locale)
    url = f"https://www.imdb.com/{lang}/search/title/?count=250&series=tt{series_id}&sort=release_date,asc"
    logger.info("Fetching bulk episodes for series %s", imdb_id)
    resp = niquests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if resp.status_code != 200:
        logger.error("Error fetching %s: %s", url, resp.status_code)
        raise Exception(f"Error fetching {url}")
    tree = html.fromstring(resp.content or b"")
    script = tree.xpath('//script[@id="__NEXT_DATA__"]/text()')
    if not script or type(script) is not list:
        logger.error("No script found with id '__NEXT_DATA__'")
        raise Exception("No script found with id '__NEXT_DATA__'")
    raw_json = json.loads(str(script[0]))
    episodes = parse_json_bulked_episodes(raw_json)
    logger.debug("Fetched %d episodes for series %s", len(episodes), imdb_id)
    return episodes


@lru_cache(maxsize=128)
def get_episodes(
    imdb_id: str, season=1, locale: Optional[str] = None
) -> SeasonEpisodesList:
    """wrap until deprecation : use get_season_episodes instead for seasons
    or get_all_episodes for all episodes
    """
    logger.warning(
        "get_episodes is deprecating, use get_season_episodes or get_all_episodes instead."
    )
    return get_season_episodes(imdb_id, season, locale)


def get_akas(imdb_id: str) -> Union[AkasData, list]:
    imdb_id, _ = normalize_imdb_id(imdb_id)
    raw_json = _get_extended_title_info(imdb_id)
    if not raw_json:
        logger.warning("No AKAs found for title %s", imdb_id)
        return []
    akas = parse_json_akas(raw_json)
    logger.debug("Fetched %d AKAs for title %s", len(akas), imdb_id)
    return akas


def get_all_interests(imdb_id: str):
    """
        Fetch all 'interests' for a title using the provided IMDb ID.

    In the context of IMDb data, 'interests' are thematic tags, topics, or metadata associated with a title,
    such as genres, themes, or other descriptors that go beyond the standard genre classification.
    These interests are extracted from the extended title information returned by IMDb's GraphQL API.

    Note: This function makes an additional request to IMDb's GraphQL endpoint, which may be slower and
    more resource-intensive than standard API calls. Use this function only if you require interests
    beyond what is available in movie.genres, as it can impact performance.
    """
    imdb_id, _ = normalize_imdb_id(imdb_id)
    raw_json = _get_extended_title_info(imdb_id)
    if not raw_json:
        logger.warning("No interests found for title %s", imdb_id)
        return []
    interests = []
    interests_edges = raw_json.get("interests", {}).get("edges", [])
    for edge in interests_edges:
        node = edge.get("node", {})
        primary_text = node.get("primaryText", {}).get("text", "")
        if primary_text:
            interests.append(primary_text)
    logger.debug("Fetched %d interests for title %s", len(interests), imdb_id)
    return interests


def get_trivia(imdb_id: str) -> List[Dict]:
    imdb_id, _ = normalize_imdb_id(imdb_id)
    raw_json = _get_extended_title_info(imdb_id)
    if not raw_json:
        logger.warning("No trivia found for title %s", imdb_id)
        return []
    trivia_list = parse_json_trivia(raw_json)
    logger.debug("Fetched %d trivia items for title %s", len(trivia_list), imdb_id)
    return trivia_list


def get_reviews(imdb_id: str) -> List[Dict]:
    imdb_id, _ = normalize_imdb_id(imdb_id)
    raw_json = _get_extended_title_info(imdb_id)
    if not raw_json:
        logger.warning("No reviews found for title %s", imdb_id)
        return []
    reviews_list = parse_json_reviews(raw_json)
    logger.debug("Fetched %d reviews for title %s", len(reviews_list), imdb_id)
    return reviews_list


@lru_cache(maxsize=128)
def _get_extended_title_info(imdb_id) -> dict:
    """
    Fetch extended info (like AKAs) using IMDb's GraphQL API.
    """
    imdbId = "tt" + imdb_id
    url = "https://api.graphql.imdb.com/"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
    }
    query = (
        """
    query {
      title(id: "%s") {
        id
        titleText {
          text
        }
        originalTitle: originalTitleText {
          text
        }
          interests(first:20){
            edges{node{primaryText{text}}}
       }
        akas(first: 200) {
          edges {
            node {
              country { name: text code: id }
              language { name: text code: id }
              title: text
            }
          }
        }
         trivia(first: 50) {
      edges {
        node {
          id
          displayableArticle {
            body {
              plaidHtml
            }
          }
          interestScore {
            usersVoted
            usersInterested
          }
        }
      }
    }
    reviews(first: 50) {
      edges {
        node {
          id
          spoiler
          author {
            nickName
          }
          summary {
            originalText
          }
          text {
            originalText {
              plaidHtml
            }
          }
          authorRating
          submissionDate
          helpfulness {
            upVotes
            downVotes
          }
          __typename
        }
      }
    }
      }
    }
    """
        % imdbId
    )
    payload = {"query": query}
    logger.info("Fetching title %s from GraphQL API", imdb_id)
    resp = niquests.post(url, headers=headers, json=payload)
    if resp.status_code != 200:
        logger.error("GraphQL request failed: %s", resp.status_code)
        raise Exception(f"GraphQL request failed: {resp.status_code}")
    data = resp.json()
    if "errors" in data:
        logger.error("GraphQL error: %s", data["errors"])
        raise Exception(f"GraphQL error: {data['errors']}")
    raw_json = data.get("data", {}).get("title", {})
    return raw_json


def get_filmography(imdb_id) -> dict:
    """
    Fetch full filmography for a person using the provided IMDb ID.
    """
    imdb_id, _ = normalize_imdb_id(imdb_id)
    raw_json = _get_extended_name_info(imdb_id)
    if not raw_json:
        logger.warning("No full_credit found for name %s", imdb_id)
        return []
    full_credits_list = parse_json_filmography(raw_json)
    logger.debug("Fetched full_credits for name %s", imdb_id)
    return full_credits_list


def _get_extended_name_info(person_id) -> dict:
    """
    Fetch extended person info using IMDb's GraphQL API.
    """
    person_id = "nm" + person_id

    query = (
        """
        query {
          name(id: "%s") {
            nameText {
              text
            }
        
            credits(first: 250
            filter: {
        categories: [
          "production_designer"
          "casting_department"
          "director"
          "composer"
          "casting_director"
          "executive"
          "art_director"
          "actress"
          "costume_designer"
          "writer"
          "camera_department"
          "art_department"
          "publicist"
          "cinematographer"
          "location_management"
          "soundtrack"
          "sound_department"
          "talent_agent"
          "set_decorator"
          "animation_department"
          "make_up_department"
          "costume_department"
          "script_department"
          "producer"
          "stunts"
          "editor"        
          "stunt_coordinator"
          "special_effects"
          "assistant_director"
          "editorial_department"
          "music_department"
          "transportation_department"
          "actor"
          "visual_effects"
          "production_manager"
          "production_designer"
          "casting_department"
          "director"
          "composer"        
          "archive_sound"
          "casting_director"
          "art_director"
        ]
      }
            ) 
           
            {
              edges {
                node {
                  category {
                    id
                  }
        
                  title {
                    id
                    primaryImage {
                      url
                    }
                    #certificate {rating}
                    originalTitleText {
                      text
                    }
                    titleText {
                      text
                    }
                    titleType {
                      #text
                      id
                    }
                    releaseYear {
                      year
                    }
                  }
                }
              }
        
              pageInfo {
                endCursor
                hasNextPage
              }
            }
          }
        }

    """
        % person_id
    )
    url = "https://api.graphql.imdb.com/"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
    }
    payload = {"query": query}
    logger.info("Fetching person %s from GraphQL API", person_id)
    resp = niquests.post(url, headers=headers, json=payload)
    if resp.status_code != 200:
        logger.error("GraphQL request failed: %s", resp.status_code)
        raise Exception(f"GraphQL request failed: {resp.status_code}")
    data = resp.json()
    if "errors" in data:
        logger.error("GraphQL error: %s", data["errors"])
        raise Exception(f"GraphQL error: {data['errors']}")
    raw_json = data.get("data", {}).get("name", {})
    return raw_json
