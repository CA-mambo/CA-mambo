import os
import sys
import json
import urllib.request
import random
import datetime

# 🏃♀️ Mambo Pixel Sprite (Base64 PNG)
# Generated from user image, resized to 12x12, transparent background
MAMBO_B64 = """iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAYAAABWdVznAAABCGlDQ1BJQ0MgUHJvZmlsZQAAeJxjYGA8wQAELAYMDLl5JUVB7k4KEZFRCuwPGBiBEAwSk4sLGHADoKpv1yBqL+viUYcLcKakFicD6Q9ArFIEtBxopAiQLZIOYWuA2EkQtg2IXV5SUAJkB4DYRSFBzkB2CpCtkY7ETkJiJxcUgdT3ANk2uTmlyQh3M/Ck5oUGA2kOIJZhKGYIYnBncAL5H6IkfxEDg8VXBgbmCQixpJkMDNtbGRgkbiHEVBYwMPC3MDBsO48QQ4RJQWJRIliIBYiZ0tIYGD4tZ2DgjWRgEL7AwMAVDQsIHG5TALvNnSEfCNMZchhSgSKeDHkMyQx6QJYRgwGDIYMZAKbWPz9HbOBQAAACDElEQVR4nGOsZ2Bg+mQRyv7u3a0pz/592qHu3MgpyMmv9uHvv203d1T6c3PxHVp/8dTW0NBQ5tWrV/9laWRg+FdxfRcHt5RegrpxbJKEgCIDBxsfw4trSzNlBPj4fzByHWNAAiwg4o1PvY6QkPxRMRH5a+/ffvC78/T4TJn/51J+i/II3fvFdP4/AwNjg5bWf7gGJkY2Qy4OcaaHz89cFmS499xc6IXNLwZmsb+crAz/vn+3ZGRgeFR/4AAzAwPDP0YGBgYQ/p8XEtL958tbOzkJCTMZKUGGt7/+/f1w5ToTgwDrk59/2S3bVm99CvIvE0hxpINVMP/fd/kyUoJ6Jk4y77yiA/9KqTA/+8PD/oXpH5PQ0/cfk+3t7SGuARFfPvxk+/H9z2+2//9Y5WWNhf4zszEr8KvJ/vz2i/fXn39s37/+fSMmJva/kYHhP8g5DM3ixg7fOZlTbor/UGZhl/qr7Rp99czaSQZ87P8kWXjZMxbsObYN5nSwDb942Nj/cjAzvv/B8P/rp386p3avDOfk4vn1T0q9E6QYFAcgxeBQ+v//PyNjWNieeim+n7r/ZRfc/K38k5X5Hzvb37cKVqps9npqv5d859D6DLMB7CQIYGRYtmyXx5MzW3r+M7F8EBGTuCHnkNPqYsZ5n+H/fwZGRkawDcgArFlFUalbXVm1SkZSMhrEh4UODAAAxqfH5tXGEhUAAAAASUVORK5CYII="""

def is_prime(n):
    """Check if a number is prime."""
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def get_token():
    """Try to get token from ENV first, then Keyring."""
    token = os.environ.get("GH_Token")
    if not token:
        try:
            import keyring
            token = keyring.get_password("github_service", "access_token")
        except Exception:
            pass
    return token

def fetch_contributions(username, token):
    url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    query = """
    query {
      user(login: "%s") {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """ % username
    
    data = json.dumps({"query": query}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            if 'errors' in result:
                print(f"GraphQL Error: {result['errors']}")
                sys.exit(1)
            return result
    except Exception as e:
        print(f"Error fetching data: {e}")
        sys.exit(1)

def generate_mock_data():
    """Generates realistic mock data if token is missing."""
    print("No token found. Generating Mock Data for preview...")
    weeks = []
    current_date = datetime.date.today()
    # Generate 53 weeks of data
    for w in range(53):
        week_data = []
        for d in range(7):
            # Randomly assign contributions
            count = 0
            r = random.random()
            if r > 0.85:
                # Mix of different contribution levels
                count = random.choice([1, 2, 3, 5, 8, 13, 21, 64]) 
            week_data.append({
                "contributionCount": count,
                "date": (current_date - datetime.timedelta(weeks=(52-w), days=(6-d))).isoformat()
            })
        weeks.append({"contributionDays": week_data})
    
    return {
        "data": {
            "user": {
                "contributionsCollection": {
                    "contributionCalendar": {
                        "weeks": weeks
                    }
                }
            }
        }
    }

def generate_svg(weeks_data, username, is_mock=False):
    cell_size = 14
    gap = 3
    header_height = 20
    row_height = cell_size + gap
    
    num_weeks = len(weeks_data)
    svg_width = num_weeks * (cell_size + gap) + gap 
    svg_height = 7 * row_height + gap + header_height
    
    svg_parts = []
    # 1. SVG Header
    svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}">')
    
    # Background
    svg_parts.append(f'<rect width="100%" height="100%" fill="#0d1117" rx="4" />')
    
    # Title
    title_text = "🌱 Mambo's Garden" if not is_mock else "🌱 Mambo's Garden (Demo)"
    svg_parts.append(f'<text x="{svg_width/2}" y="15" text-anchor="middle" fill="#58a6ff" font-size="14" font-family="sans-serif" font-weight="bold">{title_text}</text>')

    # 2. Draw Grid (Pixel Mambo + Mud)
    for week_index, week in enumerate(weeks_data):
        x = week_index * (cell_size + gap) + gap
        days = week['contributionDays']
        
        for day_index in range(7):
            if day_index < len(days):
                count = days[day_index]['contributionCount']
            else:
                count = 0 
            
            y = day_index * row_height + gap + header_height
            
            # Logic:
            # If 0 commits -> Draw Mud Emoji 
            # If > 0 commits -> Draw Mambo Pixel Sprite
            
            if count == 0:
                # Draw Mud Emoji
                center_x = x + cell_size / 2
                center_y = y + cell_size / 2 + 1
                svg_parts.append(f'<text x="{center_x}" y="{center_y}" text-anchor="middle" dominant-baseline="middle" font-size="12">🟫</text>')
            else:
                # Draw Mambo Image with floating animation
                # Use SMIL animateTransform for "movement/breathing"
                svg_parts.append(f'''
                <g transform="translate({x}, {y})">
                    <image href="data:image/png;base64,{MAMBO_B64}" width="14" height="14" x="0" y="0" />
                    <animateTransform attributeName="transform" type="translate" values="0,0; 0,-1; 0,0" dur="1.5s" repeatCount="indefinite" />
                </g>
                ''')

    # 3. Footer
    svg_parts.append(f'<text x="{svg_width/2}" y="{svg_height-2}" text-anchor="middle" fill="#6e7681" font-size="9" font-family="sans-serif">Generated by garden_gen.py</text>')

    svg_parts.append('</svg>')
    return "\n".join(svg_parts)

def main():
    username = "CA-mambo" 
    if len(sys.argv) > 1:
        username = sys.argv[1]
        
    print(f"Initializing Garden Generator for {username}...")
    token = get_token()
    
    is_mock = False
    if not token:
        data = generate_mock_data()
        is_mock = True
    else:
        print(f"Fetching real contributions...")
        data = fetch_contributions(username, token)

    try:
        weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
    except KeyError:
        print("Failed to parse calendar data.")
        data = generate_mock_data()
        weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
        is_mock = True

    svg_content = generate_svg(weeks, username, is_mock=is_mock)
    
    output_file = "garden.svg"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Successfully generated {output_file}! (Mock Mode: {is_mock})")

if __name__ == "__main__":
    main()
