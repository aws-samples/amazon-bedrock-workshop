from typing import Any
from defusedxml import ElementTree
from collections import defaultdict
import tools


def call_function(tool_name, parameters):
    func = getattr(tools, tool_name)
    output = func(**parameters)
    return output


def format_result(tool_name, output):
    return f"""
<function_results>
<result>
<tool_name>{tool_name}</tool_name>
<stdout>
{output}
</stdout>
</result>
</function_results>
"""


def etree_to_dict(t) -> dict[str, Any]:
    d = {t.tag: {}}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(("@" + k, v) for k, v in t.attrib.items())
    if t.text and t.text.strip():
        if children or t.attrib:
            d[t.tag]["#text"] = t.text
        else:
            d[t.tag] = t.text
    return d
