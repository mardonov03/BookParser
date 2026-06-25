import logging
import re
import fitz
import json

from starlette.responses import JSONResponse


class ParserService:
    async def parser(self, content, filename, body, titles):
        try:
            if filename.endswith('.pdf'):
                doc = fitz.open(stream=content, filetype="pdf")
                return await self.pdf2json(doc, body, titles)
            elif filename.endswith('.txt'):
                return await self.txt2json(content)

        except Exception as e:
            logging.error(f'error path: router.py, function: parser, log: {e}')

    async def pdf2json(self, doc, body, titles):
        toc = doc.get_toc()
        current_chapter = None
        current_section = None
        mets = []
        mets_json = []
        start_met = []
        count = None
        count_json = []
        structure = {}
        
        for i, entry in enumerate(toc):
            level, title, page = entry
            title_upper = title.upper().strip()

            if title_upper.startswith(titles):

                if not start_met:
                    start_met.append(i)

                parts = title_upper.split()
                chapter_number = parts[1] if len(parts) > 1 and parts[1].isdigit() else parts[0].replace(titles,
                                                                                                         '').strip()

                if chapter_number is None:
                    continue
                next_title = toc[i + 1][1] if i + 1 < len(toc) else title

                if count is None:
                    count = title_upper.lower() + ' ' + next_title.lower()
                    count_json = next_title.lower().replace('\n', '')

                else:
                    mets.append([count, title_upper.lower() + ' ' + next_title.lower()])
                    mets_json.append([count_json, next_title.lower().replace('\n', '')])
                    count = title_upper.lower() + ' ' + next_title.lower()
                    count_json = next_title.strip().lower()

                structure[chapter_number] = {
                    "title": next_title.strip().lower(),
                    "body": "",
                    "sections": {}
                }
                current_chapter = chapter_number
                current_section = None

            elif current_chapter and title[0].isdigit():
                section_number = title.split()[0]
                clean_section_title = title[len(section_number):].strip()

                level = section_number.count('.') if not section_number.endswith('.') else sum(
                    c.isdigit() for c in section_number) - 1

                if level == 1:

                    if count is None:
                        count = section_number.lower() + clean_section_title.lower() if clean_section_title.startswith(
                            '.') else section_number.lower() + ' ' + clean_section_title.lower()
                        count_json = clean_section_title.lower().replace('\n', '')
                    else:
                        mets.append([count,
                                     section_number.lower() + clean_section_title.lower() if clean_section_title.startswith(
                                         '.') else section_number.lower() + ' ' + clean_section_title.lower()])
                        mets_json.append([count_json, clean_section_title.lower().replace('\n', '')])
                        count = section_number.lower() + clean_section_title.lower() if clean_section_title.startswith(
                            '.') else section_number.lower() + ' ' + clean_section_title.lower()
                        count_json = clean_section_title.lower()
                    structure[current_chapter]["sections"][section_number] = {
                        "title": clean_section_title.lower(),
                        "body": "",
                        "subsections": {}
                    }
                    current_section = section_number
                elif level == 2:

                    if count is None:
                        count = section_number.lower() + clean_section_title.lower() if clean_section_title.startswith(
                            '.') else section_number.lower() + ' ' + clean_section_title.lower()
                        count_json = clean_section_title.lower().replace('\n', '')

                    else:
                        mets.append([count,
                                     section_number.lower() + clean_section_title.lower() if clean_section_title.startswith(
                                         '.') else section_number.lower() + ' ' + clean_section_title.lower()])
                        mets_json.append([count_json, clean_section_title.lower().replace('\n', '')])
                        count = section_number.lower() + clean_section_title.lower() if clean_section_title.startswith(
                            '.') else section_number.lower() + ' ' + clean_section_title.lower()
                        count_json = clean_section_title.lower()
                    if current_section and section_number.startswith(current_section):
                        structure[current_chapter]["sections"][current_section]["subsections"][
                            section_number] = {
                            "title": clean_section_title.lower(),
                            "body": "",
                        }
                    else:
                        structure[current_chapter]["sections"][section_number] = {
                            "title": clean_section_title.lower(),
                            "body": "",
                            "subsections": {}
                        }
        if body is True:
            book_text = ''
            processed_pages = set()

            for i2 in range(start_met[0], len(toc)):
                level, title, page = toc[i2]
                if page in processed_pages:
                    continue
                processed_pages.add(page)
                page = doc.load_page(page - 1)
                tex = page.get_text("text").replace('\n', '')
                book_text += tex.lower()

            book_text = re.sub(r'\s{2,}', ' ', book_text).strip()

            for sublist in mets:
                for i in range(len(sublist)):
                    sublist[i] = ' '.join(sublist[i].split())
                    sublist[i] = sublist[i].lower()

            for (start, end), (original_start, original_end) in zip(mets, mets_json):
                body = ''
                if start in book_text:
                    start_index = book_text.index(start) + len(start) + 1
                    if end in book_text:
                        end_index = book_text.index(end)
                        body = book_text[start_index:end_index].strip()

                        for chapter_number, chapter_data in structure.items():
                            if chapter_data['title'] == original_start:
                                structure[chapter_number]['body'] = body
                            else:
                                for section_number, section_data in chapter_data['sections'].items():
                                    if section_data['title'] == original_start:
                                        structure[chapter_number]['sections'][section_number]['body'] = body
                                    else:
                                        for subsection_number, subsection_data in section_data['subsections'].items():
                                            if subsection_data['title'] == original_start:
                                                structure[chapter_number]['sections'][section_number]['subsections'][
                                                    subsection_number]['body'] = body
        return JSONResponse(structure)

    async def txt2json(self, content):
        pass
