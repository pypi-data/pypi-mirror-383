from alchemistry.cli import register_command
from alchemistry.helpers import levenshtein_sort_list

# this is way worse than the original version
items: dict[tuple[str, str], str] = {('water', 'water'): 'pond', ('pond', 'pond'): 'lake', ('fire', 'earth'): 'lava', ('fire', 'water'): 'steam', ('steam', 'air'): 'cloud', ('earth', 'water'): 'mud', ('air', 'mud'): 'clay', ('cloud', 'cloud'): 'stormcloud', ('steam', 'steam'): 'pressure', ('clay', 'fire'): 'firedclay', ('stormcloud', 'stormcloud'): 'storm', ('earth', 'pressure'): 'earthquake', ('water', 'air'): 'cloud', ('water', 'earthquake'): 'tsunami', ('earth', 'earthquake'): 'disaster', ('water', 'cloud'): 'rain', ('earth', 'steam'): 'geyser', ('rain', 'storm'): 'rainstorm', ('water', 'lava'): 'obsidian', ('lava', 'obsidian'): 'lava', ('earth', 'lava'): 'volcano', ('rain', 'tsunami'): 'flashflood', ('lava', 'geyser'): 'volcano', ('water', 'geyser'): 'hotspring', ('volcano', 'lava'): 'eruption', ('mud', 'fire'): 'brick', ('brick', 'brick'): 'wall', ('wall', 'wall'): 'house', ('house', 'house'): 'village', ('village', 'village'): 'city'}

inventory: list[str] = ["water", "air", "earth", "fire"]


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
	if item1 not in inventory:
		print(f"You don't {item1}!")
		return 0
	if item2 not in inventory:
		print(f"You don't {item2}!")
		return 0
	if (item1, item2) not in items and (item2, item1) not in items:
		print(f"You tried to combine {item1} and {item2} but came up empty-handed.")
		return 0
	if (item1, item2) in items:
		print(f"You merged {item1} and {item2} and got some {items[(item1, item2)]}")
		if items[(item1, item2)] not in inventory:
			inventory.append(items[(item1, item2)])
		else:
			print("But you already had that...")
	elif (item2, item1) in items:
		print(f"You merged {item1} and {item2} and got some {items[(item2, item1)]}")
		if items[(item2, item1)] not in inventory:
			inventory.append(items[(item2, item1)])
		else:
			print("But you already had that...")
	return 0


register_command(
	"combine",
	"Mix your materials",
	"To get anywhere you'll need to make things. Use this to combine your items to get new ones.",
	["The first item", "The second item (order doesn't matter)"],
	combine_command
)
