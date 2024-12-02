ALL_EXPANSIONS = [
                    "author_id",
                    "referenced_tweets.id",
                    "referenced_tweets.id.author_id",
                    "entities.mentions.username",
                    "geo.place_id",
                    "attachments.media_keys",
                ]

ALL_TWEET_FIELDS = [
      "attachments",
                    "author_id",
                    "conversation_id",
                    "created_at",
                    "edit_controls",
                    "edit_history_tweet_ids",
                    "entities",
                    "geo",
                    "id",
                    "in_reply_to_user_id",
                    "lang",
                    "possibly_sensitive",
                    "public_metrics",
                    "referenced_tweets",
                    "reply_settings",
                    "source",
                    "text",
                    "withheld",
]

ALL_USER_FIELDS = [
    "created_at",
    "description",
    "entities",
    "id",
    "location",
    "name",
    "pinned_tweet_id",
    "profile_image_url",
    "protected",
    "public_metrics",
    "url",
    "username",
    "verified",
    "verified_type",
    "withheld",
]

ALL_PLACE_FIELDS= [
                    "contained_within",
                    "country",
                    "country_code",
                    "full_name",
                    "geo",
                    "id",
                    "name",
                    "place_type",
                ]

ALL_MEDIA_FIELDS=[
                    "alt_text",
                    "duration_ms",
                    "height",
                    "media_key",
                    "non_public_metrics",
                    "organic_metrics",
                    "preview_image_url",
                    "promoted_metrics",
                    "public_metrics",
                    "type",
                    "url",
                    "variants",
                    "width",
                ]