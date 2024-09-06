from dotenv import load_dotenv
import os
from llama_index.core import SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex,Document
from llama_index.llms.gemini import Gemini
from llama_index.core import ServiceContext
from IPython.display import display, Markdown
from PIL import Image
from bs4 import BeautifulSoup
import os
import pytesseract
import requests
import urllib.parse

# 환경변수 가져오기(API key)
load_dotenv()

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

# 멀티 턴 대화를 위한 history 리스트
history = []

# 질문에 대한 응답을 받는 함수 ask_query
def ask_query(query, history):
    # 대화 히스토리에 현재 쿼리를 추가
    history.append({"role": "user", "content": query})
    
    # 대화 히스토리를 문자열로 병합
    formatted_history = "\n".join([f"{item['role']}: {item['content']}" for item in history])
    
    # 쿼리 엔진에 현재 히스토리를 전달하여 응답 생성
    response = query_engine.query(formatted_history)
     
    # 응답을 히스토리에 추가
    history.append({"role": "ai", "content": response})
    
    return response

# 문서의 형식 = 텍스트 
# tesseract 를 사용하기 위해서는 따로 설치를 하여야 합니다
# 튜토리얼 : https://www.allmyuniverse.com/implementing-python-ocr-with-tesseract/ 
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

image_dir = r'data_png'

doc2_text = " "

for filename in os.listdir(image_dir):
    if (filename.endswith(".png")):
        image_path = os.path.join(image_dir,filename)
        try:
            text = pytesseract.image_to_string(Image.open(image_path), lang='kor')
            doc2_text += text + "\n\n"

            print(f"Text from{filename}")
        except Exception as e:
            print(f"Error in {filename}")

#PDF크롤링
import os
import requests
import urllib.parse
from bs4 import BeautifulSoup

def crawing_pdfs():
    for i in range(1,3):

        url = f"https://www.imokorea.org/board/board.asp?page={i}&bandStart=1&findStr=&findBase=&findType=&B_ID=ordinance&ty=list"
        data_folder = r"data_pdf"

        # 웹 페이지의 HTML 가져오기
        html = requests.get(url)
        html.raise_for_status()

        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(html.text, 'html.parser')

        # 모든 링크 찾기
        pdf_links = soup.find_all('a', href=True)

        # PDF 링크만 필터링하여 다운로드
        for link in pdf_links:
            href = link['href']
            if href.endswith('.pdf'):
                # 처음 만난 url 의 이름 
                print(href)

                # 웬진 모르겠지만 이런 형식을 요구하니 필요한 부분만 남기기 
                url = href
                modified_url = url.replace('/board/downLoad.asp?filename=', '')
                print(modified_url)

                # euc-kr 방식으로 인코딩 해주기
                encode_fname_url = urllib.parse.quote(modified_url.encode('euc-kr'))
                print(encode_fname_url)
                final_encoded_url = f"{"https://www.imokorea.org/upfiles/board/"}{encode_fname_url}"
                print(final_encoded_url)

                # 저장할 파일 이름과 경로 설정
                pdf_name = url.split('=')[-1]
                print(pdf_name)
                pdf_path = os.path.join(data_folder, pdf_name)

                # PDF 파일 다운로드
                try:
                    with requests.get(final_encoded_url, stream=True) as r:
                        r.raise_for_status()
                        with open(pdf_path, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                    print(f"Downloaded: {final_encoded_url}")
                except Exception as e:
                    print(f"Failed to download {final_encoded_url}: {e}")

crawing_pdfs()

# PNG 업로드
# 객체로 변환하기 
doc2 = Document(text=doc2_text)
# Document 객체 출력
print(doc2)

# 학습 데이터 위치 설정 후 불러오기
input_dir = r"data_pdf"
reader = SimpleDirectoryReader(input_dir=input_dir)
doc1 = reader.load_data()

# 파일 결합
doc1 += doc2

# 입베딩 다운로드
embed_model_ko = HuggingFaceEmbedding(model_name="bespin-global/klue-sroberta-base-continue-learning-by-mnr") 

# llama index 설정
llm = Gemini(model_name='models/gemini-1.5-flash', request_timeout=120.0)

service_context = ServiceContext.from_defaults(llm=llm, chunk_size=800, chunk_overlap=20, embed_model=embed_model_ko)
index = VectorStoreIndex.from_documents(doc1,service_context=service_context,show_progress=True)

index.storage_context.persist()

query_engine = index.as_query_engine()



