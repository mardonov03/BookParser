import logging

import fitz

class ParserService:
    async def parser(self, content, filename):
        try:
            if filename.endswith('.pdf'):
                return await self.pdf2json()
            elif filename.endswith('.txt'):
                return await self.txt2json()

            # doc = fitz.open(stream=content, filetype="pdf")
        except Exception as e:
            logging.error(f'error path: router.py, function: parser, log: {e}')

    async def txt2json(self):
        pass

    async def pdf2json(self):
        pass

    async def take_body(self):
        pass