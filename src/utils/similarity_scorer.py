from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from transformers import pipeline

translation_pipeline = pipeline("translation", model="Helsinki-NLP/opus-mt-bn-en")
similarity_model = SentenceTransformer("all-mpnet-base-v2")


def get_translation(sentence_list: list[str]) -> list[str]:
    """Returns translations for each sentence in the sentence_list. The sentences are
    expected to be in bangla language

    Args:
        sentence_list (list[str]): list of bangla sentences

    Returns:
        list[str]: list of english translated sentences
    """
    # Removing empty strings for sentence_list
    sentence_list = [sentence.strip() for sentence in sentence_list if sentence]
    model_output: list[dict[str, str]] = translation_pipeline(sentence_list)
    return [x["translation_text"] for x in model_output]


def find_similar_sentences(sentence_dict: dict[str, str]) -> dict[str, dict[str, str]]:
    """Using Sentence Transformer, sentences with similar contexts will be found.
    It will be done by turning each sentence into an embedding and then
    performing agglomerative clustering

    Args:
        sentence_dict (dict[str, str]): the list of sentences with each having a unique id

    Returns:
        dict[str, dict[str, str]]: the key is a number, the value is a dict of similar sentences, each with unique id
    """
    embeddings = similarity_model.encode(sentences=list(sentence_dict.values()))

    # Checking similarity score using Agglomerative clustering
    clustering = AgglomerativeClustering(n_clusters=None, distance_threshold=0.3, metric="cosine", linkage="average")
    labels = clustering.fit_predict(embeddings)

    clusters: dict[str, dict[str, str]] = {}
    for id, sentence, label in zip(sentence_dict.keys(), sentence_dict.values(), labels):
        if str(label) in clusters:
            clusters[str(label)][id] = sentence
        else:
            clusters[str(label)] = {id: sentence}

    return clusters
