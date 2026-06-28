from fastapi import APIRouter, UploadFile, File
from service import ParserService

router = APIRouter()

@router.get('/')
async def test():
    return 'tests'

# start_page: метка от пользователья с какой страницы нужно начать парсинг. если start_page = None то парсим с page 1
# end_page: метка от пользователья до какой страницы нужно парсит. если end_page = None то парсим до последной страницы
# body: нужга ли тело книги (default = True)
# titles: если есть в книге слова которых можно испльзовать как метки то пользователь может указать их для более точного парсинга (пример: Глава)
@router.post('/parser')
async def parser(file: UploadFile = File(...), body: bool = True, titles: str = None, start_page: str = 1, end_page: str = None):
    service = ParserService()
    content = await file.read()
    return await service.parser(content, file.filename, body, titles, start_page, end_page)