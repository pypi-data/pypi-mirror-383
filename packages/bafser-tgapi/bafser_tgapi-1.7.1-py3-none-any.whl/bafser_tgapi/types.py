from datetime import datetime
from typing import Any, Literal, Union, override

from bafser import JsonObj, JsonOpt, Undefined


class WebhookInfo(JsonObj):
    # https://core.telegram.org/bots/api#webhookinfo
    url: str


class User(JsonObj):
    # https://core.telegram.org/bots/api#user
    id: int
    is_bot: bool
    first_name: str
    last_name: str = ""
    username: str = ""
    language_code: str = ""


class Chat(JsonObj):
    # https://core.telegram.org/bots/api#chat
    id: int
    type: Literal["private", "group", "supergroup", "channel"]
    title: str = ""
    is_forum: bool = False


class MessageEntity(JsonObj):
    class _User(JsonObj):
        id: int

    Type = Literal["mention", "hashtag", "cashtag", "bot_command", "url", "email", "phone_number", "bold", "italic", "underline",
                   "strikethrough", "spoiler", "blockquote", "expandable_blockquote", "code", "pre", "text_link", "text_mention", "custom_emoji"]
    # https://core.telegram.org/bots/api#messageentity
    type: Type
    offset: int
    length: int
    url: JsonOpt[str] = Undefined
    user: JsonOpt[_User] = Undefined
    language: JsonOpt[str] = Undefined
    custom_emoji_id: JsonOpt[str] = Undefined

    @staticmethod
    def text_mention(offset: int, length: int, user_id: int):
        return MessageEntity(type="text_mention", offset=offset, length=length, user=MessageEntity._User(id=user_id))

    @staticmethod
    def blockquote(offset: int, length: int):
        return MessageEntity(type="blockquote", offset=offset, length=length)

    @staticmethod
    def spoiler(offset: int, length: int):
        return MessageEntity(type="spoiler", offset=offset, length=length)

    @staticmethod
    def bold(offset: int, length: int):
        return MessageEntity(type="bold", offset=offset, length=length)

    @staticmethod
    def italic(offset: int, length: int):
        return MessageEntity(type="italic", offset=offset, length=length)

    @staticmethod
    def underline(offset: int, length: int):
        return MessageEntity(type="underline", offset=offset, length=length)

    @staticmethod
    def code(offset: int, length: int):
        return MessageEntity(type="code", offset=offset, length=length)

    @staticmethod
    def text_link(offset: int, length: int, url: str):
        return MessageEntity(type="text_link", offset=offset, length=length, url=url)

    @staticmethod
    def len(text: str):
        return len(MessageEntity.encode_text(text)) // 2

    @staticmethod
    def encode_text(text: str):
        return text.encode("utf-16-le")

    @staticmethod
    def decode_text(text: bytes):
        return text.decode("utf-16-le")

    def get_msg_text(self, msg: str):
        text = MessageEntity.encode_text(msg)
        s = self.offset * 2 - 2
        e = s + self.length * 2
        return MessageEntity.decode_text(text[s:e])

    def copy(self):
        return MessageEntity(
            type=self.type,
            offset=self.offset,
            length=self.length,
            url=self.url,
            user=self.user,
            language=self.language,
            custom_emoji_id=self.custom_emoji_id,
        )


class PhotoSize(JsonObj):
    # https://core.telegram.org/bots/api#photosize
    file_id: str
    file_unique_id: str
    width: int
    height: int
    file_size: JsonOpt[int]


class Audio(JsonObj):
    # https://core.telegram.org/bots/api#audio
    file_id: str
    file_unique_id: str
    duration: int
    performer: JsonOpt[str]
    title: JsonOpt[str]
    file_name: JsonOpt[str]
    mime_type: JsonOpt[str]
    file_size: JsonOpt[int]
    thumbnail: JsonOpt[PhotoSize]


class Document(JsonObj):
    # https://core.telegram.org/bots/api#document
    file_id: str
    file_unique_id: str
    thumbnail: JsonOpt[PhotoSize]
    file_name: JsonOpt[str]
    mime_type: JsonOpt[str]
    file_size: JsonOpt[int]


class Sticker(JsonObj):
    # https://core.telegram.org/bots/api#sticker
    file_id: str
    file_unique_id: str
    type: str
    width: int
    height: int
    is_animated: bool
    is_video: bool
    thumbnail: JsonOpt[PhotoSize]
    emoji: JsonOpt[str]
    set_name: JsonOpt[str]
    # premium_animation: JsonOpt[File]
    # mask_position: JsonOpt[MaskPosition]
    custom_emoji_id: JsonOpt[str]
    needs_repainting: bool = False
    file_size: JsonOpt[int]


class Video(JsonObj):
    # https://core.telegram.org/bots/api#video
    file_id: str
    file_unique_id: str
    width: int
    height: int
    duration: int
    thumbnail: JsonOpt[PhotoSize]
    cover: list[PhotoSize] = []
    start_timestamp: JsonOpt[int]
    file_name: JsonOpt[str]
    mime_type: JsonOpt[str]
    file_size: JsonOpt[int]


class VideoNote(JsonObj):
    # https://core.telegram.org/bots/api#videonote
    file_id: str
    file_unique_id: str
    length: int
    duration: int
    thumbnail: JsonOpt[PhotoSize]
    file_size: JsonOpt[int]


class Voice(JsonObj):
    # https://core.telegram.org/bots/api#voice
    file_id: str
    file_unique_id: str
    duration: int
    mime_type: JsonOpt[str]
    file_size: JsonOpt[int]


class LinkPreviewOptions(JsonObj):
    # https://core.telegram.org/bots/api#linkpreviewoptions
    is_disabled: JsonOpt[bool] = Undefined
    url: JsonOpt[str] = Undefined
    prefer_small_media: JsonOpt[bool] = Undefined
    prefer_large_media: JsonOpt[bool] = Undefined
    show_above_text: JsonOpt[bool] = Undefined

    @staticmethod
    def disable():
        return LinkPreviewOptions(is_disabled=True)


class Message(JsonObj):
    # https://core.telegram.org/bots/api#message
    __datetime_parser__ = datetime.fromtimestamp
    message_id: int
    message_thread_id: JsonOpt[int]
    sender: JsonOpt[User]
    chat: Chat
    reply_to_message: JsonOpt["Message"]
    is_topic_message: bool = False
    text: str = ""
    date: datetime
    entities: list[MessageEntity] = []
    link_preview_options: JsonOpt[LinkPreviewOptions] = Undefined
    audio: JsonOpt[Audio]
    document: JsonOpt[Document]
    photo: JsonOpt[list[PhotoSize]]
    sticker: JsonOpt[Sticker]
    video: JsonOpt[Video]
    video_note: JsonOpt[VideoNote]
    voice: JsonOpt[Voice]
    caption: JsonOpt[str]
    caption_entities: list[MessageEntity] = []

    @override
    def _parse(self, key: str, v: Any, json: dict[str, Any]):
        if key == "from":
            return "sender"


class InaccessibleMessage(JsonObj):
    # https://core.telegram.org/bots/api#inaccessiblemessage
    __datetime_parser__ = datetime.fromtimestamp
    message_id: int
    chat: Chat
    date: datetime
    message_thread_id = Undefined


class MessageId(JsonObj):
    # https://core.telegram.org/bots/api#messageid
    message_id: int


class InlineQuery(JsonObj):
    # https://core.telegram.org/bots/api#inlinequery
    id: str
    sender: User
    query: str
    offset: str
    chat_type: JsonOpt[Literal["sender", "private", "group", "supergroup", "channel"]]

    @override
    def _parse(self, key: str, v: Any, json: dict[str, Any]):
        if key == "from":
            return "sender"


type MaybeInaccessibleMessage = Message | InaccessibleMessage


class CallbackQuery(JsonObj):
    # https://core.telegram.org/bots/api#callbackquery
    id: str
    sender: User
    message: JsonOpt[MaybeInaccessibleMessage]
    inline_message_id: JsonOpt[str]
    chat_instance: str
    data: JsonOpt[str]
    game_short_name: JsonOpt[str]

    @override
    def _parse(self, key: str, v: Any, json: dict[str, Any]):
        if key == "from":
            return "sender"


class ChosenInlineResult(JsonObj):
    # https://core.telegram.org/bots/api#choseninlineresult
    result_id: str
    sender: User
    # location: Location
    inline_message_id: JsonOpt[str]
    query: str

    @override
    def _parse(self, key: str, v: Any, json: dict[str, Any]):
        if key == "from":
            return "sender"


class ChatMember(JsonObj):
    # https://core.telegram.org/bots/api#chatmember
    status: Literal["creator", "administrator", "member", "restricted", "left", "kicked"]
    user: User


class ChatMemberUpdated(JsonObj):
    # https://core.telegram.org/bots/api#chatmemberupdated
    chat: Chat
    sender: User
    date: int
    old_chat_member: ChatMember
    new_chat_member: ChatMember
    # invite_link: JsonOpt[ChatInviteLink]
    via_join_request: JsonOpt[bool]
    via_chat_folder_invite_link: JsonOpt[bool]

    @override
    def _parse(self, key: str, v: Any, json: dict[str, Any]):
        if key == "from":
            return "sender"


class Update(JsonObj):
    # https://core.telegram.org/bots/api#update
    update_id: int
    message: JsonOpt[Message]
    inline_query: JsonOpt[InlineQuery]
    callback_query: JsonOpt[CallbackQuery]
    chosen_inline_result: JsonOpt[ChosenInlineResult]
    my_chat_member: JsonOpt[ChatMemberUpdated]


class InputTextMessageContent(JsonObj):
    # https://core.telegram.org/bots/api#inputtextmessagecontent
    message_text: str
    parse_mode: JsonOpt[Literal["MarkdownV2", "HTML", "Markdown"]] = Undefined
    entities: JsonOpt[list[MessageEntity]] = Undefined
    link_preview_options: JsonOpt[LinkPreviewOptions] = Undefined

    @staticmethod
    def nw(message_text: str, use_markdown: bool = False):
        return InputTextMessageContent(
            message_text=message_text,
            parse_mode="MarkdownV2" if use_markdown else Undefined
        )


type InputMessageContent = InputTextMessageContent


class CallbackGame(JsonObj):
    # https://core.telegram.org/bots/api#callbackgame
    pass


class CopyTextButton(JsonObj):
    # https://core.telegram.org/bots/api#copytextbutton
    text: str


class InlineKeyboardButton(JsonObj):
    # https://core.telegram.org/bots/api#inlinekeyboardbutton
    text: str
    url: JsonOpt[str] = Undefined
    callback_data: JsonOpt[str] = Undefined
    # web_app: WebAppInfo
    # login_url: LoginUrl
    switch_inline_query: JsonOpt[str] = Undefined
    switch_inline_query_current_chat: JsonOpt[str] = Undefined
    # switch_inline_query_chosen_chat: SwitchInlineQueryChosenChat
    copy_text: JsonOpt[CopyTextButton] = Undefined
    callback_game: JsonOpt[CallbackGame] = Undefined
    # pay: bool

    @staticmethod
    def callback(text: str, callback_data: str):
        return InlineKeyboardButton(text=text, callback_data=callback_data)

    @staticmethod
    def inline_query_current_chat(text: str, query: str):
        return InlineKeyboardButton(text=text, switch_inline_query_current_chat=query)

    @staticmethod
    def run_game(text: str):
        return InlineKeyboardButton(text=text, callback_game=CallbackGame())

    @staticmethod
    def open_url(text: str, url: str):
        return InlineKeyboardButton(text=text, url=url)


class InlineKeyboardMarkup(JsonObj):
    # https://core.telegram.org/bots/api#inlinekeyboardmarkup
    inline_keyboard: list[list[InlineKeyboardButton]]


class InlineQueryResult:
    # https://core.telegram.org/bots/api#inlinequeryresult
    pass


class InlineQueryResultArticle(JsonObj, InlineQueryResult):
    # https://core.telegram.org/bots/api#inlinequeryresultarticle
    type: Literal["article"] = JsonObj.field(default="article", init=False)
    id: str
    title: str
    input_message_content: InputMessageContent
    reply_markup: JsonOpt[InlineKeyboardMarkup] = Undefined
    url: JsonOpt[str] = Undefined
    description: JsonOpt[str] = Undefined
    thumbnail_url: JsonOpt[str] = Undefined
    thumbnail_width: JsonOpt[int] = Undefined
    thumbnail_height: JsonOpt[int] = Undefined


class InlineQueryResultGame(JsonObj, InlineQueryResult):
    # https://core.telegram.org/bots/api#inlinequeryresultgame
    type: Literal["game"] = JsonObj.field(default="game", init=False)
    id: str
    game_short_name: str
    reply_markup: JsonOpt[InlineKeyboardMarkup] = Undefined


class BotCommand(JsonObj):
    # https://core.telegram.org/bots/api#botcommand
    command: str  # 1-32 characters. Can contain only lowercase English letters, digits and underscores.
    description: str  # 1-256 characters.


BotCommandScopeType = Literal["default", "all_private_chats", "all_group_chats",
                              "all_chat_administrators", "chat", "chat_administrators", "chat_member"]


class BotCommandScope(JsonObj):
    # https://core.telegram.org/bots/api#botcommandscope
    type: BotCommandScopeType
    chat_id: JsonOpt[Union[str, int]] = Undefined
    user_id: JsonOpt[int] = Undefined

    @staticmethod
    def default():
        return BotCommandScope(type="default")

    @staticmethod
    def all_private_chats():
        return BotCommandScope(type="all_private_chats")

    @staticmethod
    def all_group_chats():
        return BotCommandScope(type="all_group_chats")

    @staticmethod
    def all_chat_administrators():
        return BotCommandScope(type="all_chat_administrators")

    @staticmethod
    def chat(chat_id: Union[str, int]):
        return BotCommandScope(type="chat", chat_id=chat_id)

    @staticmethod
    def chat_administrators(chat_id: Union[str, int]):
        return BotCommandScope(type="chat_administrators", chat_id=chat_id)

    @staticmethod
    def chat_member(chat_id: Union[str, int], user_id: int):
        return BotCommandScope(type="chat_member", chat_id=chat_id, user_id=user_id)


class ReplyParameters(JsonObj):
    # https://core.telegram.org/bots/api#replyparameters
    message_id: int
    chat_id: JsonOpt[int | str] = Undefined
    allow_sending_without_reply: JsonOpt[bool] = Undefined
    quote: JsonOpt[str] = Undefined
    quote_parse_mode: JsonOpt[str] = Undefined
    quote_entities: JsonOpt[list[MessageEntity]] = Undefined
    quote_position: JsonOpt[int] = Undefined
    checklist_task_id: JsonOpt[int] = Undefined


class StickerSet(JsonObj):
    # https://core.telegram.org/bots/api#stickerset
    name: str
    title: str
    sticker_type: str
    stickers: list[Sticker]
    thumbnail: JsonOpt[PhotoSize]


class InputMedia(JsonObj):
    # https://core.telegram.org/bots/api#inputmedia
    type: Literal["photo", "video", "animation", "audio", "document"]
    media: str
    caption: JsonOpt[str] = Undefined
    parse_mode: JsonOpt[Literal["MarkdownV2"]] = Undefined
    caption_entities: JsonOpt[list[MessageEntity]] = Undefined
    show_caption_above_media: JsonOpt[bool] = Undefined
    has_spoiler: JsonOpt[bool] = Undefined

    def __init__(self, media: str):
        self.media = media

    def set_caption(self, caption: JsonOpt[str] = Undefined, parse_mode: JsonOpt[Literal["MarkdownV2"]] = Undefined,
                    caption_entities: JsonOpt[list[MessageEntity]] = Undefined, show_caption_above_media: JsonOpt[bool] = Undefined,
                    has_spoiler: JsonOpt[bool] = Undefined):
        self.caption = caption
        self.parse_mode = parse_mode
        self.caption_entities = caption_entities
        self.show_caption_above_media = show_caption_above_media
        self.has_spoiler = has_spoiler
        return self


class InputMediaPhoto(InputMedia):
    # https://core.telegram.org/bots/api#inputmediaphoto
    type: Literal["photo"] = JsonObj.field(default="photo", init=False)  # pyright: ignore[reportIncompatibleVariableOverride]


class InputMediaVideo(InputMedia):
    # https://core.telegram.org/bots/api#inputmediavideo
    type: Literal["video"] = JsonObj.field(default="video", init=False)  # pyright: ignore[reportIncompatibleVariableOverride]
    thumbnail: JsonOpt[str] = Undefined
    cover: JsonOpt[str] = Undefined
    start_timestamp: JsonOpt[int] = Undefined
    width: JsonOpt[int] = Undefined
    height: JsonOpt[int] = Undefined
    duration: JsonOpt[int] = Undefined
    supports_streaming: JsonOpt[bool] = Undefined


class InputMediaAnimation(InputMedia):
    # https://core.telegram.org/bots/api#inputmediaanimation
    type: Literal["animation"] = JsonObj.field(default="animation", init=False)  # pyright: ignore[reportIncompatibleVariableOverride]
    thumbnail: JsonOpt[str] = Undefined
    width: JsonOpt[int] = Undefined
    height: JsonOpt[int] = Undefined
    duration: JsonOpt[int] = Undefined


class InputMediaAudio(InputMedia):
    # https://core.telegram.org/bots/api#inputmediaaudio
    type: Literal["audio"] = JsonObj.field(default="audio", init=False)  # pyright: ignore[reportIncompatibleVariableOverride]
    thumbnail: JsonOpt[str] = Undefined
    duration: JsonOpt[int] = Undefined
    performer: JsonOpt[str] = Undefined
    title: JsonOpt[str] = Undefined


class InputMediaDocument(InputMedia):
    # https://core.telegram.org/bots/api#inputmediadocument
    type: Literal["document"] = JsonObj.field(default="document", init=False)  # pyright: ignore[reportIncompatibleVariableOverride]
    thumbnail: JsonOpt[str] = Undefined
    disable_content_type_detection: JsonOpt[bool] = Undefined
