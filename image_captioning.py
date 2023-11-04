from langchain.document_loaders import ImageCaptionLoader
from langchain.indexes import VectorstoreIndexCreator
from transformers import pipeline
from datasets import load_dataset
from db_config import connect_db, add_data


def get_captions(image_dir, device):
    # directory = "frames"
    # image_paths = [
    #     os.path.join(directory, file)
    #     for file in sorted(os.listdir(directory))  # sorting is necessary for correct times
    #     if file.endswith(("jpg", "jpeg", "png"))
    # ]

    dataset = load_dataset("imagefolder", data_dir=image_dir)
    dataset = dataset["train"]["image"]
    pipe = pipeline(
        "image-to-text", model="Salesforce/blip-image-captioning-base", device=device
    )
    results = pipe(dataset)
    # data processing
    captions = [item["generated_text"] for result in results for item in result]
    return captions


def store_captions(captions, vid_info, db_user, db_password):
    # connect to database
    engine = connect_db(db_user, db_password)
    add_data(engine, vid_info, captions)


# loader = ImageCaptionLoader(path_images=image_paths)
# list_docs = loader.load()
# print(list_docs)

# index = VectorstoreIndexCreator().from_loaders([loader])
# print(index)

# query = "What is happening in the image?"
# print(index.query(query))
