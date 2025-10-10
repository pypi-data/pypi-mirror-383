import json
from pathlib import Path

import httpx
import pytest

from rdflib import Dataset

from kurra.db import upload, clear_graph
from kurra.sparql import query
from kurra.utils import RenderFormat, render_sparql_result, make_httpx_client

LANG_TEST_VOC = Path(__file__).parent / "language-test.ttl"
TESTING_GRAPH = "https://example.com/testing-graph"


def test_query_db(fuseki_container, http_client):
    port = fuseki_container.get_exposed_port(3030)

    SPARQL_ENDPOINT = f"http://localhost:{port}/ds"
    TESTING_GRAPH = "https://example.com/testing-graph"
    upload(SPARQL_ENDPOINT, LANG_TEST_VOC, TESTING_GRAPH, False, http_client)

    q = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#> 
        SELECT * 
        WHERE { 
            GRAPH ?g {
                ?c a skos:Concept .
            } 
        }"""

    assert "--- | ---" in render_sparql_result(query(SPARQL_ENDPOINT, q, http_client))

    assert (
        "c"
        in json.loads(
            (
                render_sparql_result(
                    query(SPARQL_ENDPOINT, q, http_client), RenderFormat.json
                )
            )
        )["head"]["vars"]
    )

    # test return format options

    q = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#> 
        SELECT * 
        WHERE {
            GRAPH ?g {
                ?c a skos:Concept ;
                    skos:prefLabel "English only"@en ;
                .
            }
        }"""

    r = query(
        SPARQL_ENDPOINT, q, http_client, return_python=True, return_bindings_only=True
    )
    assert r[0]["c"]["value"] == "https://example.com/demo-vocabs/language-test/en-only"

    r = query(
        SPARQL_ENDPOINT, q, http_client, return_python=True, return_bindings_only=False
    )
    assert (
        r["results"]["bindings"][0]["c"]["value"]
        == "https://example.com/demo-vocabs/language-test/en-only"
    )

    r = query(
        SPARQL_ENDPOINT, q, http_client, return_python=False, return_bindings_only=False
    )
    assert isinstance(r, str)
    r2 = json.loads(r)
    assert (
        r2["results"]["bindings"][0]["c"]["value"]
        == "https://example.com/demo-vocabs/language-test/en-only"
    )

    r = query(
        SPARQL_ENDPOINT, q, http_client, return_python=False, return_bindings_only=True
    )
    assert isinstance(r, str)
    r2 = json.loads(r)
    assert (
        r2[0]["c"]["value"] == "https://example.com/demo-vocabs/language-test/en-only"
    )

    q = "ASK {?s ?p ?o}"
    r = query(SPARQL_ENDPOINT, q, http_client)  # False, False
    assert r == '{"head": {}, "boolean": true}'

    q = "ASK {?s ?p ?o}"
    r = query(SPARQL_ENDPOINT, q, http_client, return_python=True)
    assert r["boolean"]

    q = "ASK {?s ?p ?o}"
    r = query(
        SPARQL_ENDPOINT, q, http_client, return_python=True, return_bindings_only=True
    )
    assert r

    q = "ASK {?s ?p ?o}"
    r = query(SPARQL_ENDPOINT, q, http_client, return_bindings_only=True)
    assert r == "true"

    q = "ASK {?s ?p <http://nothing.com/x>}"
    r = query(
        SPARQL_ENDPOINT, q, http_client, return_python=True, return_bindings_only=True
    )
    assert not r


def test_query_file():
    q = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#> 
        SELECT * 
        WHERE {
            ?c a skos:Concept ;
                skos:prefLabel ?pl ;
            .
            
            OPTIONAL {
                ?c skos:altLabel ?al .
            }
        }
        LIMIT 3"""

    assert "--- | --- | ---" in render_sparql_result(query(LANG_TEST_VOC, q))

    assert (
        "pl"
        in json.loads(render_sparql_result(query(LANG_TEST_VOC, q), RenderFormat.json))[
            "head"
        ]["vars"]
    )

    # test return format options

    q = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#> 
        SELECT * 
        WHERE {
            ?c a skos:Concept ;
                skos:prefLabel ?pl ;
            .

            OPTIONAL {
                ?c skos:altLabel ?al .
            }
        }
        LIMIT 3"""

    r = query(LANG_TEST_VOC, q, return_python=True, return_bindings_only=True)
    assert r[0]["c"]["value"] == "https://example.com/demo-vocabs/language-test/en-only"

    r = query(LANG_TEST_VOC, q, return_python=True, return_bindings_only=False)
    assert (
        r["results"]["bindings"][0]["c"]["value"]
        == "https://example.com/demo-vocabs/language-test/en-only"
    )

    r = query(LANG_TEST_VOC, q, return_python=False, return_bindings_only=False)
    assert isinstance(r, str)
    r2 = json.loads(r)
    assert (
        r2["results"]["bindings"][0]["c"]["value"]
        == "https://example.com/demo-vocabs/language-test/en-only"
    )

    r = query(LANG_TEST_VOC, q, return_python=False, return_bindings_only=True)
    assert isinstance(r, str)
    r2 = json.loads(r)
    assert (
        r2[0]["c"]["value"] == "https://example.com/demo-vocabs/language-test/en-only"
    )

    q = "ASK {?s ?p ?o}"
    r = query(LANG_TEST_VOC, q)  # False, False
    assert r == '{"head": {}, "boolean": true}'

    q = "ASK {?s ?p ?o}"
    r = query(LANG_TEST_VOC, q, return_python=True)
    assert r["boolean"]

    q = "ASK {?s ?p ?o}"
    r = query(LANG_TEST_VOC, q, return_python=True, return_bindings_only=True)
    assert r

    q = "ASK {?s ?p ?o}"
    r = query(LANG_TEST_VOC, q, return_bindings_only=True)
    assert r == "true"

    q = "ASK {?s ?p <http://nothing.com/x>}"
    r = query(LANG_TEST_VOC, q, return_python=True, return_bindings_only=True)
    assert not r


def test_duplicates():
    rdf_data = """
    PREFIX people: <https://linked.data.gov.au/dataset/people/>
    PREFIX schema: <https://schema.org/>

    people:nick
        a
            schema:Person , 
            schema:Patient ;
        schema:name "Nick" ;
        schema:age 42 ;
        schema:parent people:george ;
    .

    people:george
        a schema:Person ; 
        schema:name "George" ;
        schema:age 70 ;    
    .
    """

    q = """
    PREFIX people: <https://linked.data.gov.au/dataset/people/>
    PREFIX schema: <https://schema.org/>

    SELECT ?p ?name
    WHERE {
        ?p 
            a schema:Person ;
            schema:name ?name ;
            schema:age ?age ;
        .

        FILTER (?age < 50)
    }
    """

    assert len(query(rdf_data, q, return_python=True, return_bindings_only=True)) == 1


def test_auth(fuseki_container, http_client):
    SPARQL_ENDPOINT = f"http://localhost:{fuseki_container.get_exposed_port(3030)}/ds"

    upload(SPARQL_ENDPOINT, LANG_TEST_VOC, TESTING_GRAPH, False, http_client)

    q = "ASK {?s ?p ?o}"
    r = query(
        SPARQL_ENDPOINT, q, http_client, return_python=True, return_bindings_only=True
    )
    assert r

    with pytest.raises(RuntimeError):
        query(
            SPARQL_ENDPOINT, q, None, return_python=True, return_bindings_only=True
        )


def test_construct(fuseki_container, http_client):
    SPARQL_ENDPOINT = f"http://localhost:{fuseki_container.get_exposed_port(3030)}/ds"

    upload(SPARQL_ENDPOINT, LANG_TEST_VOC, TESTING_GRAPH, False, http_client)

    q = """
        CONSTRUCT { ?s ?p ?o }
        WHERE {
            GRAPH ?g {
                ?s ?p ?o
            }
        }
        LIMIT 3       
        """

    r = query(SPARQL_ENDPOINT, q, http_client)
    assert len(r) == 3


def test_insert(fuseki_container, http_client):
    SPARQL_ENDPOINT = f"http://localhost:{fuseki_container.get_exposed_port(3030)}/ds"

    upload(SPARQL_ENDPOINT, LANG_TEST_VOC, TESTING_GRAPH, False, http_client)

    q = """
        INSERT { ?s ?p ?o }
        WHERE {
            GRAPH ?g {
                ?s ?p ?o
            }
        }
        LIMIT 3       
        """

    with pytest.raises(NotImplementedError):
        r = query(SPARQL_ENDPOINT, q, http_client)


def test_204_response(fuseki_container, http_client):
    # DROP data from SPARQL Endpoint
    SPARQL_ENDPOINT = f"http://localhost:{fuseki_container.get_exposed_port(3030)}/ds"

    upload(SPARQL_ENDPOINT, LANG_TEST_VOC, TESTING_GRAPH, False, http_client)
    r = query(SPARQL_ENDPOINT, "DROP ALL", http_client=httpx.Client(auth=("admin", "admin")), return_python=True, return_bindings_only=True)
    assert r == ""

    # DROP data from a file
    with pytest.raises(NotImplementedError):
        query(Path(__file__).parent / "vocab.nq", "DROP ALL", return_python=True, return_bindings_only=True)

    # DROP no data
    clear_graph(SPARQL_ENDPOINT, "all", http_client)
    r = query(SPARQL_ENDPOINT, "DROP ALL", http_client=httpx.Client(auth=("admin", "admin")), return_python=True, return_bindings_only=True)
    assert r == ""


def test_describe(fuseki_container, http_client):
    # DROP data from SPARQL Endpoint
    SPARQL_ENDPOINT = f"http://localhost:{fuseki_container.get_exposed_port(3030)}/ds"

    query(SPARQL_ENDPOINT, "DROP ALL", http_client=http_client)
    upload(SPARQL_ENDPOINT, LANG_TEST_VOC, TESTING_GRAPH, False, http_client)

    g = query(SPARQL_ENDPOINT, "DESCRIBE <https://example.com/demo-vocabs/language-test>", http_client=http_client)
    # print(g.serialize(format="longturtle"))
    assert len(g) == 16