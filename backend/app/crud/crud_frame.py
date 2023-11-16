from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from models import Frame


class CRUDFrame:
    def __init__(self, model):
        self.model = model

    def get(
        self, db: Session, video_id: int, start_sec: int, end_sec: int
    ) -> list[str]:
        # get frames within the specified timestamp range
        frames = db.scalars(
            select(Frame.frame_path)
            .filter(
                and_(
                    Frame.video_id == video_id,
                    Frame.timestamp.between(start_sec, end_sec),
                )
            )
            .order_by(Frame.timestamp)
        ).all()

        return frames

    def create(self, db: Session, vid_id: int, output_dir: str) -> list[Frame]:
        rows = []
        for time, frame_file in enumerate(os.listdir(output_dir)):
            frame_path = os.path.join(output_dir, frame_file)

            res = Frame(timestamp=(time + 1), frame_path=frame_path, video_id=vid_id)
            rows.append(res)

        db.add_all(rows)
        db.flush()
        return rows


frame = CRUDFrame(Frame)
frame.get
