from typing import List, Optional
from sqlalchemy import ForeignKey, String, Text, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(Text, unique=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(String(255))
    desc: Mapped[Optional[str]] = mapped_column(Text)
    length: Mapped[int]

    captions: Mapped[List["Frame"]] = relationship(cascade="all, delete")
    audio_texts: Mapped[List["AudioText"]] = relationship(cascade="all, delete")

    def __repr__(self) -> str:
        return f"Video(id={self.id!r}, title={self.title!r}, url={self.url!r}, author={self.author!r}, desc={self.desc!r}, length={self.length!r})"


class AudioText(Base):
    __tablename__ = "audio_texts"
    __table_args__ = (
        CheckConstraint("start_time < end_time", name="start_end_time_chk"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    start_time: Mapped[int]
    end_time: Mapped[int]
    text: Mapped[str] = mapped_column(Text)

    video_id: Mapped[int] = mapped_column(ForeignKey("videos.id"))


class Frame(Base):
    __tablename__ = "frames"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[int]
    frame_path: Mapped[str] = mapped_column(Text)

    video_id: Mapped[int] = mapped_column(ForeignKey("videos.id"))


# Legacy
# class Caption(Base):
#     __tablename__ = "captions"
#     id: Mapped[int] = mapped_column(primary_key=True)
#     timestamp: Mapped[int]
#     caption: Mapped[str] = mapped_column(Text)

#     video_id: Mapped[int] = mapped_column(ForeignKey("videos.id"))

#     def __repr__(self) -> str:
#         return f"Caption(id={self.id!r}, timestamp={self.timestamp!r}, caption={self.caption!r}, video_id={self.video_id!r})"
