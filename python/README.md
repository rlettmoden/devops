# Yodelr Implementation

Twitter is a service that implements a social media-like posting system with user management and topic tracking capabilities.

## Overview

The implementation consists of three main files:
- twitter.py - Contains the abstract base class defining the service interface
- twitter_fast_retrieval.py - Contains the concrete implementation optimized for fast retrieval
- post.py - Contains the Post class and tag parsing functionality

## Implementation Details

The TwitterFastRetrieval class uses the following data structures for efficient retrieval:
- Posts array for chronological storage
- User-to-timestamp mapping
- Timestamp-to-post index mapping
- Tag-to-timestamp mapping

## Requirements

- Python 3.7+

## Running the Tests

- Run the tests using:
```
python -m unittest twitter?test.py
```