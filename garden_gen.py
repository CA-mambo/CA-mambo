import os
import sys
import json
import urllib.request
import random
import datetime

def get_token():
    """Try to get token from ENV first, then Keyring."""
    token = os.environ.get("GH_TOKEN")
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
            # Randomly assign contributions (higher probability of 0, some sprouts/flowers)
            count = 0
            r = random.random()
            if r > 0.85:
                count = random.randint(1, 6)
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

    # 2. Draw Grid
    # We also collect coordinates for the animation path
    path_points = []

    for week_index, week in enumerate(weeks_data):
        x = week_index * (cell_size + gap) + gap
        days = week['contributionDays']
        
        for day_index in range(7):
            if day_index < len(days):
                count = days[day_index]['contributionCount']
            else:
                count = 0 
            
            y = day_index * row_height + gap + header_height
            
            fill_color = "#21262d" # Mud (Empty)
            icon = ""
            
            if count > 0:
                # Agent Efficiency Logic: High commit counts need higher thresholds
                if count < 32:
                    fill_color = "#238636" # Sprout (1-31 commits)
                    icon = "🌱"
                elif count < 128:
                    fill_color = "#006d77" # Flowers (32-127 commits) - Extended to cover gap
                    icon = "🌸"
                else:
                    fill_color = "#05461f" # Trees (>= 128 commits)
                    icon = "🌳"
            
            # Draw Cell
            svg_parts.append(f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="{fill_color}" rx="2" />')
            
            # Draw Icon
            if icon:
                center_y = y + cell_size / 2 + 1 
                center_x = x + cell_size / 2
                svg_parts.append(f'<text x="{center_x}" y="{center_y}" text-anchor="middle" dominant-baseline="middle" font-size="10" font-family="sans-serif">{icon}</text>')

    # 3. Animation: The "Watering Cloud" ☁️
    if path_points:
        # Construct path string for animateMotion: M x1,y1 L x2,y2 ...
        # To prevent jumping across large gaps (like weekends), we can insert move commands if distance is too large
        # But for simplicity, let's just connect them.
        
        # A better path logic:
        path_d = "M " + path_points[0]
        for pt in path_points[1:]:
            path_d += f" L {pt}"
            
        svg_parts.append(f'<g>')
        # The Cloud
        svg_parts.append(f'  <text x="0" y="0" font-size="12" text-anchor="middle">☁️</text>')
        # The Path animation
        svg_parts.append(f'  <animateMotion dur="45s" repeatCount="indefinite" path="{path_d}" />')
        svg_parts.append(f'</g>')

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
        # Fallback to mock on error
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