from utils.doc_utils.doc_reader_utils import DOC_READERS
from utils.doc_utils.text_splitters_utils import get_text_splitter
from base import configs as cfg
import os

class DocumentLoader:

    def __init__(self):
        self.child_text_splitter = get_text_splitter(
            chunk_size=cfg.CHILD_CHUNK_SIZE,
            chunk_overlap=cfg.CHUNK_OVERLAP
        )
        self.parent_text_splitter = get_text_splitter(
            chunk_size=cfg.PARENT_CHUNK_SIZE,
            chunk_overlap=cfg.CHUNK_OVERLAP
        )

    def load_one_file(self, file_path):
        file_extension = os.path.splitext(file_path)[1].lower()
        file_name = os.path.basename(file_path)
        text = DOC_READERS[file_extension](file_path)
        docs = self.parent_text_splitter.split_text(text)

        for i, doc in enumerate(docs):
            child_docs = self.child_text_splitter.split_text(doc)
            for j, child_doc in enumerate(child_docs):
                yield {
                    "text": child_doc,
                    "source": file_name,
                    "parent_id": f'parent_{i}',
                    "parent_content": doc
                }
    def load_directory(self, directory_path):
        chunks = []
        for file_name in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file_name)
            if os.path.isfile(file_path):
                for chunk in self.load_one_file(file_path):
                    chunks.append(chunk)
        return chunks
if __name__ == '__main__':
    from datas.filepaths import PDFS_DIR
    loader = DocumentLoader()
    chunks = loader.load_directory(PDFS_DIR)
    print(len(chunks))
    # print(chunks[0])