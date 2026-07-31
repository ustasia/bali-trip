"""
발리 여행 모닝 브리핑
매일 KST 08:00에 GitHub Actions cron으로 실행.
여행 전: D-day 카운트 + 여행 첫날 리마인드 + 준비 상태
여행 중: 오늘 일정 + 날씨 + 팁
여행 후: 정리 종료
"""

import os
import sys
import smtplib
import ssl
from datetime import date, datetime, timezone, timedelta
from email.message import EmailMessage
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import json

from trip_data import (
    TRIP_START,
    TRIP_END,
    DAYS,
    PRE_TRIP_STATUS,
    d_day_reminders,
)

# ─────────────────────────────────────────────
# 설정
# ─────────────────────────────────────────────

KST = timezone(timedelta(hours=9))
WEEKDAY_KR = ["월", "화", "수", "목", "금", "토", "일"]

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

# 여행 첫날 미리보기용 (여행 전 매일 붙임)
FIRST_TRIP_DAY_KEY = "2026-08-05"


# ─────────────────────────────────────────────
# 유틸
# ─────────────────────────────────────────────

def today_kst() -> date:
    """KST 기준 오늘 날짜."""
    return datetime.now(KST).date()


def fmt_kdate(d: date) -> str:
    """`8월 5일 화` 스타일."""
    return f"{d.month}월 {d.day}일 {WEEKDAY_KR[d.weekday()]}"


def fetch_weather(lat: float, lon: float) -> dict | None:
    """
    open-meteo에서 하루치 날씨 fetch. 키 불필요.
    반환: {tmax, tmin, precip_prob, code} or None
    """
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code",
            "timezone": "Asia/Jakarta",
            "forecast_days": 1,
        }
        url = f"https://api.open-meteo.com/v1/forecast?{urlencode(params)}"
        with urlopen(url, timeout=10) as res:
            data = json.loads(res.read().decode("utf-8"))
        daily = data.get("daily", {})
        return {
            "tmax": daily.get("temperature_2m_max", [None])[0],
            "tmin": daily.get("temperature_2m_min", [None])[0],
            "precip_prob": daily.get("precipitation_probability_max", [None])[0],
            "code": daily.get("weather_code", [None])[0],
        }
    except Exception as e:
        print(f"[weather fetch failed] {e}", file=sys.stderr)
        return None


def fetch_exchange_rate() -> tuple[float, str] | None:
    """
    1 IDR = ? KRW 실시간 환율 fetch.
    open.er-api.com은 무료·등록 불필요·하루 1회 갱신.
    반환: (환율, 갱신일 문자열) or None (실패시)
    """
    try:
        with urlopen("https://open.er-api.com/v6/latest/IDR", timeout=10) as res:
            data = json.loads(res.read().decode("utf-8"))
        if data.get("result") != "success":
            return None
        krw = data.get("rates", {}).get("KRW")
        updated = data.get("time_last_update_utc", "")[:16]  # 앞 16자만 (요일·일·월·연)
        if krw is None:
            return None
        return float(krw), updated
    except Exception as e:
        print(f"[exchange fetch failed] {e}", file=sys.stderr)
        return None


def weather_emoji(code: int | None) -> str:
    """open-meteo WMO 날씨 코드 → 이모지."""
    if code is None:
        return "🌡️"
    if code == 0:
        return "☀️"
    if code in (1, 2):
        return "🌤️"
    if code == 3:
        return "☁️"
    if code in (45, 48):
        return "🌫️"
    if code in (51, 53, 55, 56, 57):
        return "🌦️"
    if code in (61, 63, 65, 66, 67, 80, 81, 82):
        return "🌧️"
    if code in (71, 73, 75, 77, 85, 86):
        return "🌨️"
    if code in (95, 96, 99):
        return "⛈️"
    return "🌡️"


# ─────────────────────────────────────────────
# 콘텐츠 렌더링
# ─────────────────────────────────────────────

def render_kakao_pre_trip(today: date, days_left: int, first_day: dict, rate_info) -> str:
    """여행 전 카톡 요약 (평문 · 옵션 A 양식)."""
    first_wk = WEEKDAY_KR[TRIP_START.weekday()]
    lines = [f"🌅 발리 여행 D-{days_left}", ""]
    lines.append(f"📅 여행 첫날 ({TRIP_START.month}/{TRIP_START.day} {first_wk})")
    for t, text, _ in first_day["timeline"][:5]:
        lines.append(f"{t} {text}")
    lines.append("")

    reminders = d_day_reminders(days_left)
    if reminders:
        lines.append("💡 리마인더")
        for r in reminders[:3]:
            lines.append(f"- {r}")
        lines.append("")

    if rate_info:
        rate_val, _ = rate_info
        lines.append(f"💱 1 IDR ≈ {rate_val:.4f}원")
    else:
        lines.append("💱 1 IDR ≈ 0.08원")

    return "\n".join(lines)


def render_kakao_during_trip(today: date, day: dict, weather_first: dict | None, rate_info) -> str:
    """여행 중 카톡 요약 (평문 · 옵션 A 양식)."""
    weekday = WEEKDAY_KR[today.weekday()]
    lines = [f"🌅 {today.month}/{today.day} {weekday} · 발리 {day['day_num']}일째", ""]

    lines.append(f"📍 {day['title']}")
    for t, text, _ in day["timeline"][:5]:
        lines.append(f"{t} {text}")
    lines.append("")

    if weather_first:
        name, w = weather_first
        emo = weather_emoji(w["code"])
        pp = w.get("precip_prob")
        pp_txt = f" · 강수 {pp}%" if pp is not None else ""
        lines.append(f"🌤️ {name} {w['tmin']:.0f}~{w['tmax']:.0f}°C{pp_txt}")

    if day.get("tips"):
        lines.append(f"💡 {day['tips'][0]}")

    if rate_info:
        rate_val, _ = rate_info
        lines.append(f"💱 1 IDR ≈ {rate_val:.4f}원")
    else:
        lines.append("💱 1 IDR ≈ 0.08원")

    return "\n".join(lines)


def render_pre_trip(today: date) -> tuple[str, str, str]:
    """여행 전 · D-day + 첫날 리마인드 + 준비 상태."""
    days_left = (TRIP_START - today).days

    first = DAYS[FIRST_TRIP_DAY_KEY]

    tl_html = "".join(
        f'<tr><td class="tl-time">{t}</td><td class="tl-text">{text}'
        + (f'<span class="tl-note">{note}</span>' if note else "")
        + "</td></tr>"
        for (t, text, note) in first["timeline"]
    )

    done_html = "".join(f"<li>✅ {x}</li>" for x in PRE_TRIP_STATUS["done"])
    pending_html = "".join(f"<li>⏳ {x}</li>" for x in PRE_TRIP_STATUS["pending"])

    reminders = d_day_reminders(days_left)
    reminders_html = ""
    if reminders:
        items = "".join(f"<li>{x}</li>" for x in reminders)
        reminders_html = f"""
        <section>
          <h2>💡 오늘의 리마인더 (D-{days_left})</h2>
          <ul class="reminders">{items}</ul>
        </section>
        """

    # 환율 fetch
    rate_info = fetch_exchange_rate()
    if rate_info:
        rate_val, rate_updated = rate_info
        rate_line = f"1 IDR ≈ {rate_val:.4f}원 (갱신 {rate_updated} UTC)"
    else:
        rate_line = "1 IDR ≈ 0.08원 (기본값)"

    # 카톡 요약
    kakao_text = render_kakao_pre_trip(today, days_left, first, rate_info)

    subject = f"🌅 발리 여행 D-{days_left} · {fmt_kdate(today)}"

    html = f"""
    <div class="brief">
      <div class="header">
        <div class="date">{fmt_kdate(today)}</div>
        <div class="dday">발리 여행 <strong>D-{days_left}</strong></div>
      </div>

      <section>
        <h2>📍 여행 첫날 미리보기 (8/5 수 · 인천 → 호치민)</h2>
        <table class="timeline">{tl_html}</table>
      </section>

      {reminders_html}

      <section>
        <h2>📋 준비 상태</h2>
        <div class="status-grid">
          <div class="status-col">
            <div class="status-label">완료 ({len(PRE_TRIP_STATUS['done'])})</div>
            <ul>{done_html}</ul>
          </div>
          <div class="status-col">
            <div class="status-label">대기 ({len(PRE_TRIP_STATUS['pending'])})</div>
            <ul>{pending_html}</ul>
          </div>
        </div>
      </section>

      <section class="kakao-share">
        <h2>📱 카톡 공유용</h2>
        <div class="kakao-desc">아래를 롱프레스로 복사해 배우자에게 전송</div>
        <pre class="kakao-text">{kakao_text}</pre>
      </section>

      <div class="footer">
        <p>💱 {rate_line}</p>
        <p>여행 앱: <a href="https://ustasia.github.io/bali-trip/">ustasia.github.io/bali-trip</a></p>
      </div>
    </div>
    """
    return subject, html, kakao_text


def render_during_trip(today: date) -> tuple[str, str, str]:
    """여행 중 · 오늘 일정 + 날씨 + 팁."""
    key = today.isoformat()
    day = DAYS.get(key)
    if not day:
        return "🌅 발리 여행 · 오늘 일정 없음", "<p>오늘 일정 데이터가 없어요.</p>"

    tl_html = "".join(
        f'<tr><td class="tl-time">{t}</td><td class="tl-text">{text}'
        + (f'<span class="tl-note">{note}</span>' if note else "")
        + "</td></tr>"
        for (t, text, note) in day["timeline"]
    )

    hotel_html = ""
    if day["hotel_out"] or day["hotel_in"]:
        parts = []
        if day["hotel_out"]:
            parts.append(f"🏨← {day['hotel_out']}")
        if day["hotel_in"]:
            parts.append(f"🏨→ {day['hotel_in']}")
        hotel_html = f'<div class="hotel-line">{"  ·  ".join(parts)}</div>'

    # 날씨
    weather_html = ""
    weather_first = None  # 카톡 요약에 넘길 첫 지역 날씨
    if day.get("regions_weather"):
        rows = []
        for name, lat, lon in day["regions_weather"]:
            w = fetch_weather(lat, lon)
            if w and w["tmax"] is not None:
                if weather_first is None:
                    weather_first = (name, w)
                emo = weather_emoji(w["code"])
                pp = w.get("precip_prob")
                pp_txt = f" · 강수 {pp}%" if pp is not None else ""
                rows.append(
                    f'<tr><td class="w-region">{name}</td>'
                    f'<td class="w-val">{emo} {w["tmin"]:.0f}°C ~ {w["tmax"]:.0f}°C{pp_txt}</td></tr>'
                )
            else:
                rows.append(f'<tr><td class="w-region">{name}</td><td class="w-val">데이터 없음</td></tr>')
        if rows:
            weather_html = f"""
            <section>
              <h2>🌤️ 오늘 날씨</h2>
              <table class="weather">{"".join(rows)}</table>
            </section>
            """

    tips_html = ""
    if day.get("tips"):
        items = "".join(f"<li>{x}</li>" for x in day["tips"])
        tips_html = f"""
        <section>
          <h2>💡 오늘의 팁</h2>
          <ul class="tips">{items}</ul>
        </section>
        """

    meals_html = ""
    if day.get("meals"):
        blocks = []
        for label, items in day["meals"].items():
            chips = "".join(f'<span class="chip">{x}</span>' for x in items)
            blocks.append(f'<div class="meal-block"><div class="meal-label">{label}</div><div class="chips">{chips}</div></div>')
        meals_html = f"""
        <section>
          <h2>🍽️ 후보</h2>
          {"".join(blocks)}
        </section>
        """

    subject = f"🌅 발리 {day['day_num']}일째 · {day['title']}"

    # 환율 fetch
    rate_info = fetch_exchange_rate()
    if rate_info:
        rate_val, rate_updated = rate_info
        rate_line = f"1 IDR ≈ {rate_val:.4f}원 (갱신 {rate_updated} UTC)"
    else:
        rate_line = "1 IDR ≈ 0.08원 (기본값)"

    # 카톡 요약
    kakao_text = render_kakao_during_trip(today, day, weather_first, rate_info)

    html = f"""
    <div class="brief">
      <div class="header">
        <div class="date">{fmt_kdate(today)}</div>
        <div class="dday">발리 여행 <strong>{day['day_num']}일째</strong></div>
        <div class="title">{day['title']}</div>
      </div>

      {hotel_html}

      <section>
        <h2>📍 오늘 일정</h2>
        <table class="timeline">{tl_html}</table>
      </section>

      {weather_html}
      {tips_html}
      {meals_html}

      <section class="kakao-share">
        <h2>📱 카톡 공유용</h2>
        <div class="kakao-desc">아래를 롱프레스로 복사해 배우자에게 전송</div>
        <pre class="kakao-text">{kakao_text}</pre>
      </section>

      <div class="footer">
        <p>💱 {rate_line}</p>
        <p>🕐 현지시간대: WITA (KST -1h)</p>
        <p>여행 앱: <a href="https://ustasia.github.io/bali-trip/">ustasia.github.io/bali-trip</a></p>
      </div>
    </div>
    """
    return subject, html, kakao_text


def render_post_trip(today: date) -> tuple[str, str, str | None]:
    """여행 후 · 하루만 안내 (오래 발송하지 않도록)."""
    days_since = (today - TRIP_END).days
    subject = "🌅 발리 여행 종료 · 모닝 브리핑 정지 예정"
    html = f"""
    <div class="brief">
      <div class="header">
        <div class="date">{fmt_kdate(today)}</div>
        <div class="dday">발리 여행 종료 D+{days_since}</div>
      </div>
      <section>
        <p>여행 잘 다녀오셨나요? 이 브리핑은 이제 별 내용 없이 발송돼요.</p>
        <p>GitHub Actions에서 <code>morning-brief.yml</code>을 비활성화하시거나, 여행 계획을 새로 짜서 이 인프라를 재활용하실 수 있어요.</p>
      </section>
    </div>
    """
    return subject, html, None


# ─────────────────────────────────────────────
# HTML 셸 (공통 스타일)
# ─────────────────────────────────────────────

def wrap_html(body: str, og_title: str = "발리 여행 브리핑", og_desc: str = "오늘의 일정·팁·환율") -> str:
    return f"""<!doctype html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta property="og:title" content="{html_escape(og_title)}">
<meta property="og:description" content="{html_escape(og_desc)}">
<meta property="og:type" content="article">
<title>{html_escape(og_title)}</title>
<style>
  body {{ margin:0; padding:0; background:#f7f3ec; font-family:-apple-system, "Apple SD Gothic Neo", "Segoe UI", sans-serif; color:#2b2419; }}
  .brief {{ max-width:560px; margin:0 auto; padding:20px 16px 32px; }}
  .header {{ padding:16px 0 20px; border-bottom:1px solid #e8dfd0; margin-bottom:18px; }}
  .header .date {{ font-size:13px; color:#8a7d68; letter-spacing:1px; }}
  .header .dday {{ font-size:24px; font-weight:700; color:#0d5a6b; margin-top:4px; }}
  .header .dday strong {{ color:#e85d4f; }}
  .header .title {{ font-size:15px; color:#4a3f2a; margin-top:6px; font-weight:500; }}
  section {{ margin-bottom:22px; }}
  h2 {{ font-size:14px; color:#0d5a6b; margin:0 0 10px; letter-spacing:0.5px; }}
  .hotel-line {{ font-size:12px; color:#8a7d68; padding:8px 12px; background:white; border-radius:8px; border:1px solid #e8dfd0; margin-bottom:16px; }}
  table.timeline {{ width:100%; border-collapse:collapse; }}
  table.timeline td {{ padding:8px 0; border-bottom:1px dashed #e8dfd0; vertical-align:top; }}
  table.timeline tr:last-child td {{ border-bottom:none; }}
  .tl-time {{ width:70px; font-family:"JetBrains Mono", monospace; font-size:12px; color:#0d5a6b; font-weight:600; }}
  .tl-text {{ font-size:14px; color:#2b2419; line-height:1.5; }}
  .tl-note {{ display:block; font-size:11.5px; color:#8a7d68; margin-top:2px; }}
  table.weather {{ width:100%; border-collapse:collapse; background:white; border-radius:10px; overflow:hidden; }}
  table.weather td {{ padding:9px 12px; border-bottom:1px solid #f0e8d8; font-size:13px; }}
  table.weather tr:last-child td {{ border-bottom:none; }}
  .w-region {{ width:120px; color:#8a7d68; }}
  .w-val {{ color:#2b2419; font-weight:500; }}
  ul.tips, ul.reminders {{ margin:0; padding-left:18px; }}
  ul.tips li, ul.reminders li {{ font-size:13px; color:#2b2419; margin-bottom:5px; line-height:1.5; }}
  ul.reminders li {{ color:#8a4a1d; }}
  .status-grid {{ display:table; width:100%; }}
  .status-col {{ display:table-cell; width:50%; vertical-align:top; padding-right:8px; }}
  .status-label {{ font-size:11.5px; color:#8a7d68; margin-bottom:6px; font-weight:600; letter-spacing:0.5px; }}
  .status-col ul {{ margin:0; padding-left:0; list-style:none; }}
  .status-col li {{ font-size:12.5px; margin-bottom:4px; color:#2b2419; line-height:1.5; }}
  .meal-block {{ margin-bottom:10px; }}
  .meal-label {{ font-size:12px; color:#4a3f2a; font-weight:600; margin-bottom:5px; }}
  .chips {{ display:flex; flex-wrap:wrap; gap:5px; }}
  .chip {{ font-size:11.5px; padding:4px 10px; background:white; border:1px solid #e8dfd0; border-radius:100px; color:#2b2419; }}
  .kakao-share h2 {{ color:#3c2f00; }}
  .kakao-desc {{ font-size:11px; color:#8a7d68; margin-bottom:8px; }}
  .kakao-text {{
    background:#fef8dc;
    border:1px solid #f9e39a;
    border-radius:10px;
    padding:14px 16px;
    font-family:-apple-system, "Apple SD Gothic Neo", "Segoe UI", sans-serif;
    font-size:13px;
    line-height:1.7;
    color:#2b2419;
    white-space:pre-wrap;
    word-wrap:break-word;
    margin:0;
    -webkit-user-select:all;
    user-select:all;
  }}
  .footer {{ padding-top:14px; border-top:1px solid #e8dfd0; font-size:11px; color:#8a7d68; }}
  .footer p {{ margin:4px 0; }}
  .footer a {{ color:#0d5a6b; text-decoration:none; }}
</style>
</head><body>{body}</body></html>"""


# ─────────────────────────────────────────────
# SMTP 발송
# ─────────────────────────────────────────────

BRIEFINGS_DIR = "briefings"
BRIEFING_URL_BASE = "https://ustasia.github.io/bali-trip/briefings"


def html_escape(s: str) -> str:
    """텔레그램 HTML용 이스케이프 (기본 3개)."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def save_briefing_html(today: date, html: str) -> tuple[str, str]:
    """
    브리핑 HTML을 저장소에 저장. workflow가 이후에 커밋·푸시.
    반환: (저장 경로, GitHub Pages 공개 URL)
    """
    os.makedirs(BRIEFINGS_DIR, exist_ok=True)
    filename = f"{today.isoformat()}.html"
    path = os.path.join(BRIEFINGS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    url = f"{BRIEFING_URL_BASE}/{filename}"
    return path, url


def render_telegram_message(kakao_text: str, briefing_url: str) -> str:
    """
    카톡용 평문을 텔레그램 리치 HTML로 개선.
    - 이모지 헤더(🌅 📅 📍 💡 🌤️ 💱)로 시작하는 줄은 <b> 강조
    - 마지막에 웹뷰 링크 첨부
    """
    HEADER_PREFIXES = ("🌅", "📅", "📍", "💡", "🌤️", "💱")
    lines_in = kakao_text.split("\n")
    lines_out = []
    for line in lines_in:
        if any(line.startswith(p) for p in HEADER_PREFIXES):
            lines_out.append(f"<b>{html_escape(line)}</b>")
        else:
            lines_out.append(html_escape(line))
    lines_out.append("")
    lines_out.append(f'📄 <a href="{html_escape(briefing_url)}">브리핑 자세히 보기</a>')
    return "\n".join(lines_out)


def send_telegram(token: str, chat_id: str, text: str) -> bool:
    """
    텔레그램 봇으로 메시지 전송.
    HTML parse_mode 사용 (지원 태그: <b>, <i>, <u>, <s>, <a>, <code>, <pre>).
    반환: 성공 여부
    """
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    }).encode("utf-8")
    try:
        req = Request(url, data=payload, method="POST")
        with urlopen(req, timeout=10) as res:
            result = json.loads(res.read().decode("utf-8"))
            return bool(result.get("ok"))
    except Exception as e:
        print(f"[telegram send failed] {e}", file=sys.stderr)
        return False


def send_email(subject: str, html_body: str, smtp_user: str, smtp_pass: str, recipients: list[str]):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = ", ".join(recipients)
    msg.set_content("HTML 이메일입니다. HTML을 볼 수 있는 클라이언트에서 열어주세요.")
    msg.add_alternative(html_body, subtype="html")

    ctx = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls(context=ctx)
        s.login(smtp_user, smtp_pass)
        s.send_message(msg)


# ─────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────

def main():
    smtp_user = os.environ.get("SMTP_USER", "").strip()
    smtp_pass = os.environ.get("SMTP_PASS", "").strip()
    recipients_raw = os.environ.get("RECIPIENTS", "").strip()
    tg_token = os.environ.get("TELEGRAM_TOKEN", "").strip()
    tg_chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

    if not smtp_user or not smtp_pass or not recipients_raw:
        print("[error] SMTP_USER, SMTP_PASS, RECIPIENTS 환경변수 필요", file=sys.stderr)
        sys.exit(1)

    recipients = [r.strip() for r in recipients_raw.split(",") if r.strip()]

    today = today_kst()
    print(f"[info] today (KST) = {today}")

    if today < TRIP_START:
        subject, body, kakao_text = render_pre_trip(today)
    elif TRIP_START <= today <= TRIP_END:
        subject, body, kakao_text = render_during_trip(today)
    else:
        # 여행 종료 3일까지만 발송 (자동 정지 유도)
        if (today - TRIP_END).days > 3:
            print("[info] 여행 종료 3일 초과 → 발송 안 함")
            return
        subject, body, kakao_text = render_post_trip(today)

    html = wrap_html(body, og_title=subject)

    # 로컬 테스트 모드
    if os.environ.get("DRY_RUN") == "1":
        out = "/tmp/morning_brief_preview.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[dry-run] subject: {subject}")
        print(f"[dry-run] preview: {out}")
        if kakao_text:
            print(f"[dry-run] telegram text:\n{kakao_text}")
        return

    # 이메일 발송
    try:
        send_email(subject, html, smtp_user, smtp_pass, recipients)
        print(f"[ok] email sent: {subject} → {recipients}")
    except Exception as e:
        print(f"[error] email failed: {e}", file=sys.stderr)

    # 브리핑 HTML 저장소에 저장 (workflow가 이후 커밋·푸시)
    briefing_path, briefing_url = save_briefing_html(today, html)
    print(f"[ok] briefing saved: {briefing_path}")
    print(f"[info] briefing url: {briefing_url}")

    # 텔레그램 발송 (환경변수 있을 때만, 실패해도 종료 코드 정상)
    if tg_token and tg_chat and kakao_text:
        tg_message = render_telegram_message(kakao_text, briefing_url)
        ok = send_telegram(tg_token, tg_chat, tg_message)
        print(f"[{'ok' if ok else 'warn'}] telegram sent: {ok}")
    elif tg_token and tg_chat:
        print("[info] telegram: kakao_text 없어 스킵 (post-trip)")
    else:
        print("[info] telegram: TELEGRAM_TOKEN/CHAT_ID 없어 스킵")


if __name__ == "__main__":
    main()
