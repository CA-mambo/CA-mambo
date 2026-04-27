import os
import sys
import json
import urllib.request

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

def generate_svg(weeks_data, username):
    cell_size = 14
    gap = 3
    header_height = 20
    row_height = cell_size + gap
    
    num_weeks = len(weeks_data)
    svg_width = num_weeks * (cell_size + gap) + gap 
    svg_height = 7 * row_height + gap + header_height
    
    svg_parts = []
    svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}">')
    svg_parts.append(f'<rect width="100%" height="100%" fill="#0d1117" />')
    svg_parts.append(f'<text x="{svg_width/2}" y="15" text-anchor="middle" fill="#58a6ff" font-size="14" font-family="sans-serif">🌱 {username}\'s Garden</text>')

    for week_index, week in enumerate(weeks_data):
        x = week_index * (cell_size + gap) + gap
        days = week['contributionDays']
        
        for day_index in range(7):
            if day_index < len(days):
                count = days[day_index]['contributionCount']
            else:
                count = 0 
            
            y = day_index * row_height + gap + header_height
            
            fill_color = "#21262d"
            icon = ""
            
            if count > 0:
                if count == 1:
                    fill_color = "#238636"
                    icon = "🌱"
                elif count < 5:
                    fill_color = "#006d77"
                    icon = "🌸"
                else:
                    fill_color = "#05461f"
                    icon = "🌳"
            
            svg_parts.append(f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="{fill_color}" rx="2" />')
            
            if icon:
                center_y = y + cell_size / 2 + 1 
                center_x = x + cell_size / 2
                svg_parts.append(f'<text x="{center_x}" y="{center_y}" text-anchor="middle" dominant-baseline="middle" font-size="10" font-family="sans-serif">{icon}</text>')

    svg_parts.append('</svg>')
    return "\n".join(svg_parts)

def main():
    username = "CA-mambo" 
    if len(sys.argv) > 1:
        username = sys.argv[1]
        
    token = get_token()
    if not token:
        print("Error: No GitHub token found.")
        sys.exit(1)

    print(f"Fetching contributions for {username}...")
    data = fetch_contributions(username, token)
    
    weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
    svg_content = generate_svg(weeks, username)
    
    with open("garden.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("garden.svg generated successfully!")

if __name__ == "__main__":
    main()