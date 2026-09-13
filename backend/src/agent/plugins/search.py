from google.genai import types
from src.agent.tools import execute_tool, format_search_observation
from src.agent.fc_client import call_with_tools
from src.agent.prompts import AGENT_SYSTEM_FC

def run_loop(client, kb, question, sub_queries, history_text, scope, max_iterations=4):
    contents = [types.Content(role="user", parts=[types.Part(text=f"سؤال المدرس: {question}\nالاستعلامات الفرعية: {sub_queries}\nالسياق: {history_text[:800]}")])]
    all_hits = []
    file_contents = {}
    trace = []
    for iteration in range(max_iterations):
        resp = call_with_tools(client, contents, AGENT_SYSTEM_FC)
        cand = resp.candidates[0] if resp.candidates else None
        if not cand or not cand.content or not cand.content.parts:
            break
        part = cand.content.parts[0]
        if hasattr(part, "function_call") and part.function_call and part.function_call.name:
            fc = part.function_call
            name = fc.name
            args = dict(fc.args) if fc.args else {}
            trace.append({"tool": name, "args": args})
            result = execute_tool(name, args, kb, client, inherited_scope=scope)
            if isinstance(result, list):
                all_hits.extend(result)
                obs_text = format_search_observation(result, max_hits=8, max_chars=600)
            else:
                file_contents[args.get("path","")] = result
                obs_text = f"محتوى الملف ({len(result)} حرف): {result[:400]}"
            contents.append(cand.content)
            contents.append(types.Content(role="user", parts=[types.Part(function_response=types.FunctionResponse(name=name, response={"result": obs_text[:2000]}))]))
            if len(all_hits) >= 40:
                break
            continue
        else:
            break
    return all_hits, file_contents, trace, contents
