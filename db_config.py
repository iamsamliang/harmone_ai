from sqlalchemy import create_engine
from db_models import Base, Video, Caption
from sqlalchemy.orm import Session


# Create engine and session
def connect_db(user, password):
    engine = create_engine(
        f"postgresql://{user}:{password}@localhost/companion", echo=True
    )
    Base.metadata.create_all(engine)  # create tables if don't exist
    return engine


def add_data(engine, video: dict, captions: list[str]):
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


def get_captions(engine, video_id):
    pass
