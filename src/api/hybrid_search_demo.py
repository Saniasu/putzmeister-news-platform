from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from dotenv import load_dotenv
import os

load_dotenv()

# -----------------------------------
# Azure Search configuration
# -----------------------------------

SEARCH_ENDPOINT = "https://putzmeister-search.search.windows.net"
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")
INDEX_NAME = "news-index"

client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=INDEX_NAME,
    credential=AzureKeyCredential(SEARCH_API_KEY)
)

# -------------------------------------------------
# Example query embedding
# -------------------------------------------------
# We reuse an embedding from one of your articles
# simply to demonstrate vector search.

sample_vector = [
    0.03840380534529686,
    0.0019417904550209641,
    0.035385534167289734,
    0.010143198072910309,
    0.04341896250844002,
    0.01258388627320528
]

# IMPORTANT:
# The vector length must exactly match the size
# used in your index.
# We therefore pad remaining values with zeros.

while len(sample_vector) < 384:
    sample_vector.append(0.0)

vector_query = VectorizedQuery(
    vector=sample_vector,
    k_nearest_neighbors=5,
    fields="embedding"
)

results = client.search(
    search_text="Kevin Warsh",
    vector_queries=[vector_query],
    top=5
)

print("\n===== HYBRID SEARCH RESULTS =====\n")

for result in results:
    print("Title:", result.get("title"))
    print("Source:", result.get("source_name"))
    print("Sentiment:", result.get("sentiment_label"))
    print("-" * 80)