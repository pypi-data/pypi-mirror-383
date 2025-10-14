import requests

cookies = {
    '__cf_bm': 'qapFQnURmsDjodqwDDE2VJEMDE5866xaIzDIFJYBYic-1760430147.1560142-1.0.1.1-uz.QYeX27.Ct2u5cZkUI9hCbAX8aZBUpMm4c8wf0IJQF_cBSUJZKetDDCn5iKC49aGUYAqVNtjzN14uqqvFVkcPJebrD8aiKCRMEKtEHKza5RnzuDf_VBoyCWZeNRmv4',
    'guest_id': 'v1%3A176020461781201487',
    '__cuid': '1f6139431072490b848ff94dee1d113c',
    'gt': '1977990316373180578',
}

headers = {
    'accept': '*/*',
    'accept-language': 'ru',
    'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
    'content-type': 'application/json',
    'dnt': '1',
    'origin': 'https://x.com',
    'priority': 'u=1, i',
    'referer': 'https://x.com/',
    'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    'x-client-transaction-id': 'wznRh++Xo/waTQ+/x3vOwzygAnUidXs67YUYb4Hb6fSCWv2pluyFtfJOGGOG9Y2W1xZnXcem08bTwssU9jjOKPu3dafowA',
    'x-guest-token': '1977990316373180578',
    'x-twitter-active-user': 'yes',
    'x-twitter-client-language': 'ru',
    'x-xp-forwarded-for': '960a8f5002c71d325303d033e9b07ad9dedc7320f48a54f9b13e635280c37b0cc38ec45ffe493eb7fda9ad0d545b551aaf40467eff5aad58aef2c710a283e65ceb6889d60b54322f2282c82df8f1bd27bcc22e471394f9152ba173a51e61b1d7e848f04b81bb6ea263d20ba3f3dbf8c535267c6a17da8ce8e0fcf304e4b925b7ae1bdc59b267ec78596d1f9bd20d16910b797e7c09cbcf34c26ff606a759d18904fc7279c0748cbd84312c32b3b5b80e21270411b06dd3cef4286233d03d20c859947119564b8b9f4f5dad439654613448905235b4cac1c798d739fc5903db92f5a3a5065dbec504e23d87fa0d57d4111bace271348519ee65b97ba56c764761e5',
    # 'cookie': '__cf_bm=qapFQnURmsDjodqwDDE2VJEMDE5866xaIzDIFJYBYic-1760430147.1560142-1.0.1.1-uz.QYeX27.Ct2u5cZkUI9hCbAX8aZBUpMm4c8wf0IJQF_cBSUJZKetDDCn5iKC49aGUYAqVNtjzN14uqqvFVkcPJebrD8aiKCRMEKtEHKza5RnzuDf_VBoyCWZeNRmv4; guest_id=v1%3A176020461781201487; __cuid=1f6139431072490b848ff94dee1d113c; gt=1977990316373180578',
}

params = {
    'variables': '{"tweetId":"1770713399158055191","includePromotedContent":true,"withBirdwatchNotes":true,"withVoice":true,"withCommunity":true}',
    'features': '{"creator_subscriptions_tweet_preview_api_enabled":true,"premium_content_api_read_enabled":false,"communities_web_enable_tweet_community_results_fetch":true,"c9s_tweet_anatomy_moderator_badge_enabled":true,"responsive_web_grok_analyze_button_fetch_trends_enabled":false,"responsive_web_grok_analyze_post_followups_enabled":false,"responsive_web_jetfuel_frame":true,"responsive_web_grok_share_attachment_enabled":true,"articles_preview_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,"responsive_web_twitter_article_tweet_consumption_enabled":true,"tweet_awards_web_tipping_enabled":false,"responsive_web_grok_show_grok_translated_post":false,"responsive_web_grok_analysis_button_from_backend":true,"creator_subscriptions_quote_tweet_preview_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":true,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,"longform_notetweets_rich_text_read_enabled":true,"longform_notetweets_inline_media_enabled":true,"payments_enabled":false,"profile_label_improvements_pcf_label_in_post_enabled":true,"responsive_web_profile_redirect_enabled":false,"rweb_tipjar_consumption_enabled":true,"verified_phone_label_enabled":false,"responsive_web_grok_image_annotation_enabled":true,"responsive_web_grok_imagine_annotation_enabled":true,"responsive_web_grok_community_note_auto_translation_is_enabled":false,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"responsive_web_graphql_timeline_navigation_enabled":true,"responsive_web_enhance_cards_enabled":false}',
    'fieldToggles': '{"withArticleRichContentState":true,"withArticlePlainText":false}',
}

response = requests.get(
    'https://api.x.com/graphql/WvlrBJ2bz8AuwoszWyie8A/TweetResultByRestId',
    params=params,
    headers=headers,
)

print(response.json())
