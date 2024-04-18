#!/bin/bash

#cd $JARVIS_WORKSPACE/JARVIS/workspace/home/workspace/$TARGET_REPO_NAME
#echo $JARVIS_WORKSPACE/JARVIS/workspace/home/workspace/$TARGET_REPO_NAME
cd /home/workspace/JARVIS/workspace/home/workspace/$TARGET_REPO_NAME
echo /home/workspace/JARVIS/workspace/home/workspace/$TARGET_REPO_NAME

mkdir patches

# 현재 변경 사항이 있는 파일 목록 가져옴.
files=$(git diff --name-only)
​
# 각 파일별로 diff를 생성합니다.
for file in $files; do
    # 경로에서 슬래시를 대시로 대체하여 파일명을 생성
    diff_file="$(echo $file | sed 's/\//_/g').diff"
    # git diff 결과를 파일에 저장
    git diff -- "$file" > "$JARVIS_WORKSPACE/JARVIS/workspace/outputs/$diff_file"
    echo "Saved diff for $file to $JARVIS_WORKSPACE/JARVIS/workspace/outputs/$diff_file"
done

