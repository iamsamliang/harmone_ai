from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Video


class CRUDVideo:
    def __init__(self, model):
        self.model = model

    def get(self, db: Session, yt_url: str) -> Video | None:
        """Return video from this url | None

        Args:
            db: DB Session
            yt_url (str): URL of YouTube video

        Returns:
            Video of url | None
        """
        return db.scalars(select(Video).filter_by(url=yt_url).limit(1)).first()

    def create(self, db: Session, video: dict, yt_url: str) -> Video:
        """Assumes we only create a video that doesn't exist and add to DB"""
        vid_obj = Video(
            title=video["title"],
            url=video["url"],
            author=video["author"],
            desc=video["desc"],
            length=video["length"],
        )
        db.add(vid_obj)
        db.flush()
        return vid_obj


video = CRUDVideo(Video)
