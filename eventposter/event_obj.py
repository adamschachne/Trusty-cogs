import discord
import re

from typing import List, Tuple, Optional, cast

from discord.ext.commands.converter import Converter
from discord.ext.commands.errors import BadArgument

IMAGE_LINKS = re.compile(r"(http[s]?:\/\/[^\"\']*\.(?:png|jpg|jpeg|gif|png))")


class Event:
    hoster: discord.Member
    members: List[Tuple[discord.Member, str]]
    event: str
    max_slots: Optional[int]
    approver: Optional[discord.Member]
    message: Optional[discord.Message]
    channel: Optional[discord.TextChannel]

    def __init__(
        self,
        hoster: discord.Member,
        members: List[Tuple[discord.Member, str]],
        event: str,
        max_slots: Optional[int],
        approver: Optional[discord.Member] = None,
        message: Optional[discord.Message] = None,
        channel: Optional[discord.TextChannel] = None,
    ):
        self.hoster = hoster
        self.members = members
        self.event = event
        self.max_slots = max_slots
        self.approver = approver
        self.message = message
        self.channel = channel

    @classmethod
    async def from_json(cls, data: dict, guild: discord.Guild):
        channel = cast(discord.TextChannel, guild.get_channel(data["channel"]))
        message = None
        if not channel:
            return None
        try:
            message = await channel.fetch_message(data["message"])
        except AttributeError:
            message = await channel.get_message(data["message"])  # type: ignore
        except Exception:
            # Return None if we can't find the original events
            return None
        hoster = guild.get_member(data["hoster"])
        if not hoster:
            return None
        members = []
        for m, p_class in data["members"]:
            mem = guild.get_member(m)
            if not mem:
                continue
            members.append((mem, p_class))

        max_slots = None
        if "max_slots" in data:
            max_slots = data["max_slots"]
        return cls(
            hoster,
            members,
            data["event"],
            max_slots,
            guild.get_member(data["approver"]),
            message,
            channel
        )

    def to_json(self):
        return {
            "hoster": self.hoster.id,
            "members": [(m.id, p_class) for m, p_class in self.members],
            "event": self.event,
            "max_slots": self.max_slots,
            "approver": self.approver.id if self.approver else None,
            "message": self.message.id if self.message else None,
            "channel": self.channel.id if self.channel else None
        }


class ValidImage(Converter):
    async def convert(self, ctx, argument):
        search = IMAGE_LINKS.search(argument)
        if not search:
            raise BadArgument("That's not a valid image link.")
        else:
            return argument
