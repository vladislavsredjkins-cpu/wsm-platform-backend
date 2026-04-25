import resend
import time

resend.api_key = "re_8x1qQdHz_AJ7mCFCQrUL643WC3EV1M2hz"

FROM_EMAIL = "WSM Platform <noreply@ranking.worldstrongman.org>"
PROMO_CODE = "WSM50"
DEADLINE = "May 31, 2026"
REGISTER_URL = "https://ranking.worldstrongman.org/register/athlete"

athletes = [
    {"name": "Muhammad Nur Arif", "email": "nurarifkhalil39@gmail.com", "country": "Malaysia"},
    {"name": "Bartłomiej Tarapata", "email": "Bartektarapata@gmail.com", "country": "Poland"},
    {"name": "Marc Martinez", "email": "Marcmartinez14e@gmail.com", "country": "Spain"},
    {"name": "Niko Voutilainen", "email": "voutilainen@windowslive.com", "country": "Finland"},
    {"name": "Youssef Daas", "email": "fssodaas@gmail.com", "country": "Tunisia"},
    {"name": "Ilya Lisitskiy", "email": "rabota564738@yandex.ru", "country": "Russia"},
    {"name": "Prince Emmanuel Lartey", "email": "kolikomavel3@gmail.com", "country": "Ghana"},
    {"name": "Ahmed Alismaily", "email": "ahmedalismaily200@gmail.com", "country": "Oman"},
    {"name": "Matthew Staal", "email": "matstaal13@gmail.com", "country": "Great Britain"},
    {"name": "Anastasia Petrova", "email": "na.kalinechenko@gmail.com", "country": "Russia"},
    {"name": "Martin Tye", "email": "Martintye@hotmail.co.uk", "country": "Great Britain"},
    {"name": "Albin Hasanović", "email": "albin.hasanovic.89@gmail.com", "country": "Serbia"},
    {"name": "Przemysław Marczewski", "email": "marczes1987@wp.pl", "country": "Poland"},
    {"name": "Dmitry Aliakhnovich", "email": "nok.1995@inbox.ru", "country": "Belarus"},
    {"name": "Temirlan Kenzhekhanov", "email": "Timaboyka@mail.ru", "country": "Kazakhstan"},
    {"name": "Stephane Koumou Ayo", "email": "Stephanekoumou@yahoo.fr", "country": "Cameroon"},
    {"name": "Martin Lovíšek", "email": "meartinxxx@gmail.com", "country": "Slovakia"},
    {"name": "Ghadeer Mearaj", "email": "Gh.mearaj@gmail.com", "country": "Bahrain"},
    {"name": "Sameer Abubaqr", "email": "Sameermohammed05@gmail.com", "country": "Bahrain"},
    {"name": "Sumit Dhankhar", "email": "dhankharsumit09@gmail.com", "country": "India"},
    {"name": "Vinícius Escarlate Bueno", "email": "vinnie.mamute@outlook.com", "country": "Brazil"},
    {"name": "Jamie Mosley", "email": "Thelabel.co2025@gmail.com", "country": "England"},
    {"name": "Artem Mironov", "email": "vip.miron4ik13@gmail.com", "country": "Russia"},
    {"name": "Nicolas Acheampong", "email": "legacynicks@gmail.com", "country": "Ghana"},
    {"name": "Aidan Howell", "email": "aidan1howell@gmail.com", "country": "USA"},
    {"name": "Patrick Pulz", "email": "Patrick.pulz.2@gmail.com", "country": "Austria"},
    {"name": "Shane Hodgins", "email": "hodginsau@hotmail.com", "country": "Australia"},
    {"name": "T York", "email": "yorkstrongfamily@gmail.com", "country": "USA"},
    {"name": "Ulfr Molette", "email": "ulfrmolette1718@gmail.com", "country": "USA"},
    {"name": "Abd El Nour Fakhouri", "email": "Fahorenor@gmail.com", "country": "Egypt"},
    {"name": "Gergas", "email": "samogergas@gmail.com", "country": "Egypt"},
    {"name": "Justin Grigg", "email": "justingrigg85@outlook.com", "country": "USA"},
    {"name": "Mariusz Arendacz", "email": "Mariusz.Arendacz1@gmail.com", "country": "Poland"},
    {"name": "Kyle Clossick", "email": "Kclossick94@gmail.com", "country": "USA"},
    {"name": "Sergei Grecenuk", "email": "grecenuksergej342@gmail.com", "country": "Russia"},
    {"name": "Mikita Nizhnik", "email": "nikitanizhnik1992@gmail.com", "country": "Belarus"},
    {"name": "Sina Ruppenthal", "email": "sina-ruppenthal@web.de", "country": "Germany"},
    {"name": "David Majaya Mberi", "email": "majayamberi2016@gmail.com", "country": "Zambia"},
    {"name": "Moritz Mader", "email": "worldsstrongestcloud@icloud.com", "country": "Germany"},
    {"name": "Steven Owens", "email": "stevieowens1934@yahoo.com", "country": "USA"},
    {"name": "Tiago Aparecido de Oliveira", "email": "tiagostrongman16@gmail.com", "country": "Brazil"},
    {"name": "Mark Sobhi", "email": "marksobhi479@gmail.com", "country": "Egypt"},
    {"name": "Rinat", "email": "18180808@bk.ru", "country": "Russia"},
    {"name": "Angeline Berva", "email": "ange.berva@gmail.com", "country": "France"},
    {"name": "Mohamad Meheich", "email": "m.meheich@hotmail.com", "country": "Australia"},
    {"name": "Juan Ferrer Casanova", "email": "ferrerstrong@gmail.com", "country": "Spain"},
    {"name": "Lucas Dmitruk", "email": "Lucasftw93@gmail.com", "country": "Argentina"},
    {"name": "Bruno Farrobo", "email": "phgf09@gmail.com", "country": "Portugal"},
    {"name": "Daniel Rodriguez Rincon", "email": "abogado@daniel-rodriguez.es", "country": "Spain"},
    {"name": "Mikel Prieto Calvo", "email": "mikelprietocalvo@hotmail.com", "country": "Spain"},
    {"name": "Karanpreet Singh Dhaliwal", "email": "dhaliwalkaran20@gmail.com", "country": "India"},
    {"name": "Paul Mwanza", "email": "Paulmwanza258@gmail.com", "country": "Zambia"},
    {"name": "Jessica Adodo", "email": "Jadodo1210@gmail.com", "country": "USA"},
    {"name": "Beauvois Mathieu", "email": "mathieu.beauvois@gmail.com", "country": "France"},
]

def build_email(athlete):
    first = athlete["name"].split()[0]
    country = athlete["country"]
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0a0a;padding:40px 20px;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;">

  <tr><td style="background:#111;border-radius:16px 16px 0 0;padding:32px 40px;text-align:center;border-bottom:2px solid #c9a84c;">
    <img src="https://worldstrongman.org/wp-content/uploads/2026/02/logo_wsm.png-scaled.png" width="70" alt="WSM" style="margin-bottom:16px;"/>
    <div style="color:#c9a84c;font-size:11px;letter-spacing:4px;text-transform:uppercase;margin-bottom:8px;">World Strongman International Union</div>
    <div style="color:#fff;font-size:26px;font-weight:800;">WORLD CHAMPIONSHIP 2026</div>
    <div style="color:#888;font-size:14px;margin-top:6px;">📍 Dubai, UAE &nbsp;·&nbsp; December 4–5, 2026</div>
  </td></tr>

  <tr><td style="background:#161616;padding:40px;">
    <p style="color:#fff;font-size:20px;font-weight:700;margin:0 0 8px;">Dear {first},</p>
    <p style="color:#aaa;font-size:15px;line-height:1.7;margin:0 0 24px;">
      Your qualification application for the <strong style="color:#fff;">World Strongman Championship 2026</strong> has been received.<br/>
      Complete your <strong style="color:#fff;">official registration on the WSM platform</strong> and unlock your full athlete package.
    </p>

    <div style="background:#1e1e1e;border-radius:12px;padding:28px;margin-bottom:24px;border:1px solid #2a2a2a;">
      <div style="color:#c9a84c;font-size:11px;letter-spacing:3px;text-transform:uppercase;margin-bottom:20px;">✦ What's included in your registration</div>

      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:14px;"><tr>
        <td width="44"><div style="width:36px;height:36px;background:#c9a84c;border-radius:8px;text-align:center;line-height:36px;">🏆</div></td>
        <td style="padding-left:14px;">
          <div style="color:#fff;font-size:14px;font-weight:700;margin-bottom:2px;">Public Athlete Profile</div>
          <div style="color:#888;font-size:13px;">Your personal page on ranking.worldstrongman.org — visible to fans, media, federations and sponsors worldwide.</div>
        </td>
      </tr></table>

      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:14px;"><tr>
        <td width="44"><div style="width:36px;height:36px;background:#c9a84c;border-radius:8px;text-align:center;line-height:36px;">📊</div></td>
        <td style="padding-left:14px;">
          <div style="color:#fff;font-size:14px;font-weight:700;margin-bottom:2px;">Official WSM World Ranking</div>
          <div style="color:#888;font-size:13px;">Every result at WSM-sanctioned competitions earns you ranking points. Recognized by 60+ national federations.</div>
        </td>
      </tr></table>

      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:14px;"><tr>
        <td width="44"><div style="width:36px;height:36px;background:#c9a84c;border-radius:8px;text-align:center;line-height:36px;">🤝</div></td>
        <td style="padding-left:14px;">
          <div style="color:#fff;font-size:14px;font-weight:700;margin-bottom:2px;">3 Personal Sponsor Slots — Included</div>
          <div style="color:#888;font-size:13px;">Display your sponsors' logos on your public athlete profile. Give your partners international visibility.</div>
        </td>
      </tr></table>

      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:14px;"><tr>
        <td width="44"><div style="width:36px;height:36px;background:#c9a84c;border-radius:8px;text-align:center;line-height:36px;">🌍</div></td>
        <td style="padding-left:14px;">
          <div style="color:#fff;font-size:14px;font-weight:700;margin-bottom:2px;">International Recognition from {country}</div>
          <div style="color:#888;font-size:13px;">Officially listed as a WSM athlete. Verified status linked to your national federation.</div>
        </td>
      </tr></table>

      <table width="100%" cellpadding="0" cellspacing="0"><tr>
        <td width="44"><div style="width:36px;height:36px;background:#c9a84c;border-radius:8px;text-align:center;line-height:36px;">🎯</div></td>
        <td style="padding-left:14px;">
          <div style="color:#fff;font-size:14px;font-weight:700;margin-bottom:2px;">Championship Entry — Dubai 2026</div>
          <div style="color:#888;font-size:13px;">Official entry to the World Strongman Championship 2026. Live results, protocols and certificates.</div>
        </td>
      </tr></table>
    </div>

    <div style="background:linear-gradient(135deg,#1a1500,#2a2000);border:1px solid #c9a84c;border-radius:12px;padding:28px;margin-bottom:24px;text-align:center;">
      <div style="color:#c9a84c;font-size:11px;letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;">⚡ Exclusive offer for qualified athletes</div>
      <div style="color:#fff;font-size:17px;font-weight:600;margin-bottom:16px;">Register now and get <strong style="color:#c9a84c;">50% OFF</strong> your registration fee</div>
      <div style="background:#c9a84c;color:#000;font-size:26px;font-weight:900;letter-spacing:6px;padding:14px 32px;border-radius:8px;display:inline-block;">{PROMO_CODE}</div>
      <div style="color:#888;font-size:13px;margin-top:14px;">Valid until <strong style="color:#fff;">{DEADLINE}</strong> · Limited spots available</div>
    </div>

    <div style="text-align:center;margin-bottom:24px;">
      <a href="{REGISTER_URL}" style="display:inline-block;background:#c9a84c;color:#000;font-size:16px;font-weight:800;padding:18px 48px;border-radius:10px;text-decoration:none;">
        REGISTER NOW →
      </a>
      <div style="color:#666;font-size:12px;margin-top:10px;">ranking.worldstrongman.org</div>
    </div>

    <div style="background:#1a0a0a;border:1px solid #3a1515;border-radius:10px;padding:16px 20px;margin-bottom:24px;">
      <div style="color:#ff6b6b;font-size:13px;font-weight:600;margin-bottom:4px;">⏰ Limited spots available</div>
      <div style="color:#888;font-size:13px;line-height:1.5;">Promo code <strong style="color:#fff;">WSM50</strong> expires {DEADLINE}. Registration closes when all spots are filled.</div>
    </div>

    <div style="border-top:1px solid #222;padding-top:20px;">
      <div style="color:#fff;font-size:14px;font-weight:600;">WSM Team</div>
      <div style="color:#c9a84c;font-size:13px;">World Strongman International Union</div>
      <div style="color:#555;font-size:12px;margin-top:6px;">📍 Riga, Latvia | Dubai, UAE<br/>🌐 worldstrongman.org</div>
    </div>
  </td></tr>

  <tr><td style="background:#0d0d0d;padding:20px 40px;border-radius:0 0 16px 16px;text-align:center;border-top:1px solid #1a1a1a;">
    <div style="color:#444;font-size:11px;">© 2026 World Strongman International Union · All Rights Reserved</div>
  </td></tr>

</table>
</td></tr>
</table>
</body>
</html>"""

def send_campaign():
    print(f"\n🚀 WSM 2026 Email Campaign")
    print(f"📧 Sending to {len(athletes)} athletes\n")
    
    sent = []
    failed = []

    for i, athlete in enumerate(athletes):
        try:
            params = {
                "from": FROM_EMAIL,
                "to": [athlete["email"]],
                "subject": f"{athlete['name'].split()[0]}, your WSM 2026 spot is reserved — 50% OFF ends {DEADLINE}",
                "html": build_email(athlete),
            }
            email = resend.Emails.send(params)
            sent.append(athlete["name"])
            print(f"✅ [{i+1}/{len(athletes)}] {athlete['name']} → {athlete['email']}")
        except Exception as e:
            failed.append({"name": athlete["name"], "email": athlete["email"], "error": str(e)})
            print(f"❌ [{i+1}/{len(athletes)}] {athlete['name']} → ERROR: {e}")
        
        time.sleep(0.3)

    print(f"\n📊 Results:")
    print(f"   ✅ Sent: {len(sent)}")
    print(f"   ❌ Failed: {len(failed)}")
    
    if failed:
        print(f"\n⚠️  Failed:")
        for f in failed:
            print(f"   - {f['name']} ({f['email']}): {f['error']}")

    print(f"\n✅ Campaign complete!")

if __name__ == "__main__":
    send_campaign()
