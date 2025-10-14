import random

items = {"water", "earth", "air", "fire"}

recipes = {('water', 'water'): 'pond', ('pond', 'pond'): 'lake', ('fire', 'earth'): 'lava', ('fire', 'water'): 'steam', ('steam', 'air'): 'cloud', ('earth', 'water'): 'mud', ('air', 'mud'): 'clay', ('cloud', 'cloud'): 'stormcloud', ('steam', 'steam'): 'pressure', ('clay', 'fire'): 'firedclay', ('stormcloud', 'stormcloud'): 'storm', ('earth', 'pressure'): 'earthquake', ('water', 'air'): 'cloud', ('water', 'earthquake'): 'tsunami', ('earth', 'earthquake'): 'disaster', ('water', 'cloud'): 'rain', ('earth', 'steam'): 'geyser', ('rain', 'storm'): 'rainstorm', ('water', 'lava'): 'obsidian', ('lava', 'obsidian'): 'lava'}

rejects = []

for i in recipes.values():
	items.add(i)
try:
	while True:
		item1 = random.choice(list(items))
		item2 = random.choice(list(items))

		if (item1, item2) not in recipes and (item1, item2) not in rejects and (item2, item1) not in recipes and (item2, item1) not in rejects:
			item = input(f"The combination of {item1} and {item2} should be: ").strip()
			if item != "":
				items.add(item)
				recipes[(item1, item2)] = item
			else:
				rejects.append((item1, item2))
				rejects.append((item2, item1))

except KeyboardInterrupt:
	print("\n")
	print(recipes)