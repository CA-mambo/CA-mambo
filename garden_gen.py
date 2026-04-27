import os
import sys
import json
import urllib.request
import random
import datetime

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
    for w in range(53):
        week_data = []
        for d in range(7):
            count = 0
            r = random.random()
            if r > 0.85:
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

# 🏃♀️ Vector Mambo Template
# Drawn using pure SVG shapes for 100% compatibility
MAMBO_SVG_TEMPLATE = '''
<g transform="translate(0, {y})">
    <!-- Vector Mambo -->
    <!-- Ears -->
    <path d="M 6,12 L 4,5 L 8,12 Z" fill="#8B5A2B" />
    <path d="M 10,12 L 12,5 L 8,12 Z" fill="#8B5A2B" />
    <!-- Head -->
    <circle cx="8" cy="12" r="5" fill="#8B5A2B" />
    <!-- Face -->
    <circle cx="8" cy="12" r="4" fill="#FFE4C4" />
    <!-- Eyes -->
    <circle cx="6.5" cy="11" r="0.8" fill="#000" />
    <circle cx="9.5" cy="11" r="0.8" fill="#000" />
    <!-- Hat -->
    <ellipse cx="8" cy="7" rx="4" ry="3" fill="#6A5ACD" />
    <!-- Dress -->
    <rect x="4" y="17" width="8" height="6" fill="#4169E1" />
    
    <!-- Animation -->
    <animateMotion path="M {start_x},0 L {end_x},0" dur="40s" repeatCount="indefinite" />
    <animateTransform attributeName="transform" type="translate" values="0,0; 0,-2; 0,0" dur="0.6s" repeatCount="indefinite" additive="sum" />
</g>
'''

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

    # 2. Draw Grid (Plants & Mud)
    for week_index, week in enumerate(weeks_data):
        x = week_index * (cell_size + gap) + gap
        days = week['contributionDays']
        
        for day_index in range(7):
            if day_index < len(days):
                count = days[day_index]['contributionCount']
            else:
                count = 0 
            
            y = day_index * row_height + gap + header_height
            center_x = x + cell_size / 2
            center_y = y + cell_size / 2 + 1
            
            if count == 0:
                # Draw Mud Emoji
                svg_parts.append(f'<text x="{center_x}" y="{center_y}" text-anchor="middle" dominant-baseline="middle" font-size="12"></text>')
            else:
                # Draw Plant Emoji
                emoji = "🌱"
                if count >= 64:
                    emoji = "🌳" # Tree
                elif is_prime(count):
                    emoji = "🌸" # Flower (Prime)
                
                svg_parts.append(f'<text x="{center_x}" y="{center_y}" text-anchor="middle" dominant-baseline="middle" font-size="12">{emoji}</text>')

    # 3. Patrolling Vector Mambo (Foreground Layer)
    # Mambo walks at y=25 (just below title, above grid)
    mambo_y = 25
    svg_parts.append(MAMBO_SVG_TEMPLATE.format(y=mambo_y, start_x=-20, end_x=svg_width+20))

    # 4. Footer
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
