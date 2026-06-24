import fitz
import json
import asyncio
import warnings
import re
book_folder = '../test/books/Руководство_Бухгалтерия_для_Узбекистана_ред_3_0.pdf'
# book_folder = '../test/books/book.txt'
structure = {}
titles = 'ГЛАВА'

#значение True добавит тело к статьям при создании JSON если вам это не нужно переключите на False
ifuneed_body = True

async def take_book(book_folder):
    try:
        if book_folder:
            if book_folder.endswith('.pdf'):
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                reader = fitz.open(book_folder)
                return reader

            elif book_folder.endswith('.txt'):
                with open(book_folder, 'r', encoding='utf-8') as book:
                    content = book.read()
                return content
    except Exception as e:
        print(f'error324524 {e}')
        return None

async def book_to_json():
    global book_folder, structure, titles, ifuneed_body
    try:
        if book_folder is None:
            print('book_folder is None')
            return

        book = await take_book(book_folder)
        if book is None:
            print('book is None')
            return

        if isinstance(book, fitz.Document):
            toc = book.get_toc()
            current_chapter = None
            current_section = None
            mets = []
            mets_json = []
            start_met = []
            count = None
            count_json = []

            for i, entry in enumerate(toc):
                level, title, page = entry
                title_upper = title.upper().strip()

                if title_upper.startswith(titles):

                    if not start_met:
                        start_met.append(i)

                    parts = title_upper.split()
                    chapter_number = parts[1] if len(parts) > 1 and parts[1].isdigit() else parts[0].replace(titles,'').strip()

                    if chapter_number is None:
                        continue
                    next_title = toc[i + 1][1] if i + 1 < len(toc) else title

                    if count is None:
                        count = title_upper.lower() + ' ' + next_title.lower()
                        count_json = next_title.lower().replace('\n','')

                    else:
                        mets.append([count, title_upper.lower() + ' ' + next_title.lower()])
                        mets_json.append([count_json, next_title.lower().replace('\n','')])
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

                    level = section_number.count('.') if not section_number.endswith('.') else sum(c.isdigit() for c in section_number)-1

                    if level == 1:

                        if count is None:
                            count = section_number.lower() + clean_section_title.lower() if clean_section_title.startswith('.') else section_number.lower() + ' ' + clean_section_title.lower()
                            count_json = clean_section_title.lower().replace('\n','')
                        else:
                            mets.append([count,section_number.lower() + clean_section_title.lower() if clean_section_title.startswith('.') else section_number.lower() + ' ' + clean_section_title.lower()])
                            mets_json.append([count_json, clean_section_title.lower().replace('\n','')])
                            count = section_number.lower() + clean_section_title.lower() if clean_section_title.startswith('.') else section_number.lower() + ' ' + clean_section_title.lower()
                            count_json = clean_section_title.lower()
                        structure[current_chapter]["sections"][section_number] = {
                            "title": clean_section_title.lower(),
                            "body": "",
                            "subsections": {}
                        }
                        current_section = section_number
                    elif level == 2:

                        if count is None:
                            count = section_number.lower() + clean_section_title.lower() if clean_section_title.startswith('.') else section_number.lower() + ' ' + clean_section_title.lower()
                            count_json = clean_section_title.lower().replace('\n','')

                        else:
                            mets.append([count,section_number.lower() + clean_section_title.lower() if clean_section_title.startswith('.') else section_number.lower() + ' ' + clean_section_title.lower()])
                            mets_json.append([count_json, clean_section_title.lower().replace('\n','')])
                            count = section_number.lower() + clean_section_title.lower() if clean_section_title.startswith('.') else section_number.lower() + ' ' + clean_section_title.lower()
                            count_json = clean_section_title.lower()
                        if current_section and section_number.startswith(current_section):
                            structure[current_chapter]["sections"][current_section]["subsections"][section_number] = {
                                "title": clean_section_title.lower(),
                                "body": "",
                            }
                        else:
                            structure[current_chapter]["sections"][section_number] = {
                                "title": clean_section_title.lower(),
                                "body": "",
                                "subsections": {}
                            }
            if ifuneed_body is True:
                book_text = ''
                processed_pages = set()

                for i2 in range(start_met[0], len(toc)):
                    level, title, page = toc[i2]
                    if page in processed_pages:
                        continue
                    processed_pages.add(page)
                    page = book.load_page(page - 1)
                    tex = page.get_text("text").replace('\n', '')
                    book_text += tex.lower()

                book_text = re.sub(r'\s{2,}', ' ', book_text).strip()

                await take_body(structure, mets, mets_json, book_text)

            with open('book_structure.json', 'w', encoding='utf-8') as json_file:
                json.dump(structure, json_file, ensure_ascii=False, indent=4)

        elif isinstance(book, str):
            paragraphs = [p.strip() for p in book.split('\n') if p.strip()]
            structure = {}
            current_chapter = None
            current_section = None
            mets = []
            mets_json = []
            start_met = []
            count = None
            count_json = []

            for index, paragraph in enumerate(paragraphs):
                words = paragraph.split()
                for word in words:
                    if titles in word:
                        chapter_pos = word.find(titles)

                        if len(word) > chapter_pos + 5 and word[chapter_pos + 5:].isdigit():
                            chapter_number = word[chapter_pos + 5:]
                            title_text = " ".join(words[words.index(word) + 1:]).strip()
                        elif chapter_pos == 0 and len(words) > words.index(word) + 1 and words[
                            words.index(word) + 1].isdigit():
                            chapter_number = words[words.index(word) + 1]
                            title_text = " ".join(words[words.index(word) + 2:]).strip()
                        else:
                            continue

                        if not title_text and index + 1 < len(paragraphs):
                            title_text = paragraphs[index + 1].strip()

                        uppercase_count = sum(1 for char in title_text if char.isupper())

                        chapter_title = title_text
                        if uppercase_count > 3:
                            next_index = index + 1
                            stop = False

                            while next_index < len(paragraphs) and not stop:
                                next_paragraph = paragraphs[next_index].strip().split()

                                for next_word in next_paragraph:
                                    if next_word.isupper():
                                        chapter_title += " " + next_word
                                    else:
                                        stop = True
                                        break
                                next_index += 1

                        chapter_title_words = chapter_title.split()
                        unique_words = []
                        for word in chapter_title_words:
                            if word not in unique_words:
                                unique_words.append(word)
                        chapter_title = " ".join(unique_words)

                        if chapter_number not in structure:
                            current_chapter = chapter_number

                            if not start_met:
                                start_met.append(book.index(paragraphs[index])+5)

                            if count is None:
                                count = titles.lower()+' '+chapter_number + ' ' + chapter_title.lower()
                                count_json = chapter_title.lower().replace('\n', '')

                            else:
                                mets.append([count, titles.lower()+' '+chapter_number + ' ' + chapter_title.lower()])
                                mets_json.append([count_json, chapter_title.lower().replace('\n', '')])
                                count = titles.lower()+' '+chapter_number + ' ' + chapter_title.lower()
                                count_json = chapter_title.strip().lower()

                            structure[current_chapter] = {
                                "title": chapter_title.strip().lower(),
                                "body": "",
                                "sections": {}
                            }
                            current_section = None
                if current_chapter:
                    for word in words:
                        section_number = ''.join(char for char in word if char.isdigit() or char == '.')
                        section_title = " ".join(words[words.index(word) + 1:]).strip()

                        uppercase_count = sum(1 for char in section_title if char.isupper())

                        chapter_title_secs = section_title
                        if uppercase_count > 3:
                            next_index = index + 1
                            stop = False

                            while next_index < len(paragraphs) and not stop:
                                next_paragraph = paragraphs[next_index].strip().split()

                                for next_word in next_paragraph:
                                    if next_word.isupper():
                                        chapter_title_secs += " " + next_word
                                    else:
                                        stop = True
                                        break
                                next_index += 1
                            chapter_title_words_secs = chapter_title_secs.split()
                            unique_words = []
                            for word in chapter_title_words_secs:
                                if word not in unique_words:
                                    unique_words.append(word)
                            chapter_title_secs = " ".join(unique_words)
                        else:
                            chapter_title_secs = paragraphs[index].replace(str(section_number),'').strip()

                        if not chapter_title_secs and index + 1 < len(paragraphs):
                            chapter_title_secs = paragraphs[index + 1].strip()

                        if section_number.startswith(current_chapter + "."):
                            meaningful_dot_count = section_number.count('.') if not section_number.endswith('.') else sum(c.isdigit() for c in section_number)-1

                            if meaningful_dot_count == 1:

                                if count is None:
                                    count = section_number.lower() + chapter_title_secs.lower() if chapter_title_secs.startswith('.') else section_number.lower() + ' ' + chapter_title_secs.lower()
                                    count_json = chapter_title_secs.lower().replace('\n', '')
                                else:
                                    mets.append([count,section_number.lower() + chapter_title_secs.lower() if chapter_title_secs.startswith('.') else section_number.lower() + ' ' + chapter_title_secs.lower()])
                                    mets_json.append([count_json, chapter_title_secs.lower().replace('\n', '')])
                                    count = section_number.lower() + chapter_title_secs.lower() if chapter_title_secs.startswith('.') else section_number.lower() + ' ' + chapter_title_secs.lower()
                                    count_json = chapter_title_secs.lower()

                                structure[current_chapter]["sections"][section_number] = {
                                    "title": chapter_title_secs.lower(),
                                    "body": "",
                                    "subsections": {}
                                }
                                current_section = section_number
                            elif meaningful_dot_count == 2 and current_section:
                                if count is None:
                                    count = section_number.lower() + chapter_title_secs.lower() if chapter_title_secs.startswith('.') else section_number.lower() + ' ' + chapter_title_secs.lower()
                                    count_json = chapter_title_secs.lower().replace('\n', '')
                                else:
                                    mets.append([count,section_number.lower() + chapter_title_secs.lower() if chapter_title_secs.startswith('.') else section_number.lower() + ' ' + chapter_title_secs.lower()])
                                    mets_json.append([count_json, chapter_title_secs.lower().replace('\n', '')])
                                    count = section_number.lower() + chapter_title_secs.lower() if chapter_title_secs.startswith('.') else section_number.lower() + ' ' + chapter_title_secs.lower()
                                    count_json = chapter_title_secs.lower()

                                structure[current_chapter]["sections"][current_section]["subsections"][
                                    section_number] = {
                                    "title": chapter_title_secs.lower(),
                                    "body": ""
                                }
            if ifuneed_body is True:
                book_text = ''
                for i in range(start_met[0],len(book)):
                    book_text+=book[i].lower()

                tex = book_text.replace('\n', ' ')
                book_text = re.sub(r'\s{2,}', ' ', tex).strip()

                await take_body(structure, mets, mets_json, book_text)

            with open('book_structure.json', 'w', encoding='utf-8') as json_file:
                json.dump(structure, json_file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f'error9685073: {e}')

async def take_body(structure,mets,mets_json,book_text):
    try:
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
    except Exception as e:
        print(f'error87549873: {e}')

asyncio.run(book_to_json())
