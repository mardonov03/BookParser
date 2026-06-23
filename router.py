from fastapi import APIRouter, UploadFile, File
from service import ParserService as service

router = APIRouter()

@router.get('/')
async def test():
    return 'test'

@router.post('/parser')
async def parser(file: UploadFile = File(...)):
    content = await file.read()
    return await service.parser(content, file.filename)