# PyBoostyApi Docs

## Classes
###  BoostyApi

## Methods

create(path: str) -> BoostyAPI

get_blog_href(self) -> str

close(self)

---


get_blog_stats(self) -> dict

get_subscribers(self, limit: int, sort_by: str, order: str) -> dict
- sort_by - (on_time, payments)
- sort_order - (gt, lt)

get_contacts(self, limit: int, sort_by: str, sort_order: str) -> dict
- sort_by - (time, unread, name)
- sort_order - (asc, desc)

get_user_dialog(self, user_id: int) -> dict
- user_id - id of user from which you want to get dialog(you can get it from get_contacts())

get_subscription_levels(self, show_deleted: bool, show_free_level: bool) -> list[dict]

get_blog_metrics(self, time_from: int, time_to: int) -> dict
- time_from - start metrics time
- time_to - end metrics time

get_donations(self, limit: int, sort_by: str, order: str) -> dict
- sort_by - (time, amount)
- order - (lt, gt)

get_post_sales(self, limit: int, sort_by: str, order: str) -> dict
- sort_by - (time, amount)
- order - (lt, gt)

get_posts(self, blog_name: str) -> dict
- blog_name - example: get_posts("/boosty")(pass nothing to use your own blog)

get_blog_info(self, blog_name: str) -> dict
- blog_name - example: get_blog_info("/boosty")(pass nothing to use your own blog)

create_post(self, title: str, content: str, subscription_level_id: int, price: int, tags: str, deny_comments: bool, wait_video: bool, has_chat: bool) -> dict
- subscription_level_id - int(can get ids from subscription_levels())
- tags - your post tags. example: "tag1, tag2, tag3"

get_media_posts(self, blog_name: str, media_type: str, limit: int, limit_by: str) -> dict
- blog_name - example: get_media_posts("/boosty",...)(pass nothing to use your own blog)
- media_type - (all, image, video, audio)
- limit - <=50
- limit_by - (post, media)
