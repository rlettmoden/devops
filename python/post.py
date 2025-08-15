import re

# Start with # followed by arbitrary many letters, numbers and underscores but at least on of them
TAG_REGEX = r"#[0-9a-zA-Z_]+"

def parse_tags_from_post(post_text: str) -> set[str]:
    """
    Extracts all tags starting with # followed by one or more characters in the set [09azAZ_] from a post

    Args:
        post_text (str): Post to extract the tags from

    Returns:
        set[str]: All the tags (duplicates are removed) occuring in the text
    """       

    # Use regex to effectively find all tags text. re.findall returns an empty list, if no matches are found 
    tags = re.findall(TAG_REGEX, post_text)
    # next, ensure that we have unique tags by removing duplicates
    tags = set(tags)
    # filter out hashtags
    tags = set(tag[1:] for tag in tags)
    return tags

class Post():
    """
    Stores the username, post text, timestamp and tags included in the post 
    """    

    def __init__(self, user_name: str, post_text: str, timestamp: int) -> None:
        """
        Stores the given parameters and parses the tags from the posts

        Args:
            user_name (str): User name of the post
            post_text (str): Content of the post with < 140 characters
            timestamp (int): Timestamp in number of seconds
        """        
        super().__init__()
        self.user_name = user_name
        self.post_text = post_text
        self.timestamp = timestamp

        # extract tags
        self.tags = parse_tags_from_post(post_text)