from pathlib import Path
import sys
from pprint import pprint

import tiktoken


# Allow running this file directly from the test directory.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.chunking import WordChunker, TokenChunker, SentenceChunker
from src.models import Document, Chunk


text = None
encoding = tiktoken.encoding_for_model('gpt-4o')

with open(Path(__file__).resolve().parent / 'data' / 'architecture_of_tomorrow.md', 'r') as fp:
    text = fp.read()

print(f'Loaded text with {len(encoding.encode(text))} tokens')

token_chunker = TokenChunker()

chunks = token_chunker.chunk([Document(
    doc_id='test-doc',
    text=text,
    metadata={}
)])

print(f'splitted into {len(chunks)} chunks')
pprint(chunks[:2])

for i, chunk in enumerate(chunks):
    tokens = encoding.encode(chunk.text)
    print(f'num tokens in chunk {i} = {len(tokens)}')


sentence_chunker = SentenceChunker()

chunks = sentence_chunker.chunk([
    Document(doc_id='test-doc', text=text, metadata={})
])

print("Sentence chunker output: ")
pprint(chunks[:3])