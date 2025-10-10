import json
from pathlib import Path

import httpx
from rdflib import Graph, Dataset

from kurra.db import sparql
from kurra.utils import load_graph


def query(
    p: Path | str | Graph | Dataset,
    q: str,
    http_client: httpx.Client = None,
    return_python: bool = False,
    return_bindings_only: bool = False,
):
    if "CONSTRUCT" in q or "DESCRIBE" in q:
        if isinstance(p, str) and p.startswith("http"):
            if http_client is None:
                http_client = httpx.Client()

            headers = {
                "Content-Type": "application/sparql-query",
                "Accept": "text/turtle"
            }
            r = http_client.post(p, content=q, headers=headers)

            return Graph().parse(data=r.text, format="turtle")

        if isinstance(p, str) and not p.startswith("http"):
            # parse it and handle it as a Graph
            p = load_graph(p)

        if isinstance(p, Path):
            p = load_graph(p)

        # if we are here, path_str_graph_or_sparql_endpoint is a Graph
        r = p.query(q)
        return r.graph
    elif "INSERT" in q or "DELETE" in q:
        raise NotImplementedError("INSERT & DELETE queries are not yet implemented by this interface. Try kurra.db.sparql")

    elif "DROP" in q:
        if isinstance(p, str) and p.startswith("http"):
            r = sparql(p, q, http_client, True, False)

            if r == "":
                return ""
        else:
            raise NotImplementedError("DROP commands are not yet implemented for files")

    else:  # SELECT or ASK
        close_http_client = False
        if http_client is None:
            http_client = httpx.Client()
            close_http_client = True

        r = None
        if isinstance(p, str) and p.startswith("http"):
            r = sparql(p, q, http_client, True, False)

        if r is None:
            x = load_graph(p).query(q)
            r = json.loads(x.serialize(format="json"))

        if close_http_client:
            http_client.close()

        match (return_python, return_bindings_only):
            case (True, True):
                if r.get("results") is not None:
                    return r["results"]["bindings"]
                elif r.get("boolean") is not None:  # ASK
                    return r["boolean"]
                else:
                    return r
            case (True, False):
                return r
            case (False, True):
                if r.get("results") is not None:
                    return json.dumps(r["results"]["bindings"])
                elif r.get("boolean") is not None:  # ASK
                    return json.dumps(r["boolean"])
                else:
                    return json.dumps(r)
            case _:
                return json.dumps(r)
