import pathlib
from random import sample

def generate_login(adjective_count: int = 2, noun_count: int = 1) -> str:
    assets = pathlib.Path(__file__).parent.parent.parent.joinpath('assets')
    adjectives = assets.joinpath('adjectives.txt')
    nouns = assets.joinpath('nouns.txt')
    choices = list()
    with open(adjectives, 'r') as adj_file, open(nouns, 'r') as noun_file:
        adj_lines, noun_lines = adj_file.readlines(), noun_file.readlines()
        chosen = sample(adj_lines, adjective_count) + sample(noun_lines, noun_count)
        chosen = [ line.strip() for line in chosen ]
        choices = chosen
    # with open(nouns, 'r') as noun_file:
    #     lines = noun_file.readlines()
    #     chosen = [ line.strip() for line in sample(lines, noun_count) ]
    #     choices.extend(chosen)

    return '-'.join(choices)
    