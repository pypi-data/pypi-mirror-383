# CliSelf/modules/profile_manager.py
import os
from pyrogram import Client
from ..core.logger import get_logger

logger = get_logger("profile")

class ProfileManager:
    """
    ProfileManager
    ---------------
    مدیریت تنظیمات پروفایل تلگرام با سیستم لاگ مرکزی.
    """

    def __init__(self, client: Client):
        self.client = client
        logger.info("ProfileManager initialized successfully.")

    async def set_first_name(self, first_name: str):
        try:
            if not first_name:
                raise ValueError("first_name cannot be empty.")

            logger.info(f"Updating FIRST name to '{first_name}'")
            await self.client.update_profile(first_name=first_name)
            msg = f"First name updated successfully to '{first_name}'."
            logger.info(msg)
            return f"✅ {msg}"

        except Exception as e:
            logger.exception(f"Error updating first name: {e}")
            raise

    async def set_last_name(self, last_name: str):
        try:
            if not last_name:
                raise ValueError("last_name cannot be empty.")

            logger.info(f"Updating LAST name to '{last_name}'")
            await self.client.update_profile(last_name=last_name)
            msg = f"Last name updated successfully to '{last_name}'."
            logger.info(msg)
            return f"✅ {msg}"

        except Exception as e:
            logger.exception(f"Error updating last name: {e}")
            raise

    async def set_bio(self, bio: str):
        try:
            if not bio:
                raise ValueError("bio cannot be empty.")
            logger.info(f"Updating bio: '{bio}'")
            await self.client.update_profile(bio=bio)
            msg = "Bio updated successfully."
            logger.info(msg)
            return f"✅ {msg}"

        except Exception as e:
            logger.exception(f"Error updating bio: {e}")
            raise

    async def set_username(self, username: str):
        try:
            if not username:
                raise ValueError("username cannot be empty.")
            uname = username.lstrip("@")
            logger.info(f"Updating username to @{uname}")
            await self.client.set_username(uname)
            msg = f"Username updated successfully to @{uname}."
            logger.info(msg)
            return f"✅ {msg}"

        except Exception as e:
            logger.exception(f"Error updating username: {e}")
            raise

    async def set_photo(self, message):
        try:
            if not message.reply_to_message:
                raise ValueError("Reply to a media message required.")
            media_msg = message.reply_to_message

            if not (media_msg.photo or media_msg.video or media_msg.document):
                raise ValueError("Replied message must contain a media file.")

            logger.info("Downloading media for profile photo update...")
            path = await media_msg.download()
            logger.info(f"Media downloaded to {path}")

            await self.client.set_profile_photo(photo=path)
            os.remove(path)
            msg = "Profile photo updated successfully."
            logger.info(msg)
            return f"✅ {msg}"

        except Exception as e:
            logger.exception(f"Error updating profile photo: {e}")
            raise
