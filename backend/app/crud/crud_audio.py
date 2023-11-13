from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import Session

from backend.app.models import AudioText


class CRUDAudioText:
    def __init__(self, model):
        self.model = model

    def get(
        self, db: Session, video_id: int, start_sec: int, end_sec: int
    ) -> list[str]:
        overlap_duration = func.least(AudioText.end_time, end_sec) - func.greatest(
            AudioText.start_time, start_sec
        )

        # subquery to find the duration of the largest overlap
        largest_overlap_duration_subq = (
            db.query(func.max(overlap_duration).label("max_overlap_duration"))
            .filter(
                or_(
                    and_(
                        AudioText.start_time < start_sec, AudioText.end_time > start_sec
                    ),
                    and_(AudioText.start_time < end_sec, AudioText.end_time > end_sec),
                ),
                and_(AudioText.video_id == video_id),
            )
            .subquery()
        )

        ###################################################################################################

        # query for intervals with the largest overlap duration
        intervals_with_largest_overlap = db.scalars(
            select(AudioText)
            .where(
                or_(
                    and_(
                        AudioText.start_time < start_sec, AudioText.end_time > start_sec
                    ),
                    and_(AudioText.start_time < end_sec, AudioText.end_time > end_sec),
                ),
                and_(
                    AudioText.video_id == video_id,
                    overlap_duration
                    == largest_overlap_duration_subq.c.max_overlap_duration,
                ),
            )
            .order_by(AudioText.start_time.asc())
        ).all()

        ###################################################################################################

        # query for completely overlapped intervals
        completely_overlapped_intervals = db.scalars(
            select(AudioText.text)
            .where(
                and_(
                    AudioText.start_time >= start_sec,
                    AudioText.end_time <= end_sec,
                    AudioText.video_id == video_id,
                )
            )
            .order_by(AudioText.start_time.asc())
        ).all()

        ###################################################################################################

        # putting the transcriptions in order by time
        overlap_len = len(intervals_with_largest_overlap)
        if overlap_len == 1:
            elem = intervals_with_largest_overlap[0]
            if elem.start_time < start_sec:
                completely_overlapped_intervals.insert(0, elem.text)
            else:
                completely_overlapped_intervals.append(elem.text)
        elif overlap_len == 2:
            completely_overlapped_intervals.insert(
                0, intervals_with_largest_overlap[0].text
            )
            completely_overlapped_intervals.append(
                intervals_with_largest_overlap[1].text
            )

        return completely_overlapped_intervals

    def create(
        self, db: Session, video_id: int, audio_texts: list[tuple]
    ) -> list[AudioText]:
        rows = []
        for start_t, end_t, txt in audio_texts:
            res = AudioText(
                start_time=start_t, end_time=end_t, text=txt, video_id=video_id
            )
            rows.append(res)

        db.add_all(rows)
        db.flush()
        return rows


audiotext = CRUDAudioText(AudioText)
