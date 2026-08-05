import shutil
from pathlib import Path


source = Path(r"\\192.168.0.75\sollim광주\매각건 스캔파일\260723_P14_신탁\신탁통지서\우담-01")
target = source.parent

# 모든 하위 파일을 '신탁통지서' 폴더로 이동
files = [path for path in source.rglob("*") if path.is_file()]
total = len(files)

for index, file in enumerate(files, start=1):
    shutil.move(str(file), str(target / file.name))
    progress = index / total * 100
    print(f"[{index}/{total}] ({progress:.1f}%) {file.name}")

# '신탁통지서' 아래의 빈 폴더를 가장 안쪽부터 삭제
folders = sorted(
    (path for path in target.rglob("*") if path.is_dir()),
    key=lambda path: len(path.parts),
    reverse=True,
)
for folder in folders:
    try:
        folder.rmdir()
    except OSError:
        pass  # 비어 있지 않은 폴더는 유지

print(f"파일 {total}개 이동 및 빈 폴더 삭제 완료")
