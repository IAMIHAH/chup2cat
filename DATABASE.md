# 읽어두기
**고유 번호**는 Discord에서 부여한 Snowflakes,

**순번**은 첩첩냥에서 부여한 임의의 숫자,

**식별자**는 제공자 구별 없이 식별을 위한 임의의 숫자나 영어의 조합

# user.db
`userId` 유저 고유 번호

`exp` 채팅패스 경험치

`level` 채팅패스 레벨 (다음 레벨업 확인용)

`cooldown` 다음 경험치 획득 가능 시간 (UNIX Time)

`reward` reward.db로 이전 (현재 사용 X)

`bottleMultiple` 경험치 증가 배수

`bottlePeriod` 경험치 증가 종료 시간 (UNIX Time)

# season.db

`level` 보상을 획득할 채팅패스 레벨

`item(1,2,3)` 일반 보상 아이템 식별자

`item(1,2,3)_amount` 일반 보상 아이템 획득 개수

`item(1,2,3)_data` 획득할 아이템 데이터 (물약 기간 등)

`premium`, `premium_amount`, `premium_data` 프리미엄 (서버 부스팅) 아이템 관련 (위와 내용은 같음)

# reward.db

`userId` 유저 고유 번호

`level` 채팅패스 레벨

`rewardId` season.db에 기록된 리워드 순번 (`item(1,2,3)`의 숫자)

`rewarded` 1이면 획득함 (중복획득방지)

# log.db

`time` 이벤트 발생 시각 (UNIX Time)

`event` 이벤트 타입

`userId` 유저저 고유 번호

`gainedExp` 이벤트 `ExpFrom***`일 때 획득한 경험치 (음수도 가능)

`cmdUserId` 관리자가 실행한 이벤트일 경우 이벤트를 실행한 관리자

`item` 해당 이벤트로 획득한 아이템

`itemAmount` 아이템 개수

`chId` 이벤트 발생 채널 고유 번호

`msgId` 이벤트 발생 메시지 고유 번호

# item.db

`itemId` 아이템 식별자

`emoji` 아이템 이모지

`ko` 한국어 이름

`en` 영어 이름

`desc_ko` 한국어 설명

`desc_en` 영어 설명

# inventory.db

※ 테이블 명은 무조건 `유저 고유 번호`여야 함

`item` 아이템 식별자

`amount` 개수

`data` 아이템 데이터

PRIMARY KEY = `item` and `data`
`item`값이 중복이어도 `data`값이 다르면 내부에서 다른 아이템으로 침

# account.db

`discordId` 유저 고유 번호

`twitchId` Twitch에서 부여한 계정 ID

`email` (Discord 로그인 시) 이메일 (기본값 null)

`phone` 휴대전화번호 (웹사이트 인증 시)

`ok` ??? 이거 뭐였지 일단 놔둬보세요 0도 있고 1도 있는데 이거

# attendance.db

※ 테이블 명은 무조건 `attendance-연도-월` 이어야 함 (월은 한자리수면 앞에 0 붙어야됨)

`userId` 유저 고유 번호

`day(1~31)` 출석 여부 (2 이상 = 출석 인정)

# gamble.db

테이블 명 `blackjack`

`userId` 유저 고유 번호

`channelId` 스레드 고유 번호

`betting` 냥코인 개수

`player` 플레이어 보유 카드

`dealer` 딜러 보유 카드

`remained` 남은 카드

# 이벤트 데이터베이스

`userId` 유저 고유 번호

`point` (컬럼명 변경가능) 이벤트 포인트 개수
