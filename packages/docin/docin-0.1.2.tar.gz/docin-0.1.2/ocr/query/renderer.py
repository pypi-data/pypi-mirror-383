from spacy.tokens import Doc
from IPython.display import display, HTML
from spacy import displacy
import spacy # Import spacy to create a blank model

# Load a spaCy model with a lemmatizer
# Using 'en_core_web_sm' as a common small model.
# You might need to download it if you haven't: !python -m spacy download en_core_web_sm
try:
    nlp_lemma = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model 'en_core_web_sm'...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp_lemma = spacy.load("en_core_web_sm")


def get_lemma_or_original(text):
    """
    Lemmatizes a single word or returns the original text if lemmatization fails.
    """
    if not text:
        return text
    doc = nlp_lemma(text)
    # Assuming the label is a single word, take the lemma of the first token
    if doc and doc[0].lemma_ != '-PRON-': # Exclude pronoun lemma
        return doc[0].lemma_
    return text # Return original if lemma is pronoun or empty


def find_entity_spans(document, response):
    """
    Finds the start and end indices of entities from LLM response in the document.

    Args:
        document: The original text document string.
        response: A dictionary from the LLM containing entities and their texts.

    Returns:
        A list of dictionaries, where each dictionary represents an entity
        with 'start', 'end', 'label', and 'text' keys.
    """
    entities_for_displacy = []

    for label, texts in response.items():
        if not isinstance(texts, list):
            texts = [texts]

        # Lemmatize the label before finding spans
        lemmatized_label = get_lemma_or_original(label)


        for text_to_find in texts:
            if text_to_find and text_to_find != 'None':
                document_lower = document.lower()
                text_to_find_lower = text_to_find.lower()
                start = 0
                while True:
                    start = document_lower.find(text_to_find_lower, start)
                    if start == -1:
                        break
                    end = start + len(text_to_find_lower)

                    entities_for_displacy.append({
                        "start": start,
                        "end": end,
                        "label": lemmatized_label.lower(), # Use the lemmatized label
                        "text": document[start:end]
                    })
                    start += len(text_to_find_lower)

    return entities_for_displacy

def prepare_displacy_data(document, entities):
    """
    Prepares data and options for displacy rendering.

    Args:
        document: The original text document string.
        entities: A list of dictionaries with entity information.

    Returns:
        A tuple containing the displacy_data dictionary and the options dictionary.
    """
    # Create a blank spaCy Doc object - needed for displacy's data structure
    nlp = spacy.blank("en")
    doc = nlp.make_doc(document)

    # Define colors for displacy
    color = ['red','blue','orange','yellow']
    color_iter = iter(color)
    # Get unique lemmatized entity labels from the entities list
    entity_labels = list(set([ent["label"] for ent in entities]))
    colors = {label: next(color_iter) for label in entity_labels}

    options = {"ents": entity_labels, "colors": colors}

    displacy_data = {
        "text": document,
        "ents": entities,
        "title": None
    }

    return displacy_data, options

def render_displacy_output(displacy_data, options):
    """
    Renders the displacy visualization.

    Args:
        displacy_data: Dictionary containing text and entities for displacy.
        options: Dictionary containing rendering options.

    Returns:
        An IPython.display.HTML object with the displacy rendering.
    """
    return displacy.render(displacy_data, style="ent", jupyter=False, options=options, manual=True)
