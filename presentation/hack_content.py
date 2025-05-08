from dataclasses import dataclass

@dataclass
class HackContent:
    """
    Class representing the content of a hack.
    """

    id: int;
    title: str;
    authors: list;
    image_url: str;

    def __init__(self, title: str, authors: list, image_url: str = None, id: int = None):
        self.title = title
        self.authors = authors
        self.image_url = image_url
        self.id = id

    def __str__(self):
        return f"{self.title} by {', '.join(self.authors)}"

    def author_as_string(self):
        return ", ".join(self.authors)

def map_hack_content(hack) -> HackContent:
    """
    Map a hack object to HackContent.
    """

    return HackContent(
        title=hack["name"],
        authors=[author["name"] for author in hack["authors"]],
        image_url=hack["images"][0],
        id=hack["id"]
    );