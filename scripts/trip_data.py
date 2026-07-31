"""
발리 가족 여행 2026.08 · 일정 데이터
morning_brief.py 에서 참조.
"""

from datetime import date

TRIP_START = date(2026, 8, 5)
TRIP_END = date(2026, 8, 17)

# 일자별 데이터. 키 = ISO date 문자열.
# timeline: (시각, 텍스트, 옵션 주석) 튜플 리스트
# region_weather: 브리핑에 넣을 날씨 지역들 (open-meteo 좌표)
DAYS = {
    "2026-08-05": {
        "day_num": 1,
        "title": "인천 → 호치민 · 1군 시내 관광",
        "type": "travel",
        "hotel_out": None,
        "hotel_in": "ibis Saigon Airport",
        "timeline": [
            ("07:00", "인천공항 도착 · 체크인·수하물", None),
            ("10:35", "VN409 인천 → 호치민 (약 5h)", None),
            ("14:00", "탄손낫 도착 · ibis 픽업 미팅", "Terminal 2 국제선 도착홀 · Inner Lane · Pillar No.08 · Ibis 사인"),
            ("15:00", "ibis 체크인 · 짐 정리", None),
            ("17:00", "Grab → 1군 · 통일궁 외관", None),
            ("17:30", "노트르담 성당 · 중앙우체국", None),
            ("18:30", "벤탄 마켓 인근 저녁", None),
            ("20:00", "Bitexco Sky Deck 야경 / 벤탄 야시장", None),
            ("21:30", "Grab → ibis 복귀", "내일 아침 06:30 셔틀"),
        ],
        "tips": [
            "여권·항공권·바우처·현금 최종 확인",
            "지오 기내 놀거리 (스티커북·간식)",
            "베트남 입국심사 있음 (환승 아닌 실제 입국)",
            "1군 야경 관광 · Grab 앱 미리 설치",
        ],
        "meals": None,
        "regions_weather": [("서울", 37.57, 126.98), ("호치민", 10.82, 106.63)],
    },
    "2026-08-06": {
        "day_num": 2,
        "title": "호치민 → 덴파사르 → 사누르",
        "type": "travel",
        "hotel_out": "ibis Saigon Airport",
        "hotel_in": "Palette Signature Sanur",
        "timeline": [
            ("06:30", "ibis 셔틀 → 공항", None),
            ("10:10", "VN641 호치민 → 덴파사르 (약 3h50m)", None),
            ("14:00", "덴파사르 도착, 입국 수속", "e-VOA·Love Bali·All Indonesia 준비"),
            ("15:00", "JohnTaxi 픽업 → Palette Signature 사누르 (25,000원)", "차로 20~30분"),
            ("저녁", "자유시간 · 사누르 비치 산책, 모래놀이, 저녁 식사", "내일 07:00 픽업"),
        ],
        "tips": [
            "덴파사르 입국 후 심카드·환전 여부 결정",
            "일부 현금 IDR 확보 (배편 왕복 3,400,000 IDR 예정)",
            "일찍 취침 (다음날 이른 배편)",
        ],
        "meals": {
            "저녁 후보": ["Soul on the Beach 모래밭", "Byrdhouse Beach Club", "Genius Cafe 비치프론트"],
        },
        "regions_weather": [("호치민", 10.82, 106.63), ("사누르(발리)", -8.68, 115.26)],
    },
    "2026-08-07": {
        "day_num": 3,
        "title": "사누르 → 스랑안 → 길리 트라왕안 (Wahana 배편)",
        "type": "travel",
        "hotel_out": "Palette Signature Sanur",
        "hotel_in": "Villa Almarik",
        "timeline": [
            ("07:00", "JohnTaxi 픽업 → 스랑안 항구 (14,000원)", "차로 10~15분"),
            ("08:30", "Wahana 배편 출발 (스랑안)", "멀미약 30분 전 · 이지길리 대행"),
            ("10:30", "길리 트라왕안 도착 → Villa Almarik 체크인", "체크인 시간 확인"),
            ("오후", "호텔 앞 거북이 스노클링 🐢, 동네 산책", None),
            ("저녁", "동네 식당 or 리조트", None),
        ],
        "tips": [
            "배편 승선 전 화장실 · 아이 물통",
            "여권·현금(호텔·현지결제분) 챙기기",
            "짐 최소화 (배편 무게 제한)",
        ],
        "meals": {
            "저녁 후보": ["Scallywags BBQ 시푸드", "Banyan Tree 캐주얼", "Sendja @ Kardia"],
        },
        "regions_weather": [("사누르(발리)", -8.68, 115.26), ("길리 트라왕안", -8.35, 116.04)],
    },
    "2026-08-08": {
        "day_num": 4,
        "title": "길리 자유일 1",
        "type": "island",
        "hotel_out": None,
        "hotel_in": None,
        "timeline": [
            ("오전", "컨디션 보고 결정", None),
            ("오후", "컨디션 보고 결정", None),
            ("저녁", "컨디션 보고 결정", None),
        ],
        "tips": [
            "매일 아침 그날 뭐 할지 정하는 느낌",
            "무리 금지 · 리조트 안에서만 있어도 OK",
        ],
        "meals": {
            "액티비티 후보": [
                "🐢 호텔 앞 거북이 스노클링",
                "⛵ 3 길리 글래스보텀 보트 투어",
                "🚲 자전거 섬 일주",
                "🌅 Sunset Point 일몰 · 해먹 그네",
                "🐴 Cidomo 말마차",
                "🏖️ 호텔 앞 해변 · 리조트 풀",
                "🌃 Night Market 야시장",
            ],
        },
        "regions_weather": [("길리 트라왕안", -8.35, 116.04)],
    },
    "2026-08-09": {
        "day_num": 5,
        "title": "길리 자유일 2",
        "type": "island",
        "hotel_out": None,
        "hotel_in": None,
        "timeline": [
            ("오전", "컨디션 보고 결정", None),
            ("오후", "컨디션 보고 결정", None),
            ("저녁", "컨디션 보고 결정", None),
        ],
        "tips": ["오늘도 유연하게"],
        "meals": {
            "저녁 후보": ["Scallywags BBQ", "Sendja @ Kardia", "Night Market"],
        },
        "regions_weather": [("길리 트라왕안", -8.35, 116.04)],
    },
    "2026-08-10": {
        "day_num": 6,
        "title": "길리 자유일 3",
        "type": "island",
        "hotel_out": None,
        "hotel_in": None,
        "timeline": [
            ("오전", "컨디션 보고 결정", None),
            ("오후", "컨디션 보고 결정", None),
            ("저녁", "마지막 저녁 · Night Market 추천", None),
        ],
        "tips": [
            "내일 10:00 배편 · 짐 정리는 오늘 저녁부터",
            "호텔 결제 예정분 현금 확인",
        ],
        "meals": None,
        "regions_weather": [("길리 트라왕안", -8.35, 116.04)],
    },
    "2026-08-11": {
        "day_num": 7,
        "title": "길리 → 빠당바이 → 우붓",
        "type": "travel",
        "hotel_out": "Villa Almarik",
        "hotel_in": "The Westin Ubud",
        "timeline": [
            ("09:00", "체크아웃 · 항구로", None),
            ("10:00", "Wahana 배편 출발 (길리)", None),
            ("12:30", "빠당바이 도착 · JohnTaxi 픽업 (35,000원)", None),
            ("13:00", "짠디다사 점심 (마운트 아궁 배경)", None),
            ("15:30", "The Westin Ubud 체크인 (트윈룸 · 유료 1박)", None),
            ("저녁", "우붓 라이브 음악 식당 or 룸서비스", None),
        ],
        "tips": [
            "배편 30분 전 멀미약",
            "체크인 후 트윈룸 연박 확인",
            "짐 도착 후 물 마시고 낮잠",
        ],
        "meals": None,
        "regions_weather": [("길리 트라왕안", -8.35, 116.04), ("우붓", -8.51, 115.26)],
    },
    "2026-08-12": {
        "day_num": 8,
        "title": "우붓 · 몽키 포레스트",
        "type": "ubud",
        "hotel_out": None,
        "hotel_in": None,
        "timeline": [
            ("아침", "웨스틴 조식", None),
            ("오전", "몽키 포레스트 · 원숭이 조심", "안경·모자·먹을거 조심"),
            ("점심", "Milk & Madu 또는 Pizza Bagus", None),
            ("오후", "우붓 왕궁 · 예술 시장 · 요가바", None),
            ("저녁", "후보: Naughty Nuri's · Locavore to Go · Warung Biah Biah", None),
        ],
        "tips": [
            "원숭이 앞에서 셀피 X · 시선 X · 먹을거 X",
            "우붓 낮은 습해 물 자주",
        ],
        "meals": None,
        "regions_weather": [("우붓", -8.51, 115.26)],
    },
    "2026-08-13": {
        "day_num": 9,
        "title": "우붓 → 사누르 이동",
        "type": "travel",
        "hotel_out": "The Westin Ubud",
        "hotel_in": "The 1O1 Bali Oasis Sanur",
        "timeline": [
            ("아침", "웨스틴 조식 · 체크아웃", None),
            ("오전", "JohnTaxi 픽업 · 우붓 → 사누르 (30,000원)", "차로 1시간"),
            ("점심", "사누르 도착 · The 1O1 체크인 · 점심", None),
            ("오후", "사누르 비치 · 리조트 풀", None),
            ("저녁", "후보: Soul on the Beach · Byrdhouse · 호텔 근처 와룽", None),
        ],
        "tips": [
            "1O1 사누르 4박 연박 확인 (같은 방)",
            "내일 남부투어 준비",
        ],
        "meals": None,
        "regions_weather": [("우붓", -8.51, 115.26), ("사누르(발리)", -8.68, 115.26)],
    },
    "2026-08-14": {
        "day_num": 10,
        "title": "남부투어 풀데이 (사마사마 · Pandawa · Uluwatu · Jimbaran)",
        "type": "sanur",
        "hotel_out": None,
        "hotel_in": None,
        "timeline": [
            ("09:00", "사마사마 드라이버 출발 · DSLR 스냅 포함", None),
            ("10:30", "Pandawa 비치", None),
            ("12:30", "짐바란 인근 와룽 점심", None),
            ("15:30", "Uluwatu 사원 · 절벽뷰", "원숭이·사롱 대여"),
            ("18:30", "Jimbaran Bay 시푸드 디너 (해변)", "일몰 시간대 · DSLR 스냅"),
            ("21:00", "사누르 복귀", None),
        ],
        "tips": [
            "Uluwatu 원숭이 조심 (안경·귀걸이·모자)",
            "사롱은 사원 무료 대여",
            "짐바란 저녁 · 해변 신발 or 슬리퍼",
            "Kecak Dance는 패스 (일정에 없음)",
        ],
        "meals": None,
        "regions_weather": [("사누르(발리)", -8.68, 115.26), ("울루와뚜", -8.83, 115.09)],
    },
    "2026-08-15": {
        "day_num": 11,
        "title": "쿠타 서핑 (시우) · 사누르 자유일",
        "type": "sanur",
        "hotel_out": None,
        "hotel_in": None,
        "timeline": [
            ("아침", "호텔 조식", None),
            ("오전", "쿠타 이동 · Ryco 강사 서핑 강습 (150k IDR/h, 현지결제)", "구명조끼 · 자외선 차단"),
            ("점심", "쿠타 Beachwalk 쇼핑 · 점심", None),
            ("오후", "사누르 복귀 · 풀 · 낮잠", None),
            ("저녁", "후보: Massimo · Fisherman's Club · 호텔 풀사이드", None),
        ],
        "tips": [
            "Ryco 강사에게 아침 도착 시각·집결 지점 재확인",
            "지오는 사누르 남고 아빠·시우만 이동 옵션",
        ],
        "meals": None,
        "regions_weather": [("쿠타", -8.72, 115.17), ("사누르(발리)", -8.68, 115.26)],
    },
    "2026-08-16": {
        "day_num": 12,
        "title": "사누르 여유 · 마지막 정리",
        "type": "sanur",
        "hotel_out": None,
        "hotel_in": None,
        "timeline": [
            ("아침", "호텔 조식", None),
            ("오전", "리조트 풀 · 마사지 · 여유", None),
            ("오후", "사누르 비치 산책 · 기념품", None),
            ("저녁", "후보: Sindhu Night Market · Tandjung Sari · Genius Cafe", None),
        ],
        "tips": [
            "짐 정리 시작 · 습기 대비 지퍼백",
            "내일 사누르→공항 픽업 최종 확인",
            "8/17 인도네시아 독립기념일 · 이동 여유",
        ],
        "meals": None,
        "regions_weather": [("사누르(발리)", -8.68, 115.26)],
    },
    "2026-08-17": {
        "day_num": 13,
        "title": "덴파사르 → 호치민 → 인천 (귀국)",
        "type": "travel",
        "hotel_out": "The 1O1 Bali Oasis Sanur",
        "hotel_in": None,
        "timeline": [
            ("아침", "체크아웃 · 조식", None),
            ("점심", "사누르 근처 마지막 점심", None),
            ("13:00", "사누르 → 공항 픽업", "독립기념일 이동 여유"),
            ("16:00", "VN640 덴파사르 → 호치민", None),
            ("18:40", "호치민 도착 · 환승 대기", None),
            ("23:45", "VN408 호치민 → 인천 (약 5h20m)", None),
            ("06:40+1", "인천공항 도착 (다음날 아침)", None),
        ],
        "tips": [
            "환승 대기 시간 여유 있음 (약 5h)",
            "호치민 공항 저녁 식사 계획",
            "귀국 전 여권 이상 없나 확인",
        ],
        "meals": None,
        "regions_weather": [("사누르(발리)", -8.68, 115.26)],
    },
}


# 여행 전 준비 상태 (스크립트가 D-day 안내에 씀)
PRE_TRIP_STATUS = {
    "done": [
        "왕복 항공권 (베트남항공)",
        "숙소 6건 결제 · 연박 요청",
        "Wahana 배편 왕복 (이지길리)",
        "픽업 4건 (JohnTaxi)",
        "남부투어 사마사마 (DSLR 스냅)",
        "쿠타 서핑 Ryco 컨택",
    ],
    "pending": [
        "e-VOA 신청 (도착 30일 전부터)",
        "여행자보험 4인",
        "사누르 → 공항 픽업 (8/17)",
    ],
}


# D-day별 리마인더 (해당 시점에만 표시)
def d_day_reminders(days_left: int) -> list[str]:
    reminders = []
    if days_left <= 30:
        reminders.append("e-VOA 신청 가능 (도착 30일 전부터)")
    if days_left <= 14:
        reminders.append("여행자보험 4인 비교·가입")
        reminders.append("사누르 → 공항 픽업 (8/17) 예약")
    if days_left <= 7:
        reminders.append("환전 (일부 현금 IDR 확보)")
        reminders.append("여권 유효기간 확인 (귀국일 기준 6개월)")
        reminders.append("멀미약·지사제·아이 상비약")
    if days_left <= 3:
        reminders.append("짐 싸기 · 지퍼백 준비")
        reminders.append("Marriott Bonvoy 앱 · Agoda 앱 최신화")
    if days_left <= 1:
        reminders.append("모든 예약 확인서 오프라인 저장")
        reminders.append("여권·항공권·현금 재확인")
    return reminders
