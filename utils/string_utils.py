def sentence_case(name: str) -> str:
    return name.capitalize().replace('_', ' ').replace('-', ' ')