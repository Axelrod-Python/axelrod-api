import axelrod as axl

me = axl.Human(name='me')

players = (axl.TitForTat(), me)
match = axl.Match(players, turns=3)

result = match.play()
print(result)
