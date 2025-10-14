import enum

class ChatType(enum.Enum):
	PRIVATE = 'private'
	GROUP = 'group'
	SUPERGROUP = 'supergroup'
	CHANNEL = 'channel'
	
class MessageType(enum.Enum):
	TEXT = 'text'
	ANIMATION = 'animation'
	AUDIO = 'audio'
	DOCUMENT = 'document'
	PAID_MEDIA = 'paid_media'
	PHOTO = 'photo'
	STICKER = 'sticker'
	STORY = 'story'
	VIDEO = 'video'
	VIDEO_NOTE = 'video_note'
	VOICE = 'voice'
	CHECKLIST = 'checklist'
	CONTACT = 'contact'
	DICE = 'dice'
	GAME = 'game'
	POLL = 'poll'
	VENUE = 'venue'
	LOCATION = 'location'
	INVOICE = 'invoice'
	GIVEAWAY = 'giveaway'
	
