from fastapi import APIRouter, UploadFile, File
from service import ParserService

router = APIRouter()

@router.get('/')
async def test():
    return 'tests'

@router.post('/parser')
async def parser(file: UploadFile = File(...), body: bool = True, titles: str = None):
    service = ParserService()
    content = await file.read()
    return await service.parser(content, file.filename, body, titles)