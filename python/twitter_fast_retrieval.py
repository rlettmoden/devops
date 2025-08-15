from typing import List

from python.twitter import Twitter

from collections import Counter

from bisect import bisect_left, bisect_right

from post import Post



MAX_POST_LENGTH = 140


def add_timestamp_to_map(timestamp_map: dict, key: str, timestamp: int) -> None:
    """
    Simple helper to update or insert a timestamp to a map based on the key

    Args:
        timestamp_map (dict): Map to update
        key (str): Key to check
        timestamp (int): Timestamp to insert
    """    

    # check if key already exists and add the value to the array if so
    if key in timestamp_map:
        timestamp_map[key].append(timestamp)
    else:
        # otherwise create a tag entry
        timestamp_map[key] = [timestamp]


class TwitterFastRetrieval(Twitter):
    """
    Implementation of the Twitter service interface.

    This allows adding and deleting users, adding and retrieving posts
    and getting trending topics.
    
    The following data structures are used for efficient retrieval but higher maintenance costs for delete operations: 
    - Posts are stored in a simple array which allows us to use efficient range indices (as we have strictly monotonically increasing timestamps). Therefore, an index structure (timestamp to post array_index) is used to get all posts of interest
    - A map with all posts by a user and all posts mentioning a tag is used for fast retrieval without having to iterate through all posts
    - These functions come with a cost of mainting the indices during add and delete operations. Especially delete operations are expensive, as we might need to update all indices in the worst case (O(n)). This could be sped up (O(log n)) by using a tree like indexing architecture (B-Tree for example)

    Depending on the use cases of the systems (delete operations vs retrieval operations), it can be optimized . Also not thread safe

    The following code snipped only works from python 3.7 as dict items are stored in insertion order which we use to avoid additional sorting operations during retrieval
    """

    def __init__(self) -> None:
        """
        Initializes the system with empty data structures
        """        
        super().__init__()
        self.user_to_timestamp = {} # users : [timestamps]
        self.posts = [] # list[posts]
        self.timestamp_to_post_idx = {} # timestamp : post_idx
        self.tag_to_timestamp = {} # tags : [timestamps]

    def add_user(self, user_name: str) -> None:
        """
        Adds a user with the given username to the system. If the username already exists, do nothing

        Args:
            user_name (str): User name to register

        Raises:
            ValueError: If user_name already exists
        """

        # Check if user already exists
        if user_name in self.user_to_timestamp:
            # As there is no behavior stated in the exercise description, we throw an exception
            raise ValueError(f"Username <{user_name}> already exists")
        else:
            self.user_to_timestamp[user_name] = []

    def add_post(self, user_name: str, post_text: str, timestamp: int) -> None:
        """
        Adds a post for a registered user to the system and stores the post in indices for fast retrieval by user_name, tag or timestamp range. 

        Args:
            user_name (str): User name of the post
            post_text (str): Content of the post with < 140 characters
            timestamp (int): Timestamp in number of seconds

        Raises:
            ValueError: If user_name was not registered before
            ValueError: If post_text surpasses 140 characters
        """        

        # check if username is registered
        if not user_name in self.user_to_timestamp:
            raise ValueError(f"Username <{user_name}> does not exist")
        
        # check if text has the given length
        if len(post_text) > MAX_POST_LENGTH:
            raise ValueError(f"Post of length {len(post_text)} surpasses maximum length of {MAX_POST_LENGTH} characters")
        
        # check that the post is not empty
        if len(post_text) == 0:
            raise ValueError("Post is empty")

        # Create a new post instance
        post = Post(user_name, post_text, timestamp)
        # add the post
        self.posts.append(post)

        # Update all data structures with the new post
        # get index for the new post to do effective range indexing. shift by one as we already added the post
        post_array_idx = len(self.posts) - 1
        # Update index for posts
        self.timestamp_to_post_idx[timestamp] = post_array_idx
                
        # update tags to posts map
        for tag in post.tags:
            add_timestamp_to_map(self.tag_to_timestamp, tag, timestamp)

        # update user to posts map
        add_timestamp_to_map(self.user_to_timestamp, user_name, timestamp)
    
    
    def delete_user(self, user_name: str) -> None:
        """
        Deletes the given user and all posts made by the user from the system.

        Args:
            user_name: User name to delete

        Raises:
            ValueError: If the username does not exist
        """             

        # check if 
        if user_name not in self.user_to_timestamp:
            raise ValueError(f"Username <{user_name}> does not exist")

        # delete posts
        tags_with_delete_posts = []
        for timestamp in self.user_to_timestamp[user_name]:
            # gather tags which we have to delete from to iterate not through the whole tag list
            post_idx = self.timestamp_to_post_idx[timestamp]
            tags_with_delete_posts += self.posts[post_idx].tags

        # make tags unique
        tags_with_delete_posts = set(tags_with_delete_posts)
        # delete posts in tags 
        for tag in tags_with_delete_posts:
            # convert lists to sets for 
            all_posts = self.tag_to_timestamp[tag]
            delete_posts = self.user_to_timestamp[user_name]
            # use the set difference to remove all posts
            self.tag_to_timestamp[tag] =  [x for x in all_posts if x not in delete_posts]

            # clean up tag list if empty
            if len(self.tag_to_timestamp[tag]) == 0:
                del self.tag_to_timestamp[tag]

        # Update all indices
        # therefore, first get all posts of the user
        delete_post_timestamps = self.user_to_timestamp[user_name]
        # get the first index of an element that is deleted in the array. All following elements have to updated
        start_update_timestamp = list(self.timestamp_to_post_idx.keys()).index(delete_post_timestamps[0])
        # get all the elements in the post index that are updated
        update_delete_timestamps = list(self.timestamp_to_post_idx.keys())[start_update_timestamp:]

        # keep track, where we are in the delete list
        delete_list_idx = 0
        # keep track, how many positions we have to shift the index to the left at the update index
        delete_offset = 0
        # We need to iterate through the post idxs and delete or update a key
        for timestamp in update_delete_timestamps:
            # case we find a delete index
            if timestamp == delete_post_timestamps[delete_list_idx]:

                # delete post. Here, we need to shift the current array index by the amount of indices that we delete before the current position
                del self.posts[self.timestamp_to_post_idx[timestamp] - delete_offset]
                # update the position in the delete list
                delete_list_idx += 1
                delete_offset += 1
            # otherwise we have an update index
            else:
                # update key by shifting it #deletes before current position to the left
                self.timestamp_to_post_idx[timestamp] = self.timestamp_to_post_idx[timestamp] - delete_offset
            
        # delete user
        del self.user_to_timestamp[user_name]

        # delete all timestamps from the post index
        for timestamp in delete_post_timestamps:
            del self.timestamp_to_post_idx[timestamp]
        

    def get_posts_for_user(self, user_name: str) -> List[str]:
        """
        Returns a list of all post texts made by the given user sorted on descending timestamp

        Args:
            user_name (str): The user to search for

        Raises:
            ValueError: If the username does not exist

        Returns:
            List[str]: List of posts created by a user sorted on descending timestamp
        """

        # check if user_name exists
        if user_name not in self.user_to_timestamp.keys():
            raise ValueError(f"User <{user_name}> does not exist")

        out_posts = []
        # add the posts descendingly by iterating through the inversed post list  (timestamp to index)
        for timestamp in self.user_to_timestamp[user_name][::-1]:
            # add the post
            post_idx = self.timestamp_to_post_idx[timestamp]
            out_posts.append(self.posts[post_idx].post_text)
        return out_posts

    def get_posts_for_topic(self, topic: str) -> List[str]:
        """
        Returns a list of all post texts containing the given topic sorted on descending timestamp.

        Args:
            topic (str): The topic to search for

        Raises:
            ValueError: If the topic does not exist

        Returns:
            List[str]: List of posts mentioned by a topic sorted on descending timestamp
        """

        # check if topic exists
        if topic not in self.tag_to_timestamp.keys():
            raise ValueError(f"Topic <{topic}> does not exist")

        out_posts = []
        # add the posts descendingly by iterating through the inversed post list (timestamp to index) mentioning the topic
        for timestamp in self.tag_to_timestamp[topic][::-1]:
            # add the post
            post_idx = self.timestamp_to_post_idx[timestamp]
            out_posts.append(self.posts[post_idx].post_text)
        return out_posts

    def get_trending_topics(self, from_timestamp: int, to_timestamp: int) -> List[str]:
        """
        Returns a list of all unique topics mentioned in posts made in the given time interval, sorted on descending mention count primarily, alphabetically on topic secondarily. 
        The mention count for a topic is the number of posts that have mentioned this topic in the time interval. The time interval is inclusive.

        Args:
            from_timestamp (int): Inclusive start of the interval to look at in seconds 
            to_timestamp (int): Inclusive end of the interval to look at in seconds 

        Returns:
            List[str]: List of trending topics sorted on descending mention count
        """        

        # check for left interval
        if from_timestamp in self.timestamp_to_post_idx:
            interval_start_idx = self.timestamp_to_post_idx[from_timestamp]
        else:
            # look for nearest inclusive neighbor -> first value > from_timestamp
            interval_start_idx = bisect_left(list(self.timestamp_to_post_idx.keys()), from_timestamp)

        # check for right interval
        if to_timestamp in self.timestamp_to_post_idx:
            interval_end_idx = self.timestamp_to_post_idx[to_timestamp] + 1 # inclusive interval
        else:
             # look for nearest inclusive neighbor -> first value < from_timestamp
            interval_end_idx = bisect_right(list(self.timestamp_to_post_idx.keys()), to_timestamp)


        # get all the posts from the range
        posts_in_time_range = self.posts[interval_start_idx:interval_end_idx]

        # We create a counter to consistently update the tags. (With numpy we could one_hot encode topics and probably do this faster through vector additions)
        topic_counter = Counter() 
        for post in posts_in_time_range:
            topic_counter.update(post.tags)
        # get trending topics and it's count. Elements with equal counts are ordered in the order first encountered
        trending_topics = topic_counter.most_common()
        # second order sort alphabetically | This code snipped can be optimized as we are sorting two times by first index
        trending_topics = sorted(trending_topics, key=lambda x: (-x[1], x[0]))
        trending_topics = [trending_topic[0] for trending_topic in trending_topics]
        # second order sort alphabetically
        return trending_topics