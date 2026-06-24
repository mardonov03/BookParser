import logging

import fitz

class ParserService:
    async def parser(self, content, filename):
        try:
            if filename.endswith('.pdf'):
                doc = fitz.open(stream=content, filetype="pdf")
                return await self.pdf2json(doc)
            elif filename.endswith('.txt'):
                return await self.txt2json(content)

        except Exception as e:
            logging.error(f'error path: router.py, function: parser, log: {e}')

    async def pdf2json(self, doc):
        return doc.get_toc()

    async def txt2json(self, content):
        pass

    async def take_body(self):
        pass