# dify_api.py

import requests
import json
import os
import time


class DifyClient:
    def __init__(self, api_key, host, knowledge_ids):
        self.api_key = api_key
        self.host = host
        self.knowledge_ids = knowledge_ids  # Dictionary of {name: id}

    def _get_headers(self):
        """내부적으로 사용할 API 요청 헤더를 생성합니다."""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def get_all_documents(self, knowledge_id):
        """Dify 지식베이스의 모든 문서 ID와 이름을 가져옵니다."""
        all_documents = []
        page = 1
        limit = 100  # 한 번에 100개씩 요청

        list_url = f"{self.host}/datasets/{knowledge_id}/documents"
        headers = self._get_headers()
        # GET 요청에는 Content-Type이 필요하지 않으므로 제거
        if 'Content-Type' in headers:
            del headers['Content-Type']

        while True:
            try:
                print(f"🔍 Dify 문서 목록 조회... (페이지: {page}, 지식베이스 ID: {knowledge_id})")
                params = {'page': page, 'limit': limit, 'retrieval_model': 'all'}
                response = requests.get(list_url, headers=headers, params=params)
                response.raise_for_status()

                data = response.json()
                documents = data.get('data', [])

                if not documents:
                    print("ℹ️ 더 이상 가져올 문서가 없습니다.")
                    break

                all_documents.extend(documents)

                if not data.get('has_more'):
                    break

                page += 1
                time.sleep(0.5)  # 간단한 속도 제한

            except requests.exceptions.RequestException as e:
                print(f"❌ 문서 목록 조회 중 오류 발생 (지식베이스 ID: {knowledge_id}): {e}")
                break

        return all_documents

    def delete_document(self, doc_id, doc_name, knowledge_id):
        """Dify 지식베이스에서 ID를 기준으로 문서를 삭제합니다."""
        delete_url = f"{self.host}/datasets/{knowledge_id}/documents/{doc_id}"
        headers = self._get_headers()

        if 'Content-Type' in headers:
            del headers['Content-Type']

        try:
            response = requests.delete(delete_url, headers=headers)

            # 204 (No Content)와 200 (OK)을 모두 성공으로 처리
            if response.status_code in [204, 200]:
                print(f"  -> ✅ 삭제 성공 (HTTP {response.status_code}): {doc_name} (ID: {doc_id})")
                return True
            else:
                print(f"  -> ❌ 삭제 실패: {doc_name} (ID: {doc_id}) - {response.status_code} {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"  -> ❌ 문서 삭제 중 API 오류 발생: {e}")
            return False

    def clear_all_documents(self, knowledge_id):
        """지식베이스의 모든 문서를 삭제합니다."""
        print(f"--- 🧹 Dify 지식베이스 청소 시작 (ID: {knowledge_id}) ---")

        documents = self.get_all_documents(knowledge_id)

        if not documents:
            print("ℹ️ 삭제할 문서가 없습니다.")
            print(f"--- 🧹 Dify 지식베이스 청소 완료 (ID: {knowledge_id}) ---")
            return

        print(f"총 {len(documents)}개의 문서를 삭제합니다...")

        deleted_count = 0
        for doc in documents:
            doc_id = doc.get('id')
            doc_name = doc.get('name', '알 수 없는 문서')

            if doc_id:
                if self.delete_document(doc_id, doc_name, knowledge_id):
                    deleted_count += 1
                time.sleep(0.5)

        print(f"총 {deleted_count}개의 문서가 성공적으로 삭제되었습니다.")
        print(f"--- 🧹 Dify 지식베이스 청소 완료 (ID: {knowledge_id}) ---")

    def upload_file_to_dify(self, doc_name, file_content, original_file_name, knowledge_id):
        """[파일]을 Dify 지식베이스에 업로드합니다."""
        print(f"🚀 Dify 파일 업로드 시작: {doc_name} (지식베이스 ID: {knowledge_id})")

        _, extension = os.path.splitext(original_file_name)
        new_file_name = f"{doc_name}{extension}"
        url = f"{self.host}/datasets/{knowledge_id}/document/create-by-file"

        headers = self._get_headers()

        if 'Content-Type' in headers:
            del headers['Content-Type']

        files = {
            'file': (new_file_name, file_content)
        }

        metadata = {
            "name": doc_name,
            "indexing_technique": "high_quality",  # 파일 업로드는 이게 맞음
            "process_rule": {
                "mode": "automatic"
            }
        }

        data = {
            'data': json.dumps(metadata)
        }

        try:
            response = requests.post(url, headers=headers, data=data, files=files)

            if response.status_code in [200, 201]:
                print(f"✅ 업로드 성공!")
                return True
            else:
                print(f"❌ 업로드 실패: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Dify API 호출 중 오류 발생: {e}")
            return False

    # ✨ [수정] 텍스트 업로드 기능
    def upload_text_to_dify(self, doc_name, text_content, knowledge_id):
        """[텍스트]를 Dify 지식베이스에 업로드합니다."""
        print(f"🚀 Dify 텍스트 업로드 시작: {doc_name} (지식베이스 ID: {knowledge_id})")

        url = f"{self.host}/datasets/{knowledge_id}/document/create-by-text"
        headers = self._get_headers()  # Content-Type: application/json 포함

        payload = {
            "name": doc_name,
            "text": text_content,
            # ✨ [수정] 'high-quality' (하이픈) -> 'high_quality' (언더바)
            "indexing_technique": "high_quality",
            "process_rule": {
                "mode": "automatic"
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload)

            if response.status_code in [200, 201]:
                print(f"✅ 업로드 성공!")
                return True
            else:
                print(f"❌ 업로드 실패: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Dify API 호출 중 오류 발생: {e}")
            return False