#include "twitter_fast_retrieval.h"

namespace twitter
{

    TwitterFastRetrieval::TwitterFastRetrieval()
    {
    }

    TwitterFastRetrieval::~TwitterFastRetrieval()
    {
    }

    void TwitterFastRetrieval::addUser(const std::string &userName)
    {

    }

    void TwitterFastRetrieval::addPost(const std::string & userName, const std::string & postText, uint64_t timestamp)
    {

    }

    void TwitterFastRetrieval::deleteUser(const std::string &userName)
    {

    }

    PostTexts TwitterFastRetrieval::getPostsForUser(const std::string &userName) const
    {
        return PostTexts();
    }

    PostTexts TwitterFastRetrieval::getPostsForTopic(const std::string &topic) const
    {
        return PostTexts();
    }

    Topics TwitterFastRetrieval::getTrendingTopics(uint64_t fromTimestamp, uint64_t toTimestamp) const
    {
        return Topics();
    }

    std::set<std::string> parseTags(const std::string &text)
    {
        // Create iterator for matches
        std::sregex_iterator iter(text.begin(), text.end(), REGEX_TAG);
        std::sregex_iterator end;

        // Store matches in a vector
        std::set<std::string> matches;
        while (iter != end) {
            matches.insert(iter->str().substr(1));
            ++iter;
        }
        return matches;
    }

} // namespace Twitter
