from sqlalchemy import create_engine, select, and_, func, or_
from db_models import Base, Video, Caption, AudioText
from sqlalchemy.orm import Session


# Create engine and session
def connect_db(user: str, password: str):
    """Connect to PostgreSQL database

    Args:
        user (str): Username
        password (str): Password for the user

    Returns:
        Engine: The engine to connect to DB
    """
    engine = create_engine(
        f"postgresql://{user}:{password}@localhost/companion", echo=True
    )
    Base.metadata.create_all(engine)  # create tables if don't exist
    return engine


def exists(engine, yt_url: str):
    """Check if the video w/ this url already exists in the database

    Args:
        engine (Engine): Engine to connect to DB
        yt_url (str): URL of YouTube video

    Returns:
        bool: If video exists in DB
    """
    with Session(engine) as session:
        return (
            session.scalars(select(Video).filter_by(url=yt_url).limit(1)).first()
            is not None
        )


def add_data(engine, video: dict, captions: list[str], audio_texts: list[tuple]):
    """Add video, captions, and audio-as-text to the DB if they don't already exist

    Args:
        engine (Engine): Engine to connect to DB
        video (dict): video information
        captions (list[str]): captions
        audio_texts (list[tuple]): video transcription
    """
    with Session(engine) as session:
        vid_obj = session.scalars(
            select(Video).filter_by(url=video["url"]).limit(1)
        ).first()

        # don't add duplicates
        if vid_obj is None:
            print(f"\n\nAdding video and captions\n\n")
            vid_obj = Video(
                title=video["title"],
                url=video["url"],
                author=video["author"],
                desc=video["desc"],
                length=video["length"],
            )
            session.add(vid_obj)
            session.commit()

            # Add caption data
            rows = []
            for time, caption in enumerate(captions):  # assume caption in order
                res = Caption(
                    timestamp=(time + 1), caption=caption, video_id=vid_obj.id
                )
                rows.append(res)

            session.add_all(rows)
            session.commit()

            # Add audio transcription
            print(f"\n\nAdding audio transcript\n\n")
            rows = []
            for start_t, end_t, txt in audio_texts:
                res = AudioText(
                    start_time=start_t, end_time=end_t, text=txt, video_id=vid_obj.id
                )
                rows.append(res)

            session.add_all(rows)
            session.commit()


def db_get_captions(engine, video_url, start_sec, curr_sec):
    """Return captions corresponding to video_url in the time interval [start_sec, curr_sec]

    Args:
        engine (Engine): Engine to connect to DB
        video_url (str): YouTube video URL
        start_sec (int): Start of time interval (seconds)
        curr_sec (int): End of time interal (seconds)

    Returns:
        list[str]: list of captions in sequential order
    """
    with Session(engine) as session:
        video = session.scalars(select(Video).filter_by(url=video_url).limit(1)).first()

        if not video:
            print("No video found with the given URL")
            return None

        # query the Caption table for captions within the specified timestamp range
        captions = session.scalars(
            select(Caption.caption)
            .filter(
                and_(
                    Caption.video_id == video.id,
                    Caption.timestamp.between(start_sec, curr_sec),
                )
            )
            .order_by(Caption.timestamp)
        ).all()

    return captions


def db_get_transcript(engine, video_url, start_sec, end_sec):
    """Return audio-as-text corresponding to video_url in the time interval [start_sec, curr_sec]. Also include what was said from the largest non-completely overlapped time interval.

    Args:
        engine (Engine): Engine to connect to DB
        video_url (str): YouTube video URL
        start_sec (int): Start of time interval (seconds)
        end_sec (int): End of time interval (seconds)

    Returns:
        list[str]: list of audio-as-text in sequential order
    """
    with Session(engine) as session:
        video = session.scalars(select(Video).filter_by(url=video_url).limit(1)).first()

        ################################################################################################################

        overlap_duration = func.least(AudioText.end_time, end_sec) - func.greatest(
            AudioText.start_time, start_sec
        )

        # subquery to find the duration of the largest overlap
        largest_overlap_duration_subq = (
            session.query(func.max(overlap_duration).label("max_overlap_duration"))
            .filter(
                or_(
                    and_(
                        AudioText.start_time < start_sec, AudioText.end_time > start_sec
                    ),
                    and_(AudioText.start_time < end_sec, AudioText.end_time > end_sec),
                ),
                and_(AudioText.video_id == video.id),
            )
            .subquery()
        )

        ################################################################################################################

        # query for intervals with the largest overlap duration
        intervals_with_largest_overlap = session.scalars(
            select(AudioText)
            .where(
                or_(
                    and_(
                        AudioText.start_time < start_sec, AudioText.end_time > start_sec
                    ),
                    and_(AudioText.start_time < end_sec, AudioText.end_time > end_sec),
                ),
                and_(
                    AudioText.video_id == video.id,
                    overlap_duration
                    == largest_overlap_duration_subq.c.max_overlap_duration,
                ),
            )
            .order_by(AudioText.start_time.asc())
        ).all()

        ################################################################################################################

        # query for completely overlapped intervals
        completely_overlapped_intervals = session.scalars(
            select(AudioText.text)
            .where(
                and_(
                    AudioText.start_time >= start_sec,
                    AudioText.end_time <= end_sec,
                    AudioText.video_id == video.id,
                )
            )
            .order_by(AudioText.start_time.asc())
        ).all()

        ################################################################################################################

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


# import os
# from dotenv import load_dotenv

# load_dotenv()
# db_user = os.getenv("DB_USER")
# db_password = os.getenv("DB_PASSWORD")
# yt_url = "https://www.youtube.com/watch?v=hn0cygb3GLo"

# engine = connect_db(db_user, db_password)
# res = db_get_transcript(engine, yt_url, 311, 345)
# print("\n\n\n")
# print(" ".join(res))
