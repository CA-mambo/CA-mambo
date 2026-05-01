import os
import sys
import json
import urllib.request
import random
import datetime
import math
import base64

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
    """Try to get token from ENV first (GH_Token or GH_TOKEN), then Keyring."""
    token = os.environ.get("GH_Token") or os.environ.get("GH_TOKEN")
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

def get_distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def get_gif_base64(gif_path):
    """Read existing GIF file and convert to base64 data URI."""
    try:
        with open(gif_path, 'rb') as f:
            gif_data = f.read()
            b64 = base64.b64encode(gif_data).decode('utf-8')
            return f"data:image/gif;base64,{b64}"
    except Exception as e:
        print(f"Warning: Could not load GIF file. {e}")
        return None

def generate_svg(weeks_data, username, is_mock=False):
    cell_size = 14
    gap = 3
    header_height = 25
    row_height = cell_size + gap

    num_weeks = len(weeks_data)
    svg_width = num_weeks * (cell_size + gap) + gap
    svg_height = 7 * row_height + gap + header_height

    svg_parts = []
    svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}">')
    svg_parts.append(f'<rect width="100%" height="100%" fill="#0d1117" rx="4" />')

    # Header: Image + Text (centered together as a group)
    img_size = 20
    mambo_gif_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mambo_animated.gif")
    image_b64 = get_gif_base64(mambo_gif_path)

    title_text = "mambo's garden 🌸" if not is_mock else "mambo's garden  (Demo)"
    # Estimate text width for centering (~10px per char at 20px font)
    text_est_width = len(title_text) * 10
    img_gap = 20  # two-space gap between image and text
    total_width = img_size + img_gap + text_est_width
    group_center_x = svg_width / 2
    image_x = group_center_x - total_width / 2
    text_x = image_x + img_size + img_gap + text_est_width / 2

    if image_b64:
        svg_parts.append(f'<image href="{image_b64}" x="{image_x}" y="4" width="{img_size}" height="{img_size}" />')
    else:
        svg_parts.append(f'<text x="{image_x}" y="20" font-size="16">🐱</text>')

    svg_parts.append(f'<text x="{text_x}" y="20" text-anchor="middle" fill="#58a6ff" font-size="20" font-family="sans-serif" font-weight="bold">{title_text}</text>')

    # Draw Grid - collect all non-mud positions
    all_interesting_points = []
    for week_index, week in enumerate(weeks_data):
        x = week_index * (cell_size + gap) + gap
        days = week['contributionDays']
        for day_index in range(7):
            count = 0
            if day_index < len(days):
                count = days[day_index]['contributionCount']

            y = day_index * row_height + gap + header_height
            center_x = x + cell_size / 2
            center_y = y + cell_size / 2 + 1

            if count == 0:
                emoji = "🌵" if random.random() < 0.2 else "🟫"
                svg_parts.append(f'<text x="{center_x}" y="{center_y}" text-anchor="middle" dominant-baseline="middle" font-size="12">{emoji}</text>')
                if emoji == "🌵":
                    all_interesting_points.append((center_x, center_y))
            else:
                emoji = "🌱"
                if count >= 64:
                    emoji = "🌳"
                elif is_prime(count):
                    emoji = "🌸"
                svg_parts.append(f'<text x="{center_x}" y="{center_y}" text-anchor="middle" dominant-baseline="middle" font-size="12">{emoji}</text>')
                all_interesting_points.append((center_x, center_y))

    # Build round-trip patrol path: visit all non-mud points, return to start
    if all_interesting_points:
        points = list(all_interesting_points)
        points.sort(key=lambda p: (p[0], p[1]))
        path_points = [points[0]]
        remaining = points[1:]
        current = path_points[0]
        while remaining:
            next_point = min(remaining, key=lambda p: get_distance(current, p))
            path_points.append(next_point)
            remaining.remove(next_point)
            current = next_point

        # Forward path
        forward_d = f"M {path_points[0][0]},{path_points[0][1]}"
        for p in path_points[1:]:
            forward_d += f" L {p[0]},{p[1]}"

        # Return path (reverse, excluding endpoint to avoid duplication)
        return_d = ""
        for p in reversed(path_points[:-1]):
            return_d += f" L {p[0]},{p[1]}"

        # Seamless loop: start == end
        full_patrol_d = forward_d + return_d

        mambo_patrol_b64 = get_gif_base64(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "mambo_animated.gif")
        )

        if mambo_patrol_b64:
            svg_parts.append(f'''
            <g>
                <image href="{mambo_patrol_b64}" x="-9" y="-9" width="18" height="18" />
                <animateMotion path="{full_patrol_d}" dur="120s" repeatCount="indefinite" />
            </g>
            ''')

    svg_parts.append(f'<text x="{svg_width/2}" y="{svg_height-2}" text-anchor="middle" fill="#6e7681" font-size="9" font-family="sans-serif">Generated by garden_gen.py</text>')
    svg_parts.append('</svg>')
    return "\n".join(svg_parts)

def main():
    username = "CA-mambo"
    if len(sys.argv) > 1: username = sys.argv[1]

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