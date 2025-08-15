/*
 * Copyright Vespa.ai.
 * Not for redistribution outside of candidate interview context.
 */

#pragma once

#include <string>
#include <vector>
#include <stdint.h>
#include <unordered_map>
#include <vector>
#include <regex>
#include <set>

#include "twitter.h"

namespace twitter {

const std::regex REGEX_TAG("#[0-9a-zA-Z_]+");

static std::set<std::string> parseTags(const std::string& text);

struct Post{
    std::string text;
    std::set<std::string> tags;
    std::string user;
    uint64_t timestamp;

    Post(std::string text, std::string user, uint64_t timestamp)
    {
        this->text = text;
        this->user = user;
        this->timestamp = timestamp;

        this->tags = parseTags(text);
    }


};

/**
 * The Twitter service interface.
 *
 * This allows adding and deleting users, adding and retrieving posts
 * and getting trending topics.
 */
class TwitterFastRetrieval : public Twitter{

private:
    std::unordered_map<uint64_t, uint64_t> m_tagsToPosts;
    std::unordered_map<uint64_t, uint64_t> m_usersToPosts;
    std::unordered_map<uint64_t, uint64_t> m_timestampsTo;
    std::vector<Post> m_posts;

public:
     TwitterFastRetrieval();
     ~TwitterFastRetrieval();

    void addUser(const std::string &userName) override;
    void addPost(const std::string &userName,
                         const std::string &postText,
                         uint64_t timestamp) override;
    void deleteUser(const std::string &userName) override;

    PostTexts getPostsForUser(const std::string &userName) const override;
    PostTexts getPostsForTopic(const std::string &topic) const override;
    Topics getTrendingTopics(uint64_t fromTimestamp,
                                     uint64_t toTimestamp) const override;
};

}
