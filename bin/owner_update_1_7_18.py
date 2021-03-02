#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import argparse
import json
import copy
import urllib.request
import urllib.parse

SCHEME_LOCALUNIT = "personium-localunit"
UNIT_PREFIX = "u0"
CATEGORY_AD = "ad"
CELL_INDEX = f"{UNIT_PREFIX}_{CATEGORY_AD}.cell"


def convert_old_normalized_uri(uri):
    """
    Function for converting old-style localunit shema url to current-style.
    Before v1.7.17, normalized URI is created by
    replacing path-based URL's schema with `personium-localunit:/`
    """
    UNIT_URL_DUMMY = "https://impossibleurl.example.com/"
    SCHEME_UNIT_URL_OLD = "personium-localunit:/"

    # uri is not old normalized style
    if not uri.startswith(SCHEME_UNIT_URL_OLD):
        return None

    path_based_url = re.sub(f"^{SCHEME_UNIT_URL_OLD}", UNIT_URL_DUMMY, uri)
    if not re.match(f"^{UNIT_URL_DUMMY}([^/?&#]*)/?", path_based_url):
        return None

    return convert_scheme_http_to_localunit(path_based_url, UNIT_URL_DUMMY, True)


def convert_scheme_http_to_localunit(uri, unit_url, path_based):
    """
    Function for scheme conversion from http(s) to localunit
    """
    if uri is None:
        return None

    if path_based is True:
        # it is not localunit
        if not uri.startswith(unit_url):
            return uri
    else:
        raise NotImplementedError("non path-based url is not supported")

    result = re.sub(r":/(?P<cell>[^/?&#]*)/?", r":\g<cell>:/",
                    uri.replace(unit_url, f"{SCHEME_LOCALUNIT}:/"))
    return result


def main():
    """
    main function of this script
    """
    parser = argparse.ArgumentParser(
        description="Update entities in ElasticSearch")
    parser.add_argument("host", metavar="host", type=str,
                        help="elasticsearch host (ex: es.example.com)")
    parser.add_argument("--port", default=9200,
                        help="elasticsearch port (default: 9200)")

    args = parser.parse_args()

    node_url = f"http://{args.host}:{args.port}"
    search_url = f"{node_url}/{CELL_INDEX}/_search"
    req = urllib.request.Request(search_url)

    num_cells = 0
    cells_per_request = 10

    with urllib.request.urlopen(req) as res:
        body = res.read()
        body_json = json.loads(body)

        num_cells = body_json['hits']['total']

    print(f"total {num_cells} cells found")
    list_cells = []

    for i in range(0, num_cells // cells_per_request + 1):
        search_query = urllib.parse.urlencode({
            "size": cells_per_request,
            "from": i * cells_per_request,
            "sort": "_id:asc"
        })
        req = urllib.request.Request(f"{search_url}?{search_query}")
        with urllib.request.urlopen(req) as res:
            body = res.read()
            body_json = json.loads(body)
            list_cells += body_json['hits']['hits']

    print(f"fetched {len(list_cells)} docs")
    updated_cells = []

    for i in list_cells:
        hidden_json = copy.deepcopy(i['_source']['h'])
        new_owner = convert_old_normalized_uri(hidden_json['Owner'])
        if new_owner is None:
            continue

        hidden_json['Owner'] = new_owner
        update_query = urllib.parse.urlencode({
            "routing": i['_routing'],
        })
        update_body = json.dumps({
            "doc": {
                "h": hidden_json
            }
        }).encode("utf-8")
        update_url = f"{node_url}/{CELL_INDEX}/{i['_type']}/{i['_id']}/_update?{update_query}"
        headers = {
            "Content-Type": "application/json"
        }

        req = urllib.request.Request(
            update_url, update_body, headers, method="POST")

        try:
            with urllib.request.urlopen(req) as res:
                body = res.read()
        except urllib.error.HTTPError as err:
            print(err.code)
            print(err.reason)
            print(err.read())

        result = [{
            "_id": i['_id'],
            "from": i['_source']['h']['Owner'],
            "to": new_owner
        }]
        updated_cells += result

    print(f"total {len(updated_cells)} cells updated")

    refresh_url = f"{node_url}/{CELL_INDEX}/_refresh"
    req = urllib.request.Request(refresh_url)

    print(f"refreshing elasticsearch index: {CELL_INDEX}")
    try:
        with urllib.request.urlopen(req) as res:
            body = res.read()
    except urllib.error.URLError as err:
        print(err)


if __name__ == '__main__':
    main()
