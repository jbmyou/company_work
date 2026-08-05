import re
from pathlib import PurePosixPath

import pandas as pd

path_kcs = r"\\192.168.0.75\스캔파일\스캔파일log\_project\파일\중복조사\kcs별 파일정보_솔림헬프.pkl"
path_write = r"C:\Users\DATA\Desktop\배당공탁전수조사by파일명.xlsx"

# 위 파일을 읽고 파일명에 아래가 포함된 것을 추출하여 엑셀파일로 출력
# 배당 또는 공탁 또는 경매 또는 숫자2이상+금+숫자1이상 또는 숫자2이상+타배+숫자1이상
# 작성할 칼럼 : 문서구분, 매각사구분, 채무자키, 배당확인, 사건, 이름, 파일명, 비고 열을 가진 df를 엑셀파일로 출력
    # 문서구분, 매각사구분, 채무자키는 파일경로에 모두 있는 정보
    # 배당확인 : 빈칸
    # 사건 : 검색된 문구
    # 이름 : 파일명에 채무자키 다음으로 나옴
    # 파일명 : 폴더경로를 제외한 파일명 자체만
    # 비고 : 빈칸


SEARCH_PATTERN = re.compile(r"\d{2,}금\d+|\d{2,}타배\d+|\d{2,}타경\d+|배당|공탁|경매")
OUTPUT_COLUMNS = [
    "문서구분",
    "매각사구분",
    "채무자키",
    "배당확인",
    "사건",
    "이름",
    "파일명",
    "비고",
]


def extract_row(file_path):
    """조건에 맞는 파일경로를 엑셀에 기록할 한 행으로 변환한다."""
    path = PurePosixPath(str(file_path).replace("\\", "/"))
    file_name = path.name
    matches = list(dict.fromkeys(SEARCH_PATTERN.findall(file_name)))
    if not matches:
        return None

    parts = path.parts
    try:
        base_index = parts.index("솔림헬프")
        document_type = parts[base_index + 1]
        seller_type = parts[base_index + 2]
        debtor_key = parts[base_index + 3]
    except (ValueError, IndexError):
        # 예상 경로와 다른 자료는 잘못된 값으로 출력하지 않고 제외한다.
        return None

    stem_parts = path.stem.split("_")
    name = stem_parts[1].strip() if len(stem_parts) > 1 else ""

    return {
        "문서구분": document_type,
        "매각사구분": seller_type,
        "채무자키": debtor_key,
        "배당확인": "",
        "사건": ", ".join(matches),
        "이름": name,
        "파일명": file_name,
        "비고": "",
    }


def main():
    file_info = pd.read_pickle(path_kcs)
    if not isinstance(file_info, dict):
        raise TypeError("pickle 파일은 {고유키: 파일경로} 형식의 dict여야 합니다.")

    rows = []
    skipped_path_count = 0
    for file_path in file_info.values():
        row = extract_row(file_path)
        if row is not None:
            rows.append(row)
        elif SEARCH_PATTERN.search(PurePosixPath(str(file_path).replace("\\", "/")).name):
            skipped_path_count += 1

    result = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    result.to_excel(path_write, index=False)
    print(f"완료: {len(result):,}건 저장 - {path_write}")
    if skipped_path_count:
        print(f"경고: 예상 경로 형식과 달라 제외된 파일 {skipped_path_count:,}건")


if __name__ == "__main__":
    main()
