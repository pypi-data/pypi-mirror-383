def test_token_bucket_limits_calls():
    import server

    bucket = server.TokenBucket(max_calls=2, per_seconds=1000)
    assert bucket.allow() is True
    assert bucket.allow() is True
    assert bucket.allow() is False

