from sqlalchemy import create_engine, select, and_
from db_models import Base, Video, Caption, AudioText
from sqlalchemy.orm import Session


# Create engine and session
def connect_db(user, password):
    engine = create_engine(
        f"postgresql://{user}:{password}@localhost/companion", echo=True
    )
    Base.metadata.create_all(engine)  # create tables if don't exist
    return engine


def add_data(engine, video: dict, captions: list[str], audio_texts: list[tuple]):
    # Add video data
    with Session(engine) as session:
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
            res = Caption(timestamp=(time + 1), caption=caption, video_id=vid_obj.id)
            rows.append(res)

        session.add_all(rows)
        session.commit()

        # Add audio transcription
        rows = []
        for start_t, end_t, txt in audio_texts:
            res = AudioText(
                start_time=start_t, end_time=end_t, text=txt, video_id=vid_obj.id
            )
            rows.append(res)

        session.add_all(rows)
        session.commit()


def db_get_captions(engine, video_url, start_sec, curr_sec):
    with Session(engine) as session:
        video = session.scalars(select(Video).filter_by(url=video_url).limit(1)).first()

        if not video:
            print("No video found with the given URL")
            return None

        # query the Caption table for captions within the specified timestamp range
        captions = session.scalars(
            select(Caption)
            .filter(
                and_(
                    Caption.video_id == video.id,
                    Caption.timestamp.between(start_sec, curr_sec),
                )
            )
            .order_by(Caption.timestamp)
        ).all()

    return [caption.caption for caption in captions]


def db_get_transcript(engine, video_url, start_sec, curr_sec):
    pass


# import os
# from dotenv import load_dotenv

# load_dotenv()
# db_user = os.getenv("DB_USER")
# db_password = os.getenv("DB_PASSWORD")
# yt_url = "https://www.youtube.com/watch?v=hn0cygb3GLo"

# engine = connect_db(db_user, db_password)
# captions = db_get_captions(engine, yt_url, 295, 300)
