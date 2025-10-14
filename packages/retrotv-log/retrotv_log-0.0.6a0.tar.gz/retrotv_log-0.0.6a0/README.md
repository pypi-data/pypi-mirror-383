# retrotv-log
Python3의 logging을 좀 더 쓰기 편하게 하기 위한 패키지 입니다.

## 설치
```Python3
pip install retrotv-log
```

## 사용법
```Python3
from log import Log

log = Log(__name__).get_logger
log.info("this is INFO level log")
```

## 인자
|인자명|필수여부|기본값|설명|
|---|---|---|---|
|name|O|없음|로깅 호출에 사용된 logger의 이름|
|level|X|logging.INFO|로깅 레벨|
|formatter|X|[%(levelname)s] [%(asctime)s] [%(module)s]: %(message)s|로깅 메시지 포맷|
|use_console|X|True|콘솔 출력 사용여부|
|use_file|X|True|파일 기록 사용여부|
|filename|X|None|파일 기록 시, 로그가 기록할 파일 명|
|timed_rotating_file_handler|X|None|TimedRotatingFileHandler 객체. 해당 객체가 None이 아닐 경우, 파일 기록 시 해당 객체를 참고하여 로그 파일을 기록함|
