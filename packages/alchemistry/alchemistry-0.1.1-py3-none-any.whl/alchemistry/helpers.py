def levenshtein_distance(s: str, t: str) -> int:
	m, n = len(s), len(t)

	v0 = list(range(n + 1))
	v1 = [0 for _ in range(n + 1)]

	for i in range(m):
		v1[0] = i + 1

		for j in range(n):
			del_cost = v0[j + 1] + 1
			ins_cost = v1[j] + 1
			sub_cost = v0[j] if s[i] == t[j] else v0[j] + 1

			v1[j + 1] = min(del_cost, ins_cost, sub_cost)

		v0, v1 = v1, v0

	return v0[n]

def levenshtein_sort_list(comp: str, items: list[str]) -> list[tuple[int, int]]:
	return sorted(enumerate(map(lambda x: levenshtein_distance(x, comp), items)), key=lambda x: x[1])