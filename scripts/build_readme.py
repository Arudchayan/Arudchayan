#!/usr/bin/env python3
import json, os, datetime, random, re

ROYAL = "#6A0DAD"

def pick_index(n):
    # deterministic by date: different one each day
    today = datetime.datetime.utcnow().date().toordinal()
    return today % n

root = os.path.dirname(os.path.dirname(__file__))
with open(os.path.join(root, "data", "archetypes.json")) as f:
    arc = json.load(f)

idx = pick_index(len(arc))
chosen = arc[idx]

with open(os.path.join(root, "README.template.md")) as f:
    t = f.read()

mega_info = chosen.get("mega") or "—"
zmove_info = chosen.get("z_move") or "—"
tera_type = chosen.get("tera_type") or "—"

# Inject archetype panel
panel = []
panel.append(f"**Archetype:** {chosen['title']}  ")
panel.append(f"**Lead:** {chosen['lead']}")
panel.append("**Team:** " + ", ".join(chosen["team"]))
panel_text = "\n".join(panel)

t = re.sub(r"<!-- CURRENT_ARCHETYPE_START -->.*?<!-- CURRENT_ARCHETYPE_END -->",
           f"<!-- CURRENT_ARCHETYPE_START -->\n{panel_text}\n<!-- CURRENT_ARCHETYPE_END -->",
           t, flags=re.S)

t = t.replace("{{MEGA_INFO}}", mega_info)
t = t.replace("{{ZMOVE_INFO}}", zmove_info)
t = t.replace("{{TERA_TYPE}}", tera_type)

with open(os.path.join(root, "README.md"), "w") as f:
    f.write(t)
print("Built README for:", chosen["id"])
