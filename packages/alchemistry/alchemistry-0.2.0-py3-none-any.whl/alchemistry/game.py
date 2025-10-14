from alchemistry.cli import register_command
import requests
import re

inventory: set[str] = {"water", "air", "earth", "fire"}


def inventory_command() -> int:
	for material in inventory:
		print(f"{material}")

	return 0

register_command(
	"items",
	"See what items you have unlocked.",
	"This should help you mix up some new things",
	None,
	inventory_command
)


def combine_command(item1, item2) -> int:
	if item1 in inventory and item2 in inventory:
		response = requests.post(
			"https://ai.hackclub.com/chat/completions",
			headers={"Content-Type": "application/json"},
			json={
				"messages": [
					{"role": "system",
					 "content": "You are a machine that takes in two items, and combines them into a "
					 "representative merger of those two items. For example, water and water makes a "
					 "pond, or fire and earth makes lava, and lava and water makes stone. When "
					 "responding, respond with one single word, which is the outcome of the combination."},
					{"role": "user", "content": f"I combine {item1} and {item2}"}
				]
			}
		)

		content: str = response.json()["choices"][0]["message"]["content"]
		content = re.sub(r'[^a-z]', '', content.split("\n")[-1].lower())
		print(f"You combined {item1} and {item2} and got {content}")
		inventory.add(content)
	elif item1 not in inventory:
		print(f"You don't have {item1}!")
	elif item2 not in inventory:
		print(f"You don't have {item2}!")

	return 0


register_command(
	"combine",
	"Mix your materials",
	"To get anywhere you'll need to make things. Use this to combine your items to get new ones.",
	["The first item", "The second item (order doesn't matter)"],
	combine_command
)
