from __future__ import annotations

from typing import Dict, List, Any

from . import types, api

class Message:
	
	def __init__(
		self,
		bot: api.BotAPI,
		message: types.Message
	):
		self.bot = bot
		self.message = message
		
	async def delete(self) -> bool:
		return await self.bot.delete_message(
			chat_id=self.message.chat.id,
			message_id=self.message.message_id
		)
		
	async def edit_text(
		self,
		text: str,
		# inline_message_id: Optional[str] = None,
		parse_mode: str | None,
		entities: list[types.MessageEntity] | None = None,
		link_preview_options: types.LinkPreviewOptions | None = None,
		reply_markup: types.InlineKeyboardMarkup | None = None,
	) -> types.Message | bool:
		return await self.bot.edit_message_text(
			chat_id=self.message.chat.id,
			message_id=self.message.message_id,
			business_connection_id=self.message.business_connection_id,
			# inline_message_id=self.inline_message_id,
			text=text,
			parse_mode=parse_mode,
			entities=entities,
			link_preview_options=link_preview_options,
			reply_markup=reply_markup
		)
		
		
class InlineKeyboard:
	
	@staticmethod
	def from_dict(
		json_data: List[List[Dict[str, Any]]]
	) -> types.InlineKeyboardMarkup:
		keyboard = [
			[
				types.InlineKeyboardButton(**button) for button in row
			] for row in json_data
		]
		return types.InlineKeyboardMarkup(inline_keyboard=keyboard)
		
		
class MessageEntities:

	@staticmethod
	def from_dict(
		json_data: List[Dict[str, Any]]
	) -> List[types.MessageEntity]:
		return [types.MessageEntity.model_validate(item) for item in json_data]
		
