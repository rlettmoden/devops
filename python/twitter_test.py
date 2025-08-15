import unittest
from python.twitter_fast_retrieval import TwitterFastRetrieval, MAX_POST_LENGTH
from post import parse_tags_from_post


class TestTwitterFastRetrieval(unittest.TestCase):
    def setUp(self) -> None:
        self.service = TwitterFastRetrieval()

    def test_add_user(self):
        # Add a new user and check that there no posts created yet
        self.service.add_user("john")
        posts = self.service.get_posts_for_user("john")
        self.assertEqual(posts, [])

    def test_duplicate_user(self):
        # Adding the same user should raise a ValueError
        self.service.add_user("duplicate")
        with self.assertRaises(ValueError):
            self.service.add_user("duplicate")

    def test_add_post_user_not_exist(self):
        # Adding a post for a non-registered user should raise a ValueError
        with self.assertRaises(ValueError):
            self.service.add_post("nonexistent", "Hello world", 1)

    def test_add_post_exceeds_max_length(self):
        # Adding a post that exceeds MAX_POST_LENGTH should raise a ValueError
        self.service.add_user("john")
        long_text = "a" * (MAX_POST_LENGTH + 1)
        with self.assertRaises(ValueError):
            self.service.add_post("john", long_text, 1)
    
    def test_add_post_no_content(self):
        # Adding an empty post should raise a ValueError
        self.service.add_user("john")
        no_content = ""
        with self.assertRaises(ValueError):
            self.service.add_post("john", no_content, 1)

    def test_get_posts_for_user(self):
        # Create a user and add posts with increasing timestamps
        self.service.add_user("john")
        self.service.add_post("john", "First post", 1)
        self.service.add_post("john", "Second post", 2)
        self.service.add_post("john", "Third post", 3)

        # Posts should be returned in descending order (by timestamp).
        posts = self.service.get_posts_for_user("john")
        self.assertEqual(posts, ["Third post", "Second post", "First post"])

    def test_get_posts_for_topic(self):
        # Create a user and add posts that include tags
        self.service.add_user("john")
        self.service.add_post("john", "just #chilling today", 1)
        self.service.add_post("john", "eating #steak for dinner", 2)
        self.service.add_post("john", "ugh! this #steak tasted like dog food", 3)
        self.service.add_post("john", "No tags here", 4)

        # For tag 'steak', both posts (timestamps 2 and 3) should be returned in descending order by timestamp
        posts_for_python = self.service.get_posts_for_topic("steak")
        self.assertEqual(posts_for_python,
            ["ugh! this #steak tasted like dog food", "eating #steak for dinner"])

        # For tag 'chilling', only one post should be returned
        posts_for_coding = self.service.get_posts_for_topic("chilling")
        self.assertEqual(posts_for_coding, ["just #chilling today"])

        # Requesting posts for a non-existent topic should raise ValueError
        with self.assertRaises(ValueError):
            self.service.get_posts_for_topic("nonexistent")

    def test_get_trending_topics(self):
        self.service.add_user("john")
        # Add three posts with overlapping tags
        self.service.add_post("john", "just #chilling with #pizza today", 1)
        self.service.add_post("john", "eating #steak and #pizza for dinner", 2)
        self.service.add_post("john", "ugh! this #steak tasted like dog food", 3)

        # Expected counts: steak: 2, pizza: 2, chilling: 1
        # Topics are sorted alphabetically for pizza and steak as for the same count
        trending = self.service.get_trending_topics(1, 3)
        self.assertEqual(trending, ["pizza", "steak", "chilling"])

    def test_get_trending_topics_out_of_range(self):
        self.service.add_user("john")
        self.service.add_post("john", "just #chilling with #pizza today", 4)
        # There are no posts in the interval 1 to 3
        trending = self.service.get_trending_topics(1, 3)
        self.assertEqual(trending, [])

    def test_trending_topics_exact_boundaries(self):
        self.service.add_user("john")
        self.service.add_post("john", "Discussing #pizza at exactly timestamp", 1)
        self.service.add_post("john", "Discussing #steak at exactly timestamp", 10)
        # Both topics appear once and have to be sorted alphabetically
        trending = self.service.get_trending_topics(1, 10)
        self.assertEqual(trending, ["pizza", "steak"])

    def test_delete_user(self):
        # Create two users and add posts with some overlapping tags
        self.service.add_user("john")
        self.service.add_user("mayer")
        self.service.add_post("john", "Post by john with #common", 1)
        self.service.add_post("mayer", "Post by mayer with #common", 2)
        self.service.add_post("mayer", "Another post by mayer with #pizza", 3)

        # Before deletion, the tag 'common' has two posts.
        posts_common = self.service.get_posts_for_topic("common")
        self.assertEqual(posts_common, ["Post by mayer with #common", "Post by john with #common"])

        # Delete user 'mayer'
        self.service.delete_user("mayer")

        # Accessing posts for 'mayer' now should raise an error
        with self.assertRaises(ValueError):
            self.service.get_posts_for_user("mayer")

        # The tag 'pizza' should have been removed during the deletion of mayer
        with self.assertRaises(ValueError):
            self.service.get_posts_for_topic("pizza")

        # The tag 'common' should now only return john's post
        posts_common_after = self.service.get_posts_for_topic("common")
        self.assertEqual(posts_common_after, ["Post by john with #common"])

    def test_delete_nonexistent_user(self):
        # Attempting to delete a user that does not exist should raise ValueError
        with self.assertRaises(ValueError):
            self.service.delete_user("john")

    def test_parse_tags_from_post(self):
        text = "eating #steak and #pizza with #steak for dinner"  # Duplicate tag steak
        tags = parse_tags_from_post(text)
        self.assertEqual(tags, set(["steak", "pizza"]))  # Should be unique
        
        # Test with no tags
        self.assertEqual(parse_tags_from_post("Eating pizza for dinner"), set())
        
        # Test with invalid tags
        self.assertEqual(parse_tags_from_post("#"), set())
        self.assertEqual(parse_tags_from_post("#!invalid"), set())


if __name__ == "__main__":
    unittest.main()
