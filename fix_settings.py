import json
import os

path = os.path.expanduser("~/Library/Application Support/Antigravity IDE/User/settings.json")
with open(path, "r") as f:
    data = json.load(f)

changed = False

if "antigravity" in data and "ai" in data["antigravity"] and "customProviders" in data["antigravity"]["ai"]:
    providers = data["antigravity"]["ai"]["customProviders"]
    data["antigravity.ai.customModels"] = providers
    del data["antigravity"]["ai"]["customProviders"]
    if not data["antigravity"]["ai"]:
        del data["antigravity"]["ai"]
    if not data["antigravity"]:
        del data["antigravity"]
    changed = True

if "antigravity.ai.customProviders" in data:
    data["antigravity.ai.customModels"] = data["antigravity.ai.customProviders"]
    del data["antigravity.ai.customProviders"]
    changed = True

if changed:
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    print("Settings successfully migrated to flat key.")
else:
    print("Settings format already looks correct.")
