from src.agent.tools import execute_tool

def run(client, kb, question, scope, max_queries=4):
    from src.agent.decomposer import decompose_question
    sub_queries = decompose_question(client, question, max_queries=max_queries)
    hits = []
    trace = []
    if len(sub_queries) > 1:
        for sq in sub_queries[:5]:
            h = execute_tool("searchChunks", {"query": sq, "top_k": 20}, kb, client, inherited_scope=scope)
            if isinstance(h, list):
                hits.extend(h)
                trace.append({"tool": "searchChunks", "args": {"query": sq}, "decomposed": True})
    return sub_queries, hits, trace
