from dotenv import load_dotenv
from llmada.core import BianXieAdapter, ArkAdapter
import pytest
import sys
import os
load_dotenv()

class Test_Bianxie:
    @pytest.fixture
    def bianxie(self):
        return BianXieAdapter("gemini-2.5-flash-preview-05-20-nothinking")
    
    # @pytest.mark.skip("通过")
    def test_product(self,bianxie):
        result = bianxie.product('你好')
        print(result,"result")
        
    async def test_aproduct(self,bianxie):
        result = await bianxie.aproduct('你好')
        print(result,"result")


    def test_product_stream(self,bianxie):
        rus = bianxie.product_stream("你好")
        for i in rus:
            print(i)
            assert type(i) == str

    async def test_aproduct_stream(self,bianxie):
        rus = bianxie.aproduct_stream("你好")
        async for i in rus:
            print(i)
            assert type(i) == str


    def test_product_by_dict(self,bianxie):
        data = {
            "model": "gemini-2.5-flash-preview-05-20-nothinking",
            "messages": [{"role": "user", "content": "你好"}],
            "temperature": 0.7,
        }
        result = bianxie.product_by_dict(data)
        print(result,"result")

    async def test_aproduct_by_dict(self,bianxie):
        data = {
            "model": "gemini-2.5-flash-preview-05-20-nothinking",
            "messages": [{"role": "user", "content": "你好"}],
            "temperature": 0.7,
        }
        result = await bianxie.aproduct_by_dict(data)
        print(result,"result")



class Test_Ark:

    @pytest.fixture
    def ark(self):
        return ArkAdapter("doubao-1-5-pro-256k-250115")

    def test_product(self,ark):
        # @pytest.mark.skip("通过")
        result = ark.product(prompt='你好')
        print(result,'result')
        assert type(result) == str

    async def test_aproduct(self,ark):
        result = await ark.aproduct(prompt='你好')
        print(result,'result')
        assert type(result) == str
        
    def test_product_stream(self,ark):
        result = ark.product_stream(prompt='你好')
        print(result,'result')
        for chunk in result:
            print(chunk)
        # assert type(result) == str

    async def test_aproduct_stream(self,ark):
        result = ark.aproduct_stream(prompt='你好')
        async for chunk in result:
            print(chunk)


    async def test_tts(self,ark):
        await ark.tts(text = "我是一个小狗狗",
                filename = "tests/resources/work.wav")


